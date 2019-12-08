from typing import Iterable

from coord import Coord
from piece.base_piece import BasePiece
from piece_move import PieceMove


def is_piece_at(piece: BasePiece, x: int, y: int):
    if piece.x == x and piece.y == y:
        return piece


def generate_offset_moves(
    piece: BasePiece,
    all_pieces: Iterable[BasePiece],
    offsets: Iterable[Coord],
    repeat: bool = False,
):
    moves = []

    for offset in offsets:
        x = piece.x
        y = piece.y

        encountered_piece = None

        while 1 <= x <= 8 and 1 <= y <= 8 and not encountered_piece:
            x += offset.x
            y += offset.y

            for maybe_encountered in all_pieces:
                if is_piece_at(maybe_encountered, x, y):
                    encountered_piece = maybe_encountered

            if not encountered_piece:
                moves.append(PieceMove(piece, x, y))

            if not repeat:
                break

        if encountered_piece and encountered_piece.color != piece.color:
            moves.append(PieceMove(piece, x, y, encountered_piece))

    return moves


def generate_diagonal_moves(
    piece: BasePiece, all_pieces: Iterable[BasePiece], repeat: bool = True
):
    return generate_offset_moves(
        piece,
        all_pieces,
        (Coord(1, -1), Coord(-1, 1), Coord(1, 1), Coord(-1, -1)),
        repeat,
    )


def generate_straight_moves(
    piece: BasePiece, all_pieces: Iterable[BasePiece], repeat: bool = True
):
    return generate_offset_moves(
        piece,
        all_pieces,
        (Coord(1, 0), Coord(-1, 0), Coord(0, 1), Coord(0, -1)),
        repeat,
    )
