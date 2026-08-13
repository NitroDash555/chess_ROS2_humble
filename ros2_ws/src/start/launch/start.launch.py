#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable

from chess_common import repo_paths


def generate_launch_description():

    game = Node(
        package='game',
        executable='game'
    )

    stockfish = Node(
        package='stockfish_node',
        executable='stockfish_node'
    )

    cv = Node(
        package='comp_vision',
        executable='comp_vision',
        additional_env={'DEBUG': 'true'} #для рендера и сохранения картинок в pipe, закомментить если не нужно
    )

    move = Node(
        package='move',
        executable='move',
        parameters=[str(repo_paths.board_calibration_path())]
    )

    bridge = Node(
        package='arduino_bridge',
        executable='arduino_bridge',
        parameters=[str(repo_paths.arduino_cfg_path())]
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            name='ROS_LOG_DIR',
            value=str(repo_paths.log_dir())
        ),
        
        bridge,
        cv,
        move,
        stockfish,
        game
    ])
