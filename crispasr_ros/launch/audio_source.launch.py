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
    device_index = LaunchConfiguration('device_index')
    capture_sample_rate = LaunchConfiguration('capture_sample_rate')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_microphone',
            default_value='false',
            description='Whether to capture audio from live microphone instead of WAV publisher'
        ),
        DeclareLaunchArgument(
            'device_index',
            default_value='-1',
            description='Microphone input device index; -1 uses the system default'
        ),
        DeclareLaunchArgument(
            'capture_sample_rate',
            default_value='0',
            description='Microphone hardware sample rate; 0 auto-detects a usable rate'
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
            parameters=[
                config_file,
                {
                    'device_index': device_index,
                    'capture_sample_rate': capture_sample_rate,
                },
            ],
            condition=IfCondition(use_microphone)
        )
    ])
