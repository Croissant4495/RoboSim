from controller import Supervisor
from utils.CollectableManager import CollectableManager
from utils.MapManager import MapManager
from utils.RobotsManager import RobotsManager
import struct
from utils.config import *


# Supervisor setup
SupervisorRobot = Supervisor()
map_manager = MapManager(SupervisorRobot, MAP_SIZE)
collectable_manager = CollectableManager(SupervisorRobot, map_manager)
robots_manager = RobotsManager(SupervisorRobot, {0: "puck", 1: "puck2"})

i = 0
# Spawn initial obstacles and collectables
for _ in range(5):
    map_manager.spawn_random_obstacle()

for _ in range(15):
    collectable_manager.spawn_random_box(color=(0, 1, 0))

scores = [0, 0]

while SupervisorRobot.step(TIME_STEP) != -1:
    # Process incoming messages from robots
    messages = robots_manager.process_messages()
    for robot_id, msg_type, data in messages:
        if msg_type == 1:  # Score update
            scores[robot_id] += data
            collectable_manager.spawn_random_box(color=(0, 1, 0))

    # Update score display
    SupervisorRobot.setLabel(
        0,  # ID (0–9, each replaces the previous with same ID)
        f"Blue Score: {scores[0]}",  # text
        0.03, 0.03,  # x, y screen position (0–1, relative to window)
        0.08,  # font size
        0x0000FF,  # color (RGB hex)
        0.0,  # transparency (0=opaque, 1=fully transparent)
        "Tahoma"  # font
    )

    SupervisorRobot.setLabel(
        1,  # ID (0–9, each replaces the previous with same ID)
        f"Red Score: {scores[1]}",  # text
        0.9, 0.03,  # x, y screen position (0–1, relative to window)
        0.08,  # font size
        0xFF0000,  # color (RGB hex)
        0.0,  # transparency (0=opaque, 1=fully transparent)
        "Tahoma"  # font
    )

    robot_pos = robots_manager.get_robot_position(0)
    robot2_pos = robots_manager.get_robot_position(1)

    # Keep the existing proximity-based collection for comparison
    # You can remove this once the emitter/receiver system is working
    obj = collectable_manager.get_nearby_object(robot_pos, radius=0.05)
    if obj:
        collectable_manager.despawn_box(obj)
        # Don't increment score here anymore - let the robot controller handle it
        # scores[0] += 1  # Commented out
        collectable_manager.spawn_random_box()

    obj2 = collectable_manager.get_nearby_object(robot2_pos, radius=0.05)
    if obj2:
        collectable_manager.despawn_box(obj2)
        # Don't increment score here anymore - let the robot controller handle it
        # scores[1] += 1  # Commented out
        collectable_manager.spawn_random_box()

    # if i % 50 == 0:  # every 50 steps, print tracked instances
    #     print("Tracked objects:", collectable_manager.list_instances())

    i += 1