NAME=http-nudger
TAG=0.1.0-1

test:
	tox

image:
	docker build -t $(NAME):$(TAG) .

infra:
	terraform -chdir=infra/terraform init
	terraform -chdir=infra/terraform apply
	terraform -chdir=infra/terraform output -json | jq -r '.aiven_project.value.ca_cert' > ca.pem
	terraform -chdir=infra/terraform output -json | jq -r '.kafka.value.access_cert' > kafka-cert.pem
	terraform -chdir=infra/terraform output -json | jq -r '.kafka.value.access_key' > kafka-key.pem
	terraform -chdir=infra/terraform output -json | jq -r '"KAFKA_BOOTSTRAP_SERVERS=\(.kafka.value.bootstrap_servers)", "KAFKA_TOPIC=\(.kafka.value.topic_name)"' > kafka.env
	terraform -chdir=infra/terraform output -json | jq -r '"PG_HOST=\(.postgres.value.hostname)", "PG_PORT=\(.postgres.value.port)", "PG_DB=\(.postgres.value.dbname)", "PG_USER=\(.postgres.value.username)", "PG_PASSWORD=\(.postgres.value.password)"' > postgres.env

deploy_k8s:
	kubectl delete cm aiven-kafka
	kubectl delete secret aiven-postgres aiven-kafka-tls
	kubectl create cm --from-env-file=kafka.env aiven-kafka
	kubectl create secret generic --from-env-file=postgres.env aiven-postgres
	kubectl create secret generic --from-file=kafka-key.pem --from-file=kafka-cert.pem --from-file=ca.pem aiven-kafka-tls
	kubectl apply -f infra/k8s/http-nudger-monitor.yaml
	kubectl apply -f infra/k8s/http-nudger-persister.yaml

.PHONY: image test infra
