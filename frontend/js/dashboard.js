/**
 * Cloud Fog API - Dashboard JavaScript
 * Handles all data fetching, chart rendering, and real-time updates
 */

// API Endpoints
const API_ENDPOINTS = {
    getAlerts: 'https://ccj1oq37qc.execute-api.us-east-1.amazonaws.com/alerts',
    getMlDetection: 'https://ccj1oq37qc.execute-api.us-east-1.amazonaws.com/ml-detection',
    getSensorData: 'https://ccj1oq37qc.execute-api.us-east-1.amazonaws.com/sensor-data',
};

// Chart instances (to be updated dynamically)
let chartsInstances = {};
let calendarInstance = null;

// Update intervals
const UPDATE_INTERVALS = {
    alerts: 2 * 60 * 1000,      // 2 minutes
    mlDetection: 2 * 60 * 1000,  // 2 minutes
    sensorData: 2 * 60 * 1000,   // 2 minutes
};

/**
 * Initialize the dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    loadAllData();
    setupAutoRefresh();
    updateSyncStatus('Listo');
});

/**
 * Setup auto-refresh intervals
 */
function setupAutoRefresh() {
    // Refresh alerts every 2 minutes
    setInterval(() => {
        loadAlerts();
    }, UPDATE_INTERVALS.alerts);

    // Refresh ML Detection every 25 seconds
    setInterval(() => {
        loadMlDetection();
    }, UPDATE_INTERVALS.mlDetection);

    // Refresh Sensor Data every 25 seconds
    setInterval(() => {
        loadSensorData();
    }, UPDATE_INTERVALS.sensorData);
}

/**
 * Load all data on page load
 */
async function loadAllData() {
    try {
        updateSyncStatus('Sincronizando...');
        await Promise.all([
            loadAlerts(),
            loadMlDetection(),
            loadSensorData()
        ]);
        updateSyncStatus('Sincronización completada');
    } catch (error) {
        console.error('Error loading data:', error);
        updateSyncStatus('Error en sincronización');
    }
}

/**
 * Update sync status
 */
function updateSyncStatus(status) {
    const syncElement = document.getElementById('sync-status');
    if (status === 'Sincronizando...') {
        syncElement.innerHTML = '<span class="loading-spinner"></span> Sincronizando...';
    } else {
        syncElement.innerHTML = `<i class="bi bi-check-circle-fill" style="color: #198754;"></i> ${status}`;
    }
}

/**
 * Fetch data from API with error handling
 */
async function fetchData(url) {
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            mode: 'cors'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching from ${url}:`, error);
        return null;
    }
}

/**
 * =====================================================
 * ALERTS SECTION
 * =====================================================
 */

async function loadAlerts() {
    const data = await fetchData(API_ENDPOINTS.getAlerts);
    
    if (!data) {
        console.error('Failed to load alerts');
        return;
    }

    const alerts = data.alerts || [];
    updateAlertStats(alerts);
    separateAndDisplayAlerts(alerts);
    updateCalendarWithAlerts(alerts);
    updateAlertsChart(alerts);
}

function updateAlertStats(alerts) {
    // Total alerts
    document.getElementById('total-alerts').textContent = alerts.length;

    // Danger alerts
    const dangerAlerts = alerts.filter(a => a.type === 'DANGER_DETECTION');
    document.getElementById('danger-alerts').textContent = dangerAlerts.length;
}

function separateAndDisplayAlerts(alerts) {
    // Email alerts
    const emailAlerts = alerts.filter(a => a.type === 'EMAIL_ALERT');
    displayEmailAlerts(emailAlerts);

    // Danger alerts
    const dangerAlerts = alerts.filter(a => a.type === 'DANGER_DETECTION');
    displayDangerAlerts(dangerAlerts);
}

function displayEmailAlerts(alerts) {
    const tbody = document.getElementById('emailAlertsList');
    
    if (alerts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No hay alertas por email</td></tr>';
        return;
    }

    tbody.innerHTML = alerts.map(alert => {
        const date = new Date(alert.timestamp);
        const statusBadge = alert.status === 'sent' 
            ? '<span class="badge badge-success-custom">Enviado</span>'
            : '<span class="badge badge-warning-custom">Pendiente</span>';

        return `
            <tr>
                <td><small>${alert.alert_id.substring(0, 8)}...</small></td>
                <td>${alert.alert_type || 'N/A'}</td>
                <td>${statusBadge}</td>
                <td>${date.toLocaleString()}</td>
            </tr>
        `;
    }).join('');
}

function displayDangerAlerts(alerts) {
    const tbody = document.getElementById('dangerAlertsList');
    
    if (alerts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay alertas de peligro</td></tr>';
        return;
    }

    tbody.innerHTML = alerts.map(alert => {
        const date = new Date(alert.timestamp);
        const levelBadge = `<span class="badge badge-danger-custom">${alert.alert_level}</span>`;
        const prob = alert.danger_alert || 'N/A';

        return `
            <tr>
                <td><small>${alert.alert_id.substring(0, 8)}...</small></td>
                <td>${levelBadge}</td>
                <td>${alert.alert.substring(0, 40)}...</td>
                <td>${alert.temperature || 'N/A'}°C</td>
                <td>${alert.humidity ? (alert.humidity * 100).toFixed(1) : 'N/A'}%</td>
                <td>${date.toLocaleString()}</td>
            </tr>
        `;
    }).join('');
}

function updateAlertsChart(alerts) {
    const ctx = document.getElementById('alertsChart');
    
    if (!ctx) return;

    const emailCount = alerts.filter(a => a.type === 'EMAIL_ALERT').length;
    const dangerCount = alerts.filter(a => a.type === 'DANGER_DETECTION').length;

    if (chartsInstances.alerts) {
        chartsInstances.alerts.data.datasets[0].data = [emailCount, dangerCount];
        chartsInstances.alerts.update();
    } else {
        chartsInstances.alerts = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Alertas Email', 'Alertas de Peligro'],
                datasets: [{
                    data: [emailCount, dangerCount],
                    backgroundColor: ['#0dcaf0', '#dc3545'],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 12 }, padding: 15 }
                    }
                }
            }
        });
    }
}

/**
 * =====================================================
 * CALENDAR SECTION
 * =====================================================
 */

function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    calendarInstance = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        locale: 'es',
        events: [],
        eventDisplay: 'block'
    });
    calendarInstance.render();
}

function updateCalendarWithAlerts(alerts) {
    if (!calendarInstance) return;

    const events = alerts.map(alert => {
        const date = new Date(alert.timestamp);
        const color = alert.type === 'DANGER_DETECTION' ? '#dc3545' : '#0dcaf0';

        return {
            title: alert.type === 'DANGER_DETECTION' 
                ? `🚨 ${alert.alert_type || alert.alert?.substring(0, 20)}` 
                : `📧 ${alert.alert_type}`,
            date: date.toISOString().split('T')[0],
            backgroundColor: color,
            borderColor: color
        };
    });

    calendarInstance.removeAllEvents();
    calendarInstance.addEventSource(events);
}

/**
 * =====================================================
 * ML DETECTION SECTION
 * =====================================================
 */

async function loadMlDetection() {
    const data = await fetchData(API_ENDPOINTS.getMlDetection);
    
    if (!data) {
        console.error('Failed to load ML detection');
        return;
    }

    const detections = data.data || [];
    document.getElementById('ml-detections').textContent = detections.length;
    displayMlDetections(detections);
    updateMlDetectionChart(detections);
}

function displayMlDetections(detections) {
    const tbody = document.getElementById('mlDetectionList');
    
    if (detections.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No hay detecciones</td></tr>';
        return;
    }

    tbody.innerHTML = detections.slice(0, 10).map(detection => {
        const date = new Date(detection.timestamp);
        const det = detection.detection || {};
        const levelBadge = `<span class="badge badge-${getLevelColor(detection.alert_level)}">${detection.alert_level}</span>`;

        return `
            <tr>
                <td><small>${detection.id.substring(0, 8)}...</small></td>
                <td>${(det.fog * 100).toFixed(1)}%</td>
                <td>${(det.smoke * 100).toFixed(1)}%</td>
                <td>${(det.vapor * 100).toFixed(1)}%</td>
                <td>${(det.smug * 100).toFixed(1)}%</td>
                <td>${detection.alert.substring(0, 30)}...</td>
                <td>${levelBadge}</td>
                <td>${date.toLocaleString()}</td>
            </tr>
        `;
    }).join('');
}

function updateMlDetectionChart(detections) {
    const ctx = document.getElementById('mlDetectionChart');
    
    if (!ctx) return;

    // Take last 5 detections
    const lastDetections = detections.slice(0, 5).reverse();
    
    const labels = lastDetections.map((_, i) => `Det ${i + 1}`);
    const fogData = lastDetections.map(d => (d.detection?.fog || 0) * 100);
    const smokeData = lastDetections.map(d => (d.detection?.smoke || 0) * 100);
    const vaporData = lastDetections.map(d => (d.detection?.vapor || 0) * 100);
    const smugData = lastDetections.map(d => (d.detection?.smug || 0) * 100);

    if (chartsInstances.mlDetection) {
        chartsInstances.mlDetection.data.labels = labels;
        chartsInstances.mlDetection.data.datasets[0].data = fogData;
        chartsInstances.mlDetection.data.datasets[1].data = smokeData;
        chartsInstances.mlDetection.data.datasets[2].data = vaporData;
        chartsInstances.mlDetection.data.datasets[3].data = smugData;
        chartsInstances.mlDetection.update();
    } else {
        chartsInstances.mlDetection = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Niebla (%)',
                        data: fogData,
                        backgroundColor: 'rgba(13, 202, 240, 0.8)',
                        borderColor: '#0dcaf0',
                        borderWidth: 1
                    },
                    {
                        label: 'Humo (%)',
                        data: smokeData,
                        backgroundColor: 'rgba(220, 53, 69, 0.8)',
                        borderColor: '#dc3545',
                        borderWidth: 1
                    },
                    {
                        label: 'Vapor (%)',
                        data: vaporData,
                        backgroundColor: 'rgba(255, 193, 7, 0.8)',
                        borderColor: '#ffc107',
                        borderWidth: 1
                    },
                    {
                        label: 'Smug (%)',
                        data: smugData,
                        backgroundColor: 'rgba(108, 117, 125, 0.8)',
                        borderColor: '#6c757d',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { font: { size: 11 }, padding: 15 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' }
                    }
                }
            }
        });
    }
}

/**
 * =====================================================
 * SENSOR DATA SECTION
 * =====================================================
 */

async function loadSensorData() {
    const data = await fetchData(API_ENDPOINTS.getSensorData);
    
    if (!data) {
        console.error('Failed to load sensor data');
        return;
    }

    const sensorData = data.data || [];
    document.getElementById('sensor-records').textContent = sensorData.length;
    displaySensorData(sensorData);
    updateSensorCharts(sensorData);
}

function displaySensorData(sensorData) {
    const tbody = document.getElementById('sensorDataList');
    
    if (sensorData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No hay datos de sensores</td></tr>';
        return;
    }

    tbody.innerHTML = sensorData.slice(0, 10).map(sensor => {
        const date = new Date(sensor.timestamp);
        const levelBadge = `<span class="badge badge-${getLevelColor(sensor.alert_level)}">${sensor.alert_level}</span>`;

        return `
            <tr>
                <td><small>${sensor.id.substring(0, 8)}...</small></td>
                <td>${sensor.temperature}°C</td>
                <td>${(sensor.humidity * 100).toFixed(1)}%</td>
                <td>${(sensor.probability_fog * 100).toFixed(1)}%</td>
                <td>${(sensor.probability_smoke * 100).toFixed(1)}%</td>
                <td>${(sensor.probability_vapor * 100).toFixed(1)}%</td>
                <td>${(sensor.probability_smug * 100).toFixed(1)}%</td>
                <td>${levelBadge}</td>
                <td>${date.toLocaleString()}</td>
            </tr>
        `;
    }).join('');
}

function updateSensorCharts(sensorData) {
    if (sensorData.length === 0) return;

    // Take last 5 records
    const lastData = sensorData.slice(0, 5).reverse();
    const labels = lastData.map((_, i) => `T${i + 1}`);
    const temperatures = lastData.map(s => s.temperature);
    const humidities = lastData.map(s => (s.humidity * 100).toFixed(1));
    const fogProbs = lastData.map(s => (s.probability_fog * 100).toFixed(1));
    const smokeProbs = lastData.map(s => (s.probability_smoke * 100).toFixed(1));
    const vaporProbs = lastData.map(s => (s.probability_vapor * 100).toFixed(1));
    const smugProbs = lastData.map(s => (s.probability_smug * 100).toFixed(1));

    // Temperature Chart
    updateLineChart('temperatureChart', 'temperature', labels, temperatures, 'Temperatura (°C)', '#dc3545');

    // Humidity Chart
    updateLineChart('humidityChart', 'humidity', labels, humidities, 'Humedad (%)', '#0dcaf0');

    // Probabilities Chart
    updateProbabilitiesChart(labels, fogProbs, smokeProbs, vaporProbs, smugProbs);
}

function updateLineChart(canvasId, chartKey, labels, data, label, color) {
    const ctx = document.getElementById(canvasId);
    
    if (!ctx) return;

    if (chartsInstances[chartKey]) {
        chartsInstances[chartKey].data.labels = labels;
        chartsInstances[chartKey].data.datasets[0].data = data;
        chartsInstances[chartKey].update();
    } else {
        chartsInstances[chartKey] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: color,
                    backgroundColor: color + '20',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: color,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { font: { size: 12 }, padding: 15 }
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

function updateProbabilitiesChart(labels, fogProbs, smokeProbs, vaporProbs, smugProbs) {
    const ctx = document.getElementById('probabilitiesChart');
    
    if (!ctx) return;

    if (chartsInstances.probabilities) {
        chartsInstances.probabilities.data.labels = labels;
        chartsInstances.probabilities.data.datasets[0].data = fogProbs;
        chartsInstances.probabilities.data.datasets[1].data = smokeProbs;
        chartsInstances.probabilities.data.datasets[2].data = vaporProbs;
        chartsInstances.probabilities.data.datasets[3].data = smugProbs;
        chartsInstances.probabilities.update();
    } else {
        chartsInstances.probabilities = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Niebla (%)',
                        data: fogProbs,
                        borderColor: '#0dcaf0',
                        backgroundColor: 'rgba(13, 202, 240, 0.1)',
                        tension: 0.4,
                        borderWidth: 2
                    },
                    {
                        label: 'Humo (%)',
                        data: smokeProbs,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        borderWidth: 2
                    },
                    {
                        label: 'Vapor (%)',
                        data: vaporProbs,
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.4,
                        borderWidth: 2
                    },
                    {
                        label: 'Smug (%)',
                        data: smugProbs,
                        borderColor: '#6c757d',
                        backgroundColor: 'rgba(108, 117, 125, 0.1)',
                        tension: 0.4,
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { font: { size: 11 }, padding: 15 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + '%' }
                    }
                }
            }
        });
    }
}

/**
 * =====================================================
 * UTILITY FUNCTIONS
 * =====================================================
 */

function getLevelColor(level) {
    switch(level) {
        case 'DANGER': return 'danger-custom';
        case 'WARNING': return 'warning-custom';
        case 'NORMAL': return 'success-custom';
        default: return 'info-custom';
    }
}

/**
 * Format timestamp to readable date
 */
function formatDate(timestamp) {
    return new Date(timestamp).toLocaleString();
}
