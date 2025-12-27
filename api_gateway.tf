# HTTP API Gateway (más económico que REST API)
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
  description   = "Serverless API for Fog/Smoke Detection System"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["*"]
    max_age       = 300
  }

  tags = {
    Name = "Fog Smoke Detection API"
  }
}

# Stage de producción
resource "aws_apigatewayv2_stage" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }

  tags = {
    Name = "Production Stage"
  }
}

# Integraciones Lambda
resource "aws_apigatewayv2_integration" "insert_sensor_data" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.insert_sensor_data.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "insert_sensor_status" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.insert_sensor_status.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "send_alerts" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.send_alerts.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "get_sensor_data" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_sensor_data.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "get_ml_detection" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_ml_detection.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "get_alerts" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_alerts.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "get_sensor_status" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_sensor_status.invoke_arn
  payload_format_version = "2.0"
}

# Rutas
resource "aws_apigatewayv2_route" "insert_sensor_data" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /sensor-data"
  target    = "integrations/${aws_apigatewayv2_integration.insert_sensor_data.id}"
}

resource "aws_apigatewayv2_route" "insert_sensor_status" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /sensor-status"
  target    = "integrations/${aws_apigatewayv2_integration.insert_sensor_status.id}"
}

resource "aws_apigatewayv2_route" "send_alerts" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /alerts/send"
  target    = "integrations/${aws_apigatewayv2_integration.send_alerts.id}"
}

resource "aws_apigatewayv2_route" "get_sensor_data" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /sensor-data"
  target    = "integrations/${aws_apigatewayv2_integration.get_sensor_data.id}"
}

resource "aws_apigatewayv2_route" "get_ml_detection" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /ml-detection"
  target    = "integrations/${aws_apigatewayv2_integration.get_ml_detection.id}"
}

resource "aws_apigatewayv2_route" "get_alerts" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /alerts"
  target    = "integrations/${aws_apigatewayv2_integration.get_alerts.id}"
}

resource "aws_apigatewayv2_route" "get_sensor_status" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /sensor-status"
  target    = "integrations/${aws_apigatewayv2_integration.get_sensor_status.id}"
}

# Permisos para API Gateway invocar Lambda
resource "aws_lambda_permission" "api_gateway" {
  for_each = {
    insert_sensor_data   = aws_lambda_function.insert_sensor_data.function_name
    insert_sensor_status = aws_lambda_function.insert_sensor_status.function_name
    send_alerts          = aws_lambda_function.send_alerts.function_name
    get_sensor_data      = aws_lambda_function.get_sensor_data.function_name
    get_ml_detection     = aws_lambda_function.get_ml_detection.function_name
    get_alerts           = aws_lambda_function.get_alerts.function_name
    get_sensor_status    = aws_lambda_function.get_sensor_status.function_name
  }

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = each.value
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
