from typing import Union

from websockets import WebSocketServerProtocol

from actions import ServerAction
from utils import GetValueEnum, get_message


class PlayerState(GetValueEnum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    PLAYING = "PLAYING"


class PlayerColor(GetValueEnum):
    WHITE = "W"
    BLACK = "B"


class Player:
    game: "ChessGame"
    user_id: str
    socket: Union[WebSocketServerProtocol, None]
    state: PlayerState
    color: PlayerColor

    def __init__(
        self, game, user_id, color: PlayerColor, socket: WebSocketServerProtocol
    ):
        self.game = game
        self.user_id = user_id
        self.socket = socket
        self.color = color
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
        print("Setting player as connected")
        self.state = PlayerState.CONNECTED
        self.send_state()

    def set_disconnected(self):
        self.state = PlayerState.DISCONNECTED
        self.socket = None
        print("Disconnected player", self.id, self.color)

    def set_playing(self):
        self.state = PlayerState.PLAYING
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
                        },
                    ),
                )
            )
