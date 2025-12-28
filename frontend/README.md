# Cloud Fog API - Frontend Dashboard

Dashboard interactivo para monitorear el sistema de detección de niebla y humo en tiempo real.

## 📋 Características

### 1. **Dashboard Principal**
- Estadísticas en tiempo real (Total de alertas, alertas peligrosas, detecciones ML, registros sensores)
- Interfaz responsiva y moderna con diseño moderno
- Actualización automática de datos

### 2. **Sección de Alertas** 
- 📅 **Calendario interactivo**: Visualiza las fechas cuando ocurrieron las alertas
- 📊 **Gráfico de distribución**: Muestra el ratio entre alertas por email y alertas de peligro
- 📧 **Tabla de Alertas Email**: Historial de alertas enviadas por email
- 🚨 **Tabla de Alertas de Peligro**: Alertas críticas con temperatura, humedad y detalles
- **Actualización**: Cada 2 minutos

### 3. **Sección de Detección ML**
- 📈 **Gráfico de barras**: Muestra las últimas 5 detecciones con:
  - Probabilidad de Niebla (%)
  - Probabilidad de Humo (%)
  - Probabilidad de Vapor (%)
  - Probabilidad de Smug (%)
- 📋 **Tabla de historial**: Detalle de todas las detecciones ML
- **Actualización**: Cada 25 segundos

### 4. **Sección de Datos de Sensores**
- 🌡️ **Gráfico Temperatura**: Evolución temporal de la temperatura
- 💧 **Gráfico Humedad**: Evolución temporal de la humedad
- 📊 **Gráfico de Probabilidades**: Todas las métricas de detección en una sola vista
- 📋 **Tabla de histórico**: Registro detallado de todos los datos de sensores
- **Actualización**: Cada 25 segundos

## 🎨 Tecnologías Utilizadas

- **HTML5** - Estructura semántica
- **Bootstrap 5** - Framework CSS responsivo
- **Chart.js** - Gráficos interactivos (líneas, barras, doughnut)
- **FullCalendar** - Calendario interactivo
- **Bootstrap Icons** - Iconografía moderna
- **Vanilla JavaScript** - Lógica y actualizaciones en tiempo real

## 🚀 Estructura de Archivos

```
frontend/
├── index.html          # Página principal (estructura + estilos)
└── js/
    └── dashboard.js    # Lógica de datos y gráficos
```

## 🔄 Flujo de Datos

1. **Carga inicial**: Se ejecuta `loadAllData()` que carga:
   - `loadAlerts()` → API de alertas
   - `loadMlDetection()` → API de detección ML
   - `loadSensorData()` → API de datos sensores

2. **Actualizaciones automáticas**:
   - Alertas: Cada 2 minutos (120,000 ms)
   - Detección ML: Cada 25 segundos (25,000 ms)
   - Datos sensores: Cada 25 segundos (25,000 ms)

3. **Actualización de interfaz**:
   - Tablas: Se renderizan con `displayXXX()` functions
   - Gráficos: Se crean o actualizan con `updateXXXChart()` functions
   - Calendario: Se actualiza con eventos de alertas

## 📊 API Endpoints Utilizados

```javascript
const API_ENDPOINTS = {
    getAlerts: 'https://3czhlao6ei.execute-api.us-east-1.amazonaws.com/alerts',
    getMlDetection: 'https://3czhlao6ei.execute-api.us-east-1.amazonaws.com/ml-detection',
    getSensorData: 'https://3czhlao6ei.execute-api.us-east-1.amazonaws.com/sensor-data',
};
```

## 🎯 Funciones Principales

### Alertas
- `loadAlerts()` - Carga datos de alertas
- `displayEmailAlerts()` - Renderiza tabla de alertas email
- `displayDangerAlerts()` - Renderiza tabla de alertas peligrosas
- `updateAlertsChart()` - Actualiza gráfico de distribución
- `updateCalendarWithAlerts()` - Agrega eventos al calendario

### Detección ML
- `loadMlDetection()` - Carga datos de detección ML
- `displayMlDetections()` - Renderiza tabla de detecciones
- `updateMlDetectionChart()` - Gráfico de barras con 4 series

### Datos Sensores
- `loadSensorData()` - Carga datos de sensores
- `displaySensorData()` - Renderiza tabla de histórico
- `updateSensorCharts()` - Actualiza todos los gráficos de sensores
- `updateLineChart()` - Gráfico de línea genérico
- `updateProbabilitiesChart()` - Gráfico con 4 probabilidades

## 🔧 Configuración

Para cambiar los tiempos de actualización, modifica el objeto `UPDATE_INTERVALS`:

```javascript
const UPDATE_INTERVALS = {
    alerts: 2 * 60 * 1000,      // 2 minutos
    mlDetection: 25 * 1000,      // 25 segundos
    sensorData: 25 * 1000,       // 25 segundos
};
```

## 🌐 Uso

1. Abre `index.html` en un navegador web
2. El dashboard cargará automáticamente los datos
3. Los datos se actualizarán según los intervalos configurados
4. Navega entre las pestañas (Alertas, Detección ML, Datos Sensores)

## 📱 Características de Responsividad

- Diseño totalmente responsivo
- Gráficos se adaptan al tamaño de pantalla
- Tablas con scroll horizontal en dispositivos móviles
- Navbar colapsible en pantallas pequeñas

## 🎨 Esquema de Colores

- **Peligro (DANGER)**: #dc3545 (Rojo)
- **Advertencia**: #ffc107 (Amarillo)
- **Info**: #0dcaf0 (Azul claro)
- **Éxito**: #198754 (Verde)
- **Primario**: Gradiente violeta (#667eea → #764ba2)

## 📝 Notas

- CORS debe estar habilitado en los endpoints de API
- La sincronización de datos se muestra en la barra de navegación
- Cada tabla muestra los últimos 10 registros (configurable)
- Los gráficos se redibujan automáticamente con nuevos datos
- El calendario es interactivo (cambiar vista mes/semana)

## 🔐 Consideraciones de Seguridad

- Las solicitudes se hacen con `mode: 'cors'`
- Los datos se validan antes de renderizar
- Los IDs se truncan a 8 caracteres en tablas
- No se almacenan credenciales en el frontend
