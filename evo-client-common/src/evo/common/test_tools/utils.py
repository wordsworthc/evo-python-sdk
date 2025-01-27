import os
import unittest
from datetime import datetime, time, timezone
from typing import TypeVar


def utc_datetime(
    year: int, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0
) -> datetime:
    """Create a datetime object in UTC time."""
    return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc)


def utc_time(hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0) -> time:
    """Create a time object in UTC time."""
    return time(hour, minute, second, microsecond, tzinfo=timezone.utc)


_FT = TypeVar("_FT")


def long_test(test: _FT) -> _FT:
    """Decorator to mark a test as long-running.

    This decorator should be used to mark tests that take a long time to run, or that require a lot of resources. The
    decorator will cause the test to be skipped by default, and will be run only if the `CI` environment variable is
    set (as is the case in GitHub workflows).
    """
    return unittest.skipUnless("CI" in os.environ, "Make local testing faster")(test)
