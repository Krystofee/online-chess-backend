import logging
import random
from typing import Dict, List
from uuid import UUID, uuid4

from websockets import WebSocketServerProtocol

from actions import ServerAction
from base_piece import Piece, PieceType
from move import Move
from player import Player, PlayerColor
from utils import GetValueEnum, get_message

logger = logging.getLogger(__name__)

paths = {}


class GameState(GetValueEnum):
    WAITING = 'WAITING'
    PLAYING = 'PLAYING'


class ChessGame:
    id: UUID
    state: GameState

    players: Dict[str, Player]

    board: List[Piece]
    on_move: PlayerColor or None = None

    message_queue: List

    def __init__(self):
        logger.info('init new game')
        self.id = uuid4()
        self.state = GameState.WAITING
        self.players = {}
        self.connect_player_colors = [PlayerColor.WHITE, PlayerColor.BLACK]
        random.shuffle(self.connect_player_colors)
        self.board = [
            Piece(self, PieceType.ROOK, PlayerColor.BLACK, x=1, y=8),
            Piece(self, PieceType.KNIGHT, PlayerColor.BLACK, x=2, y=8),
            Piece(self, PieceType.BISHOP, PlayerColor.BLACK, x=3, y=8),
            Piece(self, PieceType.QUEEN, PlayerColor.BLACK, x=4, y=8),
            Piece(self, PieceType.KING, PlayerColor.BLACK, x=5, y=8),
            Piece(self, PieceType.BISHOP, PlayerColor.BLACK, x=6, y=8),
            Piece(self, PieceType.KNIGHT, PlayerColor.BLACK, x=7, y=8),
            Piece(self, PieceType.ROOK, PlayerColor.BLACK, x=8, y=8),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=1, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=2, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=3, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=4, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=5, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=6, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=7, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=8, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=1, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=2, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=3, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=4, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=5, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=6, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=7, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=8, y=2),
            Piece(self, PieceType.ROOK, PlayerColor.WHITE, x=1, y=1),
            Piece(self, PieceType.KNIGHT, PlayerColor.WHITE, x=2, y=1),
            Piece(self, PieceType.BISHOP, PlayerColor.WHITE, x=3, y=1),
            Piece(self, PieceType.QUEEN, PlayerColor.WHITE, x=4, y=1),
            Piece(self, PieceType.KING, PlayerColor.WHITE, x=5, y=1),
            Piece(self, PieceType.BISHOP, PlayerColor.WHITE, x=6, y=1),
            Piece(self, PieceType.KNIGHT, PlayerColor.WHITE, x=7, y=1),
            Piece(self, PieceType.ROOK, PlayerColor.WHITE, x=8, y=1),
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
            logger.info(f'connect player {websocket} {color}')
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
        return len(self.players.values()) == 2 and not any([player.can_start for player in self.players.values()])

    def start_game(self):
        self.on_move = PlayerColor.WHITE
        self.state = GameState.PLAYING

        for player in self.players.values():
            player.set_playing()

    def move(self, websocket: WebSocketServerProtocol, move: Move):
        if websocket not in [x.socket for x in self.players.values()]:
            return

        # TODO: ...still no validation implemented
        if move.takes:
            self.board = list(filter(
                lambda piece: not (piece.x == move.takes.x and piece.y == move.takes.y),
                self.board
            ))

        for piece in self.board:
            if piece.x == move.move_from.x and piece.y == move.move_from.y:
                piece.x = move.move_to.x
                piece.y = move.move_to.y

        if move.nested:
            nested = move.nested
            for piece in self.board:
                if piece.x == nested.move_from.x and piece.y == nested.move_from.y:
                    piece.x = nested.move_to.x
                    piece.y = nested.move_to.y

        self.switch_on_move()
        self.send_state()

    def switch_on_move(self):
        self.on_move = PlayerColor.WHITE if self.on_move == PlayerColor.BLACK else PlayerColor.BLACK

    def send_state(self, send_to: WebSocketServerProtocol = None):
        self.message_queue.append(
            (
                send_to,
                get_message(
                    ServerAction.GAME_STATE,
                    self.to_serializable_dict()
                )
            )
        )

    def to_serializable_dict(self):
        return {
            'id': str(self.id),
            'state': self.state.value,
            # 'players': [str(x.id) for x in self.players.values()],
            'board': [x.to_serializable_dict() for x in self.board],
            'on_move': self.on_move.value if self.on_move else None,
        }


def get_game(path):
    logger.info(f'getting game for path {path}')

    if path not in paths:
        paths[path] = ChessGame()

    logger.info(f'game {paths[path]}')

    return paths[path]
