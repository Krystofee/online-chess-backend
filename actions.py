import json
import logging

from piece_move import PieceMove
from utils import GetValueEnum

logger = logging.getLogger(__name__)


class ClientAction(GetValueEnum):
    CONNECT = "CONNECT"
    MOVE = "MOVE"
    IDENTIFY = "IDENTIFY"


class ServerAction(GetValueEnum):
    PLAYER_STATE = "PLAYER_STATE"
    GAME_STATE = "GAME_STATE"


class ActionReceiver:
    def __init__(self, websocket, game):
        self.websocket = websocket
        self.game = game

    async def listen(self):
        async for message in self.websocket:
            logger.info(f"receive {self.game} {self.websocket} {message}")
            parsed_message = json.loads(message)
            self.receive(parsed_message)

    def receive(self, action_tuple):
        if len(action_tuple) != 2:
            logger.error("Invalid message, skipping")
            return

        action = ClientAction.get_value(action_tuple[0])
        data = action_tuple[1]

        if action == ClientAction.IDENTIFY:
            user_id = data.get("id")
            self.game.identify(self.websocket, user_id)

        if action == ClientAction.CONNECT:
            user_id = data.get("id")
            self.game.connect(self.websocket, user_id)

        if action == ClientAction.MOVE:
            move = PieceMove.from_dict(data, self.game)
            self.game.move(self.websocket, move)
