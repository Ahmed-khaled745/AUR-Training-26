import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

class GoToGoalClient(Node):
    def __init__(self):
        super().__init__("go_to_goal_client")

        self.declare_parameter("service_name", "start_navigation")
        self.declare_parameter("start_delay", 5.0)

        service_name = self.get_parameter("service_name").value
        self.start_delay = self.get_parameter("start_delay").value

        self.client = self.create_client(SetBool, service_name)
        self.called = False

        self.get_logger().info(f"Will call '{service_name}' in {self.start_delay} seconds")
        self.timer = self.create_timer(self.start_delay, self.trigger_start)

    def trigger_start(self):
        if self.called:
            return
        self.called = True
        self.timer.cancel()

        if not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().error("Service not available")
            return

        request = SetBool.Request()
        request.data = True
        future = self.client.call_async(request)
        future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Service response: success={response.success}, message='{response.message}'")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

def main():
    rclpy.init()
    node = GoToGoalClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()