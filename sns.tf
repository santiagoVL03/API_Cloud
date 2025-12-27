# Tópico SNS para alertas
resource "aws_sns_topic" "alerts" {
  name              = "${var.project_name}-alerts"
  display_name      = "Fog Smoke Detection Alerts"
  
  tags = {
    Name = "Alert Notifications"
  }
}

# Suscripciones de email para las alertas
resource "aws_sns_topic_subscription" "alert_emails" {
  count     = length(var.alert_emails)
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_emails[count.index]
}

# Policy para permitir que Lambda publique en SNS
resource "aws_sns_topic_policy" "alerts_policy" {
  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = [
          "SNS:Publish"
        ]
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}
