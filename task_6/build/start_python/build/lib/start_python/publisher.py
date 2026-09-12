import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist 
from turtlesim.msg import Pose 



class Publisher(Node):
    def __init__(self):
        super().__init__("publisher")
        
        self.publisher = self.create_publisher(Twist,"/turtle1/cmd_vel",10)
        self.counter=0
        self.create_timer(1,self.timer_callback)
 
    def timer_callback(self):
        self.counter+=1
        msg = Twist()
        msg.linear.x =  2.0
        msg.angular.z = 1.0
        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = Publisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()