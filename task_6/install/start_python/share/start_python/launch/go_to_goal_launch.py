import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('start_python'),
        'config',
        'go_to_goal_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim_node',
            output='screen'
        ),
        Node(
            package='start_python',
            executable='go_to_goal',
            name='go_to_goal',
            output='screen',
            parameters=[config]
        ),
        Node(
            package='start_python',
            executable='go_to_goal_client',
            name='go_to_goal_client',
            output='screen',
            parameters=[config]
        ),
    ])