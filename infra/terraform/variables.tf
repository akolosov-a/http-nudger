variable "aiven_api_token" {
  type = string
}

variable "aiven_project_name" {
  type = string
}

variable "aiven_kafka_plan" {
  type = string
  default = "startup-2"
}

variable "aiven_pg_plan" {
  type = string
  default = "hobbyist"
}

variable "aiven_cloud_name" {
  type = string
  default = "google-europe-north1"
}
