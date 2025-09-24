# Microgrid Monitoring System

This project consists of two main components:
1. **Server-side Data Simulation** - Generates realistic microgrid data
2. **Client-side Dashboard** - Interactive web dashboard for monitoring

## Server Setup (Python)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI Server
```bash
python microgrid_server.py
```

The server will start on `http://localhost:8000` with:
- WebSocket endpoint: `ws://localhost:8000/ws`
- REST API: `http://localhost:8000/current-data`

### 3. Test Data Generation
```bash
python simple_data_generator.py
```

## Client Setup (Web Dashboard)

The dashboard is a self-contained HTML/CSS/JavaScript application that connects to the server via WebSocket.

### Features
- **Real-time Data Display**: Updates every 2 seconds
- **Generation Monitoring**: Solar, wind, and biogas power tracking
- **Battery Management**: SOC, SoH, and thermal monitoring
- **Power Flow Visualization**: Interactive system diagram
- **Weather Integration**: Real-time weather data affecting generation
- **Alert System**: Automated notifications for system issues
- **Performance Metrics**: Efficiency tracking and power quality

### Data Sources Simulated

#### Solar Generation
- DC/AC power output based on irradiance and temperature
- Module temperature effects on efficiency
- Weather-dependent variations

#### Wind Generation  
- Power curve simulation based on wind speed
- Realistic efficiency variations

#### Battery Storage
- Dynamic SOC calculations for multiple battery packs
- State of Health (SoH) monitoring
- Temperature and voltage tracking
- Charge/discharge power management

#### System Metrics
- Overall efficiency targeting 15-20% improvement
- Uptime monitoring (>99% target)
- Power quality (voltage ±2%, THD <3%)

## Usage

1. Start the Python server: `python microgrid_server.py`
2. Open the web dashboard in a browser
3. Monitor real-time microgrid data
4. Interact with the dashboard panels for detailed views

## Architecture

```
┌─────────────────┐    WebSocket/HTTP    ┌──────────────────┐
│                 │ ◄─────────────────► │                  │
│  Web Dashboard  │                     │  FastAPI Server  │
│  (Client-side)  │                     │  (Data Simulator)│
│                 │                     │                  │
└─────────────────┘                     └──────────────────┘
      │                                           │
      ▼                                           ▼
┌─────────────────┐                     ┌──────────────────┐
│ Real-time UI    │                     │ Fake IoT Data    │
│ • Charts        │                     │ • Solar/Wind/CBG │
│ • Gauges        │                     │ • Battery SOC    │
│ • Alerts        │                     │ • Weather Data   │
│ • Power Flow    │                     │ • System Metrics │
└─────────────────┘                     └──────────────────┘
```

## Data Format

The server generates JSON data with the following structure:

```json
{
  "timestamp": "2025-09-25T14:23:15",
  "generation": {
    "solar": {"dcPower": 45.8, "acPower": 43.2, "efficiency": 94.3},
    "wind": {"power": 12.3, "windSpeed": 8.2},
    "cbg": {"power": 18.5, "status": "operational"}
  },
  "storage": {
    "overallSOC": 67,
    "batteryPacks": [...]
  },
  "demand": {"totalLoad": 65.5},
  "systemMetrics": {"overallEfficiency": 92.8},
  "weather": {"temperature": 28.5, "irradiance": 875}
}
```
