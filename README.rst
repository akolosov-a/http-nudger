http-nudger
===========
``http-nudger`` is a distributed website availability monitoring
tool. The tool consists of two main components - ``monitor`` and
``persister``. The ``monitor`` periodically checks the availability of
the given website over HTTP and sends the collected metrics to the
given Kafka topic. The ``persister`` consumes the metrics from the
given Kafka topic and stores them into the given PostgresSQL database.

Installation
------------
Use pip to install ``http-nudger`` from the cloned repository::
  
  $ pip install .

To build the Docker image::
  
  $ make image

Usage
-----

The monitor process::

  $ http-nudger monitor --help
  Usage: http-nudger monitor [OPTIONS] URL

  Run monitoring for the specified URL

  Options:
    --period INTEGER                How often to perform an HTTP request to the
                                    given URL (seconds)  [default: 30]
    --timeout INTEGER               Timeout for an HTTP request (seconds)
                                    [default: 5]
    --regexp TEXT                   Regular expression to search for in the
                                    response body
    --kafka-bootstrap-servers TEXT  Kafka bootstrap servers list  [required]
    --kafka-topic TEXT              Kafka topic  [required]
    --kafka-key PATH                Kafka access key file  [default: ./kafka-
                                    key.pem]
    --kafka-cert PATH               Kafka access certificate file  [default:
                                    ./kafka-cert.pem]
    --kafka-ca PATH                 Kafka root CA cert file  [default:
                                    ./ca.pem;required]
    --help                          Show this message and exit.

The persister process::

  $ http-nudger persister --help

  Usage: http-nudger persister [OPTIONS]

  Run process for storing URL checks to the given database tables

  Options:
    --kafka-bootstrap-servers TEXT  Kafka bootstrap servers list  [required]
    --kafka-topic TEXT              Kafka topic  [required]
    --kafka-key PATH                Kafka access key file  [default: ./kafka-
                                    key.pem]
    --kafka-cert PATH               Kafka access certificate file  [default:
                                    ./kafka-cert.pem]
    --kafka-ca PATH                 Kafka root CA cert file  [default:
                                    ./ca.pem;required]
    --kafka-consumer-group TEXT     Kafka consumer group to join  [default:
                                    http-nudger-url-statuses]
    --postgres-host TEXT            Postgres hostname  [default: localhost]
    --postgres-port INTEGER         Postgres port  [default: 5432]
    --postgres-db TEXT              Postgres database  [default: http-nudger]
    --postgres-user TEXT            Postgres username  [required]
    --postgres-password TEXT        Postgres password  [required]
    --help                          Show this message and exit.

Running
-------
The provided infrastructure deployment scripts can be used to start
the ``http-nudger`` monitoring.

Create Kafka and PostgreSQL instances using `Aiven service
<https://aiven.io/>`_. Terraform tool is required::

  $ export TF_VAR_aiven_api_token=<YOUR AIVEN API TOKEN>
  $ export TF_VAR_aiven_project_name=<YOUR AIVEN PROJECT NAME>
  $ make infra

After infrastructure creation the next files with the required
connection information will be created: ``kafka.env``,
``postgres.env``, ``ca.pem``, ``kafka-key.pem``, ``kafka-cert.pem``.

To run ``monitor`` manually::
  
  $ export $(cat kafka.env)
  $ http-nudger monitor --regexp '[Mm]ath' https://c.xkcd.com/random/comic/

To run ``persister`` manually::
  
  $ export $(cat kafka.env postgres.env)
  $ http-nudger persister

To deploy ``http-nudger`` in Kubernetes the deployment manifests
provided in ``infra/k8s`` can also be used. To deploy everything with
needed secrets and configuration maps (don't forget to publish the
``http-nudger`` image)::
  
  $ export KUBECONFIG=<PATH TO YOUR KUBECONFIG>
  $ make deploy_k8s