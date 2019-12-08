from uuid import uuid4

from player import PlayerColor
from utils import GetValueEnum


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

    def __init__(self, game: "ChessGame", color, x, y):
        self.id = str(uuid4())
        self.game = game
        self.color = color
        self.x = x
        self.y = y

    def to_serializable_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "color": self.color.value,
            "x": self.x,
            "y": self.y,
        }

    def get_possible_moves(self):
        raise NotImplementedError
