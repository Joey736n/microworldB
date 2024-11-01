# NAME(S): Joe Binette
#
# APPROACH: [WRITE AN OVERVIEW OF YOUR APPROACH HERE.]
# My approach for this project was to reuse code from the previous project, and build on top of it.
# I did this with the NavigationManager class. It uses multiple maps that represent separate, closed off sections of the entire map.
#
# Each new map is only accessible by using a portal.
# For my approach to portals, my AI avoids them entirely until the current map it is in is fully explored.
# This ensures that maps will not be duplicated because the AI can be certain if the exit portal is also in the current map.
#
# The first AI to discover an exit will use it as soon as possible. This acts as a safety net for if the second AI is unable to escape for whatever reason.
# The second AI exits when it is in the exit tile's map, has no path, and the number of turns remaining is below a certain threshold.
#
# AIs will also attempt to immediately collect goals when seen.
#
# Communication of the AI takes place through the sharing of the NavigationManager object.
# Through it, they share their known information about the state of the world.
# This information includes the maps themselves, as well as where key locations are, and whether one of them has exited.
# The AI's differing behavior is moreso dependent on which one finds the exit first, though B also has an initial movement delay to help separate their pathing.
# Key locations are used to make wiser decisions about when to to use the recorded tiles. It makes it so that the AI can easily backtrack when needed.
# Exit information allows the AIs to decide whether they should exit or not.

import navigation


class AI:
    def __init__(self, max_turns):
        """
        Called once before the sim starts. You may use this function
        to initialize any data or data structures you need.
        """
        self.max_turns = max_turns
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
        print(f"message: {msg}")

        if msg:
            self.ai_map = msg
        
		# Uses percepts to add to map.
        self.ai_map.scan(percepts)
        # Figures out which tiles to prioritize. If the current map is cleared:
		# First, if ALL maps are cleared, attempts to enter a portal that leads to a new world.
        # Second, it attempts to enter the least-used portal that has a known destination.
        self.ai_map.add_frontier()
        # Displays the map.
        self.ai_map.print_map()
        # If the number of turns is running out, the AI attempts to leave.
        if self.max_turns and self.max_turns - self.turn < 100:
            self.ai_map.exit_check()
        elif not self.max_turns:
            self.ai_map.exit_check()
        # Gets the next movement direction.
        d = self.ai_map.next_direction(percepts["X"][0])
        # If the other AI hasn't left already, its turn swaps.
        if not self.ai_map.single:
            self.ai_map.swap_bot()
        return d, self.ai_map
    
