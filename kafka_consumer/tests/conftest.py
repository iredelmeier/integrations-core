# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import copy
import os
import time

import pytest
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic
from datadog_test_libs.utils.mock_dns import mock_local
from datadog_checks.dev.subprocess import run_command

from datadog_checks.dev import WaitFor, docker_run
from datadog_checks.kafka_consumer import KafkaCheck

from .common import DOCKER_IMAGE_PATH, HERE, HOST_IP, KAFKA_CONNECT_STR, LEGACY_CLIENT, TOPICS
from .runners import KConsumer, Producer

# Dummy TLS certs
CERTIFICATE_DIR = os.path.join(os.path.dirname(__file__), 'certificate')
cert = os.path.join(CERTIFICATE_DIR, 'cert.cert')
private_key = os.path.join(CERTIFICATE_DIR, 'server.pem')


if LEGACY_CLIENT:
    E2E_METADATA = {
        'custom_hosts': [('kafka1', '127.0.0.1'), ('kafka2', '127.0.0.1')],
        'start_commands': [
            'apt-get update',
            'apt-get install -y build-essential',
        ],
    }
else:
    E2E_METADATA = {
        'custom_hosts': [('broker', '127.0.0.1'), ('broker2', '127.0.0.1')],
        'docker_volumes': [
            f'{HERE}/scripts/start_commands.sh:/tmp/start_commands.sh',
            f'{HERE}/docker/kerberos/kdc/krb5_agent.conf:/etc/krb5.conf',
            f'{HERE}/docker/kerberos/kafka/broker.sasl.jaas.config:/etc/kafka/broker.sasl.jaas.config',
            f'{HERE}/docker/kerberos/kafka/broker2.sasl.jaas.config:/etc/kafka/broker2.sasl.jaas.config',
            f'{HERE}/docker/kerberos/secret:/var/lib/secret',
            f'{HERE}/docker/kerberos/client:/etc/kafka',
            ],
        'start_commands': ['bash /tmp/start_commands.sh'],
    }

INSTANCE = {
    'kafka_connect_str': '127.0.0.1:9092',
    'tags': ['optional:tag1'],
    'consumer_groups': {'my_consumer': {'marvel': [0]}},
    'broker_requests_batch_size': 1,
    'use_legacy_client': LEGACY_CLIENT,
    "sasl_mechanism": "GSSAPI",
    "sasl_kerberos_service_name": "kafka",
    "security_protocol": "SASL_PLAINTEXT",
    # will need keytab value
}


@pytest.fixture(scope='session')
def dd_environment(mock_local_kafka_hosts_dns):
    """
    Start a kafka cluster and wait for it to be up and running.
    """
    with docker_run(
        DOCKER_IMAGE_PATH,
        conditions=[
            WaitFor(setupkeytab),
            # WaitFor(create_topics, attempts=2, wait=2),
            # WaitFor(initialize_topics),
        ],
        env_vars={
            # Advertising the hostname doesn't work on docker:dind so we manually
            # resolve the IP address. This seems to also work outside docker:dind
            # so we got that goin for us.
            'KAFKA_HOST': 'localhost',
            'KRB5_CONFIG': "/etc/krb5.conf",
            'KAFKA_OPTS': "-Djava.security.auth.login.config=/etc/kafka/broker.sasl.jaas.config -Djava.security.krb5.conf=/etc/krb5.conf"

        },
    ):
        yield {
            'instances': [INSTANCE],
            'init_config': {'kafka_timeout': 30},
        }, E2E_METADATA


@pytest.fixture
def check():
    return lambda instance, init_config=None: KafkaCheck('kafka_consumer', init_config or {}, [instance])


@pytest.fixture
def kafka_instance():
    return copy.deepcopy(INSTANCE)


@pytest.fixture
def kafka_instance_tls():
    return {
        'kafka_connect_str': KAFKA_CONNECT_STR,
        'tags': ['optional:tag1'],
        'consumer_groups': {'my_consumer': {'marvel': [0]}},
        'broker_requests_batch_size': 1,
        'use_tls': True,
        'tls_validate_hostname': True,
        'tls_cert': cert,
        'tls_private_key': private_key,
        'tls_ca_cert': CERTIFICATE_DIR,
        'use_legacy_client': LEGACY_CLIENT,
    }

def setupkeytab():
    run_command(
        [
            'docker',
            'exec',
            'broker',
            'bash',
            '-c',
            '/setupkeytab.sh'
        ]
    )

def create_topics():
    client = _create_admin_client()

    for topic in TOPICS:
        client.create_topics([NewTopic(topic, 2, 1)], operation_timeout=1, request_timeout=1)

    return set(client.list_topics(timeout=1).topics.keys()) == set(TOPICS)


def initialize_topics():
    consumer = KConsumer(TOPICS)

    with Producer():
        with consumer:
            time.sleep(5)


@pytest.fixture(scope='session')
def mock_local_kafka_hosts_dns():
    mapping = {'kafka1': ('127.0.0.1', 9092), 'kafka2': ('127.0.0.1', 9093)}
    with mock_local(mapping):
        yield


def _create_admin_client():
    return AdminClient(
        {
            "bootstrap.servers": KAFKA_CONNECT_STR,
            "socket.timeout.ms": 1000,
            "sasl.mechanism": "GSSAPI",
            "sasl.kerberos.service.name": "kafka",
            "sasl.kerberos.keytab": "/var/lib/secret/kafka-client.key",
            "security.protocol": "SASL_PLAINTEXT",
            "sasl.kerberos.principal": "kafka_producer",

        }
    )
