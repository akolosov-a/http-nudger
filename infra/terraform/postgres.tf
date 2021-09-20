resource "aiven_pg" "http-nudger" {
  project      = data.aiven_project.http-nudger.project
  cloud_name   = var.aiven_cloud_name
  plan         = var.aiven_pg_plan
  service_name = "http-nudger-pg"
}

resource "aiven_database" "http-nudger" {
  project       = data.aiven_project.http-nudger.project
  service_name  = aiven_pg.http-nudger.service_name
  database_name = "http-nudger"
}

output "postgres" {
  sensitive = true
  value = {
    "hostname" = aiven_pg.http-nudger.service_host
    "port" = aiven_pg.http-nudger.service_port
    "username"    = aiven_pg.http-nudger.service_username
    "password" = aiven_pg.http-nudger.service_password
  }
}
