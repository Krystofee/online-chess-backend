from uuid import uuid4

from player import PlayerColor
from utils import GetValueEnum


class PieceType(GetValueEnum):
    PAWN = 'P'
    ROOK = 'R'
    KNIGHT = 'N'
    BISHOP = 'B'
    QUEEN = 'Q'
    KING = 'K'


class Piece:
    id: str
    type: PieceType
    color: PlayerColor
    x: int
    y: int

    def __init__(self, game, type, color, x, y):
        self.id = str(uuid4())
        self.game = game
        self.type = type
        self.color = color
        self.x = x
        self.y = y

    def to_serializable_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'color': self.color.value,
            'x': self.x,
            'y': self.y,
        }