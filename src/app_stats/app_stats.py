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
from dataclasses import dataclass, field
import time


@dataclass
class ApplicationMetrics:
    name: str = "statistics"
    class_: str = "metrics_agent"
    instance_id: int = 0
    hostname: str = "localhost"

    def increment(self, field: str, value: int = 1):
        setattr(self, field, getattr(self, field) + value)

    def reset(self):
        for field in self._stats_fields:
            setattr(self, field, 0)

    @property
    def _stats_fields(self):
        return [
            field
            for field in self.__dataclass_fields__
            if field not in ApplicationMetrics.__dataclass_fields__
        ]

    def build_metrics(self):
        fields = {field: getattr(self, field) for field in self._stats_fields}
        self.reset()
        return {
            "measurement": self.name,
            "fields": fields,
            "time": time.time(),
            "tags": {
                "hostname": self.hostname,
                "class": self.class_,
                "instance_id": self.instance_id,
            },
        }


@dataclass
class SessionMetrics(ApplicationMetrics):
    total_stats: ApplicationMetrics = field(default_factory=ApplicationMetrics)
    period_stats: ApplicationMetrics = field(default_factory=ApplicationMetrics)

    def increment(self, field: str, value: int = 1):
        self.period_stats.increment(field, value)
        self.total_stats.increment(field, value)

    def build_metrics(self):
        return self.period_stats.build_metrics()

    def build_metrics_total(self):
        return self.total_stats.build_metrics()

    def reset(self):
        self.period_stats.reset()
        self.total_stats.reset()
