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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union
from pathlib import Path
import time
from threading import Thread

from buffered import Buffer

SEND_BATCH_SIZE = 5000


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
class Counter:
    value: int = 0

    def counter(self, value: int = 1):
        self.value += value

    def reset(self):
        self.value = 0


@dataclass
class Metrics:
    def request_measurements(self):
        measurements = {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
            if getattr(self, field) > 0
        }
        self.reset([field for field in measurements])
        return measurements


class MetricsManager:

    def __init__(
        self,
        name: str = "statistics",
        class_: str = "metrics_agent",
        instance_id: int = 0,
        hostname: str = "localhost",
        build_interval: int = 0.1,
        send_interval: int = 1,
        autostart: bool = True,
        *args,
        **kwargs,
    ):
        self.name = name
        self.class_ = class_
        self.instance_id = instance_id
        self.hostname = hostname

        self.build_interval = build_interval
        self.send_interval = send_interval

        self.build_thread = Thread(target=self.build_metrics, daemon=True)
        self.send_thread = Thread(target=self.send_metrics, daemon=True)

        self._buffer = Buffer(maxlen=65_536)

        self.metrics: Metrics = Metrics()

        if autostart:
            self.start()

    def start(self):
        self.send_thread.start()
        self.build_thread.start()

    @property
    def client(self):
        if not hasattr(self, "_client"):
            raise AttributeError("Client is not set")
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def counter(self, field: str, value: int = 1):
        setattr(self.counters, field, getattr(self.counters, field) + value)

    def reset(self, fields: list[str] = None):
        fields = fields or self._stats_fields
        for field in fields:
            setattr(self, field, 0)

    @property
    def _stats_fields(self):
        return [field for field in self.counters]

    def request_measurements(self):
        measurements = {
            field: getattr(self, field)
            for field in self._stats_fields
            if getattr(self, field) > 0
        }
        self.reset([field for field in measurements])
        return measurements

    def build_metrics(self):
        measurements = [metric.request_measurements() for metric in self.metrics]
        if measurements:
            self.buffer.put(
                {
                    "measurement": self.name,
                    "fields": measurements,
                    "time": time.time_ns(),
                    "tags": {
                        "hostname": self.hostname,
                        "class": self.class_,
                        "instance_id": self.instance_id,
                    },
                }
            )
        time.sleep(self.build_interval)

    def send_metrics(self):
        metrics = self._buffer.dump(max=SEND_BATCH_SIZE)
        self.client.write(metrics)
        time.sleep(self.send_interval)

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __del__(self):
        self.client.close()
        self.build_thread.join()
        self.send_thread.join()
