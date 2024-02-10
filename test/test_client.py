from datetime import datetime, timedelta
import time


def test_client(db_client):

    assert db_client.client
    assert db_client.local_tz == "America/Vancouver"
    assert db_client.client.default_bucket == "testing"

    # Write some data to database
    db_client.send(
        [
            (
                "test_measurement",
                {"value": 100},
                datetime.now(),
                {"tag1": "value1", "tag2": "value2"},
            )
        ]
    )
    time.sleep(1)
    # Query the data
    query = f'from(bucket: "testing") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "test_measurement")'
    tables = db_client.client.query_api().query(query)
    assert len(tables) == 1
    table = tables[0]
    assert len(table.records) == 1
    record = table.records[0]
    assert record.get_value() == 100
    assert record.get_field() == "value"
    assert record.get_measurement() == "test_measurement"
    assert record.get_field() == "value"
    assert record.get_start() < datetime.now()
    assert record.get_stop() > datetime.now()
    assert record.get_time() < datetime.now()
    assert record.get_time() > datetime.now() - timedelta(hours=1)
    assert record.get_tag("tag1") == "value1"
    assert record.get_tag("tag2") == "value2"
    assert record.get_field() == "value"
