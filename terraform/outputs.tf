output "namespace" {
  description = "Created Kubernetes namespace"
  value       = kubernetes_namespace_v1.aegis.metadata[0].name
}

output "config_map_name" {
  description = "Created ConfigMap name"
  value       = kubernetes_config_map_v1.aegis_config.metadata[0].name
}

output "service_name" {
  description = "Created Service name"
  value       = kubernetes_service_v1.aegis_service.metadata[0].name
}
