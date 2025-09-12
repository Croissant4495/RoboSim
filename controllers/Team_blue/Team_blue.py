from controller import Robot

# Create the Robot instance
robot = Robot()

# Get the simulation timestep
timestep = int(robot.getBasicTimeStep())

# Initialize motors
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))   # Set to velocity control mode
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Initialize proximity sensors (8 sensors around the e-puck)
ps = []
ps_names = [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4', 'ps5', 'ps6', 'ps7'
]

for name in ps_names:
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    ps.append(sensor)

# Base speed of the robot
MAX_SPEED = 6.28  # rad/s (e-puck max wheel speed)

while robot.step(timestep) != -1:
    # Read sensor values
    ps_values = [sensor.getValue() for sensor in ps]

    # Simple obstacle detection
    right_obstacle = ps_values[0] > 80.0 or ps_values[1] > 80.0 or ps_values[2] > 80.0
    left_obstacle = ps_values[5] > 80.0 or ps_values[6] > 80.0 or ps_values[7] > 80.0

    # Default: go straight
    left_speed = MAX_SPEED
    right_speed = MAX_SPEED

    # Avoid obstacle
    if left_obstacle:
        # Turn right
        left_speed = MAX_SPEED
        right_speed = -MAX_SPEED / 2
    elif right_obstacle:
        # Turn left
        left_speed = -MAX_SPEED / 2
        right_speed = MAX_SPEED

    # Apply wheel speeds
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
