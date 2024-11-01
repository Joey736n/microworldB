# NAME(S): Joe Binette
#
# APPROACH: [WRITE AN OVERVIEW OF YOUR APPROACH HERE.]
#     Please use multiple lines (< ~80-100 char) for you approach write-up.
#     Keep it readable. In other words, don't write
#     the whole damned thing on one super long line.
#
#     In-code comments DO NOT count as a description of
#     of your approach.

import navigation


class AI:
    def __init__(self, max_turns):
        """
        Called once before the sim starts. You may use this function
        to initialize any data or data structures you need.
        """
        self.max_turns = max_turns
        self.wait = True
        self.turn = -1

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
        print(f"message: {msg}")

        if msg:
            self.ai_map = msg

        if self.wait and percepts["X"][0] != "r":
            self.wait = False
            self.ai_map.swap_bot()
            return "U", self.ai_map
        
		# Uses percepts to add to map.
        self.ai_map.scan(percepts)
        # Figures out which tiles to prioritize.
        self.ai_map.add_frontier()
        # Displays the map.
        self.ai_map.print_map()
        # Displays diagnostic information.
        # print(f"Path to next frontier: {self.current_path}")
        # print(f"Current coordinates: {self.ai_map.robot_location}")
        # Selects the foremost direction from its current path and adjusts its position accordingly.
        if self.max_turns - self.turn < 80:
            self.ai_map.exit_check()
        d = self.ai_map.next_direction(percepts["X"][0])
        if not self.ai_map.single:
            self.ai_map.swap_bot()
        return d, self.ai_map
    
	# when the map expands, it needs to update all agent locations, plus the unique tile locations