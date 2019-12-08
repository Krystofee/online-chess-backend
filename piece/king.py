from piece.base_piece import BasePiece
from piece.utils import generate_diagonal_moves, generate_straight_moves


class King(BasePiece):
    type = BasePiece.Type.KING

    def get_possible_moves(self):
        return generate_diagonal_moves(
            self, self.game.board, False
        ) + generate_straight_moves(self, self.game.board, False)
