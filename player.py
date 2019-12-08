from websockets import WebSocketServerProtocol

from actions import ServerAction
from utils import GetValueEnum, get_message


class PlayerState(GetValueEnum):
    CONNECTED = "CONNECTED"
    PLAYING = "PLAYING"


class PlayerColor(GetValueEnum):
    WHITE = "W"
    BLACK = "B"


class Player:
    game: "ChessGame"
    user_id: str
    socket: WebSocketServerProtocol
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

    def set_connected(self):
        self.state = PlayerState.CONNECTED
        self.send_state()

    def set_playing(self):
        self.state = PlayerState.PLAYING
        self.send_state()

    @property
    def can_start(self):
        return self.state.value == PlayerState.CONNECTED

    def send_state(self):
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
