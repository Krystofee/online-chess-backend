from coord import Coord
from piece.base_piece import BasePiece
from .utils import generate_offset_moves


class Knight(BasePiece):
    type = BasePiece.Type.KNIGHT

    def get_possible_moves(self):
        return generate_offset_moves(
            self,
            self.game.board,
            (
                Coord(1, 2),
                Coord(-1, 2),
                Coord(2, 1),
                Coord(-2, 1),
                Coord(1, -2),
                Coord(-1, -2),
                Coord(2, -1),
                Coord(-2, -1),
            ),
            False,
        )
