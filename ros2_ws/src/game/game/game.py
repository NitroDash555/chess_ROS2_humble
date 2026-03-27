#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from interfaces import srv

class game(Node):
    def __init__(self):
        super().__init__('game')
        self.computer_vision_client = self.create_client(srv.GetFEN, 'get_fen')
        self.stockfish_client = self.create_client(srv.GetMove, 'get_move')
        self.move_client = self.create_client(srv.Move, 'move')
        self.timer = self.create_timer(0.1, self.main_logic)
        self.my_move = False

    async def main_logic(self):
        if self.my_move:
            fen = await self.computer_vision_client()
            
            stockfish_request = srv.GetMove.Request(fen)
            move = await self.stockfish_client(stockfish_request)

            move_request = srv.Move.Request(move)
            await self.move_client(move_request)

            self.my_move = False
        else:
            input()
            self.my_move = True
        
def main(args=None):
    rclpy.init(args=args)
    node = game()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()