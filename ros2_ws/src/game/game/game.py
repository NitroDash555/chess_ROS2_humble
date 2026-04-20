#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from pathlib import Path
from collections import deque
import time

from interfaces import srv

class game(Node):
    def __init__(self):
        super().__init__('game')
        self.computer_vision_client = self.create_client(srv.GetFEN, 'get_fen')
        self.stockfish_client = self.create_client(srv.GetMove, 'get_move')
        self.move_client = self.create_client(srv.Move, 'move')

        self.my_move = True

        self.save_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent.parent / "log" / "moves.txt"
        
        with open(self.save_path, 'r', encoding='utf-8') as save_file:
            line = save_file.readline()
            prev_id = int(line.split()[5])
            self.game_id = prev_id + 1

        while not self.computer_vision_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service get_fen not available, waiting...')
        while not self.stockfish_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service get_move not available, waiting...')
        while not self.move_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service move not available, waiting...')

        self.timer = self.create_timer(0.1, self.main_logic)


    def main_logic(self):
        if self.my_move:
            cv_request = srv.GetFEN.Request()
            self.get_logger().info('создаем future')
            future = self.computer_vision_client.call_async(cv_request)
            self.get_logger().info('крутим')
            rclpy.spin_until_future_complete(self, future)
            self.get_logger().info('принимаем результат')
            fen = future.fen()
            self.get_logger().info('записываем результат')
            self.write_fen(fen)
            self.get_logger().info('результат записан')

            stockfish_request = srv.GetMove.Request()
            stockfish_request.fen = fen
            future = self.stockfish_client.call_async(stockfish_request)
            rclpy.spin_until_future_complete(self, future)

            move = future.move()

            move_request = srv.Move.Request(move)
            future = self.move_client.call_async(move_request)
            rclpy.spin_until_future_complete(self, future)

            self.my_move = False
        else:
            input()
            self.my_move = True

    def write_fen(self, fen):
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