from controller import Robot
import struct

# Create the Robot instance
robot = Robot()

# Get the simulation timestep
timestep = int(robot.getBasicTimeStep())

# Initialize motors
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))  # velocity control mode
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Initialize proximity sensors
ps = []
ps_names = ['ps0','ps1','ps2','ps3','ps4','ps5','ps6','ps7']
for name in ps_names:
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    ps.append(sensor)

# Initialize emitter
emitter = robot.getDevice('emitter')
if emitter is None:
    print("Warning: No emitter device found")

# Robot identification
ROBOT_ID = 0  # 0 = blue, 1 = red
MAX_SPEED = 6.28

# Message type constants (match referee)
MSG_DEPOSIT = 1
MSG_COLLECT = 2

# Example: map colors/types to integers
# (this must match your utils.config SCORING_RULES)
COLLECTABLE_TYPES = {
    "red": 0,
    "blue": 1,
    "black": 2
}

def send_collect(robot_id, claimed_type):
    """Send a collect request to the referee"""
    if emitter:
        message = struct.pack('iii', robot_id, MSG_COLLECT, claimed_type)
        emitter.send(message)
        print(f"Robot {robot_id} sent COLLECT request for type {claimed_type}")

def send_deposit(robot_id):
    """Send a deposit request to the referee"""
    if emitter:
        message = struct.pack('iii', robot_id, MSG_DEPOSIT, 0)
        emitter.send(message)
        print(f"Robot {robot_id} sent DEPOSIT request")

# Example simple movement + fake collection
step_count = 0
collection_cooldown = 0

while robot.step(timestep) != -1:
    step_count += 1

    # Read sensors
    ps_values = [sensor.getValue() for sensor in ps]
    right_obstacle = ps_values[0] > 80.0 or ps_values[1] > 80.0 or ps_values[2] > 80.0
    left_obstacle  = ps_values[5] > 80.0 or ps_values[6] > 80.0 or ps_values[7] > 80.0

    # Simple obstacle avoidance
    left_speed, right_speed = MAX_SPEED, MAX_SPEED
    if left_obstacle:
        left_speed, right_speed = MAX_SPEED, -MAX_SPEED/2
    elif right_obstacle:
        left_speed, right_speed = -MAX_SPEED/2, MAX_SPEED

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

    # Cooldown
    if collection_cooldown > 0:
        collection_cooldown -= 1

    # 🔹 Fake logic for testing:
    # Every 200 steps, attempt to collect a "green" box
    if step_count % 200 == 0 and collection_cooldown == 0:
        send_collect(ROBOT_ID, COLLECTABLE_TYPES["black"])
        collection_cooldown = 50

    # Every 500 steps, attempt a deposit
    if step_count % 500 == 0:
        send_deposit(ROBOT_ID)
