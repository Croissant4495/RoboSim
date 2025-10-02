from controller import Supervisor
import random
import math

class MapManager:
    def __init__(self, supervisor, map_size=(10, 10)):
        self.supervisor = supervisor
        self.map_size = map_size
        self.areas_group = self.supervisor.getFromDef("AREAS_GROUP")
        self.areas = self._read_areas()
        self.obstacle_group = supervisor.getFromDef("OBSTACLE_GROUP").getField("children")
        self.obstacles = []


    def _read_areas(self):
        """Read all Area nodes inside Areas group and store metadata."""
        areas = []
        if not self.areas_group:
            return areas
        children_field = self.areas_group.getField("children")
        for i in range(children_field.getCount()):
            node = children_field.getMFNode(i)
            translation = node.getField("translation").getSFVec3f()
            def_name = node.getDef()
            if "trap" in def_name:
                zone_type = "trap"
                size = (0.1, 0.1, 0.001)
            else:
                size = node.getField("size").getSFVec3f()

                # Optional classification based on DEF name
                if "deposit" in def_name:
                    zone_type = "deposit"
                elif "start" in def_name:
                    zone_type = "start"
                elif "swamp" in def_name:
                    zone_type = "swamp"
                elif "double" in def_name:
                    zone_type = "double"                
                else:
                    zone_type = "generic"

            areas.append({
                "center": translation,
                "size": size,
                "defName": def_name,
                "type": zone_type
            })
        return areas

    def is_in_area(self, pos, area):
        """Check if pos (x,y) is inside given area box."""
        cx, cy, _ = area["center"]
        sx, sy, _ = area["size"]
        half_x, half_y = sx / 2, sy / 2
        return (cx - half_x <= pos[0] <= cx + half_x) and \
               (cy - half_y <= pos[1] <= cy + half_y)

    def get_areas_at(self, pos):
        """Return list of areas that contain pos."""
        return [a for a in self.areas if self.is_in_area(pos, a)]

    def is_restricted(self, pos, min_clearance=0.08):
        """
        Check if position is restricted.
        Restricted = inside a deposit area OR overlapping with an obstacle.
        min_clearance controls how close we allow to obstacles (default 5cm).
        """
        # 1) Area restriction
        if any(a for a in self.get_areas_at(pos) if a["type"] in ("deposit", "trap")):
            return True

        # 2) Obstacle restriction
        for obs in self.obstacles:
            ox, oy = obs["pos"]
            dist = math.sqrt((pos[0] - ox) ** 2 + (pos[1] - oy) ** 2)
            if dist < (obs["radius"] + min_clearance):
                return True

        return False
    
    def spawn_random_obstacle(self, max_attempts=50):
        shapes = ["box", "cylinder", "cone"]
        colors = [
            (1, 0, 0),   # red
            (0, 1, 0),   # green
            (0, 0, 1),   # blue
            (0.5, 0.5, 0.5),  # gray,
            (0.6667, 0.6667, 0.5)
        ]

        shape = random.choice(shapes)
        color = colors[-1]
        size = random.uniform(0.02, 0.03)
        height = random.uniform(0.1, 0.125)

        for _ in range(max_attempts):
            x = random.uniform((-self.map_size[0] / 2) + size , (self.map_size[0] / 2) - size)
            y = random.uniform((-self.map_size[1] / 2) + size, (self.map_size[1] / 2) - size)

            if not self.is_restricted((x, y)):
                break
        

        obj_name = f"OBSTACLE_{random.randint(1000,9999)}"

        if shape == "box":
            geometry = f"Box {{ size {size} {size} {height} }}"
            bounding = geometry
        elif shape == "cylinder":
            geometry = f"Cylinder {{ radius {size} height {height} }}"
            bounding = geometry
        elif shape == "cone":
            geometry = f"Cone {{ bottomRadius {size} height {height} subdivision 32 }}"
            bounding = f"Cylinder {{ radius {size} height {height} }}"  # <--- use cylinder for bounding
        else:
            geometry = f"Box {{ size {size} {size} {height} }}"
            bounding = geometry

        node_string = f"""
        DEF {obj_name} Solid {{
        translation {x} {y} {height/2}
        name "{obj_name}"
        children [
            Shape {{
            appearance PBRAppearance {{
                baseColor {color[0]} {color[1]} {color[2]}
                roughness 1
                metalness 0
            }}
            geometry {geometry}
            }}
        ]
        boundingObject {bounding}
        
        }}
        """

        self.obstacle_group.importMFNodeFromString(-1, node_string)
        
        self.obstacles.append({
            "name": obj_name,
            "pos": (x, y),
            "radius": size   # for box/cylinder/cone, use size as an approximate radius
        })

        return {
            "name": obj_name,
            "position": (x, y),
            "shape": shape,
            "color": color
        }