def test_application_stats(test_metrics):

    assert test_metrics.name == "test_metrics"
    assert test_metrics.class_ == "test_agent"
    assert test_metrics.instance_id == 1000
    assert test_metrics.hostname == "test-hostname"
    assert test_metrics.important_metric == 0
    assert test_metrics.another_metric == 0
    assert test_metrics.extremely_important_metric == 0
    assert test_metrics.not_so_important_metric == 0

    test_metrics.counter("important_metric")
    assert test_metrics.important_metric == 1
    test_metrics.counter("important_metric", 10)
    assert test_metrics.important_metric == 11
    test_metrics.counter("another_metric", 10)
    assert test_metrics.another_metric == 10
    test_metrics.counter("extremely_important_metric", 10)


def test_application_stats_reset(test_metrics):

    test_metrics.counter("important_metric")
    test_metrics.counter("another_metric", 10)
    test_metrics.counter("extremely_important_metric", 10)
    test_metrics.counter("not_so_important_metric", 10)

    test_metrics.reset()

    assert test_metrics.important_metric == 0
    assert test_metrics.another_metric == 0
    assert test_metrics.extremely_important_metric == 0
    assert test_metrics.not_so_important_metric == 0


def test_application_stats_fields(test_metrics):

    assert test_metrics.fields == {
        "important_metric": 0,
        "another_metric": 0,
        "extremely_important_metric": 0,
        "not_so_important_metric": 0,
    }
