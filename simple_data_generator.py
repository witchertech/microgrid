
import json
import random
import math
import time
from datetime import datetime

class SimpleMicrogridDataGenerator:
    def __init__(self):
        self.battery_socs = [72, 68, 65, 63]
        self.alerts = []

    def get_time_factor(self):
        """Solar generation based on time of day"""
        hour = datetime.now().hour
        if 6 <= hour <= 18:
            return max(0, math.sin(math.pi * (hour - 6) / 12))
        return 0

    def generate_sample_data(self):
        """Generate a sample of microgrid data"""
        time_factor = self.get_time_factor()

        # Weather simulation
        irradiance = 875 * time_factor * random.uniform(0.7, 1.0)
        irradiance = max(0, min(1200, irradiance))

        # Solar generation
        solar_dc = (irradiance / 1000) * 60  # 60kW peak
        solar_ac = solar_dc * 0.95

        # Wind generation
        wind_speed = 8.2 + random.uniform(-2, 3)
        wind_power = min(25, 0.5 * wind_speed ** 2.5) if wind_speed > 3 else 0

        # Biogas
        cbg_power = 18.5 + random.uniform(-2, 2)

        # Battery simulation
        for i in range(len(self.battery_socs)):
            self.battery_socs[i] += random.uniform(-0.5, 0.5)
            self.battery_socs[i] = max(20, min(95, self.battery_socs[i]))

        # Demand simulation
        hour = datetime.now().hour
        base_demand = 40 + 20 * math.sin(math.pi * (hour - 6) / 12)
        total_demand = max(25, base_demand + random.uniform(-5, 10))

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generation": {
                "solar": {
                    "dcPower": round(max(0, solar_dc), 1),
                    "acPower": round(max(0, solar_ac), 1),
                    "efficiency": round((solar_ac / max(solar_dc, 0.1)) * 100, 1),
                    "irradiance": round(irradiance, 0),
                    "moduleTemp": round(28.5 + (irradiance / 1000) * 20, 1)
                },
                "wind": {
                    "power": round(max(0, wind_power), 1),
                    "windSpeed": round(wind_speed, 1),
                    "efficiency": round(random.uniform(87, 92), 1)
                },
                "cbg": {
                    "power": round(max(0, cbg_power), 1),
                    "status": "operational",
                    "efficiency": round(random.uniform(89, 94), 1)
                },
                "totalGeneration": round(max(0, solar_ac) + max(0, wind_power) + max(0, cbg_power), 1)
            },
            "storage": {
                "overallSOC": round(sum(self.battery_socs) / len(self.battery_socs), 0),
                "totalCapacity": 150,
                "chargePower": round(random.uniform(0, 15), 1),
                "dischargePower": 0,
                "batteryPacks": [
                    {
                        "id": i + 1,
                        "soc": round(soc, 0),
                        "soh": random.randint(93, 98),
                        "temp": round(random.uniform(23, 26), 1),
                        "voltage": round(48 + (soc - 50) * 0.02, 1)
                    }
                    for i, soc in enumerate(self.battery_socs)
                ]
            },
            "demand": {
                "totalLoad": round(total_demand, 1),
                "criticalLoads": round(total_demand * 0.4, 1),
                "flexibleLoads": round(total_demand * 0.6, 1),
                "peakReduction": round(random.uniform(20, 30), 1)
            },
            "systemMetrics": {
                "overallEfficiency": round(random.uniform(90, 95), 1),
                "uptime": round(random.uniform(99.5, 99.9), 2),
                "powerQuality": {
                    "voltage": round(230 + random.uniform(-5, 5), 1),
                    "frequency": round(50 + random.uniform(-0.1, 0.1), 2),
                    "thd": round(random.uniform(1.0, 2.5), 1)
                }
            },
            "weather": {
                "temperature": round(28.5 + random.uniform(-3, 3), 1),
                "humidity": round(random.uniform(50, 85), 0),
                "windSpeed": round(wind_speed, 1),
                "irradiance": round(irradiance, 0),
                "cloudCover": round(random.uniform(10, 80), 0)
            },
            "alerts": [
                {
                    "id": 1,
                    "type": "info" if random.random() > 0.3 else "warning",
                    "message": f"Battery Pack {random.randint(1,4)} SOC at {round(random.uniform(45, 65))}%",
                    "time": datetime.now().strftime("%H:%M")
                }
            ]
        }

        return data

# Test the generator
if __name__ == "__main__":
    generator = SimpleMicrogridDataGenerator()

    print("=== Microgrid Data Simulation Test ===")
    print("Generating 5 sample data points...")

    for i in range(5):
        data = generator.generate_sample_data()
        print(f"\n--- Sample {i+1} ---")
        print(f"Time: {data['timestamp']}")
        print(f"Solar Generation: {data['generation']['solar']['acPower']} kW")
        print(f"Wind Generation: {data['generation']['wind']['power']} kW") 
        print(f"Total Generation: {data['generation']['totalGeneration']} kW")
        print(f"Total Demand: {data['demand']['totalLoad']} kW")
        print(f"Battery SOC: {data['storage']['overallSOC']}%")
        print(f"System Efficiency: {data['systemMetrics']['overallEfficiency']}%")

        time.sleep(1)

    print("\n=== Sample JSON Output ===")
    sample_data = generator.generate_sample_data()
    print(json.dumps(sample_data, indent=2))
