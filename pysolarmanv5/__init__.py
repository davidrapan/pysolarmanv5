"""This is a Python module to interact with Solarman (IGEN-Tech) v5 based solar
inverter data loggers"""

from .pysolarmanv5 import PySolarmanV5, V5FrameError, NoSocketAvailableError
from .pysolarmanv5_async import PySolarmanV5Async

name = "pysolarmanv5"  # pylint: disable=invalid-name (C0103)

__all__ = [
    "PySolarmanV5",
    "PySolarmanV5Async",
    "V5FrameError",
    "NoSocketAvailableError",
]
