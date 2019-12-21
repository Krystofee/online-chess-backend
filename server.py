import logging.config

import yaml

if __name__ == "__main__":
    with open("logging_config.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

import os
import asyncio
import json

from asyncio import sleep

import websockets
from websockets import WebSocketServerProtocol

from actions import ActionReceiver
from game import get_game

# PORT = 9000
PORT = 3000


async def consumer_handler(websocket, path):
    game = get_game(path)
    action_receiver = ActionReceiver(websocket, game)

    async for message in websocket:
        logger.info(f"receive {game} {websocket} {path} {message}")
        parsed_message = json.loads(message)
        action_receiver.receive(parsed_message)


async def producer_handler(websocket: WebSocketServerProtocol, path: str):
    game = get_game(path)

    while True:
        await sleep(0.1)

        for socket, message in game.message_queue:
            logger.info(f"sending message {message}")

            if not socket:
                for player in game.players.values():
                    if player.socket:
                        await player.socket.send(message)
            else:
                await socket.send(message)

        game.message_queue = []


async def handler(websocket, path):
    logger.info(f"connected {websocket} {path}")

    consumer_task = asyncio.ensure_future(consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(producer_handler(websocket, path))

    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED
    )
    for task in pending:
        game = get_game(path, False)
        if game is not None:
            game.disconnect(websocket)
        task.cancel()

    return None


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logger.info("Starting server")

    start_server = websockets.serve(handler, "localhost", PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
