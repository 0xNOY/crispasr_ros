import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Get package share directory
    pkg_dir = get_package_share_directory('crispasr_ros')
    config_file = os.path.join(pkg_dir, 'config', 'params_ros2.yaml')

    return LaunchDescription([
        # Launch CrispASR node
        Node(
            package='crispasr_ros',
            executable='crispasr_node',
            name='crispasr_node',
            output='screen',
            parameters=[config_file]
        )
    ])


