from controller import Supervisor
import random

class CollectableManager:
    def __init__(self, supervisor, map_manager):
        self.supervisor = supervisor
        self.map_manager = map_manager
        self.root = supervisor.getRoot()
        self.children = self.root.getField("children")
        self.instances = {}
        self.counter = 0
        self.box_size = 0.05

        # Create a parent Group node to hold all collectables
        group_def = "COLLECTABLES_GROUP"
        node_string = f"DEF {group_def} Group {{ children [ ] }}"
        self.children.importMFNodeFromString(-1, node_string)

        # Store reference to group's children field
        self.group_node = self.supervisor.getFromDef(group_def)
        self.group_children = self.group_node.getField("children")
        

    def spawn_box(self, position=(0, 0), color=(1, 0, 0)):
        """Spawn a colored box at given position"""
        self.counter += 1
        obj_name = f"BOX_{self.counter}"

        node_string = f"""
			DEF {obj_name} Collectable {{
			translation {position[0]} {position[1]} 0.0015
			color {color[0]} {color[1]} {color[2]}
			size {self.box_size} {self.box_size} 0.0015
            solidName "{obj_name}_solid"
			}}
		"""

        self.group_children.importMFNodeFromString(-1, node_string)
        self.instances[obj_name] = {
            "position": position,
            "color": color
        }
        return obj_name

    def despawn_box(self, obj_name):
        """Remove a box by its name (DEF name)."""
        if obj_name in self.instances:
            node = self.supervisor.getFromDef(obj_name)
            if node:
                node.remove()
            del self.instances[obj_name]

    def list_instances(self):
        return list(self.instances.keys())
    
    def get_nearby_object(self, position, radius=0.1):
        """Return the name of the first object within `radius` of position, or None."""
        for name, data in self.instances.items():
            px, py = data["position"]
            dx = px - position[0]
            dy = py - position[1]
            dist = (dx**2 + dy**2) ** 0.5
            if dist <= radius:
                return name
        return None
    
    def spawn_random_box(self, color=(1, 0, 0), min_distance=0.1, max_attempts=50):
        """Spawn a box at a random free location inside map boundaries without crossing edges."""
        half_w, half_h = self.map_manager.map_size[0] / 2, self.map_manager.map_size[1] / 2
        margin = self.box_size / 2.0

        for _ in range(max_attempts):
            x = random.uniform(-half_w + margin, half_w - margin)
            y = random.uniform(-half_h + margin, half_h - margin)

            if not self.get_nearby_object((x, y), radius=min_distance) and not self.map_manager.is_restricted((x, y)):
                return self.spawn_box((x, y), color)

        print("[WARN] Could not find free spot after attempts")
        return None
    

    
