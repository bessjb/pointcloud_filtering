import math
import random

from modules.sim_object import SimObject

class LightSensor(SimObject):

    def __init__(self, sim_assets, *args, **kwargs):

        sensor_img = sim_assets.image_assets["img_light_sensor"]
        super(LightSensor, self).__init__(img=sensor_img,*args, **kwargs)

        self.type = "light_sensor"
        self.lights = []
        self.intensity = 0
        self.max_intensity = 100
        self.min_intensity = 0.1


    def update_object(self, dt):
        # a sensor only updates its intensity
        self.update_intensity()
        

    # updates the intensity of the sensor
    def update_intensity(self):
        # simple implementation. 
        self.intensity = 0
        for light in self.lights:
            distance = self.get_distance_from(light)
            # if light is too far away, sensr does not pick it up
            if distance > 500:
                self.intensity += self.min_intensity
            # if light is too close, sensor picks it up at max intensity
            if distance < 50:
                self.intensity += self.max_intensity
            if distance > 50 and distance < 500:
                inverse_square_distance =  1/(self.get_squared_distance_from(light))
                rescaled_inv_sq_dist = 250000*inverse_square_distance
                self.intensity += rescaled_inv_sq_dist

    # returns the distance of this object from other object
    def get_distance_from(self, other):
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)

    # returns squared distance of this object from other object
    def get_squared_distance_from(self, other):
        return (self.x-other.x)**2 + (self.y-other.y)**2

    # tells the sensor about all the lights in the world
    def set_lights(self, list_of_lights):
        self.lights = list_of_lights

    # retuns the light intensitiy detected by the sensor
    def get_intensity(self):
        return self.intensity