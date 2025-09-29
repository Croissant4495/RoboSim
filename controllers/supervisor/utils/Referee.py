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
        self.sim_time = 0
        self.deposit_states = {rid: {"in_progress": False, "start_time": None, "start_pos": None}
                               for rid in robots_manager.robots}
        
        self.collect_states = {rid: {"in_progress": False, "start_time": None, "start_pos": None, "claimed_type": None}
                                for rid in robots_manager.robots}

    def update(self):
        self.process_messages()
        self.check_traps()
        self.check_deposits()
        self.check_collects()
        self.sim_time += TIME_STEP

    def process_messages(self):
        """Process robot messages like deposit/collect"""
        messages = self.robots_manager.process_messages()
        for robot_id, msg_type, data in messages:
            if msg_type == 1:  # deposit
                self.start_deposit(robot_id)
            elif msg_type == 2:  # collect
                self.start_collect(robot_id, data)

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
    
    # ____________ DEPOSITING ____________
    
    def start_deposit(self, robot_id):
        robot = self.robots_manager.robots[robot_id]
        pos = robot.get_position()
        if not self.validate_deposit(robot_id):
            return

        self.deposit_states[robot_id]["in_progress"] = True
        self.deposit_states[robot_id]["start_time"] = self.sim_time
        self.deposit_states[robot_id]["start_pos"] = pos

        print(f"⏳ Robot {robot_id} started deposit attempt...")
    
    def validate_deposit(self, robot_id):
        robot = self.robots_manager.robots[robot_id]
        pos = robot.get_position()
        areas = self.map_manager.get_areas_at(pos)

        # --- 1. Ensure robot is inside a deposit area ---
        in_deposit = False
        for area in areas:
            if area["type"] == "deposit":
                in_deposit = True
                break
        
        # Ensure robot sees deposit with both color sensors
        color1, color2 = robot.get_color_readings()
        sees_deposit = (color1 == "deposit" and color2 == "deposit")
        if not in_deposit or not sees_deposit:
            print(f"Robot {robot_id} failed to deposit!")
            return False
        return True
        
    
    def handle_deposit(self, robot_id):
        robot = self.robots_manager.robots[robot_id]

        if self.validate_deposit(robot_id):
            # --- Get robot inventory ---
            counts = robot.get_inventory_counts()
            gained = 0

            # --- Base scoring ---
            for item, count in counts.items():
                item_score = self.scoring_rules.get(item, 0)
                gained += item_score * count

            # --- Bonus for full set and double set ---
            double_set = True
            for item in BASE_COLLECTABLES:
                if counts[item] != 2:
                    double_set = False
                    break

            if not double_set:
                full_set = True
                for item in self.scoring_rules:
                    if (item not in counts or counts[item] == 0) and item in BASE_COLLECTABLES:
                        full_set = False
                        break

            if double_set:
                gained += (self.set_bonus * 2)
            elif full_set:
                gained += self.set_bonus

            # --- Update score and reset inventory ---
            self.scores[robot_id] += gained
            robot.clear_inventory()

            return gained
        
    def check_deposits(self):
        for rid, state in self.deposit_states.items():
            if not state["in_progress"]:
                continue

            elapsed = self.sim_time - state["start_time"]
            robot = self.robots_manager.robots[rid]
            pos = robot.get_position()

            dx = abs(pos[0] - state["start_pos"][0])
            dy = abs(pos[1] - state["start_pos"][1])
            still = dx < 0.01 and dy < 0.01  # tolerance ~1 cm

            if elapsed >= DEPOSIT_TIME * 1000:  # 3 seconds in ms
                if still:
                    gained = self.handle_deposit(rid)
                    print(f"✅ Robot {rid} deposit confirmed, +{gained}")
                else:
                    print(f"❌ Robot {rid} moved during deposit → cancelled")
                state["in_progress"] = False
    

    # ____________ COLLECTING ____________

    def start_collect(self, robot_id, claimed_type_id):
        robot = self.robots_manager.robots[robot_id]
        pos = robot.get_position()

        # Make sure there is actually something nearby
        obj_name = self.collectable_manager.get_nearby_object(pos)
        if not obj_name:
            print(f"❌ Robot {robot_id} tried to collect but nothing nearby")
            return

        self.collect_states[robot_id] = {
            "in_progress": True,
            "start_time": self.sim_time,
            "start_pos": pos,
            "claimed_type": claimed_type_id
        }

        print(f"⏳ Robot {robot_id} started collect attempt...")

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
    
    def check_collects(self):
        for rid, state in self.collect_states.items():
            if not state["in_progress"]:
                continue

            elapsed = self.sim_time - state["start_time"]
            robot = self.robots_manager.robots[rid]
            pos = robot.get_position()

            dx = abs(pos[0] - state["start_pos"][0])
            dy = abs(pos[1] - state["start_pos"][1])
            still = dx < 0.01 and dy < 0.01  # ~1cm tolerance

            if elapsed >= COLLECT_TIME * 1000:  # ✅ only 1s required
                if still:
                    success = self.handle_collect(rid, state["claimed_type"])
                    if success:
                        print(f"✅ Robot {rid} collect confirmed")
                else:
                    print(f"❌ Robot {rid} moved during collect → cancelled")

                # reset attempt
                state["in_progress"] = False
