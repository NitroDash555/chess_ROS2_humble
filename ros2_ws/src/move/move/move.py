import chess
import rclpy
from rclpy.node import Node

from interfaces.srv import Move

START_COORDS = [0.0, 0.0]
GRIPPER_GRAB = 0
GRIPPER_DROP = 1


class move(Node):
    def __init__(self):
        super().__init__('move')

        self.declare_parameter('a1', [0.0, 0.0])
        self.declare_parameter('h1', [0.0, 0.0])
        self.declare_parameter('a8', [0.0, 0.0])
        self.declare_parameter('stash', [0.0, 0.0])
        self.declare_parameter('z_safe', 0.0)
        self.declare_parameter('z_grab', 0.0)

        self.a1 = self.get_parameter('a1').get_parameter_value().double_array_value
        self.h1 = self.get_parameter('h1').get_parameter_value().double_array_value
        self.a8 = self.get_parameter('a8').get_parameter_value().double_array_value
        self.stash = self.get_parameter('stash').get_parameter_value().double_array_value
        self.z_safe = self.get_parameter('z_safe').get_parameter_value().double_value
        self.z_grab = self.get_parameter('z_grab').get_parameter_value().double_value

        self.vector_h_axis = (
            (self.h1[0] - self.a1[0]) / 7.0,
            (self.h1[1] - self.a1[1]) / 7.0,
        )
        self.vector_v_axis = (
            (self.a8[0] - self.a1[0]) / 7.0,
            (self.a8[1] - self.a1[1]) / 7.0,
        )

        self.srv = self.create_service(Move, 'move', self.handle_move)

    def handle_move(self, request, response):
        move = chess.Move.from_uci(request.move)
        board = chess.Board(request.fen)

        self.get_logger().info('got move')
        commands = self.break_down_move(move, board)

        # TODO: заменить на отправку команд в Arduino (serial/I2C/CAN)
        self.get_logger().info(f'New move commands: {commands}')
        return response

    def break_down_move(self, move, board):
        commands = []

        self.get_logger().info('starting to break the move down')
        

        if board.is_en_passant(move):
            captured = chess.square(
                        chess.square_file(move.to_square),
                        chess.square_rank(move.from_square),
                    )
            self._approach(commands, *self.convert(captured), GRIPPER_GRAB)
            self._approach(commands, *self.stash, GRIPPER_DROP)
            self._approach(commands, *self.convert(move.from_square), GRIPPER_GRAB)
            self._approach(commands, *self.convert(move.to_square), GRIPPER_DROP)

        elif board.is_capture(move):
            self._approach(commands, *self.convert(move.to_square), GRIPPER_GRAB)
            self._approach(commands, *self.stash, GRIPPER_DROP)
            self._approach(commands, *self.convert(move.from_square), GRIPPER_GRAB)
            self._approach(commands, *self.convert(move.to_square), GRIPPER_DROP)
        
        elif board.is_castling(move):
            rank = chess.square_rank(move.from_square)
            king_file = chess.square_file(move.from_square)
            if chess.square_file(move.to_square) > king_file:
                # рокировка в сторону королевского фланга (O-O): ладья h -> f
                rook_from, rook_to = chess.square(7, rank), chess.square(5, rank)
            else:
                # рокировка в сторону ферзевого фланга (O-O-O): ладья a -> d
                rook_from, rook_to = chess.square(0, rank), chess.square(3, rank)
            self._approach(commands, *self.convert(move.from_square), GRIPPER_GRAB)
            self._approach(commands, *self.convert(move.to_square), GRIPPER_DROP)
            self._approach(commands, *self.convert(rook_from), GRIPPER_GRAB)
            self._approach(commands, *self.convert(rook_to), GRIPPER_DROP)
            
        else:
            self._approach(commands, *self.convert(move.from_square), GRIPPER_GRAB)
            self._approach(commands, *self.convert(move.to_square), GRIPPER_DROP)

        commands.append(
            f"{START_COORDS[0]};{START_COORDS[1]};{self.z_safe}"
        )
        return commands

    def _approach(self, commands, x, y, gripper):
        commands.append(f"{x};{y};{self.z_safe}")
        commands.append(f"{x};{y};{self.z_grab}")
        commands.append(gripper)
        commands.append(f"{x};{y};{self.z_safe}")

    def convert(self, square):
        square_id = square if isinstance(square, int) else chess.parse_square(square)
        col = chess.square_file(square_id)
        row = chess.square_rank(square_id)

        phys_x = self.a1[0] + col * self.vector_h_axis[0] + row * self.vector_v_axis[0]
        phys_y = self.a1[1] + col * self.vector_h_axis[1] + row * self.vector_v_axis[1]

        return round(phys_x, 2), round(phys_y, 2)


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
