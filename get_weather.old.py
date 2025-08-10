import requests
import argparse
import sys
import time
import os
from datetime import datetime
import json

# --- Configuration ---
API_URL = "https://api.weather.com/v2/pws/observations/current"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your valid API key from Weather Underground
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# --- NEW: Set the refresh interval in seconds ---
UPDATE_INTERVAL_SECONDS = 60

# --- NEW: Helper function to clear the console screen ---
def clear_screen():
    """Clears the terminal screen, works on Windows, Linux, and macOS."""
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

def fetch_weather_data(station_id: str):
    """Fetches the latest observation data for a given PWS station ID."""
    params = {"stationId": station_id, "format": "json", "units": "e", "apiKey": API_KEY}
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and "observations" in data and len(data["observations"]) > 0:
            return data["observations"][0]
        else:
            return {"error": f"No observation data found for '{station_id}'."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network request failed: {e}"}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON from server."}

def display_data(obs_data: dict, station_id: str):
    """Formats and prints the weather data to the console."""
    clear_screen()
    print("=" * 45)
    print(f"  Real-Time Weather Monitor: {station_id}")
    print(f"  (Refreshing every {UPDATE_INTERVAL_SECONDS}s. Press Ctrl+C to exit)")
    print("=" * 45)

    # --- NEW: Handle potential errors returned from the fetch function ---
    if "error" in obs_data:
        print(f"\nAn error occurred: {obs_data['error']}")
        print(f"Retrying in {UPDATE_INTERVAL_SECONDS} seconds...")
        return

    imperial = obs_data.get('imperial', {})
    obs_time_epoch = obs_data.get('epoch')
    obs_time_local = datetime.fromtimestamp(obs_time_epoch).strftime('%Y-%m-%d %I:%M:%S %p')

    print(f"Last Updated:   {obs_time_local}\n")
    print(f"Temperature:    {imperial.get('temp', 'N/A')} °F")
    print(f"Feels Like:     {imperial.get('heatIndex', 'N/A')} °F")
    print(f"Dew Point:      {imperial.get('dewpt', 'N/A')} °F")
    print(f"Humidity:       {obs_data.get('humidity', 'N/A')} %")
    print("-" * 45)
    print(f"Wind Speed:     {imperial.get('windSpeed', 'N/A')} mph from {obs_data.get('winddir', 'N/A')}°")
    print(f"Wind Gust:      {imperial.get('windGust', 'N/A')} mph")
    print("-" * 45)
    print(f"Pressure:       {imperial.get('pressure', 'N/A')} inHg")
    print(f"Precip. Rate:   {imperial.get('precipRate', 'N/A')} in/hr")
    print(f"Precip. Total:  {imperial.get('precipTotal', 'N/A')} in")
    print("=" * 45)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor current weather data from a Weather Underground PWS in real-time."
    )
    parser.add_argument("station_id", help="The PWS station ID to query (e.g., KCOHOTSU8).")
    args = parser.parse_args()
    station = args.station_id

    # --- NEW: The main monitoring loop ---
    try:
        while True:
            observations = fetch_weather_data(station)
            display_data(observations, station_id=station)
            time.sleep(UPDATE_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        # This block runs when the user presses Ctrl+C
        print("\n\nMonitor stopped. Exiting.")
        sys.exit(0)