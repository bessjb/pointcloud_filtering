import math
import random

from modules.sim_object import SimObject

class Lidar(SimObject):

    def __init__(self, sim_assets, *args, **kwargs):

        lidar_img = sim_assets.image_assets["img_lidar"]
        super(Lidar, self).__init__(img=lidar_img,*args, **kwargs)

        self.type = "lidar"
        self.robots = []
        self.robot_positions = []


    def update_object(self, dt):
        # lidar stores positions of other robots with respect to itself
        self.robot_positions = []
        for robot in self.robots:
            self.robot_positions.append((robot.x - self.x, robot.y-self.y))
        
        # remove own position
        if (0,0) in self.robot_positions:
            self.robot_positions.remove((0,0))


    # tells the lidar about all the robots in the world
    def set_robots(self, list_of_robots):
        self.robots = list_of_robots

    # retuns the positions of the robots as a list of tuples
    def get_positions(self):
        if (0,0) in self.robot_positions:
            self.robot_positions.remove((0,0))
        return self.robot_positions