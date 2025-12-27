# API Gateway URL
output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

# URLs de los endpoints
output "endpoints" {
  description = "API endpoints for all services"
  value = {
    insert_sensor_data   = "${aws_apigatewayv2_api.main.api_endpoint}/sensor-data"
    insert_sensor_status = "${aws_apigatewayv2_api.main.api_endpoint}/sensor-status"
    send_alerts          = "${aws_apigatewayv2_api.main.api_endpoint}/alerts/send"
    get_sensor_data      = "${aws_apigatewayv2_api.main.api_endpoint}/sensor-data"
    get_ml_detection     = "${aws_apigatewayv2_api.main.api_endpoint}/ml-detection"
    get_alerts           = "${aws_apigatewayv2_api.main.api_endpoint}/alerts"
    get_sensor_status    = "${aws_apigatewayv2_api.main.api_endpoint}/sensor-status"
  }
}

# Tablas DynamoDB
output "dynamodb_tables" {
  description = "DynamoDB table names"
  value = {
    sensor_data   = aws_dynamodb_table.sensor_data.name
    sensor_status = aws_dynamodb_table.sensor_status.name
    alerts        = aws_dynamodb_table.alerts.name
  }
}

# SNS Topic
output "sns_topic_arn" {
  description = "SNS Topic ARN for alerts"
  value       = aws_sns_topic.alerts.arn
}

# Lambda Functions
output "lambda_functions" {
  description = "Lambda function names"
  value = {
    insert_sensor_data   = aws_lambda_function.insert_sensor_data.function_name
    insert_sensor_status = aws_lambda_function.insert_sensor_status.function_name
    send_alerts          = aws_lambda_function.send_alerts.function_name
    get_sensor_data      = aws_lambda_function.get_sensor_data.function_name
    get_ml_detection     = aws_lambda_function.get_ml_detection.function_name
    get_alerts           = aws_lambda_function.get_alerts.function_name
    get_sensor_status    = aws_lambda_function.get_sensor_status.function_name
    check_sensor_status  = aws_lambda_function.check_sensor_status.function_name
  }
}

# EventBridge Schedule
output "sensor_check_schedule" {
  description = "EventBridge schedule for sensor checking"
  value       = aws_cloudwatch_event_rule.check_sensors_schedule.schedule_expression
}

# Alert email addresses
output "alert_email_addresses" {
  description = "Email addresses configured for alerts"
  value       = var.alert_emails
}
