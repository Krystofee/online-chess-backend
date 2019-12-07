import asyncio
import enum
import os
import random
from asyncio import sleep

import json
import websockets
from typing import Dict, List
from uuid import UUID, uuid4
from websockets import WebSocketServerProtocol

PORT = os.environ['PORT']


class GetValueEnum(enum.Enum):

    @classmethod
    def get_value(cls, value):
        return cls._value2member_map_.get(value, None)


class ClientAction(GetValueEnum):
    CONNECT = 'CONNECT'
    MOVE = 'MOVE'
    IDENTIFY = 'IDENTIFY'


class ServerAction(enum.Enum):
    PLAYER_STATE = 'PLAYER_STATE'
    GAME_STATE = 'GAME_STATE'


def get_message(action: ServerAction, message: dict):
    return json.dumps([action.value, message])


class PlayerState(enum.Enum):
    CONNECTED = 'CONNECTED'
    PLAYING = 'PLAYING'


class PlayerColor(GetValueEnum):
    WHITE = 'W'
    BLACK = 'B'


class Player:
    game: 'ChessGame'
    user_id: str
    socket: WebSocketServerProtocol
    state: PlayerState
    color: PlayerColor

    def __init__(self, game, user_id, color: PlayerColor, socket: WebSocketServerProtocol):
        self.game = game
        self.user_id = user_id
        self.socket = socket
        self.color = color
        self.state = PlayerState.CONNECTED

    @property
    def id(self):
        return self.user_id

    def set_connected(self):
        self.state = PlayerState.CONNECTED
        self.send_state()

    def set_playing(self):
        self.state = PlayerState.PLAYING
        self.send_state()

    @property
    def can_start(self):
        return self.state.value == PlayerState.CONNECTED

    def send_state(self):
        self.game.message_queue.append(
            (
                self.socket,
                get_message(
                    ServerAction.PLAYER_STATE,
                    {
                        'id': str(self.id),
                        'color': self.color.value,
                        'state': self.state.value,
                    }
                )
            )
        )


class Coord:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_dict(data: dict):
        return Coord(data['x'], data['y'])


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


class PieceType(GetValueEnum):
    PAWN = 'P'
    ROOK = 'R'
    KNIGHT = 'N'
    BISHOP = 'B'
    QUEEN = 'Q'
    KING = 'K'


class Piece:
    id: str
    type: PieceType
    color: PlayerColor
    x: int
    y: int

    def __init__(self, game, type, color, x, y):
        self.id = str(uuid4())
        self.game = game
        self.type = type
        self.color = color
        self.x = x
        self.y = y

    def to_serializable_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'color': self.color.value,
            'x': self.x,
            'y': self.y,
        }


class GameState(GetValueEnum):
    WAITING = 'WAITING'
    PLAYING = 'PLAYING'


class ChessGame:
    id: UUID
    state: GameState

    players: Dict[str, Player]

    board: List[Piece]
    on_move: PlayerColor or None = None

    message_queue: List

    def __init__(self):
        print('init new game')
        self.id = uuid4()
        self.state = GameState.WAITING
        self.players = {}
        self.connect_player_colors = [PlayerColor.WHITE, PlayerColor.BLACK]
        random.shuffle(self.connect_player_colors)
        self.board = [
            Piece(self, PieceType.ROOK, PlayerColor.BLACK, x=1, y=8),
            Piece(self, PieceType.KNIGHT, PlayerColor.BLACK, x=2, y=8),
            Piece(self, PieceType.BISHOP, PlayerColor.BLACK, x=3, y=8),
            Piece(self, PieceType.QUEEN, PlayerColor.BLACK, x=4, y=8),
            Piece(self, PieceType.KING, PlayerColor.BLACK, x=5, y=8),
            Piece(self, PieceType.BISHOP, PlayerColor.BLACK, x=6, y=8),
            Piece(self, PieceType.KNIGHT, PlayerColor.BLACK, x=7, y=8),
            Piece(self, PieceType.ROOK, PlayerColor.BLACK, x=8, y=8),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=1, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=2, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=3, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=4, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=5, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=6, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=7, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.BLACK, x=8, y=7),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=1, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=2, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=3, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=4, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=5, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=6, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=7, y=2),
            Piece(self, PieceType.PAWN, PlayerColor.WHITE, x=8, y=2),
            Piece(self, PieceType.ROOK, PlayerColor.WHITE, x=1, y=1),
            Piece(self, PieceType.KNIGHT, PlayerColor.WHITE, x=2, y=1),
            Piece(self, PieceType.BISHOP, PlayerColor.WHITE, x=3, y=1),
            Piece(self, PieceType.QUEEN, PlayerColor.WHITE, x=4, y=1),
            Piece(self, PieceType.KING, PlayerColor.WHITE, x=5, y=1),
            Piece(self, PieceType.BISHOP, PlayerColor.WHITE, x=6, y=1),
            Piece(self, PieceType.KNIGHT, PlayerColor.WHITE, x=7, y=1),
            Piece(self, PieceType.ROOK, PlayerColor.WHITE, x=8, y=1),
        ]
        self.message_queue = []

    def identify(self, websocket: WebSocketServerProtocol, user_id: str):
        player = self.players.get(user_id)

        if player:
            player.socket = websocket
            player.send_state()
            self.send_state()

    def connect(self, websocket: WebSocketServerProtocol, user_id: str):
        if self.connect_player_colors:
            color = self.connect_player_colors.pop()
            print('connect player', websocket, color)
            player = Player(self, user_id, color, websocket)
            self.players[user_id] = player

            if self.can_start():
                self.start_game()
            else:
                player.set_connected()
        elif user_id in self.players:
            player = self.players[user_id]
            player.send_state()

        self.send_state(websocket)

    def can_start(self):
        return len(self.players.values()) == 2 and not any([player.can_start for player in self.players.values()])

    def start_game(self):
        self.on_move = PlayerColor.WHITE
        self.state = GameState.PLAYING

        for player in self.players.values():
            player.set_playing()

    def move(self, websocket: WebSocketServerProtocol, move: Move):
        if websocket not in [x.socket for x in self.players.values()]:
            return

        # TODO: ...still no validation implemented
        if move.takes:
            self.board = list(filter(
                lambda piece: not (piece.x == move.takes.x and piece.y == move.takes.y),
                self.board
            ))

        for piece in self.board:
            if piece.x == move.move_from.x and piece.y == move.move_from.y:
                piece.x = move.move_to.x
                piece.y = move.move_to.y

        if move.nested:
            nested = move.nested
            for piece in self.board:
                if piece.x == nested.move_from.x and piece.y == nested.move_from.y:
                    piece.x = nested.move_to.x
                    piece.y = nested.move_to.y

        self.switch_on_move()
        self.send_state()

    def switch_on_move(self):
        self.on_move = PlayerColor.WHITE if self.on_move == PlayerColor.BLACK else PlayerColor.BLACK

    def send_state(self, send_to: WebSocketServerProtocol = None):
        self.message_queue.append(
            (
                send_to,
                get_message(
                    ServerAction.GAME_STATE,
                    self.to_serializable_dict()
                )
            )
        )

    def to_serializable_dict(self):
        return {
            'id': str(self.id),
            'state': self.state.value,
            # 'players': [str(x.id) for x in self.players.values()],
            'board': [x.to_serializable_dict() for x in self.board],
            'on_move': self.on_move.value if self.on_move else None,
        }


paths = {}


def get_game(path):
    print('getting game for', path)

    if path not in paths:
        paths[path] = ChessGame()

    print('game: ', paths[path])

    return paths[path]


async def consumer_handler(websocket, path):
    game = get_game(path)

    async for message in websocket:
        print('...receive', game, websocket, path, message)

        parsed_message = json.loads(message)

        if len(parsed_message) != 2:
            print('Invalid message')
            return

        action_value = parsed_message[0]
        action = ClientAction.get_value(action_value)
        data = parsed_message[1]

        if action == ClientAction.IDENTIFY:
            user_id = data.get('id')
            game.identify(websocket, user_id)

        if action == ClientAction.CONNECT:
            user_id = data.get('id')
            game.connect(websocket, user_id)

        if action == ClientAction.MOVE:
            move = Move.from_dict(data)
            game.move(websocket, move)


async def producer_handler(websocket: WebSocketServerProtocol, path: str):
    game = get_game(path)

    while True:
        await sleep(0.1)

        for socket, message in game.message_queue:
            print('...sending message', message)

            if not socket:
                for player in game.players.values():
                    await player.socket.send(message)
            else:
                await socket.send(message)

        game.message_queue = []


async def handler(websocket, path):
    print('...connected', websocket, path)

    consumer_task = asyncio.ensure_future(
        consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(
        producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()

    return None


print('Starting server...')
start_server = websockets.serve(handler, "0.0.0.0", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()