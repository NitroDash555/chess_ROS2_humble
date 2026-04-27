import rclpy
from rclpy.node import Node
import stockfish
from pathlib import Path

from interfaces.srv import GetMove


class stockfish_node(Node):
    def __init__(self):
        super().__init__('stockfish')
        stockfish_path = self._resolve_stockfish_path()
        self.engine = stockfish.Stockfish(path=stockfish_path)
        self.srv = self.create_service(GetMove, 'get_move', self.return_move)

    def _resolve_stockfish_path(self):
        common_paths = [
            '/usr/games/stockfish',
            '/usr/bin/stockfish',
        ]
        for path in common_paths:
            if Path(path).exists():
                return path
        return 'stockfish'

    def return_move(self, request, response):
        fen = request.fen
        response.move = self.get_move_for_fen(fen)
        return response

    def get_move_for_fen(self, fen):
        self.engine.set_fen_position(fen)
        move = self.engine.get_best_move()
        return move if move is not None else ''


def main(args=None):
    rclpy.init(args=args)
    node = stockfish_node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()