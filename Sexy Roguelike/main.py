#3rd party modules
import libtcodpy as libtcod
import pygame

#game files
import constants

#STRUCTURES

class struc_Tile:
	def __init__(self, walkable):
		self.walkable = walkable
		self.explored = False

class struc_Assets:
	def __init__(self):
		#spritesheets
		self.player0_sheet = obj_SpriteSheet("data/DawnLike/Characters/Player0.png")
		self.player1_sheet = obj_SpriteSheet("data/DawnLike/Characters/Player1.png")
		self.undead0_sheet = obj_SpriteSheet("data/DawnLike/Characters/Undead0.png")
		self.undead1_sheet = obj_SpriteSheet("data/DawnLike/Characters/Undead1.png")

		#animations
		self.A_PLAYER = self.player0_sheet.get_image(0, 7, 16, 16)
		self.A_PLAYER += self.player1_sheet.get_image(0, 7, 16, 16)
		self.A_ZOMBIE = self.undead0_sheet.get_image(5, 0, 16, 16)
		self.A_ZOMBIE += self.undead1_sheet.get_image(5, 0, 16, 16)

		#sprites
		self.S_FLOOR = pygame.image.load("data/tiles/floor.png")
		self.S_FLOOR_EXPLORED = pygame.image.load("data/tiles/floorexplored.png")

		self.S_WALL = pygame.image.load("data/tiles/wall.png")
		self.S_WALL_EXPLORED = pygame.image.load("data/tiles/wallexplored.png")

		#fonts
		self.FONT_DEBUG = pygame.font.Font("data/joystix.ttf", 16)
		self.FONT_MESSAGES = pygame.font.Font("data/joystix.ttf", 12)


#OBJECTS

class obj_Actor:
	def __init__(self,
				x, y,
				animation,
				object_type,
				animation_speed = 1.0,
				creature = None,
				ai = None,
				container = None,
				item = None):
		
		self.x = x #map address not pixel address
		self.y = y
		
		self.animation = animation #list of images
		self.animation_speed = animation_speed/1.0 #in seconds
		#animation flicker speed
		self.flicker_speed = self.animation_speed/len(self.animation)
		self.flicker_timer = 0.0
		self.sprite_image = 0

		self.object_type = object_type
		
		self.creature = creature
		if creature:
			self.creature.owner = self
		
		self.ai = ai
		if ai:
			self.ai.owner = self
		
		self.container = container
		if container:
			self.container.owner = self
		
		self.item = item
		if item:
			self.item.owner = self
	
	#draws the actor
	def draw(self):
		is_visible = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)
		if is_visible:
			if len(self.animation) <= 1:
				SURFACE_MAIN.blit(self.animation[0], (self.x*constants.CELL_WIDTH, self.y*constants.CELL_HEIGHT))
			elif len(self.animation) > 1:
				if CLOCK.get_fps() > 0.0:
					self.flicker_timer += 1/CLOCK.get_fps()
				if self.flicker_timer >= self.flicker_speed:
					self.flicker_timer = 0.0
					if self.sprite_image >= (len(self.animation)-1):
						self.sprite_image = 0
					else:
						self.sprite_image +=1
				SURFACE_MAIN.blit(self.animation[self.sprite_image], (self.x*constants.CELL_WIDTH, self.y*constants.CELL_HEIGHT))

class obj_Game:
	def __init__(self):
		self.current_map = map_create()
		self.current_objects = []
		self.message_history = []

class obj_SpriteSheet:
	"""
	Grab images out of a spritesheet
	"""
	def __init__(self, file_name):
		#load the sprite sheet
		self.sprite_sheet = pygame.image.load(file_name).convert()

	
	def get_image(self, column, row, width = constants.CELL_WIDTH, height = constants.CELL_HEIGHT, scale = None):
		#scale is a tuple (x, y)
		image_list = []

		image = pygame.Surface([width, height])
		
		image.blit(self.sprite_sheet, (0, 0), (column*width, row*height, width, height))

		image.set_colorkey(constants.COLOR_BLACK)

		if scale:
			new_w, new_h = scale
			image = pygame.transform.scale(image, (new_w, new_h))

		image_list.append(image)

		return image_list

	def get_animation(self, column, row, width = constants.CELL_WIDTH, height = constants.CELL_HEIGHT, num_sprites = 1, scale = None):
		
		image_list = []
		
		for i in range(num_sprites):
			#create blank image
			image = pygame.Surface([width, height])
			#copy image from sheet onto blank
			image.blit(self.sprite_sheet, (0, 0), (column*width+(width*i), row*height, width, height))
			#set transparency key to black
			image.set_colorkey(constants.COLOR_BLACK)

			if scale:
				new_w, new_h = scale
				image = pygame.transform.scale(image, (new_w, new_h))

			image_list.append(image)

		return image_list

#COMPONENTS
class com_Creature:
	"""
	Creatures have damage
	Creatures have health
	creatures can die
	creatures can move
	"""
	def __init__(self, name_instance, hp = 10, damage = 5, death_function = None):
		self.name_instance = name_instance
		self.maxhp = hp
		self.hp = hp
		self.damage = damage
		self.death_function = death_function

	def move(self, dx, dy):
		tile_is_walkable = GAME.current_map[self.owner.x + dx][self.owner.y + dy].walkable
		TARGET = None
		TARGET = map_creature_check(self.owner.x + dx, self.owner.y + dy, self.owner)
		if TARGET:
			self.attack(TARGET, self.damage)
		if tile_is_walkable and TARGET is None:
			self.owner.x += dx
			self.owner.y += dy
	def attack(self, TARGET, damage):
		game_message(self.name_instance + " attacks " + TARGET.creature.name_instance, constants.COLOR_WHITE)
		TARGET.creature.take_damage(self.damage)

	def take_damage(self, damage):
		self.hp -= damage
		game_message(self.name_instance + "'s HP is now " + str(self.hp) + "/" + str(self.maxhp), constants.COLOR_RED)
		if self.hp <= 0:
			if self.death_function is not None:
				self.death_function(self.owner)

class com_Item:
	def __init__(self, weight = 0.00, volume = 0.0):
		self.weight = weight
		self.volume = volume
	#todo pick up item
	def pick_up(self, actor):
		if actor.container:
			if actor.container.volume + self.volume > actor.container.max_volume:
				game_message("Not enough room.", constants.COLOR_WHITE)
			else:
				game_message("Picking up", constants.COLOR_WHITE)
				actor.container.inventory.append(self.owner)
				GAME.current_objects.remove(self.owner)
				self.container = actor.container
	#drop item
	def drop(self):
		GAME.current_objects.append(self.owner)
		self.container.inventory.remove(self.owner)
		game("Item Dropped", constants.COLOR_WHITE)
	#todo use item

class com_Container:
	def __init__(self, volume = 10.00, inventory = [], weight = 0.00):
		self.inventory = inventory
		self.max_volume = volume
		self.weight = weight

	# TODO Get names of everything in inventory
	# TODO get volume within container
	@property
	def volume(self):
		return 0.0
	
	# Todo get weight of everything in inventory

#AI
class com_AI_Test:
	def take_Turn(self):
		self.owner.creature.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))

def death_monster(monster):
	game_message(monster.creature.name_instance + " has died!", constants.COLOR_WHITE)
	monster.creature = None
	monster.ai = None
	monster.animation = [monster.animation[0]]


#MAP

def map_create():
	new_map = [[struc_Tile(True) for y in range(0, constants.MAP_HEIGHT)] for x in range (0, constants.MAP_WIDTH)]
	for x in range(constants.MAP_WIDTH):
		new_map[x][0].walkable = False
		new_map[x][constants.MAP_HEIGHT-1].walkable = False
	for y in range(constants.MAP_WIDTH):
		new_map[0][y].walkable = False
		new_map[constants.MAP_WIDTH-1][y].walkable = False

	map_make_fov(new_map)

	return new_map

def map_creature_check(x, y, excluded_object):
	TARGET = None
	for object in GAME.current_objects:
		if (object is not excluded_object and 
			object.x == x and 
			object.y == y and 
			object.creature):
			TARGET = object
		if TARGET:
			return TARGET

def map_make_fov(incoming_map):
	global FOV_MAP

	FOV_MAP = libtcod.map_new(constants.MAP_WIDTH, constants.MAP_HEIGHT)

	for y in range(constants.MAP_HEIGHT):
		for x in range(constants.MAP_WIDTH):
			libtcod.map_set_properties(FOV_MAP, x, y,
				incoming_map[x][y].walkable, incoming_map[x][y].walkable)

def map_calculate_fov():
	global FOV_CALCULATE

	if FOV_CALCULATE:
		FOV_CALCULATE = False
		libtcod.map_compute_fov(FOV_MAP, PLAYER.x, PLAYER.y, constants.SIGHT_RADIUS, constants. FOV_LIGHT_WALLS, constants.FOV_ALGO)

def map_objects_at_coords(coords_x, coords_y):
	object_options = [obj for obj in GAME.current_objects
						if obj.x == coords_x and obj.y == coords_y]
	return object_options

#DRAWING

def draw_game():
	global SURFACE_MAIN
	#TODO Clear the surface
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	#TODO draw the map
	draw_map(GAME.current_map)
	#draw the character
	for obj in GAME.current_objects:
		obj.draw()

	draw_debug()
	draw_messages()
	#updates the display
	pygame.display.flip()


def draw_map(map_to_draw):
	for x in range(0, constants.MAP_WIDTH):
		for y in range(0, constants.MAP_HEIGHT):

			is_visible = libtcod.map_is_in_fov(FOV_MAP, x, y)

			if is_visible:

				map_to_draw[x][y].explored = True

				if map_to_draw[x][y].walkable == False:
					#draw wall
					SURFACE_MAIN.blit(ASSETS.S_WALL, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
				else:
					#draw floor
					SURFACE_MAIN.blit(ASSETS.S_FLOOR, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
			elif map_to_draw[x][y].explored:
				if map_to_draw[x][y].walkable == False:
					#draw wall
					SURFACE_MAIN.blit(ASSETS.S_WALL_EXPLORED, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
				else:
					#draw floor
					SURFACE_MAIN.blit(ASSETS.S_FLOOR_EXPLORED, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

def draw_debug():
	draw_text(SURFACE_MAIN, "FPS: " + str(int(CLOCK.get_fps())), (0, 0), constants.COLOR_WHITE, constants.COLOR_BLACK)

def draw_messages():
	
	if len(GAME.message_history) <= constants.NUM_MESSAGES:
		to_draw = GAME.message_history
	else:
		to_draw = GAME.message_history[-constants.NUM_MESSAGES:]

	text_height = helper_text_height(ASSETS.FONT_MESSAGES)
	start_y = (constants.GAME_HEIGHT-(constants.NUM_MESSAGES*text_height))-5

	i = 0

	for message, color in to_draw:
		draw_text(SURFACE_MAIN, message, (0, start_y+(i*text_height)), color, constants.COLOR_BLACK)
		i += 1

def draw_text(display_surface, text, text_location, text_color, back_color = None):
	#This function takes in some text and displays it on the referenced surface
	text_surface, text_rect = helper_text_objects(text, text_color, back_color)
	text_rect.topleft = text_location
	display_surface.blit(text_surface, text_rect)

#Helpers

def helper_text_objects(incoming_text, incoming_color, incoming_BG):
	if incoming_BG:
		text_surface = ASSETS.FONT_DEBUG.render(incoming_text, False, incoming_color, incoming_BG)
	else: 
		text_surface = ASSETS.FONT_DEBUG.render(incoming_text, False, incoming_color)
	return text_surface, text_surface.get_rect()

def helper_text_height(font):
	font_object = font.render("a", False, (0,0,0))
	font_rect = font_object.get_rect()
	return font_rect.height

#GAME FUNCTIONS

def game_main_loop():
	#In this function, we loop the main game
	game_quit = False

	while not game_quit:
		player_action = "no-action"
		#handles player input
		
		player_action = handle_player_input()
		if player_action == "QUIT":
			game_quit = True
		if player_action != "no-action":
			for obj in GAME.current_objects:
				if obj.ai:
					obj.ai.take_Turn(obj.ai)
		#calculates the FOV
		map_calculate_fov()

		CLOCK.tick(constants.FPS_LIMIT)
		#draw the game

		draw_game()

	#TODO quit the game
	pygame.quit()
	exit()

def game_initialize():
	"""This functions initiatlizes the main window in pygame"""
	global SURFACE_MAIN, GAME, PLAYER, FOV_CALCULATE, CLOCK, ASSETS, BASE_ZOMBIE

	pygame.init()

	CLOCK = pygame.time.Clock()

	SURFACE_MAIN = pygame.display.set_mode((constants.GAME_WIDTH, constants.GAME_HEIGHT))

	FOV_CALCULATE = True

	GAME = obj_Game()

	ASSETS = struc_Assets()

	container_com_test = com_Container
	player_com = com_Creature("Arion")
	PLAYER = obj_Actor(1, 1, ASSETS.A_PLAYER, "Player", creature = player_com, container = container_com_test())

	item_com_test = com_Item
	zombie_AI_Test = com_AI_Test
	zombie_com = com_Creature("Zack", death_function = death_monster)
	BASE_ZOMBIE = obj_Actor(15, 15, ASSETS.A_ZOMBIE, "zombie", creature = zombie_com, ai = zombie_AI_Test, item = item_com_test)

	GAME.current_objects = [PLAYER, BASE_ZOMBIE]

def handle_player_input():
	global FOV_CALCULATE
	#get player input
	events_list = pygame.event.get()

	#TODO process player input
	for event in events_list:
		if event.type == pygame.QUIT:
			return "QUIT"
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				PLAYER.creature.move(0, -1)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_DOWN:
				PLAYER.creature.move(0, 1)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_LEFT:
				PLAYER.creature.move(-1, 0)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_RIGHT:
				PLAYER.creature.move(1, 0)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_g:
				objects_at_player = map_objects_at_coords(PLAYER.x, PLAYER.y)
				for obj in objects_at_player:
					if obj.item:
						obj.item.pick_up(PLAYER)
			
	return "no-action"

def game_message(game_msg, msg_color):
	GAME.message_history.append((game_msg, msg_color))


#EXECUTE GAME
if __name__ == "__main__":
	game_initialize()
	game_main_loop()