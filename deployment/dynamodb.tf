# Tabla para datos de sensores y detección ML
resource "aws_dynamodb_table" "sensor_data" {
  name           = "${var.project_name}-sensor-data"
  billing_mode   = "PAY_PER_REQUEST"  # Serverless - sin capacidad provisionada
  hash_key       = "id"
  range_key      = "timestamp"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "alert_level"
    type = "S"
  }

  # Índice secundario global para consultas por nivel de alerta
  global_secondary_index {
    name            = "AlertLevelIndex"
    hash_key        = "alert_level"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "Sensor Data Table"
  }
}

# Tabla para estado de sensores y cámaras
resource "aws_dynamodb_table" "sensor_status" {
  name           = "${var.project_name}-sensor-status"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  range_key      = "timestamp"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "has_alert"
    type = "S"
  }

  # Índice para consultar rápidamente sensores con problemas
  global_secondary_index {
    name            = "StatusAlertIndex"
    hash_key        = "has_alert"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "Sensor Status Table"
  }
}

# Tabla para registro de alertas enviadas
resource "aws_dynamodb_table" "alerts" {
  name           = "${var.project_name}-alerts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "alert_id"
  range_key      = "timestamp"

  attribute {
    name = "alert_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "alert_type"
    type = "S"
  }

  # Índice para consultar por tipo de alerta
  global_secondary_index {
    name            = "AlertTypeIndex"
    hash_key        = "alert_type"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "Alerts History Table"
  }
}
