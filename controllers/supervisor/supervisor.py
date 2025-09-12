from controller import Supervisor

TIME_STEP = 32

class ObjectManager:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.root = supervisor.getRoot()
        self.children = self.root.getField("children")
        self.instances = {}
        self.counter = 0

    def spawn_box(self, position=(0, 0, 0.1), color=(1, 0, 0)):
        """Spawn a colored box at given position"""
        self.counter += 1
        obj_name = f"BOX_{self.counter}"

        node_string = f"""
        DEF {obj_name} Solid {{
          translation {position[0]} {position[1]} {position[2]}
          children [
            Shape {{
              appearance PBRAppearance {{
                baseColor {color[0]} {color[1]} {color[2]}
                roughness 1
                metalness 0
              }}
              geometry Box {{
                size 0.1 0.1 0.1
              }}
            }}
          ]
          boundingObject Box {{ size 0.1 0.1 0.1 }}
          physics Physics {{}}
        }}
        """

        self.children.importMFNodeFromString(-1, node_string)
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


# Supervisor setup
robot = Supervisor()
manager = ObjectManager(robot)

i = 0
spawned_box = manager.spawn_box(position=(0.5, 0, 0.05), color=(0, 0, 1))  # spawn blue box

while robot.step(TIME_STEP) != -1:
    if i == 100:  # after 100 steps, spawn another box
        manager.spawn_box(position=(1, 0, 0.05), color=(0, 1, 0))

    if i == 200:  # after 200 steps, remove the first box
        manager.despawn_box(spawned_box)

    if i % 50 == 0:  # every 50 steps, print tracked instances
        print("Tracked objects:", manager.list_instances())

    i += 1
