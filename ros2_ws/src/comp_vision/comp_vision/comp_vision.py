#!/usr/bin/env python3

from pathlib import Path

import rclpy
from rclpy.node import Node

from interfaces.srv import GetFEN

from comp_vision.chess_vision import pipeline


class comp_vision(Node):
    def __init__(self):
        super().__init__('comp_vision')
        self.get_logger().info('создаем сервер')
        self.serv = self.create_service(GetFEN, 'get_fen', self.return_fen)
        self.get_logger().info('сервер создан')
        self.image_path = self._resolve_save_path() / 'z.jpg'

    def return_fen(self, request, response):
        response.fen = pipeline(
            str(self.image_path),
            prev_fen=request.prev_fen,
            logger=self.get_logger(),
        )
        return response

    @staticmethod
    def _resolve_save_path():
        cwd = Path.cwd().resolve()
        for candidate in (cwd, *cwd.parents):
            if (candidate / 'ros2_ws').exists() and (candidate / 'img').exists():
                img_dir = candidate / 'img'
                img_dir.mkdir(parents=True, exist_ok=True)
                return img_dir

        fallback = cwd / 'img'
        fallback.parent.mkdir(parents=True, exist_ok=True)
        return fallback


def main(args=None):
    rclpy.init(args=args)
    node = comp_vision()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
