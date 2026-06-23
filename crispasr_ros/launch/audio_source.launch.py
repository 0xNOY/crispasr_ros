import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node

def generate_launch_description():
    # Get package share directory
    pkg_dir = get_package_share_directory('crispasr_ros')
    config_file = os.path.join(pkg_dir, 'config', 'params_ros2.yaml')

    use_microphone = LaunchConfiguration('use_microphone')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_microphone',
            default_value='false',
            description='Whether to capture audio from live microphone instead of WAV publisher'
        ),
        # Launch Test Audio Publisher node (WAV playback)
        Node(
            package='crispasr_ros',
            executable='audio_publisher_node',
            name='audio_publisher_node',
            output='screen',
            parameters=[config_file],
            condition=UnlessCondition(use_microphone)
        ),
        # Launch Microphone Capture node
        Node(
            package='crispasr_ros',
            executable='microphone_node',
            name='microphone_node',
            output='screen',
            parameters=[config_file],
            condition=IfCondition(use_microphone)
        )
    ])
