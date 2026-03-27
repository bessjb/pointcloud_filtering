import argparse
import numpy as np
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from builtin_interfaces.msg import Time
import sensor_msgs_py.point_cloud2 as pc2

import open3d as o3d


class PointcloudProcessor(Node):
    def __init__(self,
                 filter_height: float | None,
                 rotate_cloud: bool,
                 rpy: tuple,
                 translate_cloud: bool,
                 xyz: tuple,
                 calculate_traversability: bool):
        super().__init__('filter_pointcloud_node')
        self.filter_height = filter_height
        self.rotate_cloud = rotate_cloud
        self.rpy = rpy
        self.translate_cloud = translate_cloud
        self.xyz = xyz
        self.calculate_traversability = calculate_traversability

        self.publisher_ = self.create_publisher(PointCloud2, 'filtered_pointcloud', 10)
        self.subscriber_ = self.create_subscription(
            PointCloud2,
            '/os1_cloud_node/points',
            self.subscriber_callback,
            10)

    def subscriber_callback(self, msg):
        cloud_array = pc2.read_points(msg, field_names=(
        "x", "y", "z", "intensity", "t", "reflectivity", "ring", "noise", "range"
        ), skip_nans=True)

        stacked_points = np.column_stack([
            cloud_array["x"],
            cloud_array["y"],
            cloud_array["z"]])

        if self.rotate_cloud:
            stacked_points = self.rotate(stacked_points, self.rpy)

        if self.translate_cloud:
            stacked_points = self.translate(stacked_points, self.xyz)

        if self.filter_height is not None:
            stacked_points = self.filter_cloud(stacked_points, self.filter_height)

        if self.calculate_traversability:
            stacked_points = self.normals_calc(stacked_points)

        out_msg = self.generate_msg_from_numpy(stacked_points, msg.header.stamp, msg.header.frame_id)

        self.publisher_.publish(out_msg)
    
    def generate_msg_from_numpy(self, points: np.ndarray, timestamp=None, frame_id="map"):
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

        if  points.shape[1] == 4:
            fields.append(PointField(name='trav', offset=12, datatype=PointField.FLOAT32, count=1))

        msg = pc2.create_cloud(header, fields, points.astype(np.float32))

        return msg

    @staticmethod
    def normals_calc(points: np.ndarray):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)

        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=0.15,
                max_nn=30
            )
        )

        normals = np.asarray(pcd.normals)
        z_axis = np.array([0, 0, 1])
        traversability = normals @ z_axis 

        points = np.column_stack((points, traversability))

        return points 

    def rotate(self, points: np.ndarray, rpy: tuple = (0.0, 0.0, 0.0)):
        R = self.generate_rotation_matrix(*rpy)
        points =  points @ R.T
        return points

    @staticmethod
    def translate(points: np.ndarray, xyz: tuple = (0.0, 0.0, 0.0)):
        T = np.array(xyz)
        points = points + T
        return points

    @staticmethod
    def filter_cloud(points: np.array, exclude_height: float = -0.2):
        points = points[points[:, 2] < exclude_height]
        return points

    @staticmethod
    def generate_rotation_matrix(rx, ry, rz):
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx),  np.cos(rx)]
        ])

        Ry = np.array([
            [ np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])

        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz),  np.cos(rz), 0],
            [0, 0, 1]
        ])

        return Rz @ Ry @ Rx


def parse_args():
    parser = argparse.ArgumentParser(
        description="A pointcloud processing ros2 node."
    )

    parser.add_argument(
        "--filter_height",
        type=float,
        default=None,
        help="Height threshold to exclude points"
    )

    parser.add_argument(
        "--rotate-cloud",
        action="store_true",
        help="Enable cloud rotation"
    )

    parser.add_argument(
        "--rpy",
        type=float,
        nargs=3,
        metavar=("ROLL", "PITCH", "YAW"),
        default=[1.5707, 0.0, 0.0],
        help="Cloud rotation in roll pitch yaw"
    )

    parser.add_argument(
        "--translate-cloud",
        action="store_true",
        help="Enable cloud translation"
    )

    parser.add_argument(
        "--xyz",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        default=[0.0, 0.0, -2.0],
        help="Cloud translation in x y z"
    )

    parser.add_argument(
        "--calculate-traversability",
        action="store_true",
        help="Enable traversability calculation"
    )

    return parser.parse_args()

def main(args=None):
    parsed_args = parse_args()

    rclpy.init(args=args)

    pointcloud_processor = PointcloudProcessor(
            filter_height=parsed_args.filter_height,
            rotate_cloud=parsed_args.rotate_cloud,
            rpy=parsed_args.rpy,
            translate_cloud=parsed_args.translate_cloud,
            xyz=parsed_args.xyz,
            calculate_traversability=parsed_args.calculate_traversability)

    rclpy.spin(pointcloud_processor)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    pointcloud_processor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

