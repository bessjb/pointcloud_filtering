import rclpy
import numpy as np

from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from builtin_interfaces.msg import Time
import sensor_msgs_py.point_cloud2 as pc2


class PointcloudProcessor(Node):
    def __init__(self):
        super().__init__('filter_plc_node')
        self.publisher_ = self.create_publisher(PointCloud2, 'filtered_pointcloud', 10)
        self.subscriber_ = self.create_subscription(
            PointCloud2,
            '/os1_cloud_node/points',
            self.subscriber_callback,
            10)

    def subscriber_callback(self, msg):
        points = pc2.read_points(msg, skip_nans=True)

        stacked_points = np.column_stack([
            points["x"],
            points["y"],
            points["z"]])

        '''
        YOUR CODE HERE
        see sensor_msgs/PointCloud2
        '''

        msg_out = self.generate_msg_from_numpy(stacked_points,
                                           msg.header.stamp,
                                           msg.header.frame_id)

        self.publisher_.publish(msg_out)

    def generate_msg_from_numpy(self, array: np.ndarray, timestamp=None, frame_id="map"):
        header = Header()
        header.frame_id = frame_id
        if isinstance(timestamp, Time):
            header.stamp = timestamp
        else:
            header.stamp = self.get_clock().now().to_msg()

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]

        msg = pc2.create_cloud(header, fields, array.astype(np.float32))

        return msg

def main(args=None):
    rclpy.init(args=args)

    pointcloud_processor = PointcloudProcessor()

    rclpy.spin(pointcloud_processor)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    pointcloud_processor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
