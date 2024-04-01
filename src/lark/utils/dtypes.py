from enum import Enum


class MessageType(Enum):
    TEXT = "text"
    INTERACTIVE = "interactive"


class ReceiveIdType(Enum):
    OPEN_ID = "open_id"
    USER_ID = "user_id"
