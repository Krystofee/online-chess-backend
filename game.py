import logging
import random
import time
from typing import Dict, List
from uuid import UUID, uuid4

from websockets import WebSocketServerProtocol

from actions import ServerAction
from game_timer import GameTimer
from piece import Bishop, King, Knight, Pawn, Queen
from piece.base_piece import BasePiece
from piece.rook import Rook
from piece_move import PieceMove
from player import Player, PlayerColor
from utils import GetValueEnum, get_message

logger = logging.getLogger(__name__)


class GameState(GetValueEnum):
    WAITING = "WAITING"
    PLAYING = "PLAYING"
    ENDED = "ENDED"


class ChessGame:
    TIMER_PERIOD = 1

    id: UUID
    state: GameState

    timer: "GameTimer"
    started_at: float = 0
    remaining_white: float = 60
    remaining_black: float = 60

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

        print("trying to identify", user_id, " found ", player)

        if player:
            player.identify(websocket)
            self.send_state()
        elif self.can_player_join():
            self.connect(websocket, user_id)

    def connect(self, websocket: WebSocketServerProtocol, user_id: str):
        if len(self.connect_player_colors) > 0:
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

        self.send_state()

    def disconnect(self, websocket: WebSocketServerProtocol):
        for player_id, player in self.players.items():
            if player.socket == websocket:
                player.set_disconnected()

        self.send_state()

    def can_player_join(self):
        return len(self.connect_player_colors) > 0

    def can_start(self):
        return len(self.players.values()) == 2 and not any(
            [player.can_start for player in self.players.values()]
        )

    def start_game(self):
        self.on_move = PlayerColor.WHITE
        self.state = GameState.PLAYING
        self.started_at = time.time()
        self.timer = GameTimer(self, self.TIMER_PERIOD)

        for player in self.players.values():
            player.set_playing()

    def timer_cycle(self):
        if self.on_move == PlayerColor.WHITE:
            self.remaining_white -= self.TIMER_PERIOD
        else:
            self.remaining_black -= self.TIMER_PERIOD

        self.message_queue.append(
            (
                None,
                get_message(
                    ServerAction.TIMER,
                    {
                        "server_time": time.time(),
                        "remaining_white": self.remaining_white,
                        "remaining_black": self.remaining_black,
                    },
                ),
            )
        )

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
            "board": [x.to_serializable_dict() for x in self.board],
            "on_move": self.on_move.value if self.on_move else None,
            "remaining_white": self.remaining_white,
            "remaining_black": self.remaining_black,
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


def get_game(path, create_new=True) -> ChessGame:
    logger.info(f"getting game for path {path}")

    if create_new and path not in paths:
        game = ChessGame()
        paths[path] = game

    logger.info(f"game {paths[path]}")

    return paths[path]
