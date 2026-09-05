resource "kubernetes_namespace_v1" "aegis" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name"       = var.app_name
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }
}

resource "kubernetes_config_map_v1" "aegis_config" {
  metadata {
    name      = "aegis-config"
    namespace = kubernetes_namespace_v1.aegis.metadata[0].name
    labels = {
      "app.kubernetes.io/name"       = var.app_name
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  data = {
    APP_NAME    = "Aegis API"
    APP_ENV     = var.environment
    APP_MESSAGE = "Hello from Aegis DevOps Platform managed by Terraform!"
    LOG_LEVEL   = "INFO"
    PORT        = "8000"
  }
}

resource "kubernetes_service_v1" "aegis_service" {
  metadata {
    name      = "aegis-service"
    namespace = kubernetes_namespace_v1.aegis.metadata[0].name
    labels = {
      "app.kubernetes.io/name"       = var.app_name
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  spec {
    selector = {
      app = var.app_name
    }

    port {
      name        = "http"
      port        = 80
      target_port = 8000
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}
