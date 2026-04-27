#!/usr/bin/env python3

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np

import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Imu
from scipy.spatial.transform import Rotation as R
from scipy.signal import butter, sosfiltfilt


def quaternion_to_euler(quaternion):
    r = R.from_quat(quaternion)
    return r.as_euler("xyz") 

def read_imu_data(
    bag_path,
    imu_topic="/imu/data",
    accel_cutoff_hz=1.0,
    rot_cutoff_hz=0.2,
    filter_order=4,
):

    storage_options = rosbag2_py.StorageOptions(
        uri=bag_path,
        storage_id='sqlite3'
    )

    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr'
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    times = []
    acc_x = []
    acc_y = []
    acc_z = []

    orien_x = []
    orien_y = []
    orien_z = []
    orien_w = []

    while reader.has_next():
        topic, data, t = reader.read_next()
        if topic != imu_topic:
            continue

        msg = deserialize_message(data, Imu)

        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        times.append(stamp)

        acc_x.append(msg.linear_acceleration.x)
        acc_y.append(msg.linear_acceleration.y)
        acc_z.append(msg.linear_acceleration.z)

        orien_x.append(msg.orientation.x)
        orien_y.append(msg.orientation.y)
        orien_z.append(msg.orientation.z)
        orien_w.append(msg.orientation.w)

    times = np.array(times)
    times = times - times[0]
    fs = 1 / np.mean(np.diff(times))

    acc = np.column_stack((acc_x, acc_y, acc_z))
    rot = np.column_stack((orien_x, orien_y, orien_z, orien_w))
    rot = quaternion_to_euler(rot)

    acc_sos = butter(filter_order, accel_cutoff_hz, btype="low", fs=fs, output="sos")
    rot_sos = butter(filter_order, rot_cutoff_hz, btype="low", fs=fs, output="sos")

    filtered_acc = sosfiltfilt(acc_sos, acc, axis=0)
    filtered_rot = sosfiltfilt(rot_sos, rot, axis=0)

    fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)

    # Raw acceleration
    axes[0].plot(times, acc[:, 0], label="ax")
    axes[0].plot(times, acc[:, 1], label="ay")
    axes[0].plot(times, acc[:, 2], label="az")
    axes[0].set_ylabel("Acceleration [m/s²]")
    axes[0].set_title("Raw IMU Linear Acceleration vs Time")
    axes[0].grid(True)
    axes[0].legend()

    # Filtered acceleration
    axes[1].plot(times, filtered_acc[:, 0], label="ax (filtered)")
    axes[1].plot(times, filtered_acc[:, 1], label="ay (filtered)")
    axes[1].plot(times, filtered_acc[:, 2], label="az (filtered)")
    axes[1].set_ylabel("Acceleration [m/s²]")
    axes[1].set_title(
        f"Filtered IMU Linear Acceleration vs Time "
        f"(Butterworth low-pass, order={filter_order}, cutoff={accel_cutoff_hz} Hz)"
    )
    axes[1].grid(True)
    axes[1].legend()

    # Raw rotation
    axes[2].plot(times, rot[:, 0], label="roll")
    axes[2].plot(times, rot[:, 1], label="pitch")
    axes[2].plot(times, rot[:, 2], label="yaw")
    axes[2].set_ylabel("Angle [rad]")
    axes[2].set_title("Raw IMU Roll / Pitch / Yaw vs Time")
    axes[2].grid(True)
    axes[2].legend()

    # Filtered rotation
    axes[3].plot(times, filtered_rot[:, 0], label="roll (filtered)")
    axes[3].plot(times, filtered_rot[:, 1], label="pitch (filtered)")
    axes[3].plot(times, filtered_rot[:, 2], label="yaw (filtered)")
    axes[3].set_xlabel("Time [s]")
    axes[3].set_ylabel("Angle [rad]")
    axes[3].set_title(
        f"Filtered IMU Roll / Pitch / Yaw vs Time "
        f"(Butterworth low-pass, order={filter_order}, cutoff={rot_cutoff_hz} Hz)"
    )
    axes[3].grid(True)
    axes[3].legend()

    plt.tight_layout()
    plt.savefig("./filtered_imu.png")

def main():
    parser = argparse.ArgumentParser(
        description="Read IMU data from a ROS 2 SQLite bag and plot it."
    )
    parser.add_argument(
        'bag_path',
        help='Path to the ROS 2 bag directory or bag URI'
    )

    args = parser.parse_args()

    try:
        read_imu_data(args.bag_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
