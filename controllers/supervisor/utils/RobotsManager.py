import struct
from utils.RobotManager import RobotManager
from utils.config import *

class RobotsManager:
    def __init__(self, supervisor, robot_defs):
        """
        :param supervisor: Webots Supervisor instance
        :param robot_defs: dict {robot_id: def_name}
        :param receiver: Webots receiver device
        """
        self.supervisor = supervisor
        self.receiver = supervisor.getDevice("receiver")
        if self.receiver:
            self.receiver.enable(TIME_STEP)
        else:
            print("Warning: No receiver device found")

        # Track per-robot managers
        self.robots = {
            rid: RobotManager(supervisor, def_name, rid)
            for rid, def_name in robot_defs.items()
        }

    def process_messages(self):
        """
        Returns list of (robot_id, message_type, data)
        Supervisor decides what to do with them.
        """
        results = []
        if not self.receiver:
            return results

        while self.receiver.getQueueLength() > 0:
            try:
                message = bytes(self.receiver.getBytes())
                robot_id, message_type, data = struct.unpack('iii', message)

                if robot_id in self.robots:
                    self.robots[robot_id].set_last_message((message_type, data))
                    results.append((robot_id, message_type, data))

            except Exception as e:
                print(f"Error processing message: {e}")

            self.receiver.nextPacket()

        return results
    
    def get_robot_position(self, robot_id):
        if robot_id in self.robots:
            return self.robots[robot_id].get_position()
        return None
    
    def get_robot_color(self, robot_id):
        if robot_id in self.robots:
            return self.robots[robot_id].get_color_readings()
        return None