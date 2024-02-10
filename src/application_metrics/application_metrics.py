#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-02-02
# Copyright © 2024 Davidson Engineering Ltd.
# ---------------------------------------------------------------------------
"""Application Metrics"""
# ---------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Union
from pathlib import Path


def load_config(filepath: Union[str, Path]) -> dict:
    if not Path(filepath).exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # if extension is .json
    if filepath.suffix == ".json":
        import json

        with open(filepath, "r") as file:
            return json.load(file)

    # if extension is .yaml
    if filepath.suffix == ".yaml":
        import yaml

        with open(filepath, "r") as file:
            return yaml.safe_load(file)
    # if extension is .toml
    if filepath.suffix == ".toml":
        import tomli

        with open(filepath, "r") as file:
            return tomli.load(file)

    # else load as binary
    with open(filepath, "rb") as file:
        return file.read()


@dataclass
class ApplicationMetricsBase:
    name: str = "statistics"
    class_: str = "metrics_agent"
    instance_id: int = 0
    hostname: str = "localhost"

    def client_from_file(self, config: Union[str, Path]):
        from influxdb_client import InfluxDBClient, WritePrecision

        config = load_config(config)
        self.client = InfluxDBClient.from_config_file(
            config, write_precision=WritePrecision.NS
        )
        return self

    def counter(self, field: str, value: int = 1):
        setattr(self, field, getattr(self, field) + value)

    def reset(self):
        for field in self._stats_fields:
            setattr(self, field, 0)

    @property
    def _stats_fields(self):
        return [
            field
            for field in self.__dataclass_fields__
            if field not in ApplicationMetricsBase.__dataclass_fields__
        ]

    @property
    def fields(self):
        return {field: getattr(self, field) for field in self._stats_fields}

    def build_metrics(self):
        return {
            "measurement": self.name,
            "fields": self.fields,
            "time": datetime.now(),
            "tags": {
                "hostname": self.hostname,
                "class": self.class_,
                "instance_id": self.instance_id,
            },
        }
