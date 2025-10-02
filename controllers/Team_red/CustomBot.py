from controller import Robot
import math
import struct

# Constants
MAX_SPEED = 6.28

# Message type constants (match referee)
MSG_DEPOSIT = 1
MSG_COLLECT = 2
MSG_TIMER = 3

# Example: map colors/types to integers
# (this must match your utils.config SCORING_RULES)
COLLECTABLE_TYPES = {
    "red": 0,
    "blue": 1,
    "black": 2
}

class CustomBot:
    def __init__(self, ROBOT_ID):
        self.robot = Robot()
        self.robot_id = ROBOT_ID
        self.timestep = int(self.robot.getBasicTimeStep())

        self.emitter = self.robot.getDevice("emitter")
        self.receiver = self.robot.getDevice("receiver")
        self.receiver.enable(self.timestep)

        self.gps = self.robot.getDevice("gps")
        self.gps.enable(self.timestep)

        self.compass = self.robot.getDevice("inertial_unit")
        self.compass.enable(self.timestep)

        self.distance_left = self.robot.getDevice("leftd")
        self.distance_left.enable(self.timestep)
        self.distance_right = self.robot.getDevice("rightd")
        self.distance_right.enable(self.timestep)
        self.distance_front = self.robot.getDevice("frontd")
        self.distance_front.enable(self.timestep)
        self.distance_back = self.robot.getDevice("backd")
        self.distance_back.enable(self.timestep)

        self.status_led = self.robot.getDevice("led9")
        self.led_state = 0

        self.color_right = self.robot.getDevice('camera1')
        self.color_right.enable(self.timestep)
        self.color_left = self.robot.getDevice('camera2')
        self.color_left.enable(self.timestep)

        self.right_motor = self.robot.getDevice("wheel1 motor")
        self.left_motor = self.robot.getDevice("wheel2 motor")

        self.left_motor.setPosition(float("+inf"))
        self.right_motor.setPosition(float("+inf"))

        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)


    def set_speed(self, left, right):
        """Set wheel speeds."""
        self.left_motor.setVelocity(left)
        self.right_motor.setVelocity(right)

    def get_position(self):
        """Return GPS (x, y)."""
        pos = self.gps.getValues()
        return [pos[0], pos[1]]

    def get_orientation(self):
        """Return compass heading in radians."""
        north = self.compass.getValues()
        rad = math.atan2(north[0], north[1])
        return rad

    def read_distances(self):
        """Return dict of all distance sensor readings."""
        return {
            "left": self.distance_left.getValue(),
            "right": self.distance_right.getValue(),
            "front": self.distance_front.getValue(),
            "back": self.distance_back.getValue()
        }

    def send_message(self, msg_type, data):
        """Send raw message to supervisor/referee."""
        message = struct.pack('iii', self.robot_id, msg_type, data)
        self.emitter.send(message)

    def receive_message(self):
        """Check for a message from supervisor/referee."""
        if self.receiver.getQueueLength() > 0:
            msg = self.receiver.getData()
            self.receiver.nextPacket()
            return msg
        return None

    def toggle_led(self):
        self.led_state = not self.led_state
        self.status_led.set(self.led_state)

    def get_time(self):
        '''Send a time request to supervisor and return the current time'''
        self.send_message(MSG_TIMER, 0)
        while True:
            time = self.receive_message()
            return time if time else None

    def wait(self, seconds):
        counter = 0
        while counter < (seconds / self.timestep):
            self.robot.step(self.timestep)
            counter += 1

    def run_sim(self):
        return self.robot.step(self.timestep)

    
    
            

