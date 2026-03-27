#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node

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
        name='main'
    )

    move = Node(
        package='move',
        executable='move',
        name='main'
    )

    return LaunchDescription([
        cv,
        move,
        stockfish,
        game
    ])