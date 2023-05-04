from typing import Optional
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from queue import Queue, Full, Empty
import time
import numpy as np
from scipy.spatial.transform import Rotation as R
import os
from rclpy.subscription import Subscription

__TOPLEVEL_DIR__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

__TOPIC__ = "/panorama/image/compressed"
__node__: Optional[Node] = None
__subscription__: Optional[Subscription] = None
xmap = np.loadtxt(f"{__TOPLEVEL_DIR__}/xmap.pgm").astype(np.float32)
ymap = np.loadtxt(f"{__TOPLEVEL_DIR__}/ymap.pgm").astype(np.float32)
__WIDTH__ = 512
__HEIGHT__ = 256
rot = R.from_euler("xyz", [180, 90, 0], degrees=True).as_matrix()


def init():
    global __node__
    if __node__ is None:
        rclpy.init()
        __node__ = rclpy.create_node("usb_webcam_display")


def subscribe(callback):
    global __subscription__, __node__
    if __node__ is None:
        return
    if __subscription__ is None:
        __subscription__ = __node__.create_subscription(CompressedImage, __TOPIC__, callback, 1)


def spherical_project(XYZ):
    lat = np.arcsin(XYZ[..., 2])
    lon = np.arctan2(XYZ[..., 1], XYZ[..., 0])

    x = lon / np.pi
    y = lat / np.pi * 2

    xy = np.stack((x, y), axis=-1)
    return xy


def spherical_project_inverse(xy, r: float = 1.0):
    lon = np.pi * xy[..., 0]
    lat = np.pi * xy[..., 1] / 2

    XYZ = np.stack(
        (
            np.cos(lat) * np.cos(lon),
            np.cos(lat) * np.sin(lon),
            np.sin(lat),
        ),
        axis=-1,
    )
    return XYZ


def remap_thubnail(img):
    res = cv2.remap(
        img,
        xmap.astype(np.float32),
        ymap.astype(np.float32),
        cv2.INTER_AREA,
        borderMode=cv2.BORDER_REPLICATE,
    )
    x, y = np.meshgrid(np.arange(__WIDTH__), np.arange(__HEIGHT__))
    x = x / __WIDTH__ * 2 - 1
    y = y / __HEIGHT__ * 2 - 1
    xy = np.stack((x, y), axis=-1)
    xyz = spherical_project_inverse(xy)
    xyz = xyz @ rot.T
    xy = spherical_project(xyz)
    x = xy[..., 0]
    y = xy[..., 1]
    xmap2 = (x + 1) / 2 * __WIDTH__
    ymap2 = (y + 1) / 2 * __HEIGHT__
    res = cv2.remap(
        res,
        xmap2.astype(np.float32),
        ymap2.astype(np.float32),
        cv2.INTER_AREA,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return res


def main():
    init()
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)

    def callback(msg):
        print("got image")
        jpg = msg.data
        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        img = remap_thubnail(img)
        cv2.imshow("image", img)
        cv2.imwrite("test.jpg", img)
        cv2.waitKey(0)

    subscribe(callback)
    rclpy.spin(__node__)


if __name__ == "__main__":
    main()
