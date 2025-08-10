# Enhanced Personal Weather Station Monitor for Weather Underground PWS

A real-time weather monitoring tool with htop-like interface, colorized displays, and inline historical trend graphs optimized for small terminal windows.

Requires a Weather Underground compatible Personal Weather Station. (Such as the AcuRite Iris)

## ✨ Key Features

### 🎨 Compact htop-like Interface
- **Rich terminal graphics** using the `rich` library
- **Single-column layout** optimized for small terminal windows (60+ characters wide)
- **Live updating display** with professional styling and borders
- **Responsive design** that works perfectly in narrow terminals, SSH sessions, and mobile apps
- **Split-screen friendly** for side-by-side terminal usage

### 📊 Inline Real-time Graphs
- **ASCII sparkline charts** integrated directly with current readings
- **Compact 25-character graphs** showing temperature, humidity, pressure, and wind trends
- **Historical data tracking** (keeps last 60 readings = 1 hour)
- **Compressed min/max ranges** displayed alongside each graph
- **Trend indicators** showing if values are rising ↗, falling ↘, or stable ─

### 🌈 Color Coding
Weather values are automatically color-coded based on ranges:

#### Temperature Colors:
- 🔵 **Blue**: ≤32°F (freezing)
- 🔷 **Cyan**: 33-50°F (cold)  
- 🟢 **Green**: 51-75°F (comfortable)
- 🟡 **Yellow**: 76-90°F (warm)
- 🔴 **Red**: >90°F (hot)

#### Humidity Colors:
- 🟡 **Yellow**: <30% (dry)
- 🟢 **Green**: 30-70% (comfortable)
- 🔷 **Cyan**: >70% (humid)

#### Wind Speed Colors:
- 🟢 **Green**: <10 mph (calm)
- 🟡 **Yellow**: 10-25 mph (moderate)
- 🔴 **Red**: >25 mph (strong)

### 🔧 Enhanced Functionality
- **Fallback mode** for systems without rich library
- **Configurable refresh interval** (default 60s)
- **Better error handling** and display
- **Cross-platform compatibility** (Windows/Linux/macOS)

## 🔑 Getting Your API Key

Before using the weather monitor, you need to obtain a Weather Underground API key. Here's how to extract it from any Weather Underground Personal Weather Station page:

### Method 1: Browser Developer Tools (Recommended)

1. **Visit any Weather Underground PWS page**:
   - Go to `https://www.wunderground.com/dashboard/pws/[STATION_ID]`
   
2. **Open Developer Tools**:
   - **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I`
   - **Firefox**: Press `F12` or `Ctrl+Shift+I`
   - **Safari**: Press `Cmd+Option+I` (Mac)

3. **Monitor Network Traffic**:
   - Click the **Network** tab in Developer Tools
   - Refresh the page (`F5` or `Ctrl+R`)
   - In the filter box, type: `observations/current`

4. **Find the API Request**:
   - Look for a request URL that contains:
     ```
     api.weather.com/v2/pws/observations/current
     ```
   - Click on this request to view details

5. **Extract the API Key**:
   - In the request details, look at the **Query String Parameters** or **Request URL**
   - Find the parameter named `apiKey`
   - Copy the long string value (usually 32 characters)
   - Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6` (32-character string)

### Method 2: Page Source Analysis

1. **Right-click** on the Weather Underground PWS page
2. **Select "View Page Source"** or press `Ctrl+U`
3. **Search for the API key** using `Ctrl+F`:
   - Search for: `apiKey`
   - Or search for: `api.weather.com`
4. **Copy the key** from the JavaScript code

### Method 3: Browser Console

1. **Open Developer Tools** (`F12`)
2. **Go to Console tab**
3. **Paste and run** this JavaScript code:
   ```javascript
   // Extract API key from page scripts
   let scripts = document.getElementsByTagName('script');
   for (let script of scripts) {
       if (script.innerHTML.includes('apiKey')) {
           let match = script.innerHTML.match(/apiKey["':]\s*["']([^"']+)["']/i);
           if (match) {
               console.log('Found API Key:', match[1]);
               break;
           }
       }
   }
   ```

### 🔧 Configure Your Application

Once you have your API key:

1. **Open** `weather_monitor_enhanced.py`
2. **Find this line** (around line 42):
   ```python
   API_KEY = "YOUR_API_KEY_HERE"  # Replace with your valid API key
   ```
3. **Replace** the example key with your extracted key:
   ```python
   API_KEY = "your_actual_api_key_here"
   ```
4. **Save the file**

### 🛡️ Security Notes

- **API keys are sensitive**: Don't share them publicly
- **Rate limits apply**: Weather Underground may limit requests per key
- **Keys may expire**: If your key stops working, repeat the extraction process
- **Use responsibly**: Don't make excessive requests (default 60s interval is appropriate)

### ⚠️ Troubleshooting API Key Issues

**If you get "Invalid API key" errors:**
- The key may have expired - extract a fresh one
- Ensure you copied the complete key (no extra spaces/characters)
- Try a different PWS station page for key extraction

**If you can't find the API key:**
- Make sure the PWS page fully loaded before checking network traffic
- Try disabling ad blockers which might interfere with API calls
- Use a different browser if the network requests aren't visible

### 📍 Finding Weather Station IDs

To find Personal Weather Station IDs to monitor:

1. **Browse Weather Underground's PWS Map**:
   - Visit: `https://www.wunderground.com/wundermap`
   - Zoom into your area of interest
   - Click on weather station icons to see their details
   - The station ID will be shown (e.g., "KCOHOTSU8")

2. **Search by Location**:
   - Go to: `https://www.wunderground.com/`
   - Search for your city/location
   - Look for "Personal Weather Stations" section
   - Click on any station to see its ID in the URL

3. **Direct URL Pattern**:
   - PWS URLs follow this format:
   - `https://www.wunderground.com/dashboard/pws/[STATION_ID]`
   - The STATION_ID is what you'll use with the application

## 🚀 Quick Start

### Installation
1. **Install dependencies:**
   ```powershell
   # Windows (PowerShell)
   .\setup.ps1
   
   # Or manually:
   pip install -r requirements.txt
   ```

2. **Run the monitor:**
   ```bash
   # Using Python directly
   python weather_monitor_enhanced.py YOUR_STATION_ID
   
   # Using the Windows batch file (convenience wrapper)
   run.bat
   ```
   
   > **Note**: The `run.bat` file is a Windows convenience wrapper that automatically launches the Python script. You'll need to edit the batch file and replace `[STATION-ID]` with your actual station ID before using it.

### Usage Examples
```bash
# Basic usage with 60s refresh
python weather_monitor_enhanced.py YOUR_STATION_ID

# Custom refresh interval (30 seconds)
python weather_monitor_enhanced.py YOUR_STATION_ID --interval 30

# Help
python weather_monitor_enhanced.py --help
```

## 📋 Requirements

- Python 3.7+
- Dependencies (auto-installed by setup.ps1):
  - `requests>=2.25.1` - API calls
  - `rich>=13.0.0` - Terminal graphics
  - `colorama>=0.4.4` - Cross-platform colors

## 📱 Compact Layout Showcase

The single-column design maximizes information density while remaining readable in small terminals:

```
┌─── Weather Monitor - YOUR_STATION_ID ────────────────────┐
│ Temperature: │ 75.2°F      │ ↗ │ ▃▄▅▆▇▆▅▄▃▂ (72-78°F)  │
│ Feels Like:  │ 78.1°F      │   │                        │
│ Humidity:    │ 65%         │ ─ │ ▆▅▄▄▅▅▆▆▅▄ (60-70%)   │
│ Wind Speed:  │ 5.2 mph N   │ ↘ │ ▂▁▂▃▄▃▂▁▂▁ (0-8mph)    │
│ Pressure:    │ 29.95 inHg  │ ↗ │ ▃▃▄▄▅▅▆▆▇▇ (29.90...)  │
│              │ Showing 12 readings  │                    │
└──────────────────────────────────────────────────────────┘
```

### Layout Benefits:
- **Minimum width**: Works in terminals as narrow as 60 characters
- **Integrated graphs**: Sparklines show alongside current values
- **Trend arrows**: Instant visual feedback on data direction
- **Compact ranges**: Min/max values in parentheses save space
- **Smart spacing**: Optimal use of available terminal real estate

## 🎯 Perfect Use Cases

### 📱 Mobile & Small Screens
- **SSH sessions** from phones/tablets
- **Terminal apps** on mobile devices
- **Narrow terminal windows** on desktop

### 💻 Development & Multi-tasking
- **Split-screen development** - monitor weather while coding
- **Tmux/screen sessions** with multiple panes
- **Small terminal multiplexer windows**
- **Docker container monitoring** with limited width

### 🌐 Remote & Embedded Systems
- **Raspberry Pi** weather stations
- **Remote server monitoring** via SSH
- **IoT device terminals** with constrained displays
- **Terminal-only environments** without GUI

## 📁 File Structure

```
PWS/
├── weather_monitor_enhanced.py  # New enhanced PWS monitor
├── requirements.txt            # Dependencies
├── setup.ps1                   # Windows setup script
└── README.md                   # This file
```

## ⚙️ Configuration

You can customize the weather thresholds by modifying the `WeatherThresholds` class:

```python
@dataclass
class WeatherThresholds:
    temp_cold: float = 32.0      # Blue threshold
    temp_cool: float = 50.0      # Cyan threshold  
    temp_warm: float = 75.0      # Green threshold
    temp_hot: float = 90.0       # Yellow threshold
    
    humidity_low: float = 30.0   # Dry threshold
    humidity_high: float = 70.0  # Humid threshold
    
    wind_moderate: float = 10.0  # Moderate wind
    wind_strong: float = 25.0    # Strong wind
```

## 🐛 Troubleshooting

### Rich Library Not Available
The application automatically falls back to a simpler display mode if the `rich` library isn't installed.

### Terminal Compatibility
- **Windows**: Works with PowerShell, Command Prompt, Windows Terminal
- **Linux/macOS**: Works with any modern terminal
- **Best experience**: Windows Terminal or modern terminal emulators

### Performance
- Uses minimal CPU (updates every 60s by default)
- Memory usage is bounded (max 60 data points stored)
- Network requests are cached until next update cycle

## 🔮 Future Enhancements

Potential additions for the next version:
- **Historical data persistence** (save to file)
- **Multiple station monitoring**
- **Weather alerts** based on thresholds
- **Export functionality** (CSV, JSON)
- **Web dashboard** interface
- **Mobile-responsive** terminal UI

---

## 📝 Important Setup Reminders

### Before First Run:
1. **Get your API key** following the [🔑 Getting Your API Key](#-getting-your-api-key) section
2. **Update the code** with your API key in `weather_monitor_enhanced.py`
3. **Find a station ID** using the [📍 Finding Weather Station IDs](#-finding-weather-station-ids) guide
4. **Install dependencies** with `pip install -r requirements.txt` or `./setup.ps1`

### Example Commands:
```bash
# Replace KCOHOTSU8 with your chosen station ID
python weather_monitor_enhanced.py YOUR_STATION_ID

# For a station near Denver, CO:
python weather_monitor_enhanced.py KCODENVER123

# For faster updates (30 seconds):
python weather_monitor_enhanced.py YOUR_STATION_ID --interval 30
```

### Quick Test:
To verify everything works, try with a known active station like `KCOHOTSU8` first, then switch to your preferred local station.

**Happy weather monitoring! 🌤️**
