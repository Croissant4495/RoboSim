from controller import Supervisor
from utils.CollectableManager import CollectableManager
from utils.MapManager import MapManager
from utils.RobotsManager import RobotsManager
from utils.Referee import Referee
import struct
from utils.config import *


# Supervisor setup
SupervisorRobot = Supervisor()
map_manager = MapManager(SupervisorRobot, MAP_SIZE)
collectable_manager = CollectableManager(SupervisorRobot, map_manager)
robots_manager = RobotsManager(SupervisorRobot, {0: "puck", 1: "puck2"})
referee = Referee(SupervisorRobot, robots_manager, map_manager, collectable_manager, set_bonus=30)

i = 0
# Spawn initial obstacles and collectables
for _ in range(3):
    map_manager.spawn_random_obstacle()

for _ in range(25):
    collectable_manager.spawn_random_collectable()

scores = [0, 0]

while SupervisorRobot.step(TIME_STEP) != -1:
    # Process incoming messages from robots
    referee.update()
    
    for rid in robots_manager.robots:
        robot = robots_manager.robots[rid]
        score = referee.get_score(robot.robot_id)
        robot.display_status(score)

    if len(collectable_manager.instances) < 15:
        collectable_manager.spawn_random_collectable()

    i += 1