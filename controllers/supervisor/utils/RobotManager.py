from controller import Supervisor

class RobotManager:
    def __init__(self, supervisor: Supervisor, robot_def: str, robot_id: int):
        self.supervisor = supervisor
        self.robot_node = supervisor.getFromDef(robot_def)
        if not self.robot_node:
            raise ValueError(f"Robot with DEF '{robot_def}' not found in world.")

        self.__capacity = 6
        self.robot_id = robot_id
        self.collected_items = []
        self.last_message = None

    def get_position(self):
        return self.robot_node.getPosition()

    def can_carry(self):
        return len(self.collected_items) < self.__capacity
    
    def add_collectable(self, collectable_type, value):
        if self.can_carry():
            self.collected_items.append({"type": collectable_type, "value": value})

    def remove_collectable(self, collectable_type):
        if collectable_type in self.collected_items:
            self.collected_items.remove(collectable_type)

    def clear_inventory(self):
        self.collected_items.clear()

    def get_inventory_counts(self):
        counts = {}
        for item in self.collected_items:
            item_type = item["type"]
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts

    def set_last_message(self, message):
        self.last_message = message
