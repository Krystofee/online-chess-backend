import threading
import time

import game


class GameTimer:
    def __init__(self, game: "game.ChessGame", interval):
        self.game = game
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.start()

    def run(self):
        while self.game.state == game.GameState.PLAYING:
            time.sleep(self.interval)
            self.game.timer_cycle()
