from piece.base_piece import BasePiece
from piece.utils import generate_diagonal_moves


class Bishop(BasePiece):
    type = BasePiece.Type.BISHOP

    def get_possible_moves(self):
        return generate_diagonal_moves(self, self.game.board)
