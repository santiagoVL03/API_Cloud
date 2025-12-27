import os
import requests
import logging
from typing import Dict, Any
from datetime import datetime
from app.utils.camera_util import CameraUtil
from app.utils.detection_util import DetectionUtil

logger = logging.getLogger(__name__)


class Cloud_fogController:
    """Controller for early detection system (Fog Computing layer)."""
    
    # Thresholds for fog and smoke conditions
    FOG_HUMIDITY_THRESHOLD = 90.0  # >= 90%
    FOG_TEMP_MIN = 5.0             # >= 5°C
    FOG_TEMP_MAX = 20.0            # <= 20°C
    
    SMOKE_TEMP_THRESHOLD = 45.0    # >= 45°C
    SMOKE_HUMIDITY_THRESHOLD = 40.0  # <= 40%
    
    def __init__(self):
        """Initialize controller with utilities and cloud API config."""
        self.camera_util = CameraUtil(camera_ip="192.168.15.66")
        self.detection_util = DetectionUtil()
        
        # Cloud API endpoint (from environment or default)
        self.cloud_api_url = os.getenv(
            'CLOUD_API_URL',
            'https://YOUR_API_URL.execute-api.us-east-1.amazonaws.com'
        )
        
    def index(self):
        """Simple health check endpoint."""
        return {'message': 'Hello, World!'}
    
    def early_detection(self, temperature: float, humidity: float) -> Dict[str, Any]:
        """
        Early detection system with HYBRID strategy:
        1. ALWAYS receives sensor data (temperature and humidity)
        2. ALWAYS sends basic data to cloud for historical tracking
        3. ONLY captures video and analyzes when thresholds are exceeded
        4. Cloud decides whether to send alerts based on all data
        
        Args:
            temperature: Temperature in Celsius
            humidity: Humidity as percentage (0-100)
            
        Returns:
            Dictionary with detection results and cloud upload status
        """
        logger.info(f"Early detection started - Temp: {temperature}°C, Humidity: {humidity}%")
        
        result = {
            'sensor_data': {
                'temperature': temperature,
                'humidity': humidity
            },
            'threshold_check': {},
            'detection_results': {},
            'cloud_upload': {}
        }
        
        # Step 1: Check thresholds
        threshold_check = self._check_thresholds(temperature, humidity)
        result['threshold_check'] = threshold_check
        
        # Step 2: Decide if video analysis is needed
        if threshold_check['should_analyze']:
            logger.info(f"Thresholds exceeded for: {threshold_check['conditions_detected']}")
            logger.info("Capturing 24 frames from IP camera...")
            
            # Capture frames from camera
            frames = self.camera_util.capture_frames(num_frames=24, delay=0.1)
            
            if not frames:
                logger.error("Failed to capture frames from camera")
                result['error'] = "Camera capture failed"
                # Use default values if camera fails
                detection_results = self._get_default_detection_results()
            else:
                logger.info(f"Successfully captured {len(frames)} frames")
                
                # Analyze frames for fog/smoke
                logger.info("Analyzing frames for fog/smoke detection...")
                detection_results = self.detection_util.analyze_frames(frames)
        else:
            # No threshold exceeded - skip video capture (save resources)
            logger.info("Thresholds not exceeded - Skipping video capture (sending basic data only)")
            detection_results = self._get_default_detection_results()
        
        result['detection_results'] = detection_results
        
        # Step 3: ALWAYS prepare data for cloud upload (with or without video analysis)
        cloud_data = self._prepare_cloud_data(
            temperature=temperature,
            humidity=humidity,
            detection_results=detection_results,
            threshold_check=threshold_check
        )
        
        # Step 4: ALWAYS upload to cloud (for historical tracking)
        logger.info("Uploading data to cloud...")
        upload_status = self._upload_to_cloud(cloud_data)
        result['cloud_upload'] = upload_status
        
        # Step 5: Generate summary message
        if threshold_check['should_analyze']:
            if detection_results['fog_detected']:
                result['message'] = f"FOG DETECTED ({detection_results['probability_fog']*100:.1f}%) - Video analyzed - Data uploaded to cloud"
            elif detection_results['smoke_detected']:
                result['message'] = f"SMOKE DETECTED ({detection_results['probability_smoke']*100:.1f}%) - Video analyzed - Data uploaded to cloud"
            else:
                result['message'] = "Threshold exceeded - Video analyzed - Data uploaded to cloud"
        else:
            result['message'] = "Normal conditions - Basic data uploaded to cloud (no video analysis)"
        
        logger.info(f"Early detection complete: {result['message']}")
        
        return result
    
    def _check_thresholds(self, temperature: float, humidity: float) -> Dict[str, Any]:
        """
        Check if sensor readings exceed thresholds for fog or smoke.
        
        FOG conditions:
        - Humidity >= 90%
        - Temperature between 5°C and 20°C
        
        SMOKE conditions:
        - Temperature >= 45°C
        - Humidity <= 40%
        
        Args:
            temperature: Temperature in Celsius
            humidity: Humidity as percentage
            
        Returns:
            Dictionary with threshold check results
        """
        fog_conditions = (
            humidity >= self.FOG_HUMIDITY_THRESHOLD and
            self.FOG_TEMP_MIN <= temperature <= self.FOG_TEMP_MAX
        )
        
        smoke_conditions = (
            temperature >= self.SMOKE_TEMP_THRESHOLD and
            humidity <= self.SMOKE_HUMIDITY_THRESHOLD
        )
        
        conditions_detected = []
        if fog_conditions:
            conditions_detected.append('FOG')
        if smoke_conditions:
            conditions_detected.append('SMOKE')
        
        return {
            'should_analyze': fog_conditions or smoke_conditions,
            'fog_conditions_met': fog_conditions,
            'smoke_conditions_met': smoke_conditions,
            'conditions_detected': conditions_detected,
            'thresholds': {
                'fog': {
                    'humidity': f'>= {self.FOG_HUMIDITY_THRESHOLD}%',
                    'temperature': f'{self.FOG_TEMP_MIN}°C - {self.FOG_TEMP_MAX}°C'
                },
                'smoke': {
                    'temperature': f'>= {self.SMOKE_TEMP_THRESHOLD}°C',
                    'humidity': f'<= {self.SMOKE_HUMIDITY_THRESHOLD}%'
                }
            }
        }
    
    def _get_default_detection_results(self) -> Dict[str, Any]:
        """
        Returns default detection results when no video analysis is performed.
        Used when thresholds are not exceeded (HYBRID strategy).
        This saves resources by skipping camera capture and CV analysis.
        """
        return {
            'fog_detected': False,
            'smoke_detected': False,
            'vapor_detected': False,
            'smog_detected': False,
            'probability_fog': 0.0,
            'probability_smoke': 0.0,
            'probability_vapor': 0.0,
            'probability_smog': 0.0,
            'frames_analyzed': 0,
            'detection_method': 'threshold_only',
            'timestamp': datetime.now().isoformat()
        }
    
    def _prepare_cloud_data(self, temperature: float, humidity: float,
                           detection_results: Dict[str, Any],
                           threshold_check: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data payload for cloud upload.
        
        Args:
            temperature: Temperature reading
            humidity: Humidity reading
            detection_results: Results from detection analysis
            threshold_check: Results from threshold checking
            
        Returns:
            Formatted data for cloud API
        """
        # Determine alert message
        alert_message = "Normal"
        danger_alert = ""
        
        if detection_results['fog_detected']:
            alert_message = "FOG DETECTED - Reduced visibility"
            danger_alert = f"High fog probability: {detection_results['probability_fog']*100:.1f}%"
        if detection_results['smoke_detected']:
            alert_message = "SMOKE DETECTED - Possible fire hazard" + alert_message
            danger_alert = f"High smoke probability: {detection_results['probability_smoke']*100:.1f}%" + danger_alert
        if threshold_check['fog_conditions_met']:
            alert_message = "FOG CONDITIONS - Monitoring" + alert_message
        if threshold_check['smoke_conditions_met']:
            alert_message = "SMOKE CONDITIONS - Monitoring" + alert_message

        # Format for cloud API (matching the Lambda function schema)
        cloud_payload = {
            "data": {
                "temperature": str(temperature),
                "humidity": str(humidity / 100.0),  # Convert to 0-1 range
                "probability_vapor": str(detection_results['probability_vapor']),
                "probability_smug": str(detection_results['probability_smog']),
                "probability_smoke": str(detection_results['probability_smoke']),
                "probability_fog": str(detection_results['probability_fog']),
                "alert": alert_message,
                "danger_alert": danger_alert
            }
        }
        
        return cloud_payload
    
    def _upload_to_cloud(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload sensor and detection data to cloud API.
        
        Args:
            data: Formatted data payload
            
        Returns:
            Upload status and response
        """
        try:
            endpoint = f"{self.cloud_api_url}/sensor-data"
            
            logger.info(f"Sending data to cloud: {endpoint}")
            
            response = requests.post(
                endpoint,
                json=data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            
            logger.info(f"Cloud upload successful: {response.status_code}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json(),
                'endpoint': endpoint
            }
            
        except requests.exceptions.Timeout:
            logger.error("Cloud upload timeout")
            return {
                'success': False,
                'error': 'Request timeout',
                'endpoint': endpoint
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'endpoint': endpoint
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during cloud upload: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'endpoint': endpoint
            }
