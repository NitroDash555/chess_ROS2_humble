#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from pathlib import Path
from collections import deque
import re
import time
import threading

from interfaces import srv

class GameNode(Node):
    def __init__(self):
        super().__init__('game')
        self.cv_client = self.create_client(srv.GetFEN, 'get_fen')
        self.stockfish_client = self.create_client(srv.GetMove, 'get_move')
        self.move_client = self.create_client(srv.Move, 'move')

        self.my_move = True
        self.busy = False
        self.last_engine_move_time = 0.0
        self.human_turn_wait_sec = 3.0

        self.save_path = self._resolve_save_path()
        self.game_id = self._init_game_id()

        # Ждём доступности сервисов (можно вынести в фон, но для простоты оставим синхронно)
        for name, client in [('get_fen', self.cv_client), 
                             ('get_move', self.stockfish_client), 
                             ('move', self.move_client)]:
            while not client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f'Service {name} not available, waiting...')

        # Таймер теперь вызывает синхронную функцию-диспетчер
        self.timer = self.create_timer(0.2, self._tick)

    def _tick(self):
        if self.busy:
            return

        if not self.my_move:
            if time.time() - self.last_engine_move_time >= self.human_turn_wait_sec:
                self.my_move = True
            return

        # Запускаем цепочку асинхронных вызовов
        self.busy = True
        try:
            future = self.cv_client.call_async(srv.GetFEN.Request())
            future.add_done_callback(self._on_fen_received)
        except Exception as e:
            self.get_logger().error(f'Failed to call GetFEN: {e}')
            self.busy = False

    def _on_fen_received(self, future):
        try:
            result = future.result()
            if result is None:
                raise RuntimeError("GetFEN returned None")
            
            fen = result.fen
            self.write_fen(fen)
            self.get_logger().info(f'FEN received: {fen}')

            # Шаг 2: Запрос хода у Stockfish
            req = srv.GetMove.Request()
            req.fen = fen
            future = self.stockfish_client.call_async(req)
            future.add_done_callback(self._on_stockfish_move_received)
        except Exception as e:
            self.get_logger().error(f'GetFEN failed: {e}')
            self.busy = False

    def _on_stockfish_move_received(self, future):
        try:
            result = future.result()
            if result is None:
                raise RuntimeError("GetMove returned None")
            
            move_value = result.move
            self.get_logger().info(f'Stockfish suggests: {move_value}')

            # Шаг 3: Выполнение хода
            req = srv.Move.Request()
            req.move = move_value
            future = self.move_client.call_async(req)
            future.add_done_callback(self._on_move_executed)
        except Exception as e:
            self.get_logger().error(f'GetMove failed: {e}')
            self.busy = False

    def _on_move_executed(self, future):
        try:
            result = future.result()
            if result is None:
                raise RuntimeError("Move service returned None")
            
            self.get_logger().info('Move executed successfully')
            self.my_move = False
            self.last_engine_move_time = time.time()
        except Exception as e:
            self.get_logger().error(f'Move execution failed: {e}')
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

        with open(self.save_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

        match = re.search(r'game_id:\s*(\d+)', first_line)
        return int(match.group(1)) + 1 if match else 1

    def write_fen(self, fen):
        if not self.save_path.exists():
            self.save_path.write_text('', encoding='utf-8')

        timestamp = time.strftime("%d.%m.%Y %H:%M:%S")
        new_line = f"time: {timestamp} | game_id: {self.game_id} | fen: {fen}\n"
        
        with open(self.save_path, 'r', encoding='utf-8') as f:
            lines = deque(f.readlines(), maxlen=300)
        lines.appendleft(new_line)
        
        with open(self.save_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)


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