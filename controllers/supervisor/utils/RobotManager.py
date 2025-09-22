from controller import Supervisor

class RobotManager:
    def __init__(self, supervisor: Supervisor, robot_def: str, robot_id: int):
        self.supervisor = supervisor
        self.robot_node = supervisor.getFromDef(robot_def)
        if not self.robot_node:
            raise ValueError(f"Robot with DEF '{robot_def}' not found in world.")

        self.robot_id = robot_id
        self.collected_items = []
        self.last_message = None

    def get_position(self):
        return self.robot_node.getPosition()

    def add_collectable(self, collectable_type: str):
        self.collected_items.append(collectable_type)

    def remove_collectable(self, collectable_type: str):
        if collectable_type in self.collected_items:
            self.collected_items.remove(collectable_type)

    def set_last_message(self, message):
        self.last_message = message
