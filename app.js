// Microgrid Dashboard JavaScript
class MicrogridDashboard {
    constructor() {
        this.charts = {};
        this.currentData = null;
        this.simulationInterval = null;
        this.isConnected = true;
        
        // Initialize the dashboard
        this.initializeData();
        this.setupEventListeners();
        this.initializeCharts();
        this.startSimulation();
        this.updateTime();
        
        // Update time every second
        setInterval(() => this.updateTime(), 1000);
    }
    
    initializeData() {
        // Base data structure with realistic initial values
        this.currentData = {
            generation: {
                solar: { dcPower: 45.8, acPower: 43.2, efficiency: 94.3, irradiance: 875, moduleTemp: 38.5 },
                wind: { power: 12.3, windSpeed: 8.2, efficiency: 89.1 },
                cbg: { power: 18.5, status: "operational", efficiency: 91.7 },
                totalGeneration: 74.0
            },
            storage: {
                overallSOC: 67,
                totalCapacity: 150,
                chargePower: 8.5,
                dischargePower: 0,
                batteryPacks: [
                    {id: 1, soc: 72, soh: 96, temp: 24.5, voltage: 48.2},
                    {id: 2, soc: 68, soh: 94, temp: 25.1, voltage: 48.0},
                    {id: 3, soc: 65, soh: 97, temp: 23.8, voltage: 47.9},
                    {id: 4, soc: 63, soh: 95, temp: 24.7, voltage: 47.8}
                ]
            },
            demand: {
                totalLoad: 65.5,
                criticalLoads: 28.2,
                flexibleLoads: 37.3,
                peakReduction: 23.4
            },
            systemMetrics: {
                overallEfficiency: 92.8,
                uptime: 99.7,
                powerQuality: { voltage: 230.5, frequency: 50.02, thd: 1.8 }
            },
            weather: {
                temperature: 28.5,
                humidity: 65,
                windSpeed: 8.2,
                irradiance: 875,
                cloudCover: 15
            },
            alerts: [
                {id: 1, type: "info", message: "Battery Pack 4 SOC below 65%", time: "14:23"},
                {id: 2, type: "warning", message: "Cloud cover increasing - generation may decrease", time: "14:18"}
            ]
        };
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchView(item.dataset.view);
            });
        });
        
        // Emergency stop
        document.getElementById('emergencyStop').addEventListener('click', () => {
            this.handleEmergencyStop();
        });
        
        // Power flow view selector
        document.getElementById('flowViewSelect').addEventListener('change', (e) => {
            this.updatePowerFlowView(e.target.value);
        });
    }
    
    initializeCharts() {
        // Solar Gauge
        this.charts.solarGauge = this.createGaugeChart('solarGauge', 
            this.currentData.generation.solar.acPower, 60, 'Solar Power', 'kW', '#FFC185');
            
        // Wind Gauge  
        this.charts.windGauge = this.createGaugeChart('windGauge', 
            this.currentData.generation.wind.power, 25, 'Wind Power', 'kW', '#1FB8CD');
            
        // CBG Gauge
        this.charts.cbgGauge = this.createGaugeChart('cbgGauge', 
            this.currentData.generation.cbg.power, 30, 'CBG Power', 'kW', '#B4413C');
            
        // Battery SOC Gauge
        this.charts.batteryGauge = this.createGaugeChart('batteryGauge', 
            this.currentData.storage.overallSOC, 100, 'Battery SOC', '%', '#5D878F');
            
        // Demand Chart
        this.charts.demandChart = this.createDemandChart();
    }
    
    createGaugeChart(canvasId, value, max, label, unit, color) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [value, max - value],
                    backgroundColor: [color, '#ECEBD5'],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                elements: {
                    arc: {
                        borderRadius: 8
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                beforeDraw: function(chart) {
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    
                    ctx.restore();
                    const fontSize = (height / 100).toFixed(2);
                    ctx.font = `bold ${fontSize}em Arial`;
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#134252';
                    
                    const text = `${value}${unit}`;
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        });
    }
    
    createDemandChart() {
        const ctx = document.getElementById('demandChart');
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['14:00', '14:05', '14:10', '14:15', '14:20', '14:25'],
                datasets: [{
                    label: 'Generation',
                    data: [72.1, 73.5, 74.8, 74.2, 74.0, 74.3],
                    borderColor: '#1FB8CD',
                    backgroundColor: 'rgba(31, 184, 205, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Demand',
                    data: [63.2, 64.8, 65.1, 65.5, 65.5, 65.2],
                    borderColor: '#B4413C',
                    backgroundColor: 'rgba(180, 65, 60, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        position: 'top',
                        labels: { usePointStyle: true, boxWidth: 6 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 60,
                        max: 80,
                        grid: { display: false }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
    
    startSimulation() {
        this.simulationInterval = setInterval(() => {
            this.simulateDataChanges();
            this.updateDashboard();
        }, 3000); // Update every 3 seconds
    }
    
    simulateDataChanges() {
        // Simulate realistic variations in the data
        const data = this.currentData;
        
        // Solar variations (weather dependent)
        const cloudFactor = (100 - data.weather.cloudCover) / 100;
        const baseIrradiance = 850 + Math.random() * 100;
        data.weather.irradiance = Math.round(baseIrradiance * cloudFactor);
        data.generation.solar.dcPower = Math.round((data.weather.irradiance / 1000) * 52 * 10) / 10;
        data.generation.solar.acPower = Math.round(data.generation.solar.dcPower * 0.94 * 10) / 10;
        
        // Wind variations
        data.weather.windSpeed = Math.max(0, 8.2 + (Math.random() - 0.5) * 4);
        data.generation.wind.power = Math.round(Math.pow(data.weather.windSpeed / 12, 3) * 25 * 10) / 10;
        
        // CBG steady with minor variations
        data.generation.cbg.power = 18.5 + (Math.random() - 0.5) * 2;
        
        // Total generation
        data.generation.totalGeneration = data.generation.solar.acPower + data.generation.wind.power + data.generation.cbg.power;
        
        // Load variations (realistic daily pattern)
        const hour = new Date().getHours();
        const baseDemand = 65.5;
        const hourlyFactor = 1 + 0.2 * Math.sin((hour - 6) * Math.PI / 12);
        data.demand.totalLoad = Math.round(baseDemand * hourlyFactor * 10) / 10;
        data.demand.criticalLoads = Math.round(data.demand.totalLoad * 0.43 * 10) / 10;
        data.demand.flexibleLoads = Math.round(data.demand.totalLoad * 0.57 * 10) / 10;
        
        // Battery management
        const powerBalance = data.generation.totalGeneration - data.demand.totalLoad;
        if (powerBalance > 0 && data.storage.overallSOC < 95) {
            data.storage.chargePower = Math.min(powerBalance * 0.8, 15);
            data.storage.dischargePower = 0;
            // Slowly increase SOC
            data.storage.overallSOC = Math.min(95, data.storage.overallSOC + 0.1);
        } else if (powerBalance < 0 && data.storage.overallSOC > 20) {
            data.storage.dischargePower = Math.min(Math.abs(powerBalance), 20);
            data.storage.chargePower = 0;
            // Slowly decrease SOC
            data.storage.overallSOC = Math.max(20, data.storage.overallSOC - 0.2);
        }
        
        // Update individual battery packs
        data.storage.batteryPacks.forEach(pack => {
            pack.soc = Math.max(20, Math.min(95, data.storage.overallSOC + (Math.random() - 0.5) * 8));
            pack.temp = 24 + (Math.random() - 0.5) * 4;
            pack.voltage = 47.5 + (pack.soc / 100) * 1.5;
        });
        
        // Weather changes
        data.weather.temperature = 28.5 + (Math.random() - 0.5) * 6;
        data.weather.cloudCover = Math.max(0, Math.min(100, data.weather.cloudCover + (Math.random() - 0.5) * 10));
        
        // System efficiency
        data.systemMetrics.overallEfficiency = 92.8 + (Math.random() - 0.5) * 2;
        
        // Randomly generate new alerts
        if (Math.random() < 0.1) { // 10% chance every update
            const alertTypes = ['info', 'warning', 'error'];
            const messages = [
                'System optimization completed',
                'Peak demand period approaching',
                'Weather forecast updated',
                'Maintenance reminder: Monthly inspection due',
                'Load balancing adjustment made'
            ];
            
            const newAlert = {
                id: Date.now(),
                type: alertTypes[Math.floor(Math.random() * alertTypes.length)],
                message: messages[Math.floor(Math.random() * messages.length)],
                time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
            };
            
            data.alerts.unshift(newAlert);
            if (data.alerts.length > 5) {
                data.alerts.pop();
            }
        }
    }
    
    updateDashboard() {
        const data = this.currentData;
        
        // Update generation values
        document.getElementById('totalGeneration').textContent = `${data.generation.totalGeneration.toFixed(1)} kW`;
        document.getElementById('solarDC').textContent = `${data.generation.solar.dcPower.toFixed(1)} kW`;
        document.getElementById('solarAC').textContent = `${data.generation.solar.acPower.toFixed(1)} kW`;
        document.getElementById('solarEfficiency').textContent = `${data.generation.solar.efficiency.toFixed(1)}%`;
        document.getElementById('windPower').textContent = `${data.generation.wind.power.toFixed(1)} kW`;
        document.getElementById('windSpeed').textContent = `${data.weather.windSpeed.toFixed(1)} m/s`;
        document.getElementById('windEfficiency').textContent = `${data.generation.wind.efficiency.toFixed(1)}%`;
        document.getElementById('cbgPower').textContent = `${data.generation.cbg.power.toFixed(1)} kW`;
        document.getElementById('cbgEfficiency').textContent = `${data.generation.cbg.efficiency.toFixed(1)}%`;
        
        // Update battery values
        document.getElementById('overallSOC').textContent = `${Math.round(data.storage.overallSOC)}%`;
        document.getElementById('chargePower').textContent = `${data.storage.chargePower.toFixed(1)} kW`;
        
        // Update demand values
        document.getElementById('criticalLoads').textContent = `${data.demand.criticalLoads.toFixed(1)} kW`;
        document.getElementById('flexibleLoads').textContent = `${data.demand.flexibleLoads.toFixed(1)} kW`;
        document.getElementById('peakReduction').textContent = `${data.demand.peakReduction.toFixed(1)}%`;
        
        // Update weather values
        document.getElementById('temperature').textContent = `${data.weather.temperature.toFixed(1)}°C`;
        document.getElementById('irradiance').textContent = `${data.weather.irradiance} W/m²`;
        document.getElementById('weatherWindSpeed').textContent = `${data.weather.windSpeed.toFixed(1)} m/s`;
        document.getElementById('cloudCover').textContent = `${Math.round(data.weather.cloudCover)}%`;
        
        // Update system metrics
        document.getElementById('overallEfficiency').textContent = `${data.systemMetrics.overallEfficiency.toFixed(1)}%`;
        document.getElementById('voltageValue').textContent = `${data.systemMetrics.powerQuality.voltage.toFixed(1)}V`;
        document.getElementById('thdValue').textContent = `${data.systemMetrics.powerQuality.thd.toFixed(1)}% THD`;
        document.getElementById('storageUtilization').textContent = `${(data.storage.overallSOC * 0.87 + Math.random() * 10).toFixed(1)}%`;
        
        // Update footer KPIs
        document.getElementById('footerUptime').textContent = `${data.systemMetrics.uptime.toFixed(1)}%`;
        document.getElementById('footerPeakReduction').textContent = `${data.demand.peakReduction.toFixed(1)}%`;
        document.getElementById('energyBalance').textContent = `${(data.generation.totalGeneration - data.demand.totalLoad).toFixed(1)} kW`;
        document.getElementById('efficiencyGain').textContent = `+${(data.systemMetrics.overallEfficiency - 75.6).toFixed(1)}%`;
        
        // Update charts
        this.updateCharts();
        
        // Update power flow diagram
        this.updatePowerFlowDiagram();
        
        // Update battery packs display
        this.updateBatteryPacks();
        
        // Update alerts
        this.updateAlerts();
        
        // Update load bars
        this.updateLoadBars();
    }
    
    updateCharts() {
        const data = this.currentData;
        
        // Update gauges
        if (this.charts.solarGauge) {
            this.charts.solarGauge.data.datasets[0].data[0] = data.generation.solar.acPower;
            this.charts.solarGauge.data.datasets[0].data[1] = 60 - data.generation.solar.acPower;
            this.charts.solarGauge.update('none');
        }
        
        if (this.charts.windGauge) {
            this.charts.windGauge.data.datasets[0].data[0] = data.generation.wind.power;
            this.charts.windGauge.data.datasets[0].data[1] = 25 - data.generation.wind.power;
            this.charts.windGauge.update('none');
        }
        
        if (this.charts.cbgGauge) {
            this.charts.cbgGauge.data.datasets[0].data[0] = data.generation.cbg.power;
            this.charts.cbgGauge.data.datasets[0].data[1] = 30 - data.generation.cbg.power;
            this.charts.cbgGauge.update('none');
        }
        
        if (this.charts.batteryGauge) {
            this.charts.batteryGauge.data.datasets[0].data[0] = data.storage.overallSOC;
            this.charts.batteryGauge.data.datasets[0].data[1] = 100 - data.storage.overallSOC;
            this.charts.batteryGauge.update('none');
        }
        
        // Update demand chart with new data point
        if (this.charts.demandChart) {
            const currentTime = new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
            this.charts.demandChart.data.labels.push(currentTime);
            this.charts.demandChart.data.datasets[0].data.push(data.generation.totalGeneration);
            this.charts.demandChart.data.datasets[1].data.push(data.demand.totalLoad);
            
            // Keep only last 10 data points
            if (this.charts.demandChart.data.labels.length > 10) {
                this.charts.demandChart.data.labels.shift();
                this.charts.demandChart.data.datasets[0].data.shift();
                this.charts.demandChart.data.datasets[1].data.shift();
            }
            
            this.charts.demandChart.update('none');
        }
    }
    
    updatePowerFlowDiagram() {
        const data = this.currentData;
        
        // Update node values
        document.getElementById('solarNodeValue').textContent = `${data.generation.solar.acPower.toFixed(1)}kW`;
        document.getElementById('windNodeValue').textContent = `${data.generation.wind.power.toFixed(1)}kW`;
        document.getElementById('cbgNodeValue').textContent = `${data.generation.cbg.power.toFixed(1)}kW`;
        document.getElementById('batteryNodeValue').textContent = `${Math.round(data.storage.overallSOC)}% SOC`;
        document.getElementById('batteryPowerValue').textContent = data.storage.chargePower > 0 ? 
            `+${data.storage.chargePower.toFixed(1)}kW` : 
            `-${data.storage.dischargePower.toFixed(1)}kW`;
        document.getElementById('criticalLoadValue').textContent = `${data.demand.criticalLoads.toFixed(1)}kW`;
        document.getElementById('flexibleLoadValue').textContent = `${data.demand.flexibleLoads.toFixed(1)}kW`;
    }
    
    updateBatteryPacks() {
        const packsContainer = document.getElementById('batteryPacksList');
        packsContainer.innerHTML = '';
        
        this.currentData.storage.batteryPacks.forEach(pack => {
            const packElement = document.createElement('div');
            packElement.className = 'pack-item';
            
            const socClass = pack.soc > 70 ? 'high' : pack.soc > 40 ? 'medium' : 'low';
            
            packElement.innerHTML = `
                <div class="pack-id">Pack ${pack.id}</div>
                <div class="pack-soc ${socClass}">${Math.round(pack.soc)}%</div>
                <div class="pack-details">
                    <span>SoH: ${pack.soh}%</span>
                    <span>${pack.temp.toFixed(1)}°C</span>
                </div>
            `;
            
            packsContainer.appendChild(packElement);
        });
    }
    
    updateAlerts() {
        const alertsList = document.getElementById('alertsList');
        alertsList.innerHTML = '';
        
        this.currentData.alerts.forEach(alert => {
            const alertElement = document.createElement('div');
            alertElement.className = `alert-item ${alert.type}`;
            alertElement.innerHTML = `
                <div style="font-weight: 500; margin-bottom: 4px;">${alert.message}</div>
                <div style="font-size: 10px; opacity: 0.7;">${alert.time}</div>
            `;
            alertsList.appendChild(alertElement);
        });
    }
    
    updateLoadBars() {
        const data = this.currentData;
        const totalLoad = data.demand.totalLoad;
        const criticalPct = (data.demand.criticalLoads / totalLoad) * 100;
        const flexiblePct = (data.demand.flexibleLoads / totalLoad) * 100;
        
        document.querySelector('.load-fill.critical').style.width = `${criticalPct}%`;
        document.querySelector('.load-fill.flexible').style.width = `${flexiblePct}%`;
    }
    
    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('currentTime').textContent = timeString;
    }
    
    switchView(viewName) {
        // Hide all views
        document.querySelectorAll('.view-content').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show selected view
        document.getElementById(`${viewName}-view`).classList.add('active');
        
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
    }
    
    updatePowerFlowView(viewType) {
        // This would update the power flow diagram based on the selected view
        console.log(`Switching power flow view to: ${viewType}`);
        // Implementation would modify the SVG display based on viewType
    }
    
    handleEmergencyStop() {
        if (confirm('Are you sure you want to initiate emergency stop? This will shut down all generation and load systems.')) {
            alert('Emergency stop initiated. All systems shutting down safely.');
            // In a real system, this would send emergency stop commands
        }
    }
    
    // Method to receive external data (for server integration)
    updateFromServer(newData) {
        this.currentData = { ...this.currentData, ...newData };
        this.updateDashboard();
    }
    
    // Connection status simulation
    simulateConnectionStatus() {
        setInterval(() => {
            // Simulate occasional connection issues (5% chance)
            if (Math.random() < 0.05) {
                this.isConnected = false;
                document.getElementById('connectionStatus').textContent = 'Disconnected';
                document.getElementById('connectionStatus').className = 'status status--error';
                
                // Reconnect after 3-10 seconds
                setTimeout(() => {
                    this.isConnected = true;
                    document.getElementById('connectionStatus').textContent = 'Connected';
                    document.getElementById('connectionStatus').className = 'status status--success';
                }, 3000 + Math.random() * 7000);
            }
        }, 30000); // Check every 30 seconds
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new MicrogridDashboard();
    window.dashboard.simulateConnectionStatus();
});

// Export for external server integration
window.MicrogridDashboard = MicrogridDashboard;