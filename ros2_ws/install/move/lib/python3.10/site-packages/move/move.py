import rclpy
from rclpy.node import Node

from interfaces.srv import Move

class move(Node):
    def __init__(self):
        super().__init__('move')
        self.srv = self.create_service(Move, 'move', self.move)

    def move(self, request, response):
        to_move = request.move
        # код для перемещения

def main(args=None):
    rclpy.init(args=args)
    node = move()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()