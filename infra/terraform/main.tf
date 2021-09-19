terraform {
  required_providers {
    aiven = {
      source  = "aiven/aiven"
      version = "2.1.19"
    }
  }
}

provider "aiven" {
  api_token = var.aiven_api_token
}

data "aiven_project" "http-nudger" {
  project = var.aiven_project_name
}
