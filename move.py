from coord import Coord


class Move:
    move_from: Coord
    move_to: Coord
    takes: Coord or None = None
    nested: 'Move' or None = None

    def __init__(self, move_from, move_to, takes=None, nested=None):
        self.move_from = Coord.from_dict(move_from)
        self.move_to = Coord.from_dict(move_to)

        if takes:
            self.takes = Coord.from_dict(takes)
        if nested:
            self.nested = Move.from_dict(nested)

    @staticmethod
    def from_dict(data: dict):
        return Move(data['from'], data['to'], data.get('takes'), data.get('nested'))