from typing import Union

from websockets import WebSocketServerProtocol

from actions import ServerAction
from utils import GetValueEnum, get_message


class PlayerState(GetValueEnum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"


class PlayerColor(GetValueEnum):
    WHITE = "W"
    BLACK = "B"


class Player:
    game: "ChessGame"
    user_id: str
    socket: Union[WebSocketServerProtocol, None]
    state: PlayerState
    color: PlayerColor
    remaining_time: float = 360  # TODO set from actual game length

    def __init__(
        self,
        game,
        user_id,
        color: PlayerColor,
        remaining_time: int,
        socket: WebSocketServerProtocol,
    ):
        self.game = game
        self.user_id = user_id
        self.socket = socket
        self.color = color
        self.remaining_time = remaining_time
        self.state = PlayerState.CONNECTED

    @property
    def id(self):
        return self.user_id

    def identify(self, websocket: WebSocketServerProtocol):
        print("player identified", websocket, self.color)
        self.socket = websocket
        self.state = PlayerState.CONNECTED
        self.send_state()

    def set_connected(self):
        self.state = PlayerState.CONNECTED
        self.send_state()

    def set_disconnected(self):
        self.state = PlayerState.DISCONNECTED
        self.socket = None

    def set_playing(self):
        self.remaining_time = self.game.total_length
        self.send_state()

    @property
    def can_start(self):
        return self.state.value == PlayerState.CONNECTED

    def send_state(self):
        if self.socket:
            self.game.message_queue.append(
                (
                    self.socket,
                    get_message(
                        ServerAction.PLAYER_STATE,
                        {
                            "id": str(self.id),
                            "color": self.color.value,
                            "state": self.state.value,
                            "remaining_time": self.remaining_time,
                        },
                    ),
                )
            )

    def get_public_state_dict(self):
        return {
            "color": self.color.value,
            "remaining_time": self.remaining_time,
            "state": self.state.value,
        }
