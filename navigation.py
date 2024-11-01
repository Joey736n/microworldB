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
		
# A numbered goal tile. It is identifiable on the map with a digit.
class Goal_Tile(Grass_Tile):
	def __init__(self, digit):
		self.tile_marker = digit
		self.frontier = False
		
# A teleporter tile. Identifiable on the map as o, b, p, or y.
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
		self.fully_explored: bool = False # When the map is fully explored (no more frontiers), this is set to true.

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
		# Corrects all positions on the map if the map was expanded on the West.
		if distance < 0:
			for i in bot_coordinates:
				if current_bot_position.world == i.world:
					i.x += abs(distance)
			for i in unique_tile_locations.values():
				if i and current_bot_position.world == i.world:
					i.x += abs(distance)
			if exit_location and exit_location.world == current_bot_position.world:
				exit_location.x += abs(distance)
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
			# Corrects all positions on the map if map was expanded north.
			for i in bot_coordinates:
				if current_bot_position.world == i.world:
					i.y += abs(distance)
			for i in unique_tile_locations.values():
				if i and current_bot_position.world == i.world:
					i.y += abs(distance)
			if exit_location and exit_location.world == current_bot_position.world:
				exit_location.y += abs(distance)
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
	
	# Adds newly discovered tiles to the map.
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
			self.expand_y(north_distance - len(percepts["N"]), current_bot_position)
		# Places tiles in a row starting from the robot's position.
		tile_placement_offset = 0
		for i in percepts["N"]:
			tile_placement_offset -= 1
			if isinstance(self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x], Unknown_Tile):
				self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x] = self.charToTile(i)
		# Checks if expanding East is necessary, and expands if needed.
		if len(percepts["E"]) > east_distance:
			self.expand_x(len(percepts["E"]) - east_distance, current_bot_position)
		# Places tiles in a row starting from the robot's position.
		tile_placement_offset = 0
		for i in percepts["E"]:
			tile_placement_offset += 1
			if isinstance(self.tile_map[current_bot_position.y][current_bot_position.x + tile_placement_offset], Unknown_Tile):
				self.tile_map[current_bot_position.y][current_bot_position.x + tile_placement_offset] = self.charToTile(i)
		# Checks if expanding South is necessary, and expands if needed.
		if len(percepts["S"]) > south_distance:
			self.expand_y(len(percepts["S"]) - south_distance, current_bot_position)
		# Places tiles in a row starting from the robot's position.
		tile_placement_offset = 0
		for i in percepts["S"]:
			tile_placement_offset += 1
			if isinstance(self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x], Unknown_Tile):
				self.tile_map[current_bot_position.y + tile_placement_offset][current_bot_position.x] = self.charToTile(i)
		# Checks if expanding West is necessary, and expands if needed.
		if len(percepts["W"]) > west_distance:
			self.expand_x(west_distance - len(percepts["W"]), current_bot_position)
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
		coord_queue = [Coordinates(current_bot_position.x, current_bot_position.y)] # The coordinates that will be checked and expanded from.
		previous_coords[self.tile_map[current_bot_position.y][current_bot_position.x]] = None # Since the search starts from where the robot is, None indicates that it is not expanded from any tile.
		while coord_queue:
			current_coords = coord_queue.pop(0) # Takes the coordinates from the front of the queue.
			# If those coordinates are at a frontier tile, the loop is exited with the current coords still saved.
			if isinstance(self.tile_map[current_coords.y][current_coords.x], Grass_Tile) and self.tile_map[current_coords.y][current_coords.x].frontier:
				return self.get_directions(current_coords, previous_coords)
			# The rest of the code in the loop adds neighboring tiles to the queue, and records them in previous_coords.
			next_coords = Coordinates(current_coords.x, current_coords.y - 1)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
			next_coords = Coordinates(current_coords.x + 1, current_coords.y)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
			next_coords = Coordinates(current_coords.x, current_coords.y + 1)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
			next_coords = Coordinates(current_coords.x - 1, current_coords.y)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords

		self.fully_explored = True
		return None
		
	# Finds the coordinates that lead from the start to end, then converts them to bot-readable directions.
	def get_coord_path_from(self, start, end):
		previous_coords = {} # Keeps track of the previous tiles the search has seen alongside their coordinates.
		coord_queue = [Coordinates(start.x, start.y)] # The coordinates that will be checked and expanded from.
		previous_coords[self.tile_map[start.y][start.x]] = None # Since the search starts from where the robot is, None indicates that it is not expanded from any tile.
		while coord_queue:
			current_coords = coord_queue.pop(0) # Takes the coordinates from the front of the queue.
			# If the correct coordinates are found, the loop is exited with the current coords still saved.
			if (current_coords.x == end.x) and (current_coords.y == end.y):
				return self.get_directions(current_coords, previous_coords) + ["U"]
			# The rest of the code in the loop adds neighboring tiles to the queue, and records them in previous_coords.
			next_coords = Coordinates(current_coords.x, current_coords.y - 1)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
			next_coords = Coordinates(current_coords.x + 1, current_coords.y)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
			next_coords = Coordinates(current_coords.x, current_coords.y + 1)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords
			next_coords = Coordinates(current_coords.x - 1, current_coords.y)
			if not isinstance(self.tile_map[next_coords.y][next_coords.x], Wall_Tile) and not isinstance(self.tile_map[next_coords.y][next_coords.x], Unknown_Tile) and self.tile_map[next_coords.y][next_coords.x] not in previous_coords.keys():
				coord_queue.append(next_coords)
				previous_coords[self.tile_map[next_coords.y][next_coords.x]] = current_coords

	# Converts a list of coordinates to usable bot directions.
	def get_directions(self, end, connections):
		coord_path = []
		# Uses previous_coords to trace the path from the frontier backwards to the robot.
		while end:
			coord_path.append(end)
			end = connections[self.tile_map[end.y][end.x]]

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

# Extended Coordinates class that includes the map the object is located in.	
class WorldCoordinates(Coordinates):
	def __init__(self, world: int, x: int, y: int):
		super().__init__(x, y)
		self.world = world
	
	def __str__(self):
		return f"(w:{self.world}, x:{self.x}, y:{self.y})"

# Global variables
unique_tile_locations = {"b": None, "o": None, "p": None, "y": None} # Where each of the portals is.
portal_uses = {"b": 0, "o": 0, "p": 0, "y": 0} # How many times each portal has been used.
portal_opposite = {"b": "o", "o": "b", "p": "y", "y": "p"} # A dict to convert a portal to its opposite.
bot_coordinates = [] # Keeps track of where each bot is.
exit_location = None # Keeps track of where the exit is.

# A class built on top of the map class. Manages multiple maps.
class NavigationManager(object):
	def __init__(self):
		self.NUM_BOTS = 2 # How many bots are in use.
		self.bot_paths = [] # The current paths each bot is taking.
		# Fills each list with the number of coordinates and paths needed.
		for i in range(self.NUM_BOTS):
			bot_coordinates.append(WorldCoordinates(0, 0, 0))
			self.bot_paths.append([])
		self.current_bot = 0 # The bot that is being used. Corresponds with its indices.
		self.maps = [Map()] # Initializes a single map.
		self.single = False # True if there is only one bot left.
		self.exited = False # True is one of the bots has started exiting.
		
	# Maps out the area around the bot.
	def scan(self, percepts):
		current_bot_coordinates = bot_coordinates[self.current_bot]
		current_bot_world = current_bot_coordinates.world
		current_map = self.maps[current_bot_world]
		current_map.scan(percepts, current_bot_coordinates)
		global exit_location
		# Each direction is checked for important tiles. If it's something that should be used immediately, it pathfinds to it.
		for index, i in enumerate(percepts["N"]):
			if i in "obyp":
				unique_tile_locations[i] = WorldCoordinates(current_bot_world, current_bot_coordinates.x, current_bot_coordinates.y - (index + 1))
			if (i == "r") and not self.exited:
				exit_location = WorldCoordinates(current_bot_world, current_bot_coordinates.x, current_bot_coordinates.y - (index + 1))
				self.exited = True
				self.bot_paths[self.current_bot] = (["N"] * (index + 1)) + ["U"]
				return
			elif i in string.digits:
				self.bot_paths[self.current_bot] = (["N"] * (index + 1)) + ["U"]
				return


		for index, i in enumerate(percepts["E"]):
			if i in "obyp":
				unique_tile_locations[i] = WorldCoordinates(current_bot_world, current_bot_coordinates.x + (index + 1), current_bot_coordinates.y)
			if (i == "r") and not self.exited:
				exit_location = WorldCoordinates(current_bot_world, current_bot_coordinates.x + (index + 1), current_bot_coordinates.y)
				self.exited = True
				self.bot_paths[self.current_bot] = (["E"] * (index + 1)) + ["U"]
				return
			elif i in string.digits:
				self.bot_paths[self.current_bot] = (["E"] * (index + 1)) + ["U"]
				return
			
		for index, i in enumerate(percepts["S"]):
			if i in "obyp":
				unique_tile_locations[i] = WorldCoordinates(current_bot_world, current_bot_coordinates.x, current_bot_coordinates.y + (index + 1))
			if (i == "r") and not self.exited:
				exit_location = WorldCoordinates(current_bot_world, current_bot_coordinates.x, current_bot_coordinates.y + (index + 1))
				self.exited = True
				self.bot_paths[self.current_bot] = (["S"] * (index + 1)) + ["U"]
				return
			elif i in string.digits:
				self.bot_paths[self.current_bot] = (["S"] * (index + 1)) + ["U"]
				return

		for index, i in enumerate(percepts["W"]):
			if i in "obyp":
				unique_tile_locations[i] = WorldCoordinates(current_bot_world, current_bot_coordinates.x - (index + 1), current_bot_coordinates.y)
			if (i == "r") and not self.exited:
				exit_location = WorldCoordinates(current_bot_world, current_bot_coordinates.x - (index + 1), current_bot_coordinates.y)
				self.exited = True
				self.bot_paths[self.current_bot] = (["W"] * (index + 1)) + ["U"]
				return
			elif i in string.digits:
				self.bot_paths[self.current_bot] = (["W"] * (index + 1)) + ["U"]
				return

	# Tells the bot where to go in order to find new tiles.
	def discover(self):
		current_bot_coordinates = bot_coordinates[self.current_bot]
		current_bot_world = current_bot_coordinates.world
		current_map = self.maps[current_bot_world]
		# Attempts to find a frontier in the current map.
		path = current_map.discover(current_bot_coordinates)
		if path:
			return path
		# If the AI was unable to find a frontier in the current map, it decides upon a portal to use.
		viable_portals = {k:v for k,v in unique_tile_locations.items() if ((v) and (v.world == current_bot_world))}
		# First, it tries to enter a portal that leads to a new map, but only if all of the current maps are fully explored.
		if all(x.fully_explored for x in self.maps):
			for k in viable_portals:
				if not unique_tile_locations[portal_opposite[k]]:
					self.maps.append(Map())
					unique_tile_locations[portal_opposite[k]] = WorldCoordinates(len(self.maps) - 1, 0, 0)
					return current_map.get_coord_path_from(current_bot_coordinates, viable_portals[k])
		# If it will not use a portal to a new map, it will instead go to the least used portal in its world.
		least_used = min(viable_portals, key=portal_uses.get)
		return current_map.get_coord_path_from(current_bot_coordinates, viable_portals[least_used])
		
	# Adds frontiers to the current map.
	def add_frontier(self):
		current_bot_coordinates = bot_coordinates[self.current_bot]
		current_bot_world = current_bot_coordinates.world
		current_map = self.maps[current_bot_world]
		current_map.add_frontier()

	# Prints the current map.
	def print_map(self):
		current_bot_coordinates = bot_coordinates[self.current_bot]
		current_bot_world = current_bot_coordinates.world
		current_map = self.maps[current_bot_world]
		current_map.print_map()

	# Pops from the bot's navigation lists. If it can't do that, it first generates a list.
	def next_direction(self, below):
		if not self.bot_paths[self.current_bot]:
			self.bot_paths[self.current_bot] = self.discover()
			return self.next_direction(below)
		d = self.bot_paths[self.current_bot].pop(0)
		if d == "N":
			bot_coordinates[self.current_bot].y -= 1
		elif d == "E":
			bot_coordinates[self.current_bot].x += 1
		elif d == "S":
			bot_coordinates[self.current_bot].y += 1
		elif d == "W":
			bot_coordinates[self.current_bot].x -= 1
		# For cases where the next step is "U", the bot makes necessary adjustments to the game state.
		elif d == "U":
			if below == "r":
				self.single = True
				self.swap_bot()
			elif below in "bopy":
				bot_coordinates[self.current_bot].x = unique_tile_locations[portal_opposite[below]].x
				bot_coordinates[self.current_bot].y = unique_tile_locations[portal_opposite[below]].y
				bot_coordinates[self.current_bot].world = unique_tile_locations[portal_opposite[below]].world
				portal_uses[below] += 1
		return d
	
	# Swaps the bot's turn, so that the proper index is used.
	def swap_bot(self):
		self.current_bot = (self.current_bot + 1) % self.NUM_BOTS
		for i in bot_coordinates:
			print(i)
		print(self.bot_paths)

	# Navigates the bot to the exit when the bot is in the exit's map.
	def exit_check(self):
		if not self.single:
			return
		if self.bot_paths[self.current_bot]:
			return
		current_bot_coordinates = bot_coordinates[self.current_bot]
		current_bot_world = current_bot_coordinates.world
		current_map = self.maps[current_bot_world]
		if exit_location and (exit_location.world == current_bot_world):
			self.bot_paths[self.current_bot] = current_map.get_coord_path_from(current_bot_coordinates, exit_location)