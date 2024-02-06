from app_stats import ApplicationStats, SessionStatistics
from dataclasses import dataclass


def test_application_stats():
    stats = ApplicationStats()
    assert stats.name == "statistics"
    assert stats.class_ == "metrics_agent"
    assert stats.instance_id == 0
    assert stats.hostname == "localhost"
    assert stats._stats_fields == []


def test_session_statistics():
    stats = SessionStatistics()
    assert stats.total_stats.name == "statistics"
    assert stats.total_stats.class_ == "metrics_agent"
    assert stats.total_stats.instance_id == 0
    assert stats.total_stats.hostname == "localhost"
    assert stats.total_stats._stats_fields == []
    assert stats.period_stats.name == "statistics"
    assert stats.period_stats.class_ == "metrics_agent"
    assert stats.period_stats.instance_id == 0
    assert stats.period_stats.hostname == "localhost"
    assert stats.period_stats._stats_fields == []


def test_custom_type():
    @dataclass
    class CustomStats(ApplicationStats):
        some_field: int = 0

    custom_stats = CustomStats(
        name="custom", class_="custom", instance_id=1, hostname="custom", some_field=0
    )
    assert custom_stats.name == "custom"
    assert custom_stats.class_ == "custom"
    assert custom_stats.instance_id == 1
    assert custom_stats.hostname == "custom"
    assert custom_stats._stats_fields == ["some_field"]
    assert custom_stats.some_field == 0
    custom_stats.increment("some_field")
    assert custom_stats.some_field == 1
    custom_stats.reset()
    assert custom_stats.some_field == 0

    class CustomSessionStats(SessionStatistics):
        def __init__(self):
            super().__init__(
                total_stats=CustomStats(
                    name="custom",
                    class_="custom",
                    instance_id=1,
                    hostname="custom",
                    some_field=0,
                ),
                period_stats=CustomStats(
                    name="custom",
                    class_="custom",
                    instance_id=1,
                    hostname="custom",
                    some_field=0,
                ),
            )

    custom_session_stats = CustomSessionStats()
    assert custom_session_stats.total_stats.name == "custom"
    assert custom_session_stats.total_stats.class_ == "custom"
    assert custom_session_stats.total_stats.instance_id == 1
    assert custom_session_stats.total_stats.hostname == "custom"
    assert custom_session_stats.total_stats._stats_fields == ["some_field"]
    assert custom_session_stats.total_stats.some_field == 0
    custom_session_stats.increment("some_field")
    assert custom_session_stats.total_stats.some_field == 1
    custom_session_stats.reset()
    assert custom_session_stats.total_stats.some_field == 0
    assert custom_session_stats.period_stats.name == "custom"
    assert custom_session_stats.period_stats.class_ == "custom"
    assert custom_session_stats.period_stats.instance_id == 1
    assert custom_session_stats.period_stats.hostname == "custom"
    assert custom_session_stats.period_stats._stats_fields == ["some_field"]
    assert custom_session_stats.period_stats.some_field == 0
    custom_session_stats.increment("some_field")
    assert custom_session_stats.period_stats.some_field == 1
    custom_session_stats.reset()
    assert custom_session_stats.period_stats.some_field == 0
    custom_session_stats.increment("some_field", 10)
    custom_session_stats.build_metrics()
    assert custom_session_stats.period_stats.some_field == 0
    assert custom_session_stats.total_stats.some_field == 10
