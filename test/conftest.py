from application_metrics import ApplicationMetricsBase
from dataclasses import dataclass
import pytest

INFLUXDB_TESTING_CONFIG_FILEPATH = "test/influxdb_testing_config.toml"
LOCAL_TZ = "America/Vancouver"


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

    return TestMetrics()


@pytest.fixture
def db_client():
    from application_metrics.client import InfluxDatabaseClient

    client = InfluxDatabaseClient(
        config=INFLUXDB_TESTING_CONFIG_FILEPATH, local_tz=LOCAL_TZ
    )

    return client
