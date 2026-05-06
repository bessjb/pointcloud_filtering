import pyglet

from modules.sim_assets import SimAssets
from modules.robot import Robot
from modules.light import Light

def run():
    window = pyglet.window.Window(1000, 1000, "EGH437 Robot Simulation", resizable=False)

    # Store objects in a batch to load them efficiently
    main_batch = pyglet.graphics.Batch()

    # groups - 0 drawn first, 10 drawn last
    groups = []
    for i in range(10):
        #groups.append(pyglet.graphics.OrderedGroup(i))  # used in older version
        groups.append(pyglet.graphics.Group(i))

    # load required assets
    assets = SimAssets()

    # list of all objects in the simulation
    sim_objects = []

    # list of lights in the simulation
    lights = []

    # list of all robots in the simulation
    robots = []


    @window.event
    def on_draw():
        window.clear()
        main_batch.draw()
    
    
    # loads the main scene
    def load_main_scene():
        # create an instance of a robot
        robot_1 = Robot(assets, x=200, y=500, batch=main_batch, group=groups[5])
        robots.append(robot_1)
        sim_objects.append(robot_1)
        #window.push_handlers(robot_1)

        # robot_2 = Robot(assets, x=600, y=200, batch=main_batch, group=groups[5])
        # robots.append(robot_2)
        # sim_objects.append(robot_2)
        
        # create an instance of a light
        light_1 = Light(assets, x=500, y=600, batch=main_batch, group=groups[5])
        lights.append(light_1)
        sim_objects.append(light_1)


    # update loop
    def update(dt):
        
        objects_to_add = []     # list of new objects to add
        # update positions, state of each object and
        # collect all children that each object may spawn
        for obj in sim_objects:
            obj.update_object(dt)
            objects_to_add.extend(obj.child_objects)
            obj.child_objects = []  # clear the list

        # add new objects
        sim_objects.extend(objects_to_add)

        # inform all light sensors about all lights
        for obj in sim_objects:
            if obj.type == "light_sensor":
                obj.set_lights(lights)

        
        # inform all lidars about all robots
        for obj in sim_objects:
            if obj.type == "lidar":
                obj.set_robots(robots)


    load_main_scene()
    pyglet.clock.schedule_interval(update, 1 / 120.0)
    pyglet.app.run()