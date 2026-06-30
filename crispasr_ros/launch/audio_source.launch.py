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
    audio_backend = LaunchConfiguration('audio_backend')
    device_index = LaunchConfiguration('device_index')
    capture_sample_rate = LaunchConfiguration('capture_sample_rate')
    arecord_command = LaunchConfiguration('arecord_command')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_microphone',
            default_value='false',
            description='Whether to capture audio from live microphone instead of WAV publisher'
        ),
        DeclareLaunchArgument(
            'audio_backend',
            default_value='arecord',
            description='Local microphone backend: arecord or sounddevice'
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
        DeclareLaunchArgument(
            'arecord_command',
            default_value='arecord -q -D default -f S16_LE -r 16000 -c 1 -t raw -',
            description='Local arecord command that writes raw 16 kHz mono S16_LE PCM to stdout'
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
                    'audio_backend': audio_backend,
                    'device_index': device_index,
                    'capture_sample_rate': capture_sample_rate,
                    'arecord_command': arecord_command,
                },
            ],
            condition=IfCondition(use_microphone)
        )
    ])
