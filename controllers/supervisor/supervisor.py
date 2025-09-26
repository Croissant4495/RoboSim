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
for _ in range(5):
    map_manager.spawn_random_obstacle()

for _ in range(15):
    collectable_manager.spawn_random_collectable()

scores = [0, 0]

while SupervisorRobot.step(TIME_STEP) != -1:
    # Process incoming messages from robots
    referee.update()

    # # Update score display
    # SupervisorRobot.setLabel(
    #     0,
    #     f"Blue Score: {referee.get_score(0)}",
    #     0.03, 0.03,
    #     0.08,
    #     0x0000FF,
    #     0.0,
    #     "Tahoma"
    # )

    # SupervisorRobot.setLabel(
    #     1,
    #     f"Red Score: {referee.get_score(1)}",
    #     0.9, 0.03,
    #     0.08,
    #     0xFF0000,
    #     0.0,
    #     "Tahoma"
    # )
    for rid in robots_manager.robots:
        robot = robots_manager.robots[rid]
        score = referee.get_score(robot.robot_id)
        robot.display_status(score)

    if len(collectable_manager.instances) < 15:
        collectable_manager.spawn_random_collectable()

    i += 1