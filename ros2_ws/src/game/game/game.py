#!/usr/bin/env python3

from collections import deque
import functools
import re
import time

import chess
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from action_msgs.msg import GoalStatus

from chess_common import repo_paths
from interfaces.action import GetFEN
from interfaces import srv

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TIMER_PERIOD_SEC = 0.2
HUMAN_TURN_WAIT_SEC = 3.0
FEN_RETRY_DELAY_SEC = 1.0
MAX_LOG_LINES = 300
GAME_ID_RE = re.compile(r'game_id:\s*(\d+)')


class FenLogger:
    def __init__(self, save_path=None):
        self.save_path = save_path or repo_paths.moves_log_path()
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


class GameNode(Node):
    def __init__(self):
        super().__init__('game')
        self.fen = START_FEN
        self.my_move = False
        self.busy = False
        self.last_engine_move_time = 0.0

        self.fen_logger = FenLogger()

        self._fen_retry_timer = None

        self.cv_client = ActionClient(self, GetFEN, 'get_fen')
        self.stockfish_client = self.create_client(srv.GetMove, 'get_move')
        self.move_client = self.create_client(srv.Move, 'move')

        self._wait_for_services()

        self.timer = self.create_timer(TIMER_PERIOD_SEC, self._tick)

    def _wait_for_services(self):
        while not self.cv_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info('Action get_fen not available, waiting...')
        for name, client in [
            ('get_move', self.stockfish_client),
            ('move', self.move_client),
        ]:
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
        goal = GetFEN.Goal()
        goal.prev_fen = self.fen
        try:
            future = self.cv_client.send_goal_async(
                goal, feedback_callback=self._on_fen_feedback)
            future.add_done_callback(self._on_goal_accepted)
        except Exception as e:
            self.get_logger().error(f'Failed to call get_fen: {e}')
            self._schedule_fen_retry()

    def _on_goal_accepted(self, future):
        try:
            goal_handle = future.result()
        except Exception as e:
            self.get_logger().error(f'get_fen goal send failed: {e}')
            self._schedule_fen_retry()
            return
        if not goal_handle.accepted:
            self.get_logger().error('get_fen goal rejected')
            self._schedule_fen_retry()
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_fen_received)

    def _on_fen_feedback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'get_fen progress: {feedback.step}/8 {feedback.message}')

    def _on_fen_received(self, future):
        result = self._get_fen_result(future)
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

        request = srv.Move.Request()
        request.move = move
        request.fen = self.fen
        self._call_service(
            self.move_client, request,
            functools.partial(self._on_move_executed, move=move), 'move')

    def _on_move_executed(self, future, move):
        result = self._get_result(future, 'move')
        if result is None:
            return

        self.get_logger().info('Move executed successfully')
        try:
            self.update_fen(move)
        except Exception as e:
            self.get_logger().error(f'Failed to apply move {move}: {e}')
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

    def _get_fen_result(self, future):
        try:
            goal_handle_result = future.result()
            if goal_handle_result is None:
                raise RuntimeError('get_fen returned None')
            if goal_handle_result.status != GoalStatus.STATUS_SUCCEEDED:
                raise RuntimeError(
                    f'get_fen did not succeed (status {goal_handle_result.status})')
            result = goal_handle_result.result
            if result is None:
                raise RuntimeError('get_fen result is None')
            return result
        except Exception as e:
            self.get_logger().error(f'get_fen failed: {e}')
            self._schedule_fen_retry()
            return None

    def _schedule_fen_retry(self):
        if self._fen_retry_timer is None:
            self.get_logger().warn('get_fen failed, retrying in '
                                   f'{FEN_RETRY_DELAY_SEC}s')
            self._fen_retry_timer = self.create_timer(
                FEN_RETRY_DELAY_SEC, self._retry_fen)

    def _retry_fen(self):
        self._fen_retry_timer.cancel()
        self._fen_retry_timer.destroy()
        self._fen_retry_timer = None
        if self.busy:
            self._request_fen()

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
