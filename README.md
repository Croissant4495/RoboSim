# RoboSim

The RoboSim is a **simulation competition environment**
inspired by RoboCup-style challenges. The goal is to program a robot
that can **collect items, avoid traps, and deposit them into scoring
zones**.

This platform is designed for intermediate to advanced programmers,
focusing on strategy, navigation, and interaction with a
**referee-supervised world**.

The competition runs inside [Webots](https://cyberbotics.com/) and uses
a **CustomBot API** that simplifies robot programming. Teams only need
to implement their robot's logic, while the referee enforces the rules.

------------------------------------------------------------------------

## Quick Start

1.  Install **Python 3.9+**\
2.  Install **Webots R2023b or newer**\
3.  Clone this repository and extract it\
4.  Open `worlds/game_world.wbt` in Webots\
5.  Load an example controller from `/controllers/team_blue` or
    `/controllers/team_red`

------------------------------------------------------------------------

## Documentation

-   **CustomBot API** -- wrapper around Webots devices (motors, sensors,
    comms)\
-   **Referee** -- supervisor that validates collects, deposits, and
    scoring\
-   **Config** -- scoring rules and collectable definitions in
    `/utils/config.py`

------------------------------------------------------------------------

## Robot Programming

Teams write strategies using only the **CustomBot API**:

``` python
from CustomBot import CustomBot

bot = CustomBot(ROBOT_ID=0)

while bot.run_sim() != -1:
    distances = bot.read_distances()
    bot.set_speed(3.0, 3.0)

    # Example: try to collect red item
    bot.send_message(bot.MSG_COLLECT, bot.COLLECTABLE_TYPES["red"])
```

------------------------------------------------------------------------

## Communication

-   📢 Announcements: GitHub Issues / Discussions\
-   💬 Community: Discord server (link *TBD*)\
-   📖 Rules: Included in *TBA*
