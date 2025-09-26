TIME_STEP = 32
MAP_SIZE = (1.5, 1.5)
TILE_SIZE = 0.25

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
                "size": 0.06,
            },
            "blue": {
                "color": (0, 0, 1),
                "size": 0.045,
            },
            "black": {
                "color": (0, 0, 0),
                "size": 0.03,
            },
            "gold": {
                "color": (1, 0.84, 0),  # shiny yellow
                "size": 0.05,
            }
        }

MESSAGE_TYPES = {
    "COLLECT": 1,
    "DEPOSIT": 2,
    "OTHER": 99
}