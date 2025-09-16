from controller import Supervisor
from utils.CollectableManager import CollectableManager
from utils.MapManager import MapManager

TIME_STEP = 32
MAP_SIZE = (2, 2)
TILE_SIZE = 0.25


# Supervisor setup
SupervisorRobot = Supervisor()
map_manager = MapManager(SupervisorRobot, MAP_SIZE)
collectable_manager = CollectableManager(SupervisorRobot, map_manager)

robot_node = SupervisorRobot.getFromDef('puck')
robot2_node = SupervisorRobot.getFromDef('puck2')

i = 0

for _ in range(5):
    map_manager.spawn_random_obstacle()

for _ in range(15):
	collectable_manager.spawn_random_box(color=(0, 1, 0))

scores = [0, 0]

while SupervisorRobot.step(TIME_STEP) != -1:

	SupervisorRobot.setLabel(
        0,                          # ID (0–9, each replaces the previous with same ID)
        f"Blue Score: {scores[0]}",          # text
        0.03, 0.03,                 # x, y screen position (0–1, relative to window)
        0.08,                        # font size
        0x0000FF,                   # color (RGB hex)
        0.0,                        # transparency (0=opaque, 1=fully transparent)
        "Tahoma"                     # font
    )

	SupervisorRobot.setLabel(
			1,                          # ID (0–9, each replaces the previous with same ID)
			f"Red Score: {scores[1]}",          # text
			0.9, 0.03,                 # x, y screen position (0–1, relative to window)
			0.08,                        # font size
			0xFF0000,                   # color (RGB hex)
			0.0,                        # transparency (0=opaque, 1=fully transparent)
			"Tahoma"                     # font
	)

	robot_pos = robot_node.getPosition()
	robot2_pos = robot2_node.getPosition()

    # Despawn closest to robot
	obj = collectable_manager.get_nearby_object(robot_pos, radius=0.05)
	if obj:
		collectable_manager.despawn_box(obj)
		scores[0] += 1
		collectable_manager.spawn_random_box()


	obj2 = collectable_manager.get_nearby_object(robot2_pos, radius=0.05)
	if obj2:
		collectable_manager.despawn_box(obj2)
		scores[1] += 1
		collectable_manager.spawn_random_box()

	# if i % 50 == 0:  # every 50 steps, print tracked instances

		# print("Tracked objects:", collectable_manager.list_instances())

	i += 1
