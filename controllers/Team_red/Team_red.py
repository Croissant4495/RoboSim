# from controller import Robot
# import struct
#
# # Create the Robot instance
# robot = Robot()
#
# # Get the simulation timestep
# timestep = int(robot.getBasicTimeStep())
#
# # Initialize motors
# left_motor = robot.getDevice('left wheel motor')
# right_motor = robot.getDevice('right wheel motor')
# left_motor.setPosition(float('inf'))  # Set to velocity control mode
# right_motor.setPosition(float('inf'))
# left_motor.setVelocity(0.0)
# right_motor.setVelocity(0.0)
#
# # Initialize proximity sensors (8 sensors around the e-puck)
# ps = []
# ps_names = [
#     'ps0', 'ps1', 'ps2', 'ps3',
#     'ps4', 'ps5', 'ps6', 'ps7'
# ]
#
# for name in ps_names:
#     sensor = robot.getDevice(name)
#     sensor.enable(timestep)
#     ps.append(sensor)
#
# # Initialize emitter for communication with supervisor
# emitter = robot.getDevice('emitter')
# if emitter is None:
#     print("Warning: No emitter device found")
#
# # Robot identification (0 for blue team, 1 for red team)
# ROBOT_ID = 1  # Red team
#
# # Base speed of the robot
# MAX_SPEED = 6.28  # rad/s (e-puck max wheel speed)
#
#
# def send_score_message(robot_id, score_increment=1):
#     """Send a message to supervisor indicating a score should be added"""
#     if emitter:
#         # Message format: [robot_id, message_type, score_increment]
#         # message_type: 1 = score update
#         message = struct.pack('iii', robot_id, 1, score_increment)
#         emitter.send(message)
#         print(f"Robot {robot_id} sent score message: +{score_increment}")
#
#
# # Simple collection detection (you'll want to improve this)
# last_position = [0, 0]
# collection_cooldown = 0
# step_count = 0
#
# while robot.step(timestep) != -1:
#     step_count += 1
#
#     # Read sensor values
#     ps_values = [sensor.getValue() for sensor in ps]
#
#     # Simple obstacle detection
#     right_obstacle = ps_values[0] > 80.0 or ps_values[1] > 80.0 or ps_values[2] > 80.0
#     left_obstacle = ps_values[5] > 80.0 or ps_values[6] > 80.0 or ps_values[7] > 80.0
#
#     # Default: go straight
#     left_speed = MAX_SPEED
#     right_speed = MAX_SPEED
#
#     # Avoid obstacle
#     if left_obstacle:
#         # Turn right
#         left_speed = MAX_SPEED
#         right_speed = -MAX_SPEED / 2
#     elif right_obstacle:
#         # Turn left
#         left_speed = -MAX_SPEED / 2
#         right_speed = MAX_SPEED
#
#     # Apply wheel speeds
#     left_motor.setVelocity(left_speed)
#     right_motor.setVelocity(right_speed)
#
#     # Cooldown for collection detection
#     if collection_cooldown > 0:
#         collection_cooldown -= 1
#
#     # Simple collection simulation (replace with actual collection logic)
#     # For now, we'll send a score message every 250 steps as a test (different from blue)
#     if step_count % 250 == 0 and collection_cooldown == 0:
#         send_score_message(ROBOT_ID, 1)
#         collection_cooldown = 50  # Prevent spam