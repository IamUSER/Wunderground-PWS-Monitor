#!/usr/bin/env python3
"""
Enhanced Personal Weather Station Monitor
Features:
- htop-like interface with real-time graphs
- Color-coded displays based on weather ranges
- Historical data tracking with sparklines
- 60-second refresh cycle
"""

import requests
import argparse
import sys
import time
import os
from datetime import datetime, timedelta
import json
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import threading

# Third-party imports (install with: pip install rich colorama)
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.live import Live
    from rich.columns import Columns
    from rich.align import Align
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.rule import Rule
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    
try:
    from colorama import Fore, Back, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# --- Configuration ---
API_URL = "https://api.weather.com/v2/pws/observations/current"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your valid API key from Weather Underground
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
UPDATE_INTERVAL_SECONDS = 60
MAX_HISTORY_POINTS = 60  # Keep 1 hour of data

@dataclass
class WeatherThresholds:
    """Define color thresholds for different weather parameters"""
    # Temperature thresholds (°F)
    temp_cold: float = 32.0
    temp_cool: float = 50.0
    temp_warm: float = 75.0
    temp_hot: float = 90.0
    
    # Humidity thresholds (%)
    humidity_low: float = 30.0
    humidity_high: float = 70.0
    
    # Wind speed thresholds (mph)
    wind_moderate: float = 10.0
    wind_strong: float = 25.0
    
    # Pressure thresholds (inHg)
    pressure_low: float = 29.80
    pressure_high: float = 30.20

class WeatherData:
    """Store and manage historical weather data"""
    
    def __init__(self, max_points: int = MAX_HISTORY_POINTS):
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.temperature = deque(maxlen=max_points)
        self.humidity = deque(maxlen=max_points)
        self.pressure = deque(maxlen=max_points)
        self.wind_speed = deque(maxlen=max_points)
        self.wind_gust = deque(maxlen=max_points)
        self.precip_rate = deque(maxlen=max_points)
        
    def add_observation(self, obs_data: dict):
        """Add new weather observation to history"""
        if "error" in obs_data:
            return
            
        imperial = obs_data.get('imperial', {})
        timestamp = datetime.fromtimestamp(obs_data.get('epoch', time.time()))
        
        self.timestamps.append(timestamp)
        self.temperature.append(self._safe_float(imperial.get('temp')))
        self.humidity.append(self._safe_float(obs_data.get('humidity')))
        self.pressure.append(self._safe_float(imperial.get('pressure')))
        self.wind_speed.append(self._safe_float(imperial.get('windSpeed')))
        self.wind_gust.append(self._safe_float(imperial.get('windGust')))
        self.precip_rate.append(self._safe_float(imperial.get('precipRate')))
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def get_sparkline(self, data_series: deque, width: int = 50) -> str:
        """Generate ASCII sparkline from data series"""
        if not data_series or len(data_series) < 2:
            return "─" * width
            
        # Filter out None values
        values = [v for v in data_series if v is not None]
        if len(values) < 2:
            return "─" * width
            
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return "─" * width
            
        # Create sparkline characters
        chars = "▁▂▃▄▅▆▇█"
        sparkline = ""
        
        # Sample data points to fit width
        step = max(1, len(values) // width)
        sampled_values = values[::step][:width]
        
        for value in sampled_values:
            normalized = (value - min_val) / (max_val - min_val)
            char_index = min(len(chars) - 1, int(normalized * (len(chars) - 1)))
            sparkline += chars[char_index]
            
        return sparkline.ljust(width, "─")

class WeatherMonitor:
    """Main weather monitoring class"""
    
    def __init__(self, station_id: str):
        self.station_id = station_id
        self.weather_data = WeatherData()
        self.thresholds = WeatherThresholds()
        self.last_update = None
        self.error_message = None
        
        # Initialize colorama for Windows compatibility
        if COLORAMA_AVAILABLE:
            colorama_init()
            
        # Setup console
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
    
    def fetch_weather_data(self) -> dict:
        """Fetch weather data from API"""
        params = {"stationId": self.station_id, "format": "json", "units": "e", "apiKey": API_KEY}
        headers = {"User-Agent": USER_AGENT}
        
        try:
            response = requests.get(API_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            if not response.text:
                return {"error": "Received empty response from server"}
                
            data = response.json()
            if data and "observations" in data and len(data["observations"]) > 0:
                return data["observations"][0]
            else:
                return {"error": f"No observation data found for '{self.station_id}'"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Network request failed: {e}"}
        except json.JSONDecodeError:
            return {"error": "Invalid response format. Check API key and station ID"}
    
    def get_color_for_temperature(self, temp: Optional[float]) -> str:
        """Get color code for temperature value"""
        if temp is None:
            return "white"
        elif temp <= self.thresholds.temp_cold:
            return "blue"
        elif temp <= self.thresholds.temp_cool:
            return "cyan"
        elif temp <= self.thresholds.temp_warm:
            return "green"
        elif temp <= self.thresholds.temp_hot:
            return "yellow"
        else:
            return "red"
    
    def get_color_for_humidity(self, humidity: Optional[float]) -> str:
        """Get color code for humidity value"""
        if humidity is None:
            return "white"
        elif humidity < self.thresholds.humidity_low:
            return "yellow"
        elif humidity > self.thresholds.humidity_high:
            return "cyan"
        else:
            return "green"
    
    def get_color_for_wind(self, wind_speed: Optional[float]) -> str:
        """Get color code for wind speed"""
        if wind_speed is None:
            return "white"
        elif wind_speed < self.thresholds.wind_moderate:
            return "green"
        elif wind_speed < self.thresholds.wind_strong:
            return "yellow"
        else:
            return "red"
    
    def create_rich_display(self, obs_data: dict) -> Layout:
        """Create rich terminal display layout"""
        # Create main layout structure - single column for small windows
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_text = Text(f"Personal Weather Station Monitor - {self.station_id}", style="bold cyan")
        header_text.append(f"\nRefreshing every {UPDATE_INTERVAL_SECONDS}s • Press Ctrl+C to exit", style="dim")
        layout["header"].update(Panel(Align.center(header_text), border_style="cyan"))
        
        # Handle errors
        if "error" in obs_data:
            error_panel = Panel(
                Text(f"Error: {obs_data['error']}", style="bold red"),
                title="Connection Error",
                border_style="red"
            )
            layout["main"].update(error_panel)
        else:
            # Combined current conditions and trends
            layout["main"].update(self.create_combined_panel(obs_data))
        
        # Footer
        footer_text = ""
        if self.last_update:
            footer_text = f"Last updated: {self.last_update.strftime('%Y-%m-%d %I:%M:%S %p')}"
        layout["footer"].update(Panel(Text(footer_text, style="dim"), border_style="dim"))
        
        return layout
    
    def create_current_conditions_panel(self, obs_data: dict) -> Panel:
        """Create current conditions display panel"""
        imperial = obs_data.get('imperial', {})
        
        # Extract values
        temp = self._safe_float(imperial.get('temp'))
        feels_like = self._safe_float(imperial.get('heatIndex'))
        humidity = self._safe_float(obs_data.get('humidity'))
        wind_speed = self._safe_float(imperial.get('windSpeed'))
        wind_gust = self._safe_float(imperial.get('windGust'))
        pressure = self._safe_float(imperial.get('pressure'))
        precip_rate = self._safe_float(imperial.get('precipRate'))
        
        # Create table
        table = Table(show_header=False, show_lines=True, box=None)
        table.add_column("Parameter", style="bold")
        table.add_column("Value")
        table.add_column("Trend", width=8)
        
        # Add rows with colors
        table.add_row(
            "Temperature",
            Text(f"{temp:.1f}°F" if temp else "N/A", style=self.get_color_for_temperature(temp)),
            self._get_trend_indicator(self.weather_data.temperature)
        )
        
        table.add_row(
            "Feels Like",
            Text(f"{feels_like:.1f}°F" if feels_like else "N/A", style=self.get_color_for_temperature(feels_like)),
            ""
        )
        
        table.add_row(
            "Humidity",
            Text(f"{humidity:.0f}%" if humidity else "N/A", style=self.get_color_for_humidity(humidity)),
            self._get_trend_indicator(self.weather_data.humidity)
        )
        
        table.add_row(
            "Wind Speed",
            Text(f"{wind_speed:.1f} mph" if wind_speed else "N/A", style=self.get_color_for_wind(wind_speed)),
            self._get_trend_indicator(self.weather_data.wind_speed)
        )
        
        if wind_gust and wind_gust > 0:
            table.add_row(
                "Wind Gust",
                Text(f"{wind_gust:.1f} mph", style=self.get_color_for_wind(wind_gust)),
                ""
            )
        
        table.add_row(
            "Pressure",
            Text(f"{pressure:.2f} inHg" if pressure else "N/A", style="green"),
            self._get_trend_indicator(self.weather_data.pressure)
        )
        
        if precip_rate and precip_rate > 0:
            table.add_row(
                "Precip Rate",
                Text(f"{precip_rate:.2f} in/hr", style="blue"),
                ""
            )
        
        return Panel(table, title="Current Conditions", border_style="green")
    
    def create_graphs_panel(self) -> Panel:
        """Create graphs display panel"""
        if len(self.weather_data.temperature) < 2:
            return Panel("Collecting data for graphs...", title="Trends", border_style="yellow")
        
        content = []
        
        # Temperature graph
        if self.weather_data.temperature:
            temp_values = [t for t in self.weather_data.temperature if t is not None]
            if temp_values:
                temp_sparkline = self.weather_data.get_sparkline(self.weather_data.temperature, 40)
                temp_range = f"{min(temp_values):.1f}°F - {max(temp_values):.1f}°F"
                content.append(f"Temperature:  {temp_sparkline} ({temp_range})")
        
        # Humidity graph
        if self.weather_data.humidity:
            humidity_values = [h for h in self.weather_data.humidity if h is not None]
            if humidity_values:
                humidity_sparkline = self.weather_data.get_sparkline(self.weather_data.humidity, 40)
                humidity_range = f"{min(humidity_values):.0f}% - {max(humidity_values):.0f}%"
                content.append(f"Humidity:     {humidity_sparkline} ({humidity_range})")
        
        # Pressure graph
        if self.weather_data.pressure:
            pressure_values = [p for p in self.weather_data.pressure if p is not None]
            if pressure_values:
                pressure_sparkline = self.weather_data.get_sparkline(self.weather_data.pressure, 40)
                pressure_range = f"{min(pressure_values):.2f} - {max(pressure_values):.2f} inHg"
                content.append(f"Pressure:     {pressure_sparkline} ({pressure_range})")
        
        # Wind speed graph
        if self.weather_data.wind_speed:
            wind_values = [w for w in self.weather_data.wind_speed if w is not None]
            if wind_values:
                wind_sparkline = self.weather_data.get_sparkline(self.weather_data.wind_speed, 40)
                wind_range = f"{min(wind_values):.1f} - {max(wind_values):.1f} mph"
                content.append(f"Wind Speed:   {wind_sparkline} ({wind_range})")
        
        graph_text = Text("\n".join(content) if content else "No graph data available")
        return Panel(graph_text, title=f"Trends (Last {len(self.weather_data.timestamps)} readings)", border_style="blue")
    
    def create_combined_panel(self, obs_data: dict) -> Panel:
        """Create combined current conditions and trends panel for small windows"""
        imperial = obs_data.get('imperial', {})
        
        # Extract values
        temp = self._safe_float(imperial.get('temp'))
        feels_like = self._safe_float(imperial.get('heatIndex'))
        humidity = self._safe_float(obs_data.get('humidity'))
        wind_speed = self._safe_float(imperial.get('windSpeed'))
        wind_gust = self._safe_float(imperial.get('windGust'))
        wind_dir = obs_data.get('winddir', 'N/A')
        pressure = self._safe_float(imperial.get('pressure'))
        precip_rate = self._safe_float(imperial.get('precipRate'))
        
        # Create compact table with conditions and inline graphs
        table = Table(show_header=False, show_lines=False, box=None, padding=(0, 1))
        table.add_column("Parameter", style="bold", width=12)
        table.add_column("Value", width=12)
        table.add_column("Trend", width=4)
        table.add_column("Graph", min_width=20)
        
        # Get appropriate graph width based on available space
        graph_width = 25  # Compact size for small windows
        
        # Temperature row
        temp_graph = ""
        if len(self.weather_data.temperature) > 1:
            temp_values = [t for t in self.weather_data.temperature if t is not None]
            if temp_values:
                temp_graph = self.weather_data.get_sparkline(self.weather_data.temperature, graph_width)
                temp_range = f"({min(temp_values):.0f}-{max(temp_values):.0f}°F)"
                temp_graph += f" {temp_range}"
        
        table.add_row(
            "Temperature:",
            Text(f"{temp:.1f}°F" if temp else "N/A", style=self.get_color_for_temperature(temp)),
            self._get_trend_indicator(self.weather_data.temperature),
            Text(temp_graph, style="dim")
        )
        
        # Feels Like row (no graph)
        table.add_row(
            "Feels Like:",
            Text(f"{feels_like:.1f}°F" if feels_like else "N/A", style=self.get_color_for_temperature(feels_like)),
            "",
            ""
        )
        
        # Humidity row
        humidity_graph = ""
        if len(self.weather_data.humidity) > 1:
            humidity_values = [h for h in self.weather_data.humidity if h is not None]
            if humidity_values:
                humidity_graph = self.weather_data.get_sparkline(self.weather_data.humidity, graph_width)
                humidity_range = f"({min(humidity_values):.0f}-{max(humidity_values):.0f}%)"
                humidity_graph += f" {humidity_range}"
        
        table.add_row(
            "Humidity:",
            Text(f"{humidity:.0f}%" if humidity else "N/A", style=self.get_color_for_humidity(humidity)),
            self._get_trend_indicator(self.weather_data.humidity),
            Text(humidity_graph, style="dim")
        )
        
        # Wind Speed row
        wind_graph = ""
        if len(self.weather_data.wind_speed) > 1:
            wind_values = [w for w in self.weather_data.wind_speed if w is not None]
            if wind_values:
                wind_graph = self.weather_data.get_sparkline(self.weather_data.wind_speed, graph_width)
                wind_range = f"({min(wind_values):.0f}-{max(wind_values):.0f}mph)"
                wind_graph += f" {wind_range}"
        
        wind_display = f"{wind_speed:.1f} mph" if wind_speed else "N/A"
        if wind_dir != 'N/A' and wind_speed:
            wind_display += f" from {wind_dir}°"
        
        table.add_row(
            "Wind Speed:",
            Text(wind_display, style=self.get_color_for_wind(wind_speed)),
            self._get_trend_indicator(self.weather_data.wind_speed),
            Text(wind_graph, style="dim")
        )
        
        # Wind Gust row (if applicable)
        if wind_gust and wind_gust > 0:
            table.add_row(
                "Wind Gust:",
                Text(f"{wind_gust:.1f} mph", style=self.get_color_for_wind(wind_gust)),
                "",
                ""
            )
        
        # Pressure row
        pressure_graph = ""
        if len(self.weather_data.pressure) > 1:
            pressure_values = [p for p in self.weather_data.pressure if p is not None]
            if pressure_values:
                pressure_graph = self.weather_data.get_sparkline(self.weather_data.pressure, graph_width)
                pressure_range = f"({min(pressure_values):.2f}-{max(pressure_values):.2f}inHg)"
                pressure_graph += f" {pressure_range}"
        
        table.add_row(
            "Pressure:",
            Text(f"{pressure:.2f} inHg" if pressure else "N/A", style="green"),
            self._get_trend_indicator(self.weather_data.pressure),
            Text(pressure_graph, style="dim")
        )
        
        # Precipitation row (if applicable)
        if precip_rate and precip_rate > 0:
            table.add_row(
                "Precip Rate:",
                Text(f"{precip_rate:.2f} in/hr", style="blue"),
                "",
                ""
            )
        
        # Add a separator line and data status
        if len(self.weather_data.temperature) < 2:
            table.add_row("", "", "", "")
            table.add_row("", Text("Collecting trend data...", style="dim italic"), "", "")
        else:
            readings_count = len(self.weather_data.timestamps)
            table.add_row("", "", "", "")
            table.add_row("", Text(f"Showing {readings_count} readings", style="dim italic"), "", "")
        
        title = f"Weather Monitor - {self.station_id}"
        return Panel(table, title=title, border_style="cyan", padding=(1, 2))
    
    def _get_trend_indicator(self, data_series: deque) -> Text:
        """Get trend indicator for a data series"""
        if len(data_series) < 3:
            return Text("─", style="dim")
        
        recent_values = [v for v in list(data_series)[-3:] if v is not None]
        if len(recent_values) < 2:
            return Text("─", style="dim")
        
        trend = recent_values[-1] - recent_values[0]
        if abs(trend) < 0.1:  # Minimal change
            return Text("─", style="dim")
        elif trend > 0:
            return Text("↗", style="green")
        else:
            return Text("↘", style="red")
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def create_fallback_display(self, obs_data: dict) -> str:
        """Create fallback display for systems without rich"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"  Personal Weather Station Monitor: {self.station_id}")
        lines.append(f"  (Refreshing every {UPDATE_INTERVAL_SECONDS}s. Press Ctrl+C to exit)")
        lines.append("=" * 70)
        
        if "error" in obs_data:
            lines.append(f"\nError: {obs_data['error']}")
            lines.append(f"Retrying in {UPDATE_INTERVAL_SECONDS} seconds...")
            return "\n".join(lines)
        
        imperial = obs_data.get('imperial', {})
        obs_time_epoch = obs_data.get('epoch')
        obs_time_local = datetime.fromtimestamp(obs_time_epoch).strftime('%Y-%m-%d %I:%M:%S %p')
        
        lines.append(f"\nLast Updated: {obs_time_local}")
        lines.append("")
        
        # Current conditions
        lines.append("CURRENT CONDITIONS:")
        lines.append("-" * 20)
        temp = self._safe_float(imperial.get('temp'))
        lines.append(f"Temperature:    {temp:.1f}°F" if temp else "Temperature:    N/A")
        
        feels_like = self._safe_float(imperial.get('heatIndex'))
        lines.append(f"Feels Like:     {feels_like:.1f}°F" if feels_like else "Feels Like:     N/A")
        
        humidity = self._safe_float(obs_data.get('humidity'))
        lines.append(f"Humidity:       {humidity:.0f}%" if humidity else "Humidity:       N/A")
        
        wind_speed = self._safe_float(imperial.get('windSpeed'))
        wind_dir = obs_data.get('winddir', 'N/A')
        lines.append(f"Wind:           {wind_speed:.1f} mph from {wind_dir}°" if wind_speed else f"Wind:           N/A from {wind_dir}°")
        
        pressure = self._safe_float(imperial.get('pressure'))
        lines.append(f"Pressure:       {pressure:.2f} inHg" if pressure else "Pressure:       N/A")
        
        lines.append("")
        lines.append("TRENDS:")
        lines.append("-" * 10)
        
        if len(self.weather_data.temperature) > 1:
            temp_sparkline = self.weather_data.get_sparkline(self.weather_data.temperature, 30)
            lines.append(f"Temperature:  {temp_sparkline}")
            
            humidity_sparkline = self.weather_data.get_sparkline(self.weather_data.humidity, 30)
            lines.append(f"Humidity:     {humidity_sparkline}")
        else:
            lines.append("Collecting data for trend graphs...")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def run(self):
        """Main monitoring loop"""
        if not RICH_AVAILABLE:
            print("Rich library not found. Using fallback display.")
            print("Install with: pip install rich colorama")
            print("=" * 50)
            time.sleep(2)
        
        try:
            if RICH_AVAILABLE and self.console:
                # Use rich live display
                with Live(refresh_per_second=1) as live:
                    while True:
                        obs_data = self.fetch_weather_data()
                        self.weather_data.add_observation(obs_data)
                        
                        if "error" not in obs_data:
                            self.last_update = datetime.now()
                        
                        layout = self.create_rich_display(obs_data)
                        live.update(layout)
                        
                        time.sleep(UPDATE_INTERVAL_SECONDS)
            else:
                # Fallback to simple display
                while True:
                    obs_data = self.fetch_weather_data()
                    self.weather_data.add_observation(obs_data)
                    
                    if "error" not in obs_data:
                        self.last_update = datetime.now()
                    
                    # Clear screen
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    display = self.create_fallback_display(obs_data)
                    print(display)
                    
                    time.sleep(UPDATE_INTERVAL_SECONDS)
                    
        except KeyboardInterrupt:
            if RICH_AVAILABLE and self.console:
                self.console.print("\n[bold red]Monitor stopped. Exiting.[/bold red]")
            else:
                print("\n\nMonitor stopped. Exiting.")
            sys.exit(0)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Personal Weather Station Monitor with graphs and color coding"
    )
    parser.add_argument("station_id", help="The PWS station ID to query (e.g., KCOHOTSU8)")
    parser.add_argument("--interval", "-i", type=int, default=60, 
                       help="Update interval in seconds (default: 60)")
    
    args = parser.parse_args()
    
    global UPDATE_INTERVAL_SECONDS
    UPDATE_INTERVAL_SECONDS = args.interval
    
    monitor = WeatherMonitor(args.station_id)
    monitor.run()

if __name__ == "__main__":
    main()
