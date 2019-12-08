import logging

from piece.base_piece import BasePiece
from piece_move import PieceMove
from player import PlayerColor

logger = logging.getLogger(__name__)


class Pawn(BasePiece):
    type = BasePiece.Type.PAWN

    @property
    def direction(self):
        return 1 if self.color == PlayerColor.WHITE else -1

    def get_possible_moves(self):
        return list(
            filter(
                bool,
                (
                    self.get_one_forward(),
                    self.get_two_forward(),
                    self.get_left_take(),
                    self.get_right_take(),
                    self.get_left_en_passant(),
                    self.get_right_en_passant(),
                ),
            )
        )

    def get_one_forward(self):
        y = self.y + 1 * self.direction
        piece = self.game.find_piece_at(self.x, y)
        if not piece:
            return PieceMove(self, self.x, y)

    def get_two_forward(self):
        if self.has_moved():
            return

        y1 = self.y + 1 * self.direction
        y2 = self.y + 2 * self.direction
        piece1 = self.game.find_piece_at(self.x, y1)
        piece2 = self.game.find_piece_at(self.x, y2)
        if not piece1 and not piece2:
            return PieceMove(self, self.x, y2)

    def get_left_take(self):
        y = self.y + 1 * self.direction
        x = self.x + 1

        piece = self.game.find_piece_at(x, y)
        if piece and self.is_enemy(piece):
            return PieceMove(self, x, y, piece)

    def get_right_take(self):
        y = self.y + 1 * self.direction
        x = self.x - 1

        piece = self.game.find_piece_at(x, y)
        if piece and self.is_enemy(piece):
            return PieceMove(self, x, y, piece)

    def get_left_en_passant(self):
        en_passant_y = 5 if self.color == PlayerColor.WHITE else 4
        if self.y != en_passant_y:
            return

        y = self.y + 1 * self.direction
        x = self.x + 1

        piece = self.game.find_piece_at(x, self.y)
        if (
            piece
            and piece.move_count == 1
            and piece.is_enemy(self)
            and piece.type == BasePiece.Type.PAWN
        ):
            return PieceMove(self, x, y, piece)

    def get_right_en_passant(self):
        en_passant_y = 5 if self.color == PlayerColor.WHITE else 4
        if self.y != en_passant_y:
            return

        y = self.y + 1 * self.direction
        x = self.x - 1

        piece = self.game.find_piece_at(x, self.y)
        if (
            piece
            and piece.move_count == 1
            and piece.is_enemy(self)
            and piece.type == BasePiece.Type.PAWN
        ):
            return PieceMove(self, x, y, piece)
