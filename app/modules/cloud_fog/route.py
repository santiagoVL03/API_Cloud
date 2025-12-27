from flask import Blueprint, make_response, jsonify, request
from .controller import Cloud_fogController


cloud_fog_bp = Blueprint('cloud_fog', __name__)
cloud_fog_controller = Cloud_fogController()


@cloud_fog_bp.route('/', methods=['GET'])
def index():
    """Example endpoint with simple greeting.
    ---
    tags:
      - Cloud Fog API
    responses:
      200:
        description: A simple greeting
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                message:
                  type: string
                  example: "Hello World!"
    """
    result = cloud_fog_controller.index()
    return make_response(jsonify(data=result))


@cloud_fog_bp.route('/early-detection', methods=['GET'])
def early_detection():
    """
    Early detection system endpoint.
    
    Receives sensor data, checks thresholds, captures camera frames,
    detects fog/smoke, and uploads to cloud.
    ---
    tags:
      - Cloud Fog API
    parameters:
      - name: temperature
        in: query
        type: number
        required: true
        description: Temperature in Celsius
        example: 15.5
      - name: humidity
        in: query
        type: number
        required: true
        description: Humidity percentage (0-100)
        example: 92.0
    responses:
      200:
        description: Detection completed successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                sensor_data:
                  type: object
                  properties:
                    temperature:
                      type: number
                      example: 15.5
                    humidity:
                      type: number
                      example: 92.0
                threshold_check:
                  type: object
                  properties:
                    should_analyze:
                      type: boolean
                      example: true
                    fog_conditions_met:
                      type: boolean
                      example: true
                    smoke_conditions_met:
                      type: boolean
                      example: false
                    conditions_detected:
                      type: array
                      items:
                        type: string
                      example: ["FOG"]
                detection_results:
                  type: object
                  properties:
                    fog_detected:
                      type: boolean
                      example: true
                    smoke_detected:
                      type: boolean
                      example: false
                    probability_fog:
                      type: number
                      example: 0.752
                    probability_smoke:
                      type: number
                      example: 0.123
                    probability_vapor:
                      type: number
                      example: 0.456
                    probability_smug:
                      type: number
                      example: 0.089
                cloud_upload:
                  type: object
                  properties:
                    success:
                      type: boolean
                      example: true
                    status_code:
                      type: integer
                      example: 200
                message:
                  type: string
                  example: "FOG DETECTED (75.2%) - Data uploaded to cloud"
      400:
        description: Invalid parameters
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Missing required parameter: temperature"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Detection failed"
    """
    try:
        # Get query parameters
        temperature = request.args.get('temperature', type=float)
        humidity = request.args.get('humidity', type=float)
        
        # Validate parameters
        if temperature is None:
            return make_response(
                jsonify(success=False, error="Missing required parameter: temperature"),
                400
            )
        
        if humidity is None:
            return make_response(
                jsonify(success=False, error="Missing required parameter: humidity"),
                400
            )
        
        # Validate ranges
        if not (-50 <= temperature <= 160):
            return make_response(
                jsonify(success=False, error="Temperature out of valid range (-50 to 160°C)"),
                400
            )
        
        if not (0 <= humidity <= 100):
            return make_response(
                jsonify(success=False, error="Humidity out of valid range (0-100%)"),
                400
            )
        
        # Execute early detection
        result = cloud_fog_controller.early_detection(
            temperature=temperature,
            humidity=humidity
        )
        
        return make_response(jsonify(success=True, data=result), 200)
        
    except Exception as e:
        return make_response(
            jsonify(success=False, error=f"Detection failed: {str(e)}"),
            500
        )
      