class Coord:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_dict(data: dict):
        return Coord(data['x'], data['y'])
