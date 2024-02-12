from __future__ import annotations
from application_metrics import ApplicationMetricsBase
from dataclasses import dataclass
import pytest

INFLUXDB_TESTING_CONFIG_FILEPATH = "test/influxdb_testing_config.toml"
LOCAL_TZ = "UTC"


@dataclass
class TestMetrics(ApplicationMetricsBase):
    name: str = "test_metrics"
    class_: str = "test_agent"
    instance_id: int = 1000
    hostname: str = "test-hostname"
    important_metric: int = 0
    another_metric: int = 0
    extremely_important_metric: int = 0
    not_so_important_metric: int = 0

@pytest.fixture
def test_metrics():
    from application_metrics import ApplicationMetricsBase

    test_metrics = TestMetrics()
    test_metrics.client = database_client()

    return test_metrics



@pytest.fixture
def database_client():
    from fast_database_clients import FastInfluxDBClient

    client = FastInfluxDBClient.from_config_file(config_file=INFLUXDB_TESTING_CONFIG_FILEPATH)


    return client
