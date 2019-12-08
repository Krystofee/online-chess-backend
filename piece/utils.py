from coord import Coord


def generate_offset_moves(piece, all_pieces, offsets, repeat=False):
    pass


def generate_diagonal_moves(piece, all_pieces, repeat=True):
    return generate_offset_moves(
        piece,
        all_pieces,
        (Coord(1, -1), Coord(-1, 1), Coord(1, 1), Coord(-1, -1)),
        repeat,
    )


def generate_straight_moves(piece, all_pieces, repeat=True):
    return generate_offset_moves(
        piece,
        all_pieces,
        (Coord(1, 0), Coord(-1, 0), Coord(0, 1), Coord(0, -1)),
        repeat,
    )
