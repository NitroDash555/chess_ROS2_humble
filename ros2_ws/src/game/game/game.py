#!/usr/bin/env python3

from collections import deque
from pathlib import Path
import re
import time

import chess
import rclpy
from rclpy.node import Node

from interfaces import srv

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TIMER_PERIOD_SEC = 0.2
HUMAN_TURN_WAIT_SEC = 3.0
MAX_LOG_LINES = 300
GAME_ID_RE = re.compile(r'game_id:\s*(\d+)')


class FenLogger:
    def __init__(self, save_path=None):
        self.save_path = save_path or self._resolve_save_path()
        self.game_id = self._init_game_id()

    def write(self, fen):
        if not self.save_path.exists():
            self.save_path.write_text('', encoding='utf-8')

        timestamp = time.strftime("%d.%m.%Y %H:%M:%S")
        new_line = f"time: {timestamp} | game_id: {self.game_id} | fen: {fen}\n"

        with open(self.save_path, 'r', encoding='utf-8') as f:
            lines = deque(f.readlines(), maxlen=MAX_LOG_LINES)
        lines.appendleft(new_line)

        with open(self.save_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def _init_game_id(self):
        if not self.save_path.exists():
            self.save_path.write_text('', encoding='utf-8')
            return 1

        with open(self.save_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

        match = GAME_ID_RE.search(first_line)
        return int(match.group(1)) + 1 if match else 1

    @staticmethod
    def _resolve_save_path():
        cwd = Path.cwd().resolve()
        for candidate in (cwd, *cwd.parents):
            if (candidate / 'ros2_ws').exists() and (candidate / 'log').exists():
                log_dir = candidate / 'log'
                log_dir.mkdir(parents=True, exist_ok=True)
                return log_dir / 'moves.txt'

        fallback = cwd / 'log' / 'moves.txt'
        fallback.parent.mkdir(parents=True, exist_ok=True)
        return fallback


class GameNode(Node):
    def __init__(self):
        super().__init__('game')
        self.fen = START_FEN
        self.my_move = False
        self.busy = False
        self.last_engine_move_time = 0.0

        self.fen_logger = FenLogger()

        self.cv_client = self.create_client(srv.GetFEN, 'get_fen')
        self.stockfish_client = self.create_client(srv.GetMove, 'get_move')
        self.move_client = self.create_client(srv.Move, 'move')

        self._wait_for_services()

        self.timer = self.create_timer(TIMER_PERIOD_SEC, self._tick)

    def _wait_for_services(self):
        services = [
            ('get_fen', self.cv_client),
            ('get_move', self.stockfish_client),
            ('move', self.move_client),
        ]
        for name, client in services:
            while not client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f'Service {name} not available, waiting...')

    def _tick(self):
        if self.busy:
            return

        if not self._should_move():
            return

        self.busy = True
        self._request_fen()

    def _should_move(self):
        if self.my_move:
            return True
        if time.time() - self.last_engine_move_time >= HUMAN_TURN_WAIT_SEC:
            self.my_move = True
            return True
        return False

    def _request_fen(self):
        request = srv.GetFEN.Request()
        request.prev_fen = self.fen
        self._call_service(
            self.cv_client, request, self._on_fen_received, 'get_fen')

    def _on_fen_received(self, future):
        result = self._get_result(future, 'get_fen')
        if result is None:
            return

        self.fen = result.fen
        self.fen_logger.write(self.fen)
        self.get_logger().info(f'FEN received: {self.fen}')

        request = srv.GetMove.Request()
        request.fen = self.fen
        self._call_service(
            self.stockfish_client, request,
            self._on_stockfish_move_received, 'get_move')

    def _on_stockfish_move_received(self, future):
        result = self._get_result(future, 'get_move')
        if result is None:
            return

        move = result.move
        self.get_logger().info(f'Stockfish suggests: {move}')

        try:
            self.update_fen(move)
        except Exception as e:
            self.get_logger().error(f'Failed to apply move {move}: {e}')
            self._finish_chain()
            return

        request = srv.Move.Request()
        request.move = move
        self._call_service(
            self.move_client, request, self._on_move_executed, 'move')

    def _on_move_executed(self, future):
        result = self._get_result(future, 'move')
        if result is None:
            return

        self.get_logger().info('Move executed successfully')
        self.my_move = False
        self.last_engine_move_time = time.time()
        self._finish_chain()

    def _call_service(self, client, request, callback, service_name):
        try:
            future = client.call_async(request)
            future.add_done_callback(callback)
        except Exception as e:
            self.get_logger().error(f'Failed to call {service_name}: {e}')
            self._finish_chain()

    def _get_result(self, future, service_name):
        try:
            result = future.result()
            if result is None:
                raise RuntimeError(f'{service_name} returned None')
            return result
        except Exception as e:
            self.get_logger().error(f'{service_name} failed: {e}')
            self._finish_chain()
            return None

    def _finish_chain(self):
        self.busy = False

    def update_fen(self, move):
        board = chess.Board(self.fen)
        move = chess.Move.from_uci(move)
        board.push(move)
        self.fen = board.fen()


def main(args=None):
    rclpy.init(args=args)
    node = GameNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
