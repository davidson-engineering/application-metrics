from datetime import datetime, timedelta, timezone
import time


def test_client(database_client):

    assert database_client
    assert database_client.local_tz == "America/Vancouver"
    assert database_client.default_bucket == "testing"

    # Write some data to database
    database_client.write(
        [
            dict(
                measurement="test_measurement",
                fields={"value": 100},
                time=datetime.now(),
                tags={"tag1": "value1", "tag2": "value2"},
            )
        ]
    )
    time.sleep(1)
    # Query the data
    query = f'from(bucket: "testing") |> range(start: -5s) |> filter(fn: (r) => r._measurement == "test_measurement")'
    tables = database_client.query(query)
    assert len(tables) == 1
    table = tables[0]
    assert len(table.records) == 1
    record = table.records[0]
    assert record.get_value() == 100
    assert record.get_field() == "value"
    assert record.get_measurement() == "test_measurement"
    assert record.get_field() == "value"
    assert record.get_start() < datetime.now(timezone.utc)
    assert record.get_stop() > datetime.now(timezone.utc)
    assert record.get_time() < datetime.now(timezone.utc)
    assert record.get_time() > datetime.now(timezone.utc) - timedelta(hours=1)
    assert record.get_field() == "value"
