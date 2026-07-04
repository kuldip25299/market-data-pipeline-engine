"""
logging_config.py
==================

Centralized logging setup.

WHY THIS FILE EXISTS
---------------------
A beginner mistake is sprinkling ``print()`` statements everywhere.
This works for a 50-line script, but breaks down immediately in a
production system for three reasons:

1. You cannot turn print statements off selectively per module.
2. You cannot ship print output to a log aggregator (e.g. Datadog,
   ELK, Splunk) that an on-call engineer uses at 3 AM.
3. print() has no severity level -- you can't distinguish a routine
   status update from a critical failure.

We configure ``logging`` once, here, and every other module simply
calls ``logging.getLogger(__name__)``. This is the standard pattern
used in production Python services.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging handlers and format.

    Args:
        level: Minimum severity to emit. Use ``logging.DEBUG`` while
            developing, ``logging.INFO`` in normal operation, and
            ``logging.WARNING`` in noisy stress tests.
    """
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-28s | %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers if configure_logging() is called twice
    # (e.g. once by a script and once by a test fixture).
    root.handlers.clear()
    root.addHandler(handler)
