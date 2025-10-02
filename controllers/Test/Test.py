from CustomBot import CustomBot, MAX_SPEED, MSG_COLLECT, MSG_DEPOSIT, COLLECTABLE_TYPES

# Robot setup
ROBOT_ID = 0
robot = CustomBot(ROBOT_ID)

# State variables
state = "exploring"
wait_counter = 0
step_count = 0


def get_camera_colors():
    """Read both cameras and return approximate colors"""
    try:
        img1 = robot.color_right.getImage()
        img2 = robot.color_left.getImage()

        if img1 is None or img2 is None:
            return "floor", "floor"

        # Get RGB from center pixel (cameras are 1x1)
        r1 = robot.color_right.imageGetRed(img1, 1, 0, 0)
        g1 = robot.color_right.imageGetGreen(img1, 1, 0, 0)
        b1 = robot.color_right.imageGetBlue(img1, 1, 0, 0)

        r2 = robot.color_left.imageGetRed(img2, 1, 0, 0)
        g2 = robot.color_left.imageGetGreen(img2, 1, 0, 0)
        b2 = robot.color_left.imageGetBlue(img2, 1, 0, 0)

        color1 = classify_color(r1, g1, b1)
        color2 = classify_color(r2, g2, b2)

        return color1, color2
    except:
        return "floor", "floor"


def classify_color(r, g, b):
    """Simple color classifier"""
    # Yellow trap border (check FIRST)
    if r > 200 and g > 200 and b < 100:
        return "yellow"
    # Black object
    if r < 60 and g < 60 and b < 60:
        return "black"
    # Red object (r dominant)
    if r > 150 and g < 100 and b < 100:
        return "red"
    # Blue object or trap (b dominant, not white)
    if b > 120 and b > r + 30 and b > g + 30:
        return "blue"
    # Orange deposit (r high, g medium, b low)
    if r > 200 and g > 100 and g < 200 and b < 100:
        return "orange"
    return "floor"


print(f"Robot {ROBOT_ID} starting...")

# Main loop
while robot.run_sim() != -1:
    step_count += 1

    # Read sensors
    distances = robot.read_distances()
    color1, color2 = get_camera_colors()

    # Debug: print colors every 50 steps
    if step_count % 50 == 0:
        pos = robot.get_position()
        print(f"Step {step_count}: Pos=({pos[0]:.3f},{pos[1]:.3f}) Colors={color1},{color2}")

    # Check for yellow traps - BACK OUT at an angle
    if "yellow" in [color1, color2]:
        print(f"YELLOW TRAP! Backing out at angle...")
        robot.set_speed(-MAX_SPEED, -MAX_SPEED / 2)  # Back and turn
        state = "avoiding"
        wait_counter = 20  # Brief maneuver
        continue

    # Handle states
    if state == "exploring":
        # Obstacle avoidance with distance sensors
        left_obstacle = distances["left"] > 80.0
        right_obstacle = distances["right"] > 80.0
        front_obstacle = distances["front"] > 80.0

        if front_obstacle:
            robot.set_speed(-MAX_SPEED / 2, MAX_SPEED / 2)
        elif left_obstacle:
            robot.set_speed(MAX_SPEED, -MAX_SPEED / 2)
        elif right_obstacle:
            robot.set_speed(-MAX_SPEED / 2, MAX_SPEED)
        else:
            robot.set_speed(MAX_SPEED, MAX_SPEED)

        # Check for collectables (if EITHER camera sees black, red, or blue)
        if color1 in ["black", "red", "blue"] or color2 in ["black", "red", "blue"]:
            # Determine which type we see
            collectable_type = None
            if color1 in ["black", "red", "blue"]:
                collectable_type = color1
            elif color2 in ["black", "red", "blue"]:
                collectable_type = color2

            if collectable_type:
                robot.set_speed(0, 0)
                pos = robot.get_position()
                type_id = COLLECTABLE_TYPES[collectable_type]
                robot.send_message(MSG_COLLECT, type_id)
                print(
                    f">>> Robot {ROBOT_ID} at ({pos[0]:.3f},{pos[1]:.3f}) sent COLLECT for {collectable_type} (type_id={type_id})")
                state = "collecting"
                wait_counter = int(1200 / robot.timestep)  # Wait 1.2 seconds to be safe

        # Check for deposit area (if EITHER camera sees orange)
        elif color1 == "orange" or color2 == "orange":
            # Move forward a bit to ensure we're fully in deposit area
            robot.set_speed(MAX_SPEED / 2, MAX_SPEED / 2)
            state = "entering_deposit"
            wait_counter = 10  # Brief forward movement

    elif state == "collecting":
        robot.set_speed(0, 0)
        wait_counter -= 1
        if wait_counter <= 0:
            # Stay stopped a bit longer to ensure we're not still over the object
            if color1 not in ["black", "red", "blue"] and color2 not in ["black", "red", "blue"]:
                print("Collection complete, resuming exploration")
                state = "exploring"
            else:
                # Still over object, wait a bit more
                wait_counter = 10

    elif state == "entering_deposit":
        # Moving forward into deposit area
        wait_counter -= 1
        if wait_counter <= 0:
            # Now stop and deposit
            robot.set_speed(0, 0)
            robot.send_message(MSG_DEPOSIT, 0)
            print(f">>> Robot {ROBOT_ID} sent DEPOSIT")
            state = "depositing"
            wait_counter = int(3200 / robot.timestep)

    elif state == "avoiding":
        # Continue the avoidance maneuver
        wait_counter -= 1
        if wait_counter <= 0:
            print("Trap avoided, resuming exploration")
            state = "exploring"

    elif state == "depositing":
        robot.set_speed(0, 0)
        wait_counter -= 1
        if wait_counter <= 0:
            print("Deposit complete, resuming exploration")
            state = "exploring"