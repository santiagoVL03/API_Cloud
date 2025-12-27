# Empaqueta funciones Lambda
data "archive_file" "lambda_functions" {
  for_each = {
    insert_sensor_data   = "insert_sensor_data.py"
    insert_sensor_status = "insert_sensor_status.py"
    send_alerts          = "send_alerts.py"
    get_sensor_data      = "get_sensor_data.py"
    get_ml_detection     = "get_ml_detection.py"
    get_alerts           = "get_alerts.py"
    get_sensor_status    = "get_sensor_status.py"
    check_sensor_status  = "check_sensor_status.py"
  }

  type        = "zip"
  source_file = "${path.module}/../lambda_functions/${each.value}"
  output_path = "${path.module}/.terraform/lambda_zips/${each.key}.zip"
}

# Lambda Function: Insertar datos de sensores
resource "aws_lambda_function" "insert_sensor_data" {
  filename         = data.archive_file.lambda_functions["insert_sensor_data"].output_path
  function_name    = "${var.project_name}-insert-sensor-data"
  role            = aws_iam_role.lambda_role.arn
  handler         = "insert_sensor_data.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["insert_sensor_data"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      SENSOR_DATA_TABLE      = aws_dynamodb_table.sensor_data.name
      ALERTS_TABLE           = aws_dynamodb_table.alerts.name
      TEMP_THRESHOLD         = var.temperature_threshold
      HUMIDITY_THRESHOLD     = var.humidity_threshold
      SMOKE_THRESHOLD        = var.smoke_probability_threshold
      FOG_THRESHOLD          = var.fog_probability_threshold
      ALERT_FUNCTION_NAME    = "${var.project_name}-send-alerts"
    }
  }

  tags = {
    Name = "Insert Sensor Data"
  }
}

# Lambda Function: Insertar estado de sensores
resource "aws_lambda_function" "insert_sensor_status" {
  filename         = data.archive_file.lambda_functions["insert_sensor_status"].output_path
  function_name    = "${var.project_name}-insert-sensor-status"
  role            = aws_iam_role.lambda_role.arn
  handler         = "insert_sensor_status.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["insert_sensor_status"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      SENSOR_STATUS_TABLE = aws_dynamodb_table.sensor_status.name
    }
  }

  tags = {
    Name = "Insert Sensor Status"
  }
}

# Lambda Function: Enviar alertas
resource "aws_lambda_function" "send_alerts" {
  filename         = data.archive_file.lambda_functions["send_alerts"].output_path
  function_name    = "${var.project_name}-send-alerts"
  role            = aws_iam_role.lambda_role.arn
  handler         = "send_alerts.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["send_alerts"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      ALERTS_TABLE   = aws_dynamodb_table.alerts.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = {
    Name = "Send Alerts"
  }
}

# Lambda Function: Obtener datos de sensores
resource "aws_lambda_function" "get_sensor_data" {
  filename         = data.archive_file.lambda_functions["get_sensor_data"].output_path
  function_name    = "${var.project_name}-get-sensor-data"
  role            = aws_iam_role.lambda_role.arn
  handler         = "get_sensor_data.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["get_sensor_data"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      SENSOR_DATA_TABLE = aws_dynamodb_table.sensor_data.name
    }
  }

  tags = {
    Name = "Get Sensor Data"
  }
}

# Lambda Function: Obtener detección ML
resource "aws_lambda_function" "get_ml_detection" {
  filename         = data.archive_file.lambda_functions["get_ml_detection"].output_path
  function_name    = "${var.project_name}-get-ml-detection"
  role            = aws_iam_role.lambda_role.arn
  handler         = "get_ml_detection.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["get_ml_detection"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      SENSOR_DATA_TABLE = aws_dynamodb_table.sensor_data.name
    }
  }

  tags = {
    Name = "Get ML Detection"
  }
}

# Lambda Function: Obtener alertas
resource "aws_lambda_function" "get_alerts" {
  filename         = data.archive_file.lambda_functions["get_alerts"].output_path
  function_name    = "${var.project_name}-get-alerts"
  role            = aws_iam_role.lambda_role.arn
  handler         = "get_alerts.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["get_alerts"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      ALERTS_TABLE      = aws_dynamodb_table.alerts.name
      SENSOR_DATA_TABLE = aws_dynamodb_table.sensor_data.name
    }
  }

  tags = {
    Name = "Get Alerts"
  }
}

# Lambda Function: Obtener estado de sensores
resource "aws_lambda_function" "get_sensor_status" {
  filename         = data.archive_file.lambda_functions["get_sensor_status"].output_path
  function_name    = "${var.project_name}-get-sensor-status"
  role            = aws_iam_role.lambda_role.arn
  handler         = "get_sensor_status.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["get_sensor_status"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      SENSOR_STATUS_TABLE = aws_dynamodb_table.sensor_status.name
    }
  }

  tags = {
    Name = "Get Sensor Status"
  }
}

# Lambda Function: Verificar estado de sensores (scheduled)
resource "aws_lambda_function" "check_sensor_status" {
  filename         = data.archive_file.lambda_functions["check_sensor_status"].output_path
  function_name    = "${var.project_name}-check-sensor-status"
  role            = aws_iam_role.lambda_role.arn
  handler         = "check_sensor_status.lambda_handler"
  source_code_hash = data.archive_file.lambda_functions["check_sensor_status"].output_base64sha256
  runtime         = "python3.11"
  timeout         = 60

  environment {
    variables = {
      SENSOR_STATUS_TABLE  = aws_dynamodb_table.sensor_status.name
      ALERT_FUNCTION_NAME  = "${var.project_name}-send-alerts"
    }
  }

  tags = {
    Name = "Check Sensor Status - Scheduled"
  }
}
