# Microgrid Monitoring System - Complete Integration Guide

## System Overview

Your microgrid monitoring system consists of two main components that work together to provide real-time visualization of your renewable energy system:

### 1. Server-Side Data Simulation (Python)
- **FastAPI WebSocket Server**: Generates realistic microgrid data
- **Real-time Data Streaming**: Updates every 2 seconds via WebSocket
- **Comprehensive Simulation**: Solar, wind, biogas, battery, weather, and system metrics
- **RESTful API**: HTTP endpoint for current data snapshot

### 2. Client-Side Dashboard (Web Application)
- **Interactive Dashboard**: Real-time monitoring interface
- **Professional UI**: Industrial-grade monitoring system appearance
- **Multi-panel Layout**: Generation, storage, demand response, and system metrics
- **Real-time Updates**: WebSocket connection for live data streaming

## Quick Start Guide

### Step 1: Set Up the Python Server

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn websockets numpy pandas
   ```

2. **Start the Server**:
   ```bash
   python microgrid_server.py
   ```

   The server will start on `http://localhost:8000`

3. **Verify Server is Running**:
   - Open `http://localhost:8000` in your browser
   - You should see: `{"message": "Microgrid Simulation Server is running"}`

### Step 2: Open the Dashboard

1. Open the web dashboard in your browser
2. The dashboard will automatically attempt to connect to `ws://localhost:8000/ws`
3. Once connected, you'll see real-time data flowing every 2 seconds

## Data Flow Architecture

```
┌─────────────────────────────────────────┐
│             Python Server               │
│  ┌─────────────────────────────────────┐│
│  │        Data Simulator               ││
│  │  • Solar generation (weather-based) ││
│  │  • Wind turbine simulation          ││
│  │  • Biogas/CBG steady generation     ││
│  │  • Battery SOC dynamics             ││
│  │  • Weather data generation          ││
│  │  • System alerts & monitoring       ││
│  └─────────────────────────────────────┘│
│                    │                    │
│  ┌─────────────────┼───────────────────┐│
│  │                 ▼                   ││
│  │           WebSocket Server          ││  
│  │     (broadcasts every 2 seconds)    ││
│  └─────────────────────────────────────┘│
└─────────────────┬───────────────────────┘
                  │ WebSocket Connection
                  │ ws://localhost:8000/ws
                  ▼
┌─────────────────────────────────────────┐
│           Web Dashboard                 │
│  ┌─────────────────────────────────────┐│
│  │           Real-time UI              ││
│  │  • Generation monitoring panels     ││
│  │  • Battery management interface     ││
│  │  • Power flow visualization         ││
│  │  • System performance metrics       ││
│  │  • Weather & forecasting display    ││
│  │  • Alert management system          ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## Simulated Data Sources

### Solar Generation
- **DC/AC Power Output**: Based on time of day and weather
- **Efficiency Calculation**: Temperature and irradiance dependent
- **Weather Effects**: Cloud coverage impacts generation
- **Daily Cycle**: Zero at night, peaks at solar noon

### Wind Generation  
- **Power Curve Simulation**: Wind speed dependent output
- **Variable Output**: 15-25 kW range with realistic fluctuations
- **Efficiency Factors**: Mechanical and electrical losses included

### Biogas/CBG Generation
- **Steady Base Load**: Consistent 18-20 kW output
- **High Reliability**: Minimal variations for grid stability
- **Operational Status**: Real-time status monitoring

### Battery Energy Storage System (BESS)
- **4 Battery Packs**: Individual SOC, SoH, temperature tracking
- **Dynamic SOC Changes**: Based on charge/discharge cycles
- **Thermal Management**: Temperature monitoring and alerts
- **State of Health**: Degradation simulation over time

### System Metrics
- **Overall Efficiency**: Target 15-20% improvement (90-95% range)
- **Uptime Monitoring**: >99% target with realistic variations
- **Power Quality**: Voltage regulation ±2%, THD <3%
- **Grid Connection**: Import/export power flow tracking

## Dashboard Features

### Real-time Panels
1. **Generation Overview**: Solar, wind, biogas power output
2. **Battery Management**: SOC levels, charging status, thermal data
3. **Power Flow Diagram**: Interactive system visualization
4. **Demand Response**: Load management and peak shaving
5. **Weather Station**: Current conditions and forecasting
6. **System Performance**: Efficiency metrics and targets
7. **Alert Management**: System notifications and maintenance

### Interactive Elements
- **Live Data Updates**: Every 2-3 seconds via WebSocket
- **Clickable Components**: Drill-down for detailed views
- **Time Range Selectors**: Historical data analysis
- **Alert Acknowledgment**: System notification management
- **Export Functions**: Data export for reporting

## Customization Options

### Modifying Data Parameters
Edit the `MicrogridSimulator` class in `microgrid_server.py`:

```python
# Change base generation capacities
self.solar_capacity = 60      # kW peak solar
self.wind_capacity = 25       # kW wind turbine
self.cbg_capacity = 22        # kW biogas

# Adjust battery system
self.battery_capacity = 150   # kWh total storage
self.num_battery_packs = 4    # Number of battery packs

# Modify update frequency
await asyncio.sleep(2)        # 2-second updates
```

### Dashboard Customization
The dashboard can be modified by editing the HTML/CSS/JavaScript files:
- `index.html`: Structure and layout
- `style.css`: Visual styling and themes
- `app.js`: Interactive functionality and data handling

## Monitoring Your System

### Key Performance Indicators (KPIs)
- **System Efficiency**: Target >92% (currently achieving 91-95%)
- **Renewable Penetration**: % of load met by renewables
- **Battery Utilization**: Charge/discharge cycle effectiveness
- **Grid Independence**: Hours of autonomous operation
- **Peak Load Reduction**: Demand response effectiveness

### Alert Types
- **Info**: Routine system notifications (battery SOC updates)
- **Warning**: Attention required (voltage deviations, weather impacts)
- **Critical**: Immediate action needed (system faults, safety issues)

### Performance Targets
Based on your original project specifications:
- **Efficiency Improvement**: 15-20% over baseline
- **System Uptime**: >99% availability
- **Peak Reduction**: 20-30% through demand response
- **Power Quality**: Voltage ±2%, THD <3%

## Troubleshooting

### Server Issues
- **Connection Refused**: Ensure server is running on port 8000
- **Data Not Updating**: Check WebSocket connection status
- **Performance Issues**: Monitor CPU usage and memory

### Dashboard Issues  
- **WebSocket Disconnection**: Server may have restarted
- **Missing Data**: Check browser console for JavaScript errors
- **Slow Updates**: Network latency or server performance

### Common Solutions
1. **Restart the server**: `python microgrid_server.py`
2. **Refresh the dashboard**: F5 or Ctrl+R
3. **Check network connectivity**: Ensure localhost access
4. **Verify dependencies**: All Python packages installed

## Advanced Features

### Data Integration
- **CSV Export**: Historical data export functionality
- **API Integration**: REST endpoints for external systems
- **Database Logging**: Optional data persistence
- **Cloud Connectivity**: Upload to ThingSpeak/AWS/Azure

### Scalability
- **Multiple Clients**: Dashboard supports multiple simultaneous users
- **Load Balancing**: Can be deployed with multiple server instances
- **Geographic Distribution**: Multiple microgrid monitoring
- **Real Hardware Integration**: Ready for actual sensor data

## Next Steps

### Phase 1: Basic Operation (Complete)
✅ Server-side data simulation
✅ Real-time WebSocket communication  
✅ Professional dashboard interface
✅ Core monitoring functionality

### Phase 2: Enhanced Features (Optional)
- [ ] Historical data storage (database integration)
- [ ] Advanced analytics and reporting
- [ ] Mobile-responsive design improvements
- [ ] User authentication and role management
- [ ] Integration with actual IoT sensors

### Phase 3: Production Deployment (Future)
- [ ] Cloud hosting setup (AWS/Azure)
- [ ] SSL/TLS security implementation
- [ ] Performance optimization
- [ ] Real sensor data integration
- [ ] Multi-site monitoring capability

This system provides a complete foundation for microgrid monitoring that can be expanded to meet your specific operational requirements.
