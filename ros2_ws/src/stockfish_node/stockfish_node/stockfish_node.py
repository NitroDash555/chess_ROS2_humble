import rclpy
from rclpy.node import Node
import stockfish

from interfaces.srv import GetMove

class stockfish_node(Node):
    def __init__(self):
        super().__init__('stockfish')
        self.srv = self.create_service(GetMove, 'get_move', self.get_move)

    def return_move(self, request, response):
        fen = request.fen
        response.move = self.get_move(fen)
        return response
        
    def get_move(self, fen):
        #код
        return 'e2e4' #пример

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