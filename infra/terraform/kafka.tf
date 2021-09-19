resource "aiven_kafka" "http-nudger" {
  project      = data.aiven_project.http-nudger.project
  cloud_name   = "google-europe-north1"
  plan         = var.aiven_kafka_plan
  service_name = "http-nudger"
  kafka_user_config {
    kafka_authentication_methods {
      certificate = true
      sasl        = false
    }
  }
}

resource "aiven_kafka_topic" "url-monitor-prod" {
  project      = data.aiven_project.http-nudger.project
  service_name = aiven_kafka.http-nudger.service_name
  topic_name   = "url-monitor-prod"
  partitions   = 3
  replication  = 2
}

resource "aiven_service_user" "kafka_overlord" {
  project      = data.aiven_project.http-nudger.project
  service_name = aiven_kafka.http-nudger.service_name
  username     = "kafka_overlord"
}

output "kafka" {
  sensitive = true
  value = {
    "service_uri" = aiven_kafka.http-nudger.service_uri
    "access_key"  = split("\n", aiven_service_user.kafka_overlord.access_key)
    "access_cert" = aiven_service_user.kafka_overlord.access_cert
    "ca_cert" = data.aiven_project.http-nudger.ca_cert
  }
}
