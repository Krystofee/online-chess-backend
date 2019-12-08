from piece.base_piece import BasePiece
from piece.utils import generate_diagonal_moves, generate_straight_moves
from piece_move import PieceMove


class King(BasePiece):
    type = BasePiece.Type.KING

    def get_possible_moves(self):
        moves = generate_diagonal_moves(
            self, self.game.board, False
        ) + generate_straight_moves(self, self.game.board, False)

        if not self.has_moved():
            h_rook = self.game.find_piece_at(8, self.y)
            if h_rook and not h_rook.has_moved():
                f_piece = self.game.find_piece_at(6, self.y)
                g_piece = self.game.find_piece_at(7, self.y)

                if not f_piece and not g_piece:
                    moves.append(
                        PieceMove(self, 7, self.y, None, PieceMove(h_rook, 6, self.y))
                    )

            a_rook = self.game.find_piece_at(1, self.y)
            if a_rook and not a_rook.has_moved():
                b_piece = self.game.find_piece_at(2, self.y)
                c_piece = self.game.find_piece_at(3, self.y)
                d_piece = self.game.find_piece_at(4, self.y)

                if not b_piece and not c_piece and not d_piece:
                    moves.append(
                        PieceMove(self, 3, self.y, None, PieceMove(a_rook, 4, self.y))
                    )

        return moves
