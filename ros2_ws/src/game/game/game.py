#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from pathlib import Path
from collections import deque
import re
import time

from interfaces import srv


class game(Node):
    def __init__(self):
        super().__init__('game')
        self.computer_vision_client = self.create_client(srv.GetFEN, 'get_fen')
        self.stockfish_client = self.create_client(srv.GetMove, 'get_move')
        self.move_client = self.create_client(srv.Move, 'move')

        self.my_move = True
        self.busy = False
        self.last_engine_move_time = 0.0
        self.human_turn_wait_sec = 3.0

        self.save_path = self._resolve_save_path()
        self.game_id = self._init_game_id()

        while not self.computer_vision_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service get_fen not available, waiting...')
        while not self.stockfish_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service get_move not available, waiting...')
        while not self.move_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service move not available, waiting...')

        self.timer = self.create_timer(0.2, self.main_logic)

    def main_logic(self):
        if self.busy:
            return

        if not self.my_move:
            if time.time() - self.last_engine_move_time >= self.human_turn_wait_sec:
                self.my_move = True
            return

        self.busy = True
        try:
            cv_request = srv.GetFEN.Request()
            future = self.computer_vision_client.call_async(cv_request)
            rclpy.spin_until_future_complete(self, future)
            cv_result = future.result()
            if cv_result is None:
                self.get_logger().error('GetFEN failed: no response')
                return

            fen = cv_result.fen
            self.write_fen(fen)

            stockfish_request = srv.GetMove.Request()
            stockfish_request.fen = fen
            future = self.stockfish_client.call_async(stockfish_request)
            rclpy.spin_until_future_complete(self, future)
            stockfish_result = future.result()
            if stockfish_result is None:
                self.get_logger().error('GetMove failed: no response')
                return

            move_value = stockfish_result.move
            move_request = srv.Move.Request()
            move_request.move = move_value
            future = self.move_client.call_async(move_request)
            rclpy.spin_until_future_complete(self, future)
            if future.result() is None:
                self.get_logger().error('Move service failed: no response')
                return

            self.my_move = False
            self.last_engine_move_time = time.time()
        finally:
            self.busy = False

    def _resolve_save_path(self):
        cwd = Path.cwd().resolve()
        for candidate in (cwd, *cwd.parents):
            if (candidate / 'ros2_ws').exists() and (candidate / 'log').exists():
                log_dir = candidate / 'log'
                log_dir.mkdir(parents=True, exist_ok=True)
                return log_dir / 'moves.txt'

        fallback = cwd / 'log' / 'moves.txt'
        fallback.parent.mkdir(parents=True, exist_ok=True)
        return fallback

    def _init_game_id(self):
        if not self.save_path.exists():
            self.save_path.write_text('', encoding='utf-8')
            return 1

        with open(self.save_path, 'r', encoding='utf-8') as save_file:
            first_line = save_file.readline().strip()

        match = re.search(r'game_id:\s*(\d+)', first_line)
        if match:
            return int(match.group(1)) + 1
        return 1

    def write_fen(self, fen):
        if not self.save_path.exists():
            self.save_path.write_text('', encoding='utf-8')

        timestamp = time.strftime("%d.%m.%Y %H:%M:%S")
        new_line = f"time: {timestamp} | game_id: {self.game_id} | fen: {fen}\n"
        with open(self.save_path, 'r', encoding='utf-8') as save_file:
            lines = deque(save_file.readlines(), maxlen=300)
        lines.appendleft(new_line)
        with open(self.save_path, 'w', encoding='utf-8') as save_file:
            save_file.writelines(lines)


def main(args=None):
    rclpy.init(args=args)
    node = game()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()