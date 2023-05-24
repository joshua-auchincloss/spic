from enum import Enum, auto


class RegisteredContent(Enum):
    TEXT = "text/plain; charset=UTF-8"
    JSON = "application/json"
    MSGPACK = "application/x-msgpack"


class LogLevel(Enum):
    headless = 0
    follow = 1
    trace = 99


class FormatMessageOps(Enum):
    to_dict = auto()
    to_json = auto()
