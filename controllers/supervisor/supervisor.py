from controller import Supervisor
from utils.CollectableManager import CollectableManager
from utils.MapManager import MapManager
import struct

TIME_STEP = 32
MAP_SIZE = (2, 2)
TILE_SIZE = 0.25

# Supervisor setup
SupervisorRobot = Supervisor()
map_manager = MapManager(SupervisorRobot, MAP_SIZE)
collectable_manager = CollectableManager(SupervisorRobot, map_manager)

# Initialize receiver for communication with robots
receiver = SupervisorRobot.getDevice('receiver')
if receiver:
    receiver.enable(TIME_STEP)
else:
    print("Warning: No receiver device found")

robot_node = SupervisorRobot.getFromDef('puck')
robot2_node = SupervisorRobot.getFromDef('puck2')

i = 0

# Spawn initial obstacles and collectables
for _ in range(5):
    map_manager.spawn_random_obstacle()

for _ in range(15):
    collectable_manager.spawn_random_box(color=(0, 1, 0))

scores = [0, 0]


def process_messages():
    """Process incoming messages from robots"""
    global scores

    if not receiver:
        return

    while receiver.getQueueLength() > 0:
        # Use getBytes() for binary data
        message_bytes = receiver.getBytes()

        try:
            # Convert to bytes object for struct.unpack
            message = bytes(message_bytes)

            # Unpack message: [robot_id, message_type, data]
            robot_id, message_type, data = struct.unpack('iii', message)

            if message_type == 1:  # Score update
                if 0 <= robot_id <= 1:
                    scores[robot_id] += data
                    print(f"Score updated for robot {robot_id}: +{data} (Total: {scores[robot_id]})")

                    # Spawn new collectable when score increases
                    collectable_manager.spawn_random_box(color=(0, 1, 0))

        except struct.error:
            print("Error: Invalid message format received")
        except Exception as e:
            print(f"Error processing message: {e}")

        receiver.nextPacket()

while SupervisorRobot.step(TIME_STEP) != -1:
    # Process incoming messages from robots
    process_messages()

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

    robot_pos = robot_node.getPosition()
    robot2_pos = robot2_node.getPosition()

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