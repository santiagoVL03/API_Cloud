variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "fog-smoke-detection"
}

variable "alert_emails" {
  description = "Email addresses for alerts"
  type        = list(string)
  default     = ["santiagovl0308@gmail.com", "jeiboxgmr@gmail.com"]
}

# Umbrales para alertas
variable "temperature_threshold" {
  description = "Temperature threshold in Celsius"
  type        = number
  default     = 45
}

variable "humidity_threshold" {
  description = "Humidity threshold (0.0 - 1.0)"
  type        = number
  default     = 0.10
}

variable "smoke_probability_threshold" {
  description = "Smoke probability threshold for danger alerts"
  type        = number
  default     = 0.70
}

variable "fog_probability_threshold" {
  description = "Fog probability threshold for danger alerts (critical for driving safety)"
  type        = number
  default     = 0.60
}
