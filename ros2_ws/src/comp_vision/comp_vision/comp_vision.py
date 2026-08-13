#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from chess_common import repo_paths
from interfaces.action import GetFEN
from comp_vision.chess_vision import pipeline


class comp_vision(Node):
    def __init__(self):
        super().__init__('comp_vision')
        self.get_logger().info('создаем сервер')
        self.action_server = ActionServer(
            self, GetFEN, 'get_fen', self.execute_callback,
            cancel_callback=self.cancel_callback,
        )
        self.get_logger().info('сервер создан')
        self.image_path = repo_paths.image_path()

    def execute_callback(self, goal_handle):
        request = goal_handle.request
        feedback = GetFEN.Feedback()

        def progress_cb(step, message):
            feedback.step = step
            feedback.message = message
            goal_handle.publish_feedback(feedback)

        result = GetFEN.Result()
        result.fen = request.prev_fen
        try:
            result.fen = pipeline(
                str(self.image_path),
                prev_fen=request.prev_fen,
                logger=self.get_logger(),
                progress_cb=progress_cb,
            )
        except Exception as e:
            self.get_logger().error(f'pipeline failed: {e}')
            goal_handle.abort()
            return result

        if goal_handle.is_cancel_requested:
            goal_handle.canceled()
            return result
        goal_handle.succeed()
        return result

    def cancel_callback(self, goal_handle):
        self.get_logger().info('cancel requested, aborting after current run')
        return rclpy.action.CancelResponse.ACCEPT


def main(args=None):
    rclpy.init(args=args)
    node = comp_vision()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()


if __name__ == '__main__':
    main()
