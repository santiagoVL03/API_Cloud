# EventBridge Rule: Ejecutar cada 2 horas
resource "aws_cloudwatch_event_rule" "check_sensors_schedule" {
  name                = "${var.project_name}-check-sensors-schedule"
  description         = "Trigger sensor status check every 2 hours"
  schedule_expression = "rate(2 hours)"

  tags = {
    Name = "Sensor Check Schedule"
  }
}

# Target: Lambda function para verificar sensores
resource "aws_cloudwatch_event_target" "check_sensors" {
  rule      = aws_cloudwatch_event_rule.check_sensors_schedule.name
  target_id = "CheckSensorStatusLambda"
  arn       = aws_lambda_function.check_sensor_status.arn
}

# Permiso para EventBridge invocar Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.check_sensor_status.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.check_sensors_schedule.arn
}
