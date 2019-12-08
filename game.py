import logging
import random
from typing import Dict, List
from uuid import UUID, uuid4

from websockets import WebSocketServerProtocol

from actions import ServerAction
from piece import Knight, Bishop, Queen, King, Pawn
from piece.base_piece import BasePiece
from piece_move import PieceMove
from piece.rook import Rook
from player import Player, PlayerColor
from utils import GetValueEnum, get_message

logger = logging.getLogger(__name__)


class GameState(GetValueEnum):
    WAITING = "WAITING"
    PLAYING = "PLAYING"


class ChessGame:
    id: UUID
    state: GameState

    players: Dict[str, Player]

    board: List[BasePiece]
    on_move: PlayerColor or None = None

    message_queue: List

    def __init__(self):
        logger.info("init new game")
        self.id = uuid4()
        self.state = GameState.WAITING
        self.players = {}
        self.connect_player_colors = [PlayerColor.WHITE, PlayerColor.BLACK]
        random.shuffle(self.connect_player_colors)
        self.board = [
            Rook(self, PlayerColor.BLACK, x=1, y=8),
            Knight(self, PlayerColor.BLACK, x=2, y=8),
            Bishop(self, PlayerColor.BLACK, x=3, y=8),
            Queen(self, PlayerColor.BLACK, x=4, y=8),
            King(self, PlayerColor.BLACK, x=5, y=8),
            Bishop(self, PlayerColor.BLACK, x=6, y=8),
            Knight(self, PlayerColor.BLACK, x=7, y=8),
            Rook(self, PlayerColor.BLACK, x=8, y=8),
            Pawn(self, PlayerColor.BLACK, x=1, y=7),
            Pawn(self, PlayerColor.BLACK, x=2, y=7),
            Pawn(self, PlayerColor.BLACK, x=3, y=7),
            Pawn(self, PlayerColor.BLACK, x=4, y=7),
            Pawn(self, PlayerColor.BLACK, x=5, y=7),
            Pawn(self, PlayerColor.BLACK, x=6, y=7),
            Pawn(self, PlayerColor.BLACK, x=7, y=7),
            Pawn(self, PlayerColor.BLACK, x=8, y=7),
            Pawn(self, PlayerColor.WHITE, x=1, y=2),
            Pawn(self, PlayerColor.WHITE, x=2, y=2),
            Pawn(self, PlayerColor.WHITE, x=3, y=2),
            Pawn(self, PlayerColor.WHITE, x=4, y=2),
            Pawn(self, PlayerColor.WHITE, x=5, y=2),
            Pawn(self, PlayerColor.WHITE, x=6, y=2),
            Pawn(self, PlayerColor.WHITE, x=7, y=2),
            Pawn(self, PlayerColor.WHITE, x=8, y=2),
            Rook(self, PlayerColor.WHITE, x=1, y=1),
            Knight(self, PlayerColor.WHITE, x=2, y=1),
            Bishop(self, PlayerColor.WHITE, x=3, y=1),
            Queen(self, PlayerColor.WHITE, x=4, y=1),
            King(self, PlayerColor.WHITE, x=5, y=1),
            Bishop(self, PlayerColor.WHITE, x=6, y=1),
            Knight(self, PlayerColor.WHITE, x=7, y=1),
            Rook(self, PlayerColor.WHITE, x=8, y=1),
        ]
        self.message_queue = []

    def identify(self, websocket: WebSocketServerProtocol, user_id: str):
        player = self.players.get(user_id)

        if player:
            player.socket = websocket
            player.send_state()
            self.send_state()

    def connect(self, websocket: WebSocketServerProtocol, user_id: str):
        if self.connect_player_colors:
            color = self.connect_player_colors.pop()
            logger.info(f"connect player {websocket} {color}")
            player = Player(self, user_id, color, websocket)
            self.players[user_id] = player

            if self.can_start():
                self.start_game()
            else:
                player.set_connected()
        elif user_id in self.players:
            player = self.players[user_id]
            player.send_state()

        self.send_state(websocket)

    def can_start(self):
        return len(self.players.values()) == 2 and not any(
            [player.can_start for player in self.players.values()]
        )

    def start_game(self):
        self.on_move = PlayerColor.WHITE
        self.state = GameState.PLAYING

        for player in self.players.values():
            player.set_playing()

    def move(self, websocket: WebSocketServerProtocol, move: PieceMove):
        if websocket not in [x.socket for x in self.players.values()]:
            return

        if move.perform(self):
            self.switch_on_move()

        self.send_state()

    def switch_on_move(self):
        self.on_move = (
            PlayerColor.WHITE
            if self.on_move == PlayerColor.BLACK
            else PlayerColor.BLACK
        )

    def send_state(self, send_to: WebSocketServerProtocol = None):
        self.message_queue.append(
            (send_to, get_message(ServerAction.GAME_STATE, self.to_serializable_dict()))
        )

    def to_serializable_dict(self):
        return {
            "id": str(self.id),
            "state": self.state.value,
            # 'players': [str(x.id) for x in self.players.values()],
            "board": [x.to_serializable_dict() for x in self.board],
            "on_move": self.on_move.value if self.on_move else None,
        }

    def find_piece_at(self, x, y) -> BasePiece or None:
        for piece in self.board:
            if piece.x == x and piece.y == y:
                return piece

    def find_piece_id(self, id) -> BasePiece or None:
        for piece in self.board:
            if piece.id == id:
                return piece


paths = {}


def get_game(path):
    logger.info(f"getting game for path {path}")

    if path not in paths:
        paths[path] = ChessGame()

    logger.info(f"game {paths[path]}")

    return paths[path]
