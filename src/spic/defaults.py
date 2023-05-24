from rich.console import Console

from .enums import LogLevel

DefaultConsole = Console(log_time=True, log_path=False)
DEFAULT_LOG_LEVEL = LogLevel.follow
