from piece.base_piece import BasePiece
from piece.utils import generate_straight_moves


class Rook(BasePiece):
    type = BasePiece.Type.ROOK

    def get_possible_moves(self):
        return generate_straight_moves(self, self.game.board)
