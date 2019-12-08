from piece.base_piece import BasePiece
from piece.utils import generate_diagonal_moves, generate_straight_moves


class Queen(BasePiece):
    type = BasePiece.Type.QUEEN

    def get_possible_moves(self):
        return generate_diagonal_moves(self, self.game.board) + generate_straight_moves(
            self, self.game.board
        )
