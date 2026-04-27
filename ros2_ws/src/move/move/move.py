import rclpy
from rclpy.node import Node

from interfaces.srv import Move

class move(Node):
    def __init__(self):
        super().__init__('move')
        self.srv = self.create_service(Move, 'move', self.handle_move)

    def handle_move(self, request, response):
        to_move = request.move
        # TODO: заменить на отправку команд в Arduino (serial/I2C/CAN)
        self.get_logger().info(f'New move request: {to_move}')
        return response

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