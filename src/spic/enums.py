from enum import Enum


class RegisteredContent(Enum):
    TEXT = "text/plain; charset=UTF-8"
    JSON = "application/json"
    MSGPACK = "application/x-msgpack"


class LogLevel(Enum):
    headless = 0
    follow = 1
    trace = 99
