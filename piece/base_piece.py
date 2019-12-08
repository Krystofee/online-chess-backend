from uuid import uuid4

from typing import TYPE_CHECKING

from player import PlayerColor
from utils import GetValueEnum

if TYPE_CHECKING:
    from game import ChessGame


class BasePiece:
    class Type(GetValueEnum):
        PAWN = "P"
        ROOK = "R"
        KNIGHT = "N"
        BISHOP = "B"
        QUEEN = "Q"
        KING = "K"

    id: str
    type: Type = None  # set in subclasses
    color: PlayerColor
    x: int
    y: int
    move_count: int = 0

    def __init__(self, game: "ChessGame", color, x, y):
        self.id = str(uuid4())
        self.game = game
        self.color = color
        self.x = x
        self.y = y

    def __eq__(self, other: "BasePiece" or None):
        return other and self.id == other.id

    def __repr__(self):
        return f"{self.color} {self.type} at [{self.x},{self.y}]"

    def to_serializable_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "color": self.color.value,
            "move_count": self.move_count,
            "x": self.x,
            "y": self.y,
        }

    def move(self, x, y):
        self.move_count += 1
        self.x = x
        self.y = y

    def get_possible_moves(self):
        raise NotImplementedError

    def is_enemy(self, piece: "BasePiece"):
        return self.color != piece.color

    def has_moved(self):
        return self.move_count > 0
