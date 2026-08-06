#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable
from pathlib import Path

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
        additional_env={'NODE_ENV': 'debug'} #для рендера и сохранения картинок в pipe, закомментить если не нужно
    )

    move = Node(
        package='move',
        executable='move',
        parameters=[_resolve_board_calibration_path()]
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            name='ROS_LOG_DIR', 
            value=str(_resolve_save_path())
        ),

        cv,
        move,
        stockfish,
        game
    ])

def _resolve_save_path():
    cwd = Path.cwd().resolve()
    # Безопасное объединение текущей директории и списка родительских директорий
    for candidate in [cwd] + list(cwd.parents):
        if (candidate / 'ros2_ws').exists() and (candidate / 'log').exists():
            log_dir = candidate / 'log'
            log_dir.mkdir(parents=True, exist_ok=True)
            return log_dir

    fallback = cwd / 'log'
    fallback.mkdir(parents=True, exist_ok=True) # Исправлен .parent на сам fallback
    return fallback

def _resolve_board_calibration_path():
    cwd = Path.cwd().resolve()
    for candidate in [cwd] + list(cwd.parents):
        if (candidate / 'ros2_ws').exists() and (candidate / 'config' / 'board_calibration.yaml').exists():
            return str(candidate / 'config' / 'board_calibration.yaml')

    return str(cwd / 'config' / 'board_calibration.yaml')
