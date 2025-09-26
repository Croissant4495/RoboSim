from controller import Supervisor
from utils.config import *
from utils.utils import *

class Referee:
    def __init__(self, supervisor, robots_manager, map_manager, collectable_manager, set_bonus=0):
        self.supervisor = supervisor
        self.robots_manager = robots_manager
        self.map_manager = map_manager
        self.collectable_manager = collectable_manager
        self.scoring_rules = SCORING_RULES
        self.set_bonus = set_bonus
        self.scores = {rid: 0 for rid in robots_manager.robots}

    def update(self):
        self.process_messages()
        self.check_traps()

    def process_messages(self):
        """Process robot messages like deposit/collect"""
        messages = self.robots_manager.process_messages()
        for robot_id, msg_type, data in messages:
            if msg_type == 1:  # deposit
                gained = self.handle_deposit(robot_id)
                print(f"Robot {robot_id} deposited, gained {gained}, total {self.scores[robot_id]}")
            elif msg_type == 2:  # collect
                self.handle_collect(robot_id, data)

    def check_traps(self):
        """Check if any robot is inside a trap and apply penalty"""
        for rid, robot in self.robots_manager.robots.items():
            pos = robot.get_position()
            areas = self.map_manager.get_areas_at(pos)
            if any(a["type"] == "trap" for a in areas):
                if robot.get_inventory_counts():  # only act if carrying something
                    print(f"⚠️ Robot {rid} fell into a trap! Inventory cleared.")
                    robot.clear_inventory()


    def get_score(self, robot_id):
        return self.scores.get(robot_id, 0)
    
    def handle_deposit(self, robot_id):
        robot = self.robots_manager.robots[robot_id]
        pos = robot.get_position()
        areas = self.map_manager.get_areas_at(pos)

        # --- 1. Ensure robot is inside a deposit area ---
        in_deposit = False
        for area in areas:
            if area["type"] == "deposit":
                in_deposit = True
                break

        if not in_deposit:
            print(f"Robot {robot_id} tried to deposit outside deposit zone!")
            return 0

        # --- 2. Get robot inventory ---
        counts = robot.get_inventory_counts()
        gained = 0

        # --- 3. Base scoring ---
        for item, count in counts.items():
            item_score = self.scoring_rules.get(item, 0)
            gained += item_score * count

        # --- 4. Bonus for full set ---
        has_full_set = True
        for item in self.scoring_rules:
            if (item not in counts or counts[item] == 0) and item in BASE_COLLECTABLES:
                has_full_set = False
                break

        if has_full_set:
            gained += self.set_bonus

        # --- 5. Double zone check ---
        in_double = False
        for area in areas:
            if area["type"] == "double":
                in_double = True
                break

        if in_double:
            gained *= 2
            print(f"Robot {robot_id} deposited in double zone, score doubled!")

        # --- 6. Update score and reset inventory ---
        self.scores[robot_id] += gained
        robot.clear_inventory()

        return gained
    
    def handle_collect(self, robot_id, claimed_type_id):
        """Robot requests to collect an item of claimed type"""
        success, actual_type = self.validate_collect(robot_id, claimed_type_id)

        if not success:
            print(f"Robot {robot_id} failed to collect (claimed {claimed_type_id}, actual {actual_type})")
            return False

        # Compute score modifiers
        base_value = self.scoring_rules.get(actual_type, 0)
        value = base_value

        areas = self.map_manager.get_areas_at(self.robots_manager.get_robot_position(robot_id))
        for area in areas:
            if area["type"] == "double":
                value *= 2
            elif area["type"] == "swamp":
                value = max(1, value // 2)

        # Store in robot inventory
        robot = self.robots_manager.robots[robot_id]
        robot.add_collectable(actual_type, value)  # robot stores type only
        print(f"Robot {robot_id} collected {actual_type} worth {value} points")
        return True

    def validate_collect(self, robot_id, claimed_type_id):
        """
        Check if the robot is near an object and its claimed type matches the actual type.
        Returns (success: bool, actual_type: str or None).
        """
        robot = self.robots_manager.robots[robot_id]
        pos = robot.get_position()
        obj_name = self.collectable_manager.get_nearby_object(pos)

        if not obj_name or not robot.can_carry():
            return False, None

        actual_type = self.collectable_manager.instances[obj_name]["type"]

        if claimed_type_id == encode_type(actual_type):
            # ✅ Match → despawn object
            self.collectable_manager.despawn_box(obj_name)
            return True, actual_type

        return False, actual_type
