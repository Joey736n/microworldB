import string

# Class that bundles together coordinate pairs.
class Coordinates(object):
    def __init__(self, x: int, y: int):
         self.x: int = x # Horizontal coordinate
         self.y: int = y # Vertical coordinate
    
    def __str__(self):
        return f"({self.x}, {self.y})"
         
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

# Abstract class that is a parent to all tiles.
# Defines behavior for how they are displayed on the map.
class Tile(object):
    def __init__(self):
        self.tile_marker: str = "T" # tile_marker is the symbol that will be used when displayed on the map.
        
    def __str__(self):
        return self.tile_marker

# Fills in positions on the map that have not been seen, but are known to exist.
# Adjacent grass tiles become frontiers.
class Unknown_Tile(Tile):
    def __init__(self):
        self.tile_marker: str = "?"
        #❔

# Represents an area that the AI cannot walk on.
class Wall_Tile(Tile):
    def __init__(self):
        self.tile_marker: str = "w"
        #⬛
        
# A walkable map tile.
# Contains a visited properties to prevent remapping the same position.
class Grass_Tile(Tile):
    def __init__(self, visited=False):
        self.tile_marker: str = "g"
        self.frontier = False
        #⬜
        
    def __str__(self):
        if not self.frontier:
            return self.tile_marker
        return "f"
        
# The exit, and ultimate objective of the AI.
class Exit_Tile(Grass_Tile):
    def __init__(self):
        self.tile_marker: str = "r"
        self.frontier = False
        #🟥
        
class Goal_Tile(Grass_Tile):
    def __init__(self, digit):
        self.tile_marker = digit
        self.frontier = False
        
class Teleporter_Tile(Grass_Tile):
    def __init__(self, color):
        self.tile_marker = color
        self.frontier = False
        
# Keeps track of where everything is.
# Expands and changes based on the AI's discoveries.
class Map(object):
    def __init__(self):
        self.map_height: int = 1
        self.map_width: int = 1
        self.tile_map = [[Unknown_Tile()]] # This is the 2D array that stores the bulk of mapping information.

	# Expands self.tile_map along the x axis in either direction.
    # Negative values expand West, positive values expand East.
    def expand_x(self, distance: int, current_bot_position):
        for index, row in enumerate(self.tile_map):
            # Case for postive values. Expands the map East by {distance} tiles.
            if distance > 0:
                self.tile_map[index] = row + ([Unknown_Tile()] * distance)
            # Case for negative values. Expands the map West by {distance} tiles.
            elif distance < 0:
                self.tile_map[index] = ([Unknown_Tile()] * abs(distance)) + row
        # Corrects the robot's position if the map was expanded on the West.
        if distance < 0:
            current_bot_position.x += abs(distance)
        self.map_width += abs(distance)

	# Expands self.tile_map along the y axis in either direction.
    # Negative values expand North, positve values expand South.
    def expand_y(self, distance: int, current_bot_position):
        new_space = []
        # Prepares the tiles that will be added to the map.
        for i in range(abs(distance)):
            new_space.append([Unknown_Tile()] * self.map_width)
        # Adds tiles at the south if distance is positive.
        if distance > 0:
            self.tile_map += new_space
        # Adds tiles at the north if distance is negative.
        elif distance < 0:
            self.tile_map = new_space + self.tile_map
            # Corrects the robots position if map was expanded north.
            current_bot_position.y += abs(distance)
        self.map_height += abs(distance)
    
	# Prints the map in an easy to read format.
    def print_map(self):
        for y in self.tile_map:
            for x in y:
                print(x, end="")
            print()
            
	# Returns a new tile based on characters found in the percepts.
    def charToTile(self, character):
        if character == "g":
            return Grass_Tile()
        elif character == "w":
            return Wall_Tile()
        elif character == "r":
            return Exit_Tile()
        elif character in string.digits:
            return Goal_Tile(character)
        elif character in "obpy":
            return Teleporter_Tile(character)
    
    # Adds newly discovered tiles to the map. This one's a whopper.
    def scan(self, percepts, current_bot_position):
        robot_x = current_bot_position.x
        robot_y = current_bot_position.y
        self.tile_map[robot_y][robot_x] = self.charToTile(percepts["X"][0])
        # x_distance are the distance from where the robot is to the edge of the map.
        north_distance = robot_y
        east_distance = (self.map_width - 1) - robot_x
        south_distance = (self.map_height - 1) - robot_y
        west_distance = robot_x
        # Checks if expanding North is necessary, and expands if needed.
        if len(percepts["N"]) > north_distance:
            self.expand_y(north_distance - len(percepts["N"]))
        # Places tiles in a row starting from the robot's position.
        tile_placement_offset = 0
        for i in percepts["N"]:
            tile_placement_offset -= 1
            if isinstance(self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x], Unknown_Tile):
                self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x] = self.charToTile(i)
        # Checks if expanding East is necessary, and expands if needed.
        if len(percepts["E"]) > east_distance:
            self.expand_x(len(percepts["E"]) - east_distance)
        # Places tiles in a row starting from the robot's position.
        tile_placement_offset = 0
        for i in percepts["E"]:
            tile_placement_offset += 1
            if isinstance(self.tile_map[current_bot_position.y][current_bot_position.x + tile_placement_offset], Unknown_Tile):
                self.tile_map[current_bot_position.y][current_bot_position.x + tile_placement_offset] = self.charToTile(i)
        # Checks if expanding South is necessary, and expands if needed.
        if len(percepts["S"]) > south_distance:
            self.expand_y(len(percepts["S"]) - south_distance)
        # Places tiles in a row starting from the robot's position.
        tile_placement_offset = 0
        for i in percepts["S"]:
            tile_placement_offset += 1
            if isinstance(self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x], Unknown_Tile):
                self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x] = self.charToTile(i)
        # Checks if expanding West is necessary, and expands if needed.
        if len(percepts["W"]) > west_distance:
            self.expand_x(west_distance - len(percepts["W"]))
        # Places tiles in a row starting from the robot's position.
        tile_placement_offset = 0
        for i in percepts["W"]:
            tile_placement_offset -= 1
            if isinstance(self.tile_map[current_bot_position.y][current_bot_position.x + tile_placement_offset], Unknown_Tile):
                self.tile_map[current_bot_position.y][current_bot_position.x + tile_placement_offset] = self.charToTile(i)
                
	# Checks grass tiles to see if they qualify as frontiers. Changes their status based on result.
    def add_frontier(self):
        for y, row in enumerate(self.tile_map):
            for x, tile in enumerate(row):
                if isinstance(tile, Grass_Tile):
                    if (isinstance(self.tile_map[y-1][x], Unknown_Tile)
                    or isinstance(self.tile_map[y][x+1], Unknown_Tile)
                    or isinstance(self.tile_map[y+1][x], Unknown_Tile)
                    or isinstance(self.tile_map[y][x-1], Unknown_Tile)):
                        tile.frontier = True
                    else:
                        tile.frontier = False

    # Returns a list containing the path to the nearest frontier tile.
    def discover(self, current_bot_position):
        previous_coords = {} # Keeps track of the previous tiles the search has seen alongside their coordinates.
        coord_path = [] # The list of coordinates that lead to a frontier.
        coord_queue = [Coordinates(current_bot_position.x, current_bot_position.y)] # The coordinates that will be checked and expanded from.
        previous_coords[self.tile_map[current_bot_position.y][current_bot_position.x]] = None # Since the search starts from where the robot is, None indicates that it is not expanded from any tile.
        while coord_queue:
            current_coords = coord_queue.pop(0) # Takes the coordinates from the front of the queue.
            # If those coordinates are at a frontier tile, the loop is exited with the current coords still saved.
            if isinstance(self.tile_map[current_coords.y][current_coords.x], Grass_Tile) and self.tile_map[current_coords.y][current_coords.x].frontier:
                break
            # The rest of the code in the loop adds neighboring tiles to the queue, and records them in previous_coords.
            next_coords = Coordinates(current_coords.x, current_coords.y - 1)
            if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
                coord_queue.append(next_coords)
                previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
            next_coords = Coordinates(current_coords.x + 1, current_coords.y)
            if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
                coord_queue.append(next_coords)
                previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
            next_coords = Coordinates(current_coords.x, current_coords.y + 1)
            if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
                coord_queue.append(next_coords)
                previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
            next_coords = Coordinates(current_coords.x - 1, current_coords.y)
            if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
                coord_queue.append(next_coords)
                previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
        
		# Uses previous_coords to trace the path from the frontier backwards to the robot.
        while current_coords:
            coord_path.append(current_coords)
            current_coords = previous_coords[self.tile_map[current_coords.y][current_coords.x]]

        coord_path = coord_path[::-1] # reverses coord_path because it's backwards.
        directions = []
        # iterates through coord_path 2 elements at a time, and creates directions using their differences.
        for coord1, coord2 in zip(coord_path, coord_path[1:]):
            if coord1.y == coord2.y + 1:
                directions.append("N")
            elif coord1.x == coord2.x - 1:
                directions.append("E")
            elif coord1.y == coord2.y - 1:
                directions.append("S")
            else:
                directions.append("W")
        return directions
    
class WorldCoordinates(Coordinates):
    def __init__(self, world: int, x: int, y: int):
        super(x, y)
        self.world = world

class NavigationManager(object):
    def __init__(self):
        self.NUM_BOTS = 2
        self.bot_coordinates = []
        for i in range(self.NUM_BOTS):
            self.bot_coordinates.append(WorldCoordinates(0, 0, 0))
        self.current_bot = 0
        self.maps = [Map()]
        b_portal_location = None
        o_portal_location = None
        p_portal_location = None
        y_portal_location = None
        exit_tile_location = None