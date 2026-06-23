"""ROS1/ROS2 compatibility layer for CrispASR ROS wrapper.
"""

from __future__ import annotations

import os
from typing import Any, Callable, List, Protocol, TypeVar, Union, cast

ParamValue = Union[bool, int, float, str, List[str]]
ParamT = TypeVar("ParamT", bound=ParamValue)

class Publisher(Protocol):
    def publish(self, message: Any) -> None: ...

def find_workspace_root(start_dir: str) -> str | None:
    """Find the workspace root directory containing pixi.toml.
    
    Args:
        start_dir: The starting directory path for search.
        
    Returns:
        The absolute path to the workspace root, or None if not found.
    """
    current = os.path.abspath(start_dir)
    while current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "pixi.toml")):
            return current
        current = os.path.dirname(current)
    return None

ROS_VERSION = int(os.environ.get("ROS_VERSION", "0"))

if ROS_VERSION == 1:
    import rospy

    class _RospyPublisher:
        def __init__(self, publisher: Any) -> None:
            self._publisher = publisher

        def publish(self, message: Any) -> None:
            self._publisher.publish(message)

    class RosNode:
        def __init__(self, name: str) -> None:
            rospy.init_node(name)
            self.name = name

        def get_param(self, name: str, default: ParamT) -> ParamT:
            return cast(ParamT, rospy.get_param("~" + name, default))

        def create_publisher(self, msg_type: Any, name: str) -> Publisher:
            # We use global name resolve by default, but fallback if specified
            topic = name if name.startswith("/") or name.startswith("~") else "~" + name
            return _RospyPublisher(
                rospy.Publisher(topic, msg_type, queue_size=10)
            )

        def create_subscriber(self, msg_type: Any, name: str, callback: Callable[[Any], None]) -> None:
            topic = name if name.startswith("/") or name.startswith("~") else "~" + name
            rospy.Subscriber(topic, msg_type, callback)

        def log_info(self, message: str) -> None:
            rospy.loginfo(message)

        def log_warn(self, message: str) -> None:
            rospy.logwarn(message)

        def log_error(self, message: str) -> None:
            rospy.logerr(message)

        def is_shutdown(self) -> bool:
            return cast(bool, rospy.is_shutdown())

        def spin(self) -> None:
            rospy.spin()

elif ROS_VERSION == 2:
    import rclpy
    import rclpy.node

    class _RclpyPublisher:
        def __init__(self, publisher: Any) -> None:
            self._publisher = publisher

        def publish(self, message: Any) -> None:
            self._publisher.publish(message)

    class RosNode:
        def __init__(self, name: str) -> None:
            rclpy.init()
            self._node = rclpy.node.Node(name)
            self.name = name

        def get_param(self, name: str, default: ParamT) -> ParamT:
            return cast(ParamT, self._node.declare_parameter(name, default).value)

        def create_publisher(self, msg_type: Any, name: str) -> Publisher:
            topic = name if name.startswith("/") or name.startswith("~/") else "~/" + name
            return _RclpyPublisher(
                self._node.create_publisher(msg_type, topic, 10)
            )

        def create_subscriber(self, msg_type: Any, name: str, callback: Callable[[Any], None]) -> None:
            topic = name if name.startswith("/") or name.startswith("~/") else "~/" + name
            self._node.create_subscription(msg_type, topic, callback, 10)

        def log_info(self, message: str) -> None:
            self._node.get_logger().info(message)

        def log_warn(self, message: str) -> None:
            self._node.get_logger().warning(message)

        def log_error(self, message: str) -> None:
            self._node.get_logger().error(message)

        def is_shutdown(self) -> bool:
            return not rclpy.ok()

        def spin(self) -> None:
            try:
                rclpy.spin(self._node)
            except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
                pass
            finally:
                self._node.destroy_node()
                if rclpy.ok():
                    rclpy.shutdown()

else:
    raise ImportError(
        "ROS_VERSION environment variable must be '1' or '2'; is a ROS "
        "environment active?"
    )

