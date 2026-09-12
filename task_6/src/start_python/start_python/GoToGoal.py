import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import SetBool
import math

class GoToGoal(Node):
    def __init__(self):
        super().__init__("go_to_goal")

        self.declare_parameter("goal_x", 10.0)
        self.declare_parameter("goal_y", 10.0)
        self.declare_parameter("linear_gain", 1.5)
        self.declare_parameter("angular_gain", 6.0)
        self.declare_parameter("distance_tolerance", 0.1)
        self.declare_parameter("angle_tolerance", 0.1)
        self.declare_parameter("loop_rate_hz", 10.0)
        self.declare_parameter("service_name", "start_navigation")

        self.goal_x = self.get_parameter("goal_x").value
        self.goal_y = self.get_parameter("goal_y").value
        self.linear_gain = self.get_parameter("linear_gain").value
        self.angular_gain = self.get_parameter("angular_gain").value
        self.distance_tolerance = self.get_parameter("distance_tolerance").value
        self.angle_tolerance = self.get_parameter("angle_tolerance").value
        loop_rate_hz = self.get_parameter("loop_rate_hz").value
        service_name = self.get_parameter("service_name").value

        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.subscriber = self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 10)
        self.current_pose = Pose()

       
        self.active = False

        self.srv = self.create_service(SetBool, service_name, self.set_bool_callback)

        self.get_logger().info(
            f"Node ready. Waiting for '{service_name}' service call to start navigating to "
            f"({self.goal_x}, {self.goal_y})"
        )

        timer_period = 1.0 / loop_rate_hz
        self.create_timer(timer_period, self.publisher_velocity)

    def set_bool_callback(self, request, response):
        self.active = request.data
        response.success = True
        response.message = "Navigation started" if self.active else "Navigation stopped"
        self.get_logger().info(response.message)
        return response

    def pose_callback(self, msg):
        self.current_pose = msg

    def publisher_velocity(self):
        msg = Twist()

        if not self.active:
            # Not started yet - publish zero velocity and do nothing else
            self.publisher.publish(msg)
            return

        distance = math.sqrt((self.goal_x - self.current_pose.x)**2 + (self.goal_y - self.current_pose.y)**2)
        angle_to_goal = math.atan2(self.goal_y - self.current_pose.y, self.goal_x - self.current_pose.x)
        angle_diff = math.atan2(
            math.sin(angle_to_goal - self.current_pose.theta),
            math.cos(angle_to_goal - self.current_pose.theta)
        )
        distance_diff = distance - self.distance_tolerance

        if abs(distance_diff) < 0.05:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info("Goal reached!")
        else:
            if abs(angle_diff) > self.angle_tolerance:
                msg.linear.x = 0.0
                msg.angular.z = self.angular_gain * angle_diff
            else:
                msg.linear.x = self.linear_gain * distance_diff
                msg.angular.z = 0.0

        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = GoToGoal()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()