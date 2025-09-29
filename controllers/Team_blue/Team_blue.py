from controller import Robot
from CustomBot import *

# Create the Robot instance
robot = Robot()
ROBOT_ID = 0  # 0 = blue, 1 = red

# Wrap with our API
myRobot = CustomBot(robot, ROBOT_ID)

collect_types = ["red", "blue", "black"]
collect_index = 0  # keeps track of which type to send

# Simple test loop
step_count = 0
collection_cooldown = 0

while robot.step(myRobot.timestep) != -1:
    step_count += 1

    # --- Simple obstacle avoidance using distance sensors ---
    distances = myRobot.read_distances()
    left_obstacle = distances["left"] > 80.0
    right_obstacle = distances["right"] > 80.0

    left_speed, right_speed = MAX_SPEED, MAX_SPEED
    if left_obstacle:
        left_speed, right_speed = MAX_SPEED, -MAX_SPEED / 2
    elif right_obstacle:
        left_speed, right_speed = -MAX_SPEED / 2, MAX_SPEED

    myRobot.set_speed(left_speed, right_speed)

    # --- Collect cooldown ---
    if collection_cooldown > 0:
        collection_cooldown -= 1

    # 🔹 Fake logic for testing
    # Every 200 steps, send COLLECT message
    if step_count % 200 == 0 and collection_cooldown == 0:
        collect_type = collect_types[collect_index]
        myRobot.send_message(myRobot.MSG_COLLECT, myRobot.COLLECTABLE_TYPES[collect_type])
        print(f"Robot {ROBOT_ID} sent COLLECT request for type {collect_type}")

        collect_index = (collect_index + 1) % len(collect_types)
        collection_cooldown = 50

    # Every 500 steps, send DEPOSIT message
    if step_count % 500 == 0:
        myRobot.send_message(myRobot.MSG_DEPOSIT, 0)
        print(f"Robot {ROBOT_ID} sent DEPOSIT request")