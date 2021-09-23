http-nudger
===========
``http-nudger`` is a distributed website availability monitoring
tool. The tool consists of two main components - ``monitor`` and
``persister``. The ``monitor`` periodically checks the availability of
the given website over HTTP and sends the collected metrics to the
given Kafka topic. The ``persister`` consumes the metrics from the
given Kafka topic and stores them into the ``url_statuses`` table of
the given PostgresSQL database.

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

Infrastructure
--------------
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

Testing
-------
Tox tool is used for running tests. Install it and other development tools with::
  
  $ pip install -r dev-requirements.txt

To run unit tests run::
  
  $ make test

To run end-to-end tests run (it will trigger infrastructure creation)::
  
  $ export TF_VAR_aiven_api_token=<YOUR AIVEN API TOKEN>
  $ export TF_VAR_aiven_project_name=<YOUR AIVEN PROJECT NAME>
  $ make e2e

Running
-------
To run ``monitor`` manually::
  
  $ export $(cat kafka.env)
  $ env http-nudger monitor --regexp '[Mm]ath' https://c.xkcd.com/random/comic/

To run ``persister`` manually::
  
  $ export $(cat kafka.env postgres.env)
  $ http-nudger persister

To deploy ``http-nudger`` in Kubernetes the deployment manifests
provided in ``infra/k8s`` can also be used. To deploy everything with
needed secrets and configuration maps (don't forget to publish the
``http-nudger`` image)::
  
  $ export KUBECONFIG=<PATH TO YOUR KUBECONFIG>
  $ make deploy_k8s

To Do
-----
- More flexible monitor configuration with ability to run many checks in one monitor process.
- Each monitoring process should also set the ID and some information
  on the availability zone it is running in.
- Maintain a DB table with the latest availability statuse per each
  configured URL calculated using the checks gathered in different
  AZs.
- Add a background web-server to each process to make it possible to
  collect readiness, healthness statuses and metrics when deployed to
  a Kubernetes environment.
