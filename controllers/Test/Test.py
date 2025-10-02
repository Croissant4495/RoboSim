from controller import Robot
import struct

# Create the Robot instance
robot = Robot()

# Get the simulation timestep
timestep = int(robot.getBasicTimeStep())

# Initialize motors
left_motor = robot.getDevice('wheel1 motor')
right_motor = robot.getDevice('wheel2 motor')
left_motor.setPosition(float('inf'))  # velocity control mode
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Initialize emitter
emitter = robot.getDevice('emitter')
if emitter is None:
    print("Warning: No emitter device found")

camera = robot.getDevice('camera1')
camera.enable(timestep)
camera2 = robot.getDevice('camera2')
camera2.enable(timestep)

led = robot.getDevice('led9')
# Example simple movement + fake collection
step_count = 0
collection_cooldown = 0
led_status = True

while robot.step(timestep) != -1:
    step_count += 1

    if step_count % 100 == 0:
        led_status = not led_status
        print(f"LED STATUS: {led_status}")
        led.set(led_status)
