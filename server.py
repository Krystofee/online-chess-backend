import asyncio
import json
import logging
import logging.config
from asyncio import sleep

import websockets
import yaml
from websockets import WebSocketServerProtocol

from actions import ActionReceiver
from game import get_game

PORT = 9000
# PORT = os.environ['PORT']


def configure_logging():
    with open('logging_config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)


async def consumer_handler(websocket, path):
    game = get_game(path)
    action_receiver = ActionReceiver(websocket, game)

    async for message in websocket:
        logger.info(f'receive {game} {websocket} {path} {message}')
        parsed_message = json.loads(message)
        action_receiver.receive(parsed_message)


async def producer_handler(websocket: WebSocketServerProtocol, path: str):
    game = get_game(path)

    while True:
        await sleep(0.1)

        for socket, message in game.message_queue:
            logger.info(f'sending message {message}')

            if not socket:
                for player in game.players.values():
                    await player.socket.send(message)
            else:
                await socket.send(message)

        game.message_queue = []


async def handler(websocket, path):
    logger.info(f'connected {websocket} {path}')

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


if __name__ == '__main__':
    configure_logging()
    logger = logging.getLogger(__name__)

    logger.info('Starting server')

    start_server = websockets.serve(handler, "localhost", PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()