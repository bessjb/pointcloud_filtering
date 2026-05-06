from modules.sim_object import SimObject

class Light(SimObject):

    def __init__(self, sim_assets, *args, **kwargs):

        light_image = sim_assets.image_assets["img_light"]
        super(Light, self).__init__(img=light_image,*args, **kwargs)

        self.type = "light"


    def update_object(self, dt):
        # a light only exists at a given position
        pass
        