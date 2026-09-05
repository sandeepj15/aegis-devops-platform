variable "namespace" {
  description = "Target Kubernetes namespace for Aegis infrastructure"
  type        = string
  default     = "aegis"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "aegis-api"
}

variable "environment" {
  description = "Target deployment environment"
  type        = string
  default     = "production"
}

variable "replicas" {
  description = "Default replica count"
  type        = number
  default     = 2
}
