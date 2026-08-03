#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable
from pathlib import Path

def generate_launch_description():
    
    game = Node(
        package='game',
        executable='game',
        name='main'
    )

    stockfish = Node(
        package='stockfish_node',
        executable='stockfish_node',
        name='main'
    )

    cv = Node(
        package='comp_vision',
        executable='comp_vision',
        name='main',
        arguments=['--ros-args', '--log-level', 'DEBUG']
    )

    move = Node(
        package='move',
        executable='move',
        name='main'
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
