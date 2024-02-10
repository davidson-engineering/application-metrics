#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-01-23
# Copyright © 2024 Davidson Engineering Ltd.
# ---------------------------------------------------------------------------

from typing import Union
from dataclasses import asdict, is_dataclass, dataclass
import logging
from datetime import datetime
import pytz

from influxdb_client import InfluxDBClient, WritePrecision

logger = logging.getLogger(__name__)


def check_attributes(
    metric: dict, keys: tuple = ("measurement", "fields", "time")
) -> bool:
    try:
        assert all(key in metric for key in keys)
    except AssertionError as e:
        raise AttributeError(f"Metric must contain {keys}") from e
    return True


def localize_timestamp(
    timestamp: Union[int, float, datetime], timezone_str: str = "UTC"
) -> datetime:
    """
    Localize a timestamp to a timezone
    :param timestamp: The timestamp to localize
    :param timezone_str: The timezone to localize to
    :return: The localized timestamp
    """

    if isinstance(timestamp, (int, float)):
        dt_utc = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        dt_utc = timestamp
    else:
        raise ValueError("timestamp must be a float, int, or datetime object")
    timezone = pytz.timezone(timezone_str)
    return timezone.localize(dt_utc)


class InfluxDatabaseClient:
    def __init__(
        self,
        config: str,
        local_tz: str = "UTC",
        write_precision: Union[str, WritePrecision] = WritePrecision.NS,
        default_bucket: str = "testing",
    ):
        self.client = InfluxDBClient.from_config_file(
            config, write_precision=write_precision
        )
        self.client.default_bucket = default_bucket
        self.local_tz = local_tz

    def convert(self, metric: Union[tuple, dict, dataclass]) -> dict:

        ensure_keys = ("measurement", "fields", "time", "tags")

        if is_dataclass(metric):
            metric = asdict(metric)

        elif isinstance(metric, tuple):
            try:
                assert len(metric) >= 3
                logger.warning(
                    "Metric has been passed as a tuple. Assuming format (measurement, fields, time, tags). Unexpected behaviour may occur."
                )
                if isinstance(metric[2], dict):
                    fields = metric[2]
                else:
                    fields = dict(value=metric[2])
                if len(metric) == 4:
                    tags = metric[3]
                else:
                    tags = {}
                metric = dict(
                    measurement=metric[0], fields=fields, time=metric[2], tags=tags
                )
            except AssertionError as e:
                msg = f"metric must be a dict containing {ensure_keys} or be a tuple of length 3 in format {ensure_keys}"
                raise ValueError(msg) from e
        elif isinstance(metric, dict):
            pass
        else:
            msg = f"metric must be a dict containing {ensure_keys} or be a tuple of length 3 in format {ensure_keys}"
            raise ValueError(msg)

        if "tags" not in metric:
            metric["tags"] = {}
        assert check_attributes(metric, ensure_keys)
        metric["time"] = localize_timestamp(metric["time"], self.local_tz)
        return metric

    def send(self, metrics: list[Union[tuple, dict, dataclass]]):
        try:
            metrics = [self.convert(metric) for metric in metrics]
        except Exception as e:
            msg = f"Error converting metrics: {e}. Continuing..."
            logger.error(msg)
            return
        self.client.write_metric(metrics)

    def ping(self):
        return self.client.ping()
