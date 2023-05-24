from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Hey(_message.Message):
    __slots__ = ["hi"]
    HI_FIELD_NUMBER: _ClassVar[int]
    hi: str
    def __init__(self, hi: _Optional[str] = ...) -> None: ...
