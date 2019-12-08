import enum
import json


def get_message(action: "ServerAction", message: dict):
    return json.dumps([action.value, message])


class GetValueEnum(enum.Enum):
    @classmethod
    def get_value(cls, value):
        return cls._value2member_map_.get(value, None)
