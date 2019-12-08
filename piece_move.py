import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import ChessGame
    from piece.base_piece import BasePiece

logger = logging.getLogger(__name__)


class PieceMove:
    piece: "BasePiece"
    takes: "BasePiece" or None = None
    nested: "PieceMove" or None = None
    x: int
    y: int

    def __init__(
        self,
        piece: "BasePiece",
        x: int,
        y: int,
        takes: "BasePiece" = None,
        nested: "PieceMove" = None,
    ):
        self.piece = piece
        self.takes = takes
        self.nested = nested
        self.x = x
        self.y = y

    def __eq__(self, other: "PieceMove"):
        return self.to_tuple() == other.to_tuple()

    def to_tuple(self):
        return self.piece, self.takes, self.x, self.y

    @staticmethod
    def from_dict(data: dict, game: "ChessGame") -> "PieceMove" or None:
        piece = game.find_piece_id(data["piece"])

        if not piece:
            raise Exception("Invalid piece")  # TODO raise invalid move

        takes = None
        if "takes" in data:
            takes = game.find_piece_id(data["takes"])

            if not takes:
                raise Exception("Invalid piece")  # TODO raise invalid move

        nested = None
        if "nested" in data and data["nested"]:
            nested = PieceMove.from_dict(data["nested"], game)

        logger.info(f'parsed move {piece} {takes} {data["x"]} {data["y"]} {nested}')

        return PieceMove(piece, data["x"], data["y"], takes, nested)

    def perform(self, game: "ChessGame") -> bool:
        # TODO: implement validation
        if self.takes:
            game.board = list(
                filter(
                    lambda piece: not (
                        piece.x == self.takes.x and piece.y == self.takes.y
                    ),
                    game.board,
                )
            )

        self.piece.x = self.x
        self.piece.y = self.y

        if self.nested:
            self.nested.piece.x = self.nested.x
            self.nested.piece.y = self.nested.y

        return True
