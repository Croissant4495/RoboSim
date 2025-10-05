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

    def get_inventory_string(self):
        """Return a string of colored blocks for inventory display."""
        # Map item types to emoji or short labels
        symbol_map = {
            "black": "[B]",
            "red": "[R]",
            "blue": "[U]",
            "green": "[G]"
        }
        return "".join(symbol_map.get(item["type"], "⬜") for item in self.collected_items)

    def display_status(self, score):
        """Show score and inventory as labels near top of screen."""
        if self.robot_id == 0:
            x, y = 0.03, 0.03
            color = 0x0000FF
        else:
            x, y = 0.9, 0.03
            color = 0xFF0000

        self.supervisor.setLabel(
            self.robot_id * 2,  # unique id for score
            f"Score: {score}",
            x, y, 0.1, color, 0.0, "Tahoma"
        )

        # Inventory label (slightly lower)
        self.supervisor.setLabel(
            self.robot_id * 2 + 1,  # unique id for inventory
            self.get_inventory_string(),
            x, y + 0.05, 0.08, color, 0.0, "Tahoma"
        )

    def classify_color(rgb):
            r, g, b = rgb
            # Very basic threshold logic, you can refine this
            if r > 200 and g > 200 and b < 100:
                return "deposit"   # yellow deposit tile
            elif r < 50 and g < 50 and b < 50:
                return "black"
            elif r > 150 and g < 80 and b < 80:
                return "red"
            elif g > 150 and r < 80 and b < 80:
                return "green"
            elif b > 150 and r < 80 and g < 80:
                return "blue"
            else:
                return "unknown"
    
    #TODO Actual implementation 
    def get_color_readings(self):
        """
        Returns (left_color, right_color) as strings.
        Possible values: 'deposit', 'black', 'red', 'green', etc.
        """
        return "deposit", "deposit"
    
        left_color = "unknown"
        right_color = "unknown"

        if self.left_sensor:
            image = self.left_sensor.getImage()
            rgb = (
                self.left_sensor.imageGetRed(image, 1, 0, 0),
                self.left_sensor.imageGetGreen(image, 1, 0, 0),
                self.left_sensor.imageGetBlue(image, 1, 0, 0),
            )
            left_color = self.classify_color(rgb)

        if self.right_sensor:
            image = self.right_sensor.getImage()
            rgb = (
                self.right_sensor.imageGetRed(image, 1, 0, 0),
                self.right_sensor.imageGetGreen(image, 1, 0, 0),
                self.right_sensor.imageGetBlue(image, 1, 0, 0),
            )
            right_color = self.classify_color(rgb)
        print(f"Colors: {left_color} , {right_color}")
        return left_color, right_color