class PieceMove:
    piece: "BasePiece"
    takes: "BasePiece" or None = None
    x: int
    y: int

    def __init__(self, piece: "BasePiece", x: int, y: int, takes: "BasePiece" = None):
        self.piece = piece
        self.takes = takes
        self.x = x
        self.y = y
