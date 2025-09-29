TIME_STEP = 32
MAP_SIZE = (1.25, 1.25)
TILE_SIZE = 0.25
DEPOSIT_TIME = 3
COLLECT_TIME = 1

TYPE_ENCODING = {
    "red": 0,
    "blue": 1,
    "black": 2,
    "gold": 3
}

BASE_COLLECTABLES = ["red", "blue", "black"]

SCORING_RULES = {
    "red": 5,       # red block worth 5 points
    "blue": 10,     # blue block worth 10 points
    "black": 15,    # green block worth 15 points
    "gold": 50      # rare golden block worth 50 points
}

COLLECTABLE_PRESETS = {
            "red": {
                "color": (1, 0, 0),
                "size": 0.04,
            },
            "blue": {
                "color": (0, 0, 1),
                "size": 0.03,
            },
            "black": {
                "color": (0, 0, 0),
                "size": 0.02,
            },
            "gold": {
                "color": (1, 0.84, 0),  # shiny yellow
                "size": 0.03,
            }
        }

MESSAGE_TYPES = {
    "COLLECT": 1,
    "DEPOSIT": 2,
    "OTHER": 99
}