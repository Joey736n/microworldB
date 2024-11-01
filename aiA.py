# NAME(S): Joe Binette
#
# APPROACH: [WRITE AN OVERVIEW OF YOUR APPROACH HERE.]
#     Please use multiple lines (< ~80-100 char) for you approach write-up.
#     Keep it readable. In other words, don't write
#     the whole damned thing on one super long line.
#
#     In-code comments DO NOT count as a description of
#     of your approach.

import random
import navigation


class AI:
    def __init__(self, max_turns):
        """
        Called once before the sim starts. You may use this function
        to initialize any data or data structures you need.
        """
        self.turn = -1
        self.ai_map = navigation.NavigationManager()

    def update(self, percepts, msg):
        """
        PERCEPTS:
        Called each turn. Parameter "percepts" is a dictionary containing
        nine entries with the following keys: X, N, NE, E, SE, S, SW, W, NW.
        Each entry's value is a single character giving the contents of the
        map cell in that direction. X gives the contents of the cell the agent
        is in.

        COMAMND:
        This function must return one of the following commands as a string:
        N, E, S, W, U

        N moves the agent north on the map (i.e. up)
        E moves the agent east
        S moves the agent south
        W moves the agent west
        U uses/activates the contents of the cell if it is useable. For
        example, stairs (o, b, y, p) will not move the agent automatically
        to the corresponding hex. The agent must 'U' the cell once in it
        to be transported.

        The same goes for goal hexes (0, 1, 2, 3, 4, 5, 6, 7, 8, 9).
        """
        self.turn += 1

        if msg:
            self.ai_map = msg

# If exit is within percepts, AI ceases intelligent behavior.
        # if "r" in percepts["N"]:
        #     return "N", self.ai_map
        # if "r" in percepts["E"]:
        #     return "E", self.ai_map
        # if "r" in percepts["S"]:
        #     return "S", self.ai_map
        # if "r" in percepts["W"]:
        #     return "W", self.ai_map
        # if percepts["X"][0] == "r":
        #     return "U", self.ai_map
        
		# Uses percepts to add to map.
        self.ai_map.scan(percepts)
        # Figures out which tiles to prioritize.
        self.ai_map.add_frontier()
        # Displays the map.
        self.ai_map.print_map()
        # If the AI is out of directions to follow, it will generate a new set.
        # if not self.current_path:
        #     self.current_path = self.ai_map.discover()
        # Displays diagnostic information.
        # print(f"Path to next frontier: {self.current_path}")
        # print(f"Current coordinates: {self.ai_map.robot_location}")
        # Selects the foremost direction from its current path and adjusts its position accordingly.
        d = self.ai_map.next_direction(percepts["X"][0])
        self.ai_map.swap_bot()
        return d, self.ai_map
    
