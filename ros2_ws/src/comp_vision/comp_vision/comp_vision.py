#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ultralytics import YOLO
import cv2

from interfaces.srv import GetFEN

class comp_vision(Node):
    def __init__(self):
        super().__init__('comp_vision')
        self.srv = self.create_service(GetFEN, 'get_fen', self.return_fen)

    def return_fen(self, request, response):
        fen = self.make_fen() #потом вместо строки здесь будет вызов функции в которой будет код комапьютерного зрения
        response.fen = fen
        return response
    
    def make_fen(self):
        #здесь будет код компьютерного зрения
        return "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 2" #временный пример

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