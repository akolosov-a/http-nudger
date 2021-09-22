NAME=http-nudger
TAG=0.1.0-1

test:
	tox

image:
	docker build -t $(NAME):$(TAG) .

infra:
	terraform -chdir=infra/terraform init
	terraform -chdir=infra/terraform apply

deploy:
	terraform -chdir=infra/terraform output -json | jq -r '.aiven_project.value.ca_cert' > ca.pem
	terraform -chdir=infra/terraform output -json | jq -r '.kafka.value.access_cert' > kafka-cert.pem
	terraform -chdir=infra/terraform output -json | jq -r '.kafka.value.access_key' > kafka-key.pem
	terraform -chdir=infra/terraform output -json | jq -r '"KAFKA_BOOTSTRAP_SERVERS=\(.kafka.value.bootstrap_servers)", "KAFKA_TOPIC=\(.kafka.value.topic_name)"' > kafka.env
	terraform -chdir=infra/terraform output -json | jq -r '"PG_HOST=\(.postgres.value.hostname)", "PG_PORT=\(.postgres.value.port)", "PG_DB=\(.postgres.value.dbname)", "PG_USER=\(.postgres.value.username)", "PG_PASSWORD=\(.postgres.value.password)"' > postgres.env


.PHONY: image test infra
