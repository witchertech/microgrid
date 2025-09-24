# -*- coding: utf-8 -*-
import asyncio
import json
import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import numpy as np
import pandas as pd
from pydantic import BaseModel

app = FastAPI(title="Microgrid Data Simulation Server", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

class MicrogridSimulator:
    def __init__(self):
        self.time_offset = 0
        self.base_wind_speed = 8.2
        self.battery_socs = [72, 68, 65, 63]  # Initial SOC for 4 battery packs
        self.system_efficiency = 92.8
        self.uptime = 99.7
        self.alerts = []
        
        # Historical data for trends
        self.historical_data = []
        self.max_history = 50
        
        # Load CSV data
        try:
            self.solar_data = pd.read_csv('Plant_1_Generation_Data.csv')
            self.solar_data['DATE_TIME'] = pd.to_datetime(self.solar_data['DATE_TIME'], format='%d/%m/%Y %H:%M')
            print(f"Loaded {len(self.solar_data)} solar data records")
        except Exception as e:
            print(f"Error loading CSV: {e}")
            self.solar_data = None
        
    def get_time_factor(self):
        """Get time-based factor for solar generation (0 at night, 1 at noon)"""
        hour = (datetime.now().hour + self.time_offset) % 24
        # Solar generation peaks at noon (12), is zero from 6 PM to 6 AM
        if 6 <= hour <= 18:
            # Sinusoidal curve peaking at noon
            return max(0, math.sin(math.pi * (hour - 6) / 12))
        return 0
    
    def get_solar_data_from_csv(self):
        """Get solar data from CSV based on current time"""
        if self.solar_data is None:
            return self.simulate_solar_fallback()
        
        # Match current time with CSV timestamps (ignore date, match time only)
        current_time = datetime.now().time()
        
        # Extract time from CSV timestamps and find closest match
        csv_times = self.solar_data['DATE_TIME'].dt.time
        time_diffs = [abs((datetime.combine(datetime.today(), t) - datetime.combine(datetime.today(), current_time)).total_seconds()) for t in csv_times]
        closest_idx = time_diffs.index(min(time_diffs))
        
        # Get data for all inverters at this time
        time_data = self.solar_data[self.solar_data['DATE_TIME'] == self.solar_data.loc[closest_idx, 'DATE_TIME']]
        
        # Aggregate data
        total_dc = time_data['DC_POWER'].sum() / 1000  # Convert to kW
        total_ac = time_data['AC_POWER'].sum() / 1000  # Convert to kW
        avg_temp = time_data['AMBIENT_TEMPERATURE'].mean()
        avg_module_temp = time_data['MODULE_TEMPERATURE'].mean()
        avg_irradiation = time_data['IRRADIATION'].mean()
        
        efficiency = (total_ac / max(total_dc, 0.1)) * 100 if total_dc > 0 else 0
        
        return {
            "dcPower": round(total_dc, 1),
            "acPower": round(total_ac, 1),
            "efficiency": round(efficiency, 1),
            "irradiance": round(avg_irradiation, 0),
            "moduleTemp": round(avg_module_temp, 1)
        }
    
    def simulate_solar_fallback(self):
        """Fallback solar simulation if CSV not available"""
        time_factor = self.get_time_factor()
        irradiance = 875 * time_factor + random.uniform(-50, 50)
        irradiance = max(0, min(1200, irradiance))
        
        temp = 28.5 + random.uniform(-3, 3)
        temp_coefficient = -0.004
        temp_loss = temp_coefficient * (temp - 25)
        efficiency = 0.20 + temp_loss
        
        dc_power = (irradiance / 1000) * 300 * efficiency
        ac_power = dc_power * random.uniform(0.93, 0.97)
        
        return {
            "dcPower": round(max(0, dc_power), 1),
            "acPower": round(max(0, ac_power), 1),
            "efficiency": round((ac_power / max(dc_power, 0.1)) * 100, 1),
            "irradiance": round(irradiance, 0),
            "moduleTemp": round(temp + (irradiance / 1000) * 20, 1)
        }
    
    def get_weather_from_csv(self):
        """Get weather data from CSV"""
        if self.solar_data is None:
            return self.simulate_weather_fallback()
        
        # Match current time with CSV timestamps (ignore date, match time only)
        current_time = datetime.now().time()
        
        # Extract time from CSV timestamps and find closest match
        csv_times = self.solar_data['DATE_TIME'].dt.time
        time_diffs = [abs((datetime.combine(datetime.today(), t) - datetime.combine(datetime.today(), current_time)).total_seconds()) for t in csv_times]
        closest_idx = time_diffs.index(min(time_diffs))
        
        # Get data for all inverters at this time
        time_data = self.solar_data[self.solar_data['DATE_TIME'] == self.solar_data.loc[closest_idx, 'DATE_TIME']]
        
        # Get weather values from CSV
        avg_temp = time_data['AMBIENT_TEMPERATURE'].mean()
        avg_module_temp = time_data['MODULE_TEMPERATURE'].mean()
        avg_irradiation = time_data['IRRADIATION'].mean()
        
        # Calculate cloud cover based on irradiation
        cloud_cover = max(0, 100 - (avg_irradiation / 10))
        
        # Simulate wind and humidity (not in CSV)
        wind_speed = self.base_wind_speed + random.uniform(-2, 3)
        wind_speed = max(0, min(20, wind_speed))
        humidity = random.uniform(50, 85)
        
        return {
            "temperature": round(avg_temp, 1),
            "humidity": round(humidity, 0),
            "windSpeed": round(wind_speed, 1),
            "irradiance": round(avg_irradiation, 0),
            "cloudCover": round(cloud_cover, 0)
        }
    
    def simulate_weather_fallback(self):
        """Fallback weather simulation if CSV not available"""
        time_factor = self.get_time_factor()
        cloud_factor = random.uniform(0.7, 1.0)
        
        irradiance = 875 * time_factor * cloud_factor
        irradiance += random.uniform(-50, 50)
        irradiance = max(0, min(1200, irradiance))
        
        wind_speed = self.base_wind_speed + random.uniform(-2, 3)
        wind_speed = max(0, min(20, wind_speed))
        
        temperature = 28.5 + random.uniform(-3, 3)
        humidity = random.uniform(50, 85)
        cloud_cover = int((1 - cloud_factor) * 100)
        
        return {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 0),
            "windSpeed": round(wind_speed, 1),
            "irradiance": round(irradiance, 0),
            "cloudCover": cloud_cover
        }
    
    def simulate_solar_generation(self, weather_data):
        """Simulate solar PV generation based on weather"""
        irradiance = weather_data["irradiance"]
        temp = weather_data["temperature"]
        
        # Solar panel efficiency decreases with temperature
        temp_coefficient = -0.004  # -0.4%/�C
        temp_loss = temp_coefficient * (temp - 25)
        efficiency = 0.20 + temp_loss  # 20% base efficiency
        
        # DC power calculation (simplified)
        panel_area = 300  # m�
        dc_power = (irradiance / 1000) * panel_area * efficiency
        
        # AC power (inverter efficiency ~95%)
        inverter_efficiency = random.uniform(0.93, 0.97)
        ac_power = dc_power * inverter_efficiency
        
        # Add some realistic noise
        dc_power += random.uniform(-2, 2)
        ac_power += random.uniform(-2, 2)
        
        module_temp = temp + (irradiance / 1000) * 20  # Module temperature
        
        return {
            "dcPower": round(max(0, dc_power), 1),
            "acPower": round(max(0, ac_power), 1),
            "efficiency": round((ac_power / max(dc_power, 0.1)) * 100, 1),
            "irradiance": irradiance,
            "moduleTemp": round(module_temp, 1)
        }
    
    def simulate_wind_generation(self, weather_data):
        """Simulate wind turbine generation"""
        wind_speed = weather_data["windSpeed"]
        
        # Wind turbine power curve (simplified)
        if wind_speed < 3:
            power = 0
        elif wind_speed < 12:
            power = min(25, 0.5 * wind_speed ** 2.5)
        else:
            power = 25
        
        # Add noise and efficiency
        efficiency = random.uniform(0.87, 0.92)
        power *= efficiency
        power += random.uniform(-1, 1)
        
        return {
            "power": round(max(0, power), 1),
            "windSpeed": wind_speed,
            "efficiency": round(efficiency * 100, 1)
        }
    
    def simulate_cbg_generation(self):
        """Simulate CBG/biogas generation"""
        # Biogas generation is relatively stable
        base_power = 18.5
        power = base_power + random.uniform(-2, 2)
        efficiency = random.uniform(0.89, 0.94)
        
        return {
            "power": round(max(0, power), 1),
            "status": "operational" if power > 15 else "reduced",
            "efficiency": round(efficiency * 100, 1)
        }
    
    def simulate_battery_system(self, net_power):
        """Simulate battery storage system with SOC dynamics"""
        total_capacity = 150  # kWh
        
        for i, pack in enumerate(self.battery_socs):
            # Simulate slight SOC changes based on charge/discharge
            if net_power > 0:  # Charging
                self.battery_socs[i] += random.uniform(0, 0.2)
            else:  # Discharging
                self.battery_socs[i] -= random.uniform(0, 0.3)
            
            # Keep SOC within realistic bounds
            self.battery_socs[i] = max(20, min(95, self.battery_socs[i]))
        
        overall_soc = sum(self.battery_socs) / len(self.battery_socs)
        
        # Determine charge/discharge power
        if net_power > 5:  # Excess generation
            charge_power = min(net_power, 15)  # Max charging rate
            discharge_power = 0
        elif net_power < -5:  # Power deficit
            charge_power = 0
            discharge_power = min(abs(net_power), 20)  # Max discharge rate
        else:
            charge_power = 0
            discharge_power = 0
        
        battery_packs = []
        for i, soc in enumerate(self.battery_socs):
            battery_packs.append({
                "id": i + 1,
                "soc": round(soc, 0),
                "soh": random.randint(93, 98),  # State of Health
                "temp": round(random.uniform(23, 26), 1),
                "voltage": round(48 + (soc - 50) * 0.02, 1)
            })
        
        return {
            "overallSOC": round(overall_soc, 0),
            "totalCapacity": total_capacity,
            "chargePower": round(charge_power, 1),
            "dischargePower": round(discharge_power, 1),
            "batteryPacks": battery_packs
        }
    
    def simulate_demand(self):
        """Simulate electrical load demand"""
        hour = datetime.now().hour
        
        # Daily load profile (higher during day, lower at night)
        base_load = 40 + 20 * math.sin(math.pi * (hour - 6) / 12)
        base_load = max(25, base_load)
        
        # Add some randomness
        total_load = base_load + random.uniform(-5, 10)
        
        critical_loads = total_load * random.uniform(0.35, 0.45)
        flexible_loads = total_load - critical_loads
        
        # Peak reduction effectiveness
        peak_reduction = random.uniform(20, 30)
        
        return {
            "totalLoad": round(total_load, 1),
            "criticalLoads": round(critical_loads, 1),
            "flexibleLoads": round(flexible_loads, 1),
            "peakReduction": round(peak_reduction, 1)
        }
    
    def calculate_system_metrics(self, generation_data, demand_data):
        """Calculate overall system performance metrics"""
        total_gen = generation_data["solar"]["acPower"] + generation_data["wind"]["power"] + generation_data["cbg"]["power"]
        total_demand = demand_data["totalLoad"]
        
        # System efficiency (simplified)
        efficiency = min(95, 90 + random.uniform(-2, 3))
        
        # Power quality simulation
        voltage = 230 + random.uniform(-5, 5)
        frequency = 50 + random.uniform(-0.1, 0.1)
        thd = random.uniform(1.0, 2.5)
        
        # Uptime simulation (very high reliability)
        self.uptime = min(100, self.uptime + random.uniform(-0.01, 0.02))
        
        return {
            "overallEfficiency": round(efficiency, 1),
            "uptime": round(self.uptime, 2),
            "powerQuality": {
                "voltage": round(voltage, 1),
                "frequency": round(frequency, 2),
                "thd": round(thd, 1)
            }
        }
    
    def generate_alerts(self, data):
        """Generate realistic system alerts"""
        new_alerts = []
        current_time = datetime.now().strftime("%H:%M")
        
        # Check for low battery SOC
        for pack in data["storage"]["batteryPacks"]:
            if pack["soc"] < 30:
                new_alerts.append({
                    "id": len(self.alerts) + len(new_alerts) + 1,
                    "type": "warning",
                    "message": f"Battery Pack {pack['id']} SOC critically low ({pack['soc']}%)",
                    "time": current_time
                })
            elif pack["soc"] < 50:
                new_alerts.append({
                    "id": len(self.alerts) + len(new_alerts) + 1,
                    "type": "info",
                    "message": f"Battery Pack {pack['id']} SOC below 50% ({pack['soc']}%)",
                    "time": current_time
                })
        
        # Check weather conditions
        if data["weather"]["cloudCover"] > 70:
            new_alerts.append({
                "id": len(self.alerts) + len(new_alerts) + 1,
                "type": "info",
                "message": "High cloud cover detected - solar generation reduced",
                "time": current_time
            })
        
        # Check power quality
        if abs(data["systemMetrics"]["powerQuality"]["voltage"] - 230) > 10:
            new_alerts.append({
                "id": len(self.alerts) + len(new_alerts) + 1,
                "type": "warning",
                "message": f"Voltage deviation: {data['systemMetrics']['powerQuality']['voltage']}V",
                "time": current_time
            })
        
        # Add new alerts and keep only recent ones
        self.alerts.extend(new_alerts)
        self.alerts = self.alerts[-10:]  # Keep only last 10 alerts
        
        return self.alerts
    
    def generate_data(self):
        """Generate complete microgrid simulation data"""
        # Get weather data from CSV
        weather_data = self.get_weather_from_csv()
        
        # Get solar data from CSV
        solar_data = self.get_solar_data_from_csv()
        wind_data = self.simulate_wind_generation(weather_data)
        cbg_data = self.simulate_cbg_generation()
        
        total_generation = solar_data["acPower"] + wind_data["power"] + cbg_data["power"]
        
        # Simulate demand
        demand_data = self.simulate_demand()
        
        # Calculate net power for battery management
        net_power = total_generation - demand_data["totalLoad"]
        
        # Simulate battery system
        storage_data = self.simulate_battery_system(net_power)
        
        # Calculate system metrics
        generation_data = {
            "solar": solar_data,
            "wind": wind_data,
            "cbg": cbg_data,
            "totalGeneration": round(total_generation, 1)
        }
        
        system_metrics = self.calculate_system_metrics(generation_data, demand_data)
        
        # Compile all data
        complete_data = {
            "timestamp": datetime.now().isoformat(),
            "generation": generation_data,
            "storage": storage_data,
            "demand": demand_data,
            "systemMetrics": system_metrics,
            "weather": weather_data,
            "alerts": []
        }
        
        # Generate alerts
        complete_data["alerts"] = self.generate_alerts(complete_data)
        
        # Store historical data
        historical_point = {
            "time": datetime.now().strftime("%H:%M"),
            "generation": total_generation,
            "demand": demand_data["totalLoad"],
            "efficiency": system_metrics["overallEfficiency"]
        }
        
        self.historical_data.append(historical_point)
        if len(self.historical_data) > self.max_history:
            self.historical_data.pop(0)
        
        complete_data["historicalData"] = self.historical_data
        
        return complete_data

# Create the simulator instance
simulator = MicrogridSimulator()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Generate new simulation data
            data = simulator.generate_data()
            
            # Send to all connected clients
            await manager.broadcast(json.dumps(data))
            
            # Wait 2 seconds before next update
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/api")
async def api_info():
    return {"message": "Microgrid Simulation Server is running", "endpoints": ["/ws"]}

@app.get("/current-data")
async def get_current_data():
    """Get current simulation data via REST API"""
    return simulator.generate_data()

if __name__ == "__main__":
    print("Starting Microgrid Simulation Server...")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("REST endpoint: http://localhost:8000/current-data")
    uvicorn.run(app, host="0.0.0.0", port=8000)
