#modules
import libtcodpy as libtcod
import pygame
import textwrap
import math

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
		self.med_wep_sheet = obj_SpriteSheet("data/DawnLike/Items/MedWep.png")
		self.shield_sheet = obj_SpriteSheet("data/DawnLike/Items/Shield.png")
		self.floor_sheet = obj_SpriteSheet("data/DawnLike/Objects/Floor.png")
		self.wall_sheet = obj_SpriteSheet("data/DawnLike/Objects/Wall.png")
		self.scroll_sheet = obj_SpriteSheet("data/DawnLike/Items/Scroll.png")
		self.flesh_sheet = obj_SpriteSheet("data/DawnLike/Items/Flesh.png")

		#animations
		self.A_PLAYER = self.player0_sheet.get_image(0, 7, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_PLAYER += self.player1_sheet.get_image(0, 7, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOMBIE = self.undead0_sheet.get_image(5, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOMBIE += self.undead1_sheet.get_image(5, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOGRE = self.undead0_sheet.get_image(7, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOGRE += self.undead1_sheet.get_image(7, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))


		#sprites
		self.S_RIBS = self.flesh_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))

		self.S_FLOOR = self.floor_sheet.get_image(1, 7, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_FLOOR_EXPLORED = self.floor_sheet.get_image(1, 10, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))


		self.S_WALL = self.wall_sheet.get_image(3, 3, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_WALL_EXPLORED = self.wall_sheet.get_image(3, 6, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))

		self.S_SWORD = self.med_wep_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_SHIELD = self.shield_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_SCROLL = self.scroll_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))



#OBJECTS
class obj_Actor:
	def __init__(self,
				x, y,
				animation,
				object_type,
				object_name,
				animation_speed = 1.0,
				creature = None,
				ai = None,
				container = None,
				item = None,
				equipment = None):
		
		self.x = x #map address not pixel address
		self.y = y
		
		self.animation = animation #list of images
		self.animation_speed = animation_speed/1.0 #in seconds
		#animation flicker speed
		self.flicker_speed = self.animation_speed/len(self.animation)
		self.flicker_timer = 0.0
		self.sprite_image = 0

		self.object_type = object_type
		self.object_name = object_name
		
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

		self.equipment = equipment
		if equipment:
			self.equipment.owner = self
			if not self.item:
				self.item = com_Item()
				self.item.owner = self
	
	@property
	def display_name(self):
		if self.creature:
			return self.creature.name_instance + " the " + self.object_name
		
		if self.item:
			if self.equipment and self.equipment.equipped:
				return self.object_name + " (equipped)"
			else:
				return self.object_name

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

	def distance_to(self, x, y):
		dx = x - self.x
		dy = y - self.y
		return math.sqrt((dx**2)+(dy**2))

	def move_towards(self, x, y):
		dx = x - self.x
		dy = y - self.y
		distance = math.sqrt((dx**2)+(dy**2))
		if distance != 0:
			dx = int(round(dx/distance))
			dy = int(round(dy/distance))
		else:
			dx = 0
			dy = 0
		self.creature.move(dx, dy)

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
	def __init__(self, name_instance, hp = 10, base_atk = 1, base_def = 0, death_function = None):
		self.name_instance = name_instance
		self.maxhp = hp
		self.hp = hp
		self.base_atk = base_atk
		self.base_def = base_def
		self.death_function = death_function

	def move(self, dx, dy):
		tile_is_walkable = GAME.current_map[self.owner.x + dx][self.owner.y + dy].walkable
		TARGET = None
		TARGET = map_creature_check(self.owner.x + dx, self.owner.y + dy, self.owner)
		if TARGET:
			self.attack(TARGET)
		if tile_is_walkable and TARGET is None:
			self.owner.x += dx
			self.owner.y += dy

	def attack(self, TARGET):
		
		damage_dealt = self.power - TARGET.creature.defence
		if damage_dealt < 0:
			damage_dealt = 0
		game_message(self.name_instance + " attacks " + TARGET.creature.name_instance, constants.COLOR_WHITE)
		TARGET.creature.take_damage(damage_dealt)

	def take_damage(self, damage):
		self.hp -= damage
		game_message(self.name_instance + "'s HP is now " + str(self.hp) + "/" + str(self.maxhp), constants.COLOR_RED)
		if self.hp <= 0:
			if self.death_function is not None:
				self.death_function(self.owner)

	def heal(self, healing):
		overflow = 0
		if self.maxhp <= self.hp:
			game_message(self.creature.name_instance + " is already at full health!")
		else:
			if self.maxhp < (self.hp + healing):
				overflow = (self.hp + healing) - self.maxhp
				self.hp = self.maxhp
				game_message(self.name_instance + " is healed for " + str(healing-overflow))
			else: 
				self.hp += healing
				game_message(self.name_instance + " is healed for " + str(healing))
	@property
	def power(self):
		total_power = self.base_atk
		if self.owner.container:
			object_bonuses = [obj.equipment.atk_bonus for obj in self.owner.container.equipped_items]
			for bonus in object_bonuses:
				total_power += bonus
		return total_power
	@property
	def defence(self):
		total_defence = self.base_def
		if self.owner.container:
			object_bonuses = [obj.equipment.def_bonus for obj in self.owner.container.equipped_items]
			for bonus in object_bonuses:
				total_defence += bonus
		return total_defence

class com_Item:
	def __init__(self, weight = 0.00, volume = 0.0, use_function = None, use_func_helper = None):
		self.weight = weight
		self.volume = volume
		self.use_function = use_function
		self.use_func_helper = use_func_helper
		self.current_container = None
	#pick up item
	def pick_up(self, actor):
		if actor.container:
			if actor.container.volume + self.volume > actor.container.max_volume:
				game_message("Not enough room.", constants.COLOR_WHITE)
			else:
				game_message("Picking up", constants.COLOR_WHITE)
				actor.container.inventory.append(self.owner)
				GAME.current_objects.remove(self.owner)
				self.current_container = actor.container
					
	#drop item
	def drop(self, new_x, new_y):
		GAME.current_objects.append(self.owner)
		self.current_container.inventory.remove(self.owner)
		self.owner.x = new_x
		self.owner.y = new_y
		self.current_container = None
		game_message("Item Dropped", constants.COLOR_WHITE)
	
	#use item
	def use(self):
		
		if self.owner.equipment:
			self.owner.equipment.toggle_equipped()
			return

		if self.use_function:
			result = None
			if not self.use_func_helper:
				result = self.use_function(self.current_container.owner)
			elif self.use_func_helper:
				result = self.use_function(self.current_container.owner, self.use_func_helper)
			else:
				print("Error, item " + str(self.owner) + " use_func_helper missing.")
				return
			if result == None:
				print("Error: item " + str(self.owner) + " use_function failed to complete.")
				return
			elif result == "cancelled":
				game_message("You can't use that right now.")
				return
			else:
				self.current_container.inventory.remove(self.owner)
				return

class com_Equipment:
	def __init__(self, atk_bonus = 0, def_bonus = 0, slot = None):
		self.atk_bonus = atk_bonus
		self.def_bonus = def_bonus
		self.slot = slot
		
		self.equipped = False

	def toggle_equipped(self):
		if self.equipped:
			self.unequip()
		else:
			self.equip()
	def equip(self):
		all_equiped_items = self.owner.item.current_container.equipped_items
		for item in all_equiped_items:
			if item.equipment.slot == self.slot:
				game_message("That slot is occupied!", constants.COLOR_RED)
				return
		self.equipped = True
		game_message("Item equipped")
	def unequip(self):
		self.equipped = False
		game_message("Item unequipped")

class com_Container:
	def __init__(self, volume = 10.00, inventory = [], weight = 0.00):
		self.inventory = inventory
		self.max_volume = volume
		self.weight = weight 

	# TODO Get names of everything in inventory
	# TODO get volume within container
	@property
	def volume(self):	
		return 0.00
		# self.contained_volume = 0.00
		# for item in enumerate(self.inventory):
		# 	if self.inventory[item].item:
		# 		self.contained_volume += inventory[item].volume
		# return self.contained_volume
	@property
	def equipped_items(self):
		list_of_equipped_items = [obj for obj in self.inventory if obj.equipment and obj.equipment.equipped]
		return list_of_equipped_items
	
	
	# Todo get weight of everything in inventory



#AI
class com_AI_Confused:
	def __init__(self, old_ai = None, num_turns = 5):
		self.old_ai = old_ai
		self.num_turns = num_turns
		self.turn_counter = 0
	def take_Turn(self):
		x = libtcod.random_get_int(None, -1, 1)
		y = libtcod.random_get_int(None, -1, 1)
		if x == 0 and y == 0:
			self.owner.creature.attack(TARGET = self.owner)
		else:
			self.owner.creature.move(x, y)
		self.turn_counter += 1
		if self.turn_counter == self.num_turns:
			self.owner.ai = self.old_ai
			game_message("The creature has broken free of the enchantment!", msg_color = constants.COLOR_RED)

class com_AI_zombie:
	def __init__(self, old_ai = None, num_turns = 0):
		self.old_ai = old_ai
		self.num_turns = num_turns
		self.turn_counter = 0

	def take_Turn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):
			if monster.distance_to(PLAYER.x, PLAYER.y) >= 2:
				monster.move_towards(PLAYER.x, PLAYER.y)
			elif PLAYER.creature.hp > 0:
				monster.creature.attack(PLAYER)
		self.turn_counter += 1
		if self.turn_counter == self.num_turns:
			self.owner.ai = old_ai

def death_monster(monster):
	game_message(monster.creature.name_instance + " the " + monster.object_name + " has been slain!", constants.COLOR_WHITE)
	monster.creature = None
	monster.ai = None
	monster.animation = ASSETS.S_RIBS
	monster.object_type = "Corpse"
	monster.object_name += " Corpse"
	monster.item = com_Item(use_function = cast_heal, use_func_helper = 6)
	monster.item.owner = monster
	if monster.container:
		for item in monster.container:
			monster.container.inventory[item].item.drop(monster.x, monster.y)



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

def map_creature_check(x, y, excluded_object = None):
	TARGET = None
	for object in GAME.current_objects:
		if (object is not excluded_object and 
			object.x == x and 
			object.y == y and 
			object.creature):
			TARGET = object
		if TARGET:
			return TARGET

def map_objects_at_coords(coords_x, coords_y):
	object_options = [obj for obj in GAME.current_objects
						if obj.x == coords_x and obj.y == coords_y]
	return object_options

def map_wall_check(x, y):
	not_wall = GAME.current_map[x][y].walkable
	return (not_wall)

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
		libtcod.map_compute_fov(FOV_MAP, PLAYER.x, PLAYER.y, constants.SIGHT_RADIUS, constants.FOV_LIGHT_WALLS, constants.FOV_ALGO)

def map_find_line(coords_a, coords_b):
	x1, y1 = coords_a
	x2, y2 = coords_b

	libtcod.line_init(x1, y1, x2, y2)

	calc_x, calc_y = libtcod.line_step()

	coords_list = []

	if x1 == x2 and y1 == y2:
		return[(x1, y1)]

	while (not calc_x is None):
		coords_list.append((calc_x, calc_y))
		calc_x, calc_y = libtcod.line_step()
	return coords_list

def map_find_radius(coords, radius):
	center_x, center_y = coords
	tile_list = []

	start_x = center_x-radius
	start_y = center_y-radius
	end_x = center_x+radius+1
	end_y = center_y+radius+1


	for x in range(start_x, end_x):
		for y in range(start_y, end_y):
			tile_list.append((x, y))
	return tile_list



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

def draw_map(map_to_draw):
	for x in range(0, constants.MAP_WIDTH):
		for y in range(0, constants.MAP_HEIGHT):

			is_visible = libtcod.map_is_in_fov(FOV_MAP, x, y)

			if is_visible:

				map_to_draw[x][y].explored = True

				if map_to_draw[x][y].walkable == False:
					#draw wall
					SURFACE_MAIN.blit(ASSETS.S_WALL[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
				else:
					#draw floor
					SURFACE_MAIN.blit(ASSETS.S_FLOOR[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
			elif map_to_draw[x][y].explored:
				if map_to_draw[x][y].walkable == False:
					#draw wall
					SURFACE_MAIN.blit(ASSETS.S_WALL_EXPLORED[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
				else:
					#draw floor
					SURFACE_MAIN.blit(ASSETS.S_FLOOR_EXPLORED[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

def draw_debug():
	draw_text(SURFACE_MAIN, "FPS: " + str(int(CLOCK.get_fps())), (0, 0), constants.COLOR_WHITE, constants.COLOR_BLACK)

def draw_messages():
	
	if len(GAME.message_history) <= constants.NUM_MESSAGES:
		to_draw = GAME.message_history
	else:
		to_draw = GAME.message_history[-constants.NUM_MESSAGES:]

	text_height = helper_text_height(constants.FONT_MESSAGES)
	start_y = (constants.GAME_HEIGHT-(constants.NUM_MESSAGES*text_height))

	i = 0

	for i, (message, color) in enumerate(to_draw):
		draw_text(SURFACE_MAIN, message, (0, start_y+(i*text_height)), color, constants.COLOR_BLACK, constants.FONT_MESSAGES)
		i += 1

def draw_text(display_surface, text, text_location, text_color, back_color = None, font = constants.FONT_DEBUG, center = False):
	#This function takes in some text and displays it on the referenced surface
	text_surface, text_rect = helper_text_objects(text, text_color, back_color, font)
	if center:
		text_rect.center = text_location
	else:
		text_rect.topleft = text_location
	display_surface.blit(text_surface, text_rect)


def draw_inspect_rect(coords, tile_color = constants.COLOR_RED, tile_alpha = 150, mark = None):
	new_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))

	new_surface.fill(tile_color)
	new_surface.set_alpha(tile_alpha)
	if mark:
		draw_text(new_surface, mark, (constants.CELL_WIDTH/2, constants.CELL_HEIGHT/2), constants.COLOR_BLACK, font = constants.FONT_CURSOR_TEXT, center = True)
	
	SURFACE_MAIN.blit(new_surface, coords)

#Helpers

def helper_text_objects(incoming_text, incoming_color, incoming_BG, font):
	if incoming_BG:
		text_surface = font.render(incoming_text, False, incoming_color, incoming_BG)
	else: 
		text_surface = font.render(incoming_text, False, incoming_color)
	return text_surface, text_surface.get_rect()

def helper_text_height(font):
	font_object = font.render("a", False, (0,0,0))
	font_rect = font_object.get_rect()
	return font_rect.height

def helper_text_width(font):
	font_object = font.render("a", False, (0,0,0))
	font_rect = font_object.get_rect()
	return font_rect.width

#menus
def menu_pause():
	#This menu pauses the game and displays a simple message
	menu_Open = True
	
	menu_text = "PAUSED"
	menu_font = constants.FONT_DEBUG

	text_height = helper_text_height(menu_font)
	text_width = len(menu_text)*helper_text_width(menu_font)

	while menu_Open:
		pause_events = pygame.event.get()
		for event in pause_events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
					menu_Open = False
		draw_text(SURFACE_MAIN, menu_text, ((constants.GAME_WIDTH/2)-text_width/2, (constants.GAME_HEIGHT/2)-text_height/2), constants.COLOR_WHITE, constants.COLOR_BLACK)
		
		CLOCK.tick(constants.FPS_LIMIT)

def menu_inventory():
	inv_Open = True

	menu_width = 216
	menu_height = 216
	menu_x = (constants.GAME_WIDTH/2) - menu_width/2
	menu_y = (constants.GAME_HEIGHT/2) - menu_height/2



	menu_font = constants.FONT_MESSAGES
	menu_text_height = helper_text_height(menu_font)
	
	local_inventory_surface = pygame.Surface((menu_width, menu_height))
	selected_line = None
	while inv_Open:
		#clear the menu
		local_inventory_surface.fill(constants.COLOR_BLACK)
		#register changes
		print_list = [obj.display_name for obj in PLAYER.container.inventory]
		
		inventory_events = pygame.event.get()
		mouse_x, mouse_y = pygame.mouse.get_pos()
		rel_mouse_x = mouse_x - menu_x
		rel_mouse_y = mouse_y - menu_y
		
		mouse_in_window = menu_width > rel_mouse_x > 0  and menu_height > rel_mouse_y > 0

		if (pygame.mouse.get_rel() != (0, 0)) and mouse_in_window:
			selected_line = int(rel_mouse_y/menu_text_height)

		for event in inventory_events:
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_g or event.key == pygame.K_ESCAPE:
					inv_Open = False
				if event.key == pygame.K_s:
					if selected_line == None or selected_line == (len(print_list)-1):
						selected_line = 0
					else:
						selected_line += 1
				if event.key == pygame.K_w:
					if selected_line == None or selected_line == 0:
						selected_line = len(print_list)-1
					else:
						selected_line -= 1
				if event.key == pygame.K_e and selected_line <= (len(print_list)-1):
					PLAYER.container.inventory[selected_line].item.use()
					inv_Open = False
				if event.key == pygame.K_f and selected_line <= (len(print_list)-1):
						PLAYER.container.inventory[selected_line].item.drop(PLAYER.x, PLAYER.y)
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					if mouse_in_window and selected_line <= (len(print_list)-1):
						PLAYER.container.inventory[selected_line].item.use()
						inv_Open = False
		
		
		#draw menu
		for line, (name) in enumerate(print_list):
			if line == selected_line:
				draw_text(local_inventory_surface, name, (0, 0+(line*menu_text_height)), constants.COLOR_WHITE, constants.COLOR_GREY, menu_font)
			else:
				draw_text(local_inventory_surface, name, (0, 0+(line*menu_text_height)), constants.COLOR_WHITE, constants.COLOR_BLACK, menu_font)
			line += 1
	
		#display menu
		draw_game()
		SURFACE_MAIN.blit(local_inventory_surface, ((menu_x), (menu_y)))
		CLOCK.tick(constants.FPS_LIMIT)
		pygame.display.update()

def menu_tile_select(coords_origin = None, max_range = None, radius = None, penetrate_walls = True, pierce_creature = True):
	menu_Open = True
	if coords_origin:
		map_coords_x, map_coords_y = coords_origin
	else:
		map_coords_x, map_coords_y = (0, 0)
	while menu_Open:
		draw_game()
		inspect_events = pygame.event.get()
		if pygame.mouse.get_rel() != (0, 0):
			mouse_x, mouse_y = pygame.mouse.get_pos()
			map_coords_x = int(mouse_x/constants.CELL_WIDTH)
			map_coords_y = int(mouse_y/constants.CELL_HEIGHT)

		valid_tiles = []

		if coords_origin:
			full_list_of_tiles = map_find_line(coords_origin, (map_coords_x, map_coords_y))
			for i, (x, y) in enumerate(full_list_of_tiles):
				if max_range and i == max_range:
					if i == max_range:
						break
				if not penetrate_walls and not map_wall_check(x, y):
					break
				if not pierce_creature and (map_creature_check(x, y)):
				 	valid_tiles.append((x, y))
				 	break
				valid_tiles.append((x, y))
		else:
			valid_tiles =[(map_coords_x, map_coords_y)]

		if radius:
			if not valid_tiles:
				valid_tiles.append(coords_origin)
			area_effect = map_find_radius(valid_tiles[-1], radius)
			for (tile_x, tile_y) in area_effect:
				draw_inspect_rect((tile_x*constants.CELL_WIDTH, tile_y*constants.CELL_HEIGHT))

		for (tile_x, tile_y) in valid_tiles:
			if (tile_x, tile_y) == (map_coords_x, map_coords_y):
				draw_inspect_rect((tile_x*constants.CELL_WIDTH, tile_y*constants.CELL_HEIGHT), tile_color = constants.COLOR_WHITE, mark = "X")
			else:
				draw_inspect_rect((tile_x*constants.CELL_WIDTH, tile_y*constants.CELL_HEIGHT), tile_color = constants.COLOR_WHITE)
		
		CLOCK.tick(constants.FPS_LIMIT)
		
		pygame.display.flip()
		
		for event in inspect_events:
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_v or event.key == pygame.K_c or event.key == pygame.K_e:
					return (valid_tiles[-1])
					menu_Open = False
				elif event.key == pygame.K_ESCAPE:
					return None
					menu_Open = False
				elif event.key == pygame.K_w:
					if map_coords_y > 0:
						map_coords_y -= 1
				elif event.key == pygame.K_a:
					if map_coords_x > 0:
						map_coords_x -= 1
				elif event.key == pygame.K_s:
					if map_coords_y < constants.MAP_HEIGHT:
						map_coords_y += 1
				elif event.key == pygame.K_d:
					if map_coords_y < constants.MAP_WIDTH:
						map_coords_x += 1
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					return (valid_tiles[-1])
					menu_Open = False
	
#MAGIC
def cast_heal(target, healing = 6):
	if target.creature:
		if target.creature.hp == target.creature.maxhp:
			return "cancelled"
		else:
			target.creature.heal(healing)
			return "healed"
		
	else:
		game_message("You can't heal an object.")
		return "cancelled"

def cast_lightning(caster, T_Range_Damage = (20, 10)):
	max_range, damage = T_Range_Damage

	start_coords = (caster.x, caster.y)
	point_selected = menu_tile_select(start_coords, max_range = max_range, penetrate_walls = False)
	
	if point_selected == None:
		return "cancelled"

	list_of_tiles = map_find_line(start_coords, point_selected)
	for (x, y) in list_of_tiles:
		target = map_creature_check(x, y)
		if target and target is not caster:
			target.creature.take_damage(damage)
	return "cast"

def cast_fireball(caster, T_range_radius_damage = (12, 3, 10)):
	max_range, local_radius, damage = T_range_radius_damage
	point_selected = menu_tile_select((caster.x, caster.y), max_range = max_range, radius = local_radius, penetrate_walls = False, pierce_creature = False)
	
	if point_selected == None:
		return "cancelled"
	tiles_to_damage = map_find_radius(point_selected, local_radius)
	
	creature_hit = False
	for (x, y) in tiles_to_damage:
		creature_to_damage = map_creature_check(x, y)
		if creature_to_damage:
			creature_hit = True
			creature_to_damage.creature.take_damage(damage)
	if creature_hit == False:
		game_message("A magnificant ball of fire sails away from your hand, slamming into the ground and creating a near-blinding conflagration that engulfs the air far around the point of impact. It's astounding to look-at, though harms no-one.")
	if creature_hit == True:
		game_message("You hear howls of pain and the sizzling of flesh as all caught in the fireball's explosion burn.")
	return "cast"

def cast_confusion(caster, duration = 5):
	point_selected = menu_tile_select()
	tile_x, tile_y = point_selected
	target = map_creature_check(tile_x, tile_y)
	if point_selected:
		if target:
			old_ai = target.ai
			target.ai = com_AI_Confused(old_ai = old_ai, num_turns = duration)
			target.ai.owner = target
			game_message("The creature's eyes glaze over.", msg_color = constants.COLOR_GREEN)
			return "confused"
		else:
			return "cancelled"
	else:
		return "cancelled"

#GENERATORS

#items
def gen_item(coords, forced_range = (1, 5)):
	global GAME
	r_min, r_max = forced_range
	generated_item = libtcod.random_get_int(None, r_min, r_max)
	new_item = None
	if generated_item == 1:
		new_item = gen_lightning_scroll(coords)
		print("Lightning")
	elif generated_item == 2:
		new_item = gen_fireball_scroll(coords)
		print("Fire")
	elif generated_item == 3:
		new_item = gen_confusion_scroll(coords)
		print("Confuse")
	elif generated_item == 4:
		new_item = gen_weapon_sword(coords)
		print("Sword")
	elif generated_item == 5:
		new_item = gen_armour_shield(coords)
		print("Shield")
	return new_item
	

def gen_lightning_scroll(coords):
	x, y = coords
	max_range = libtcod.random_get_int(None, 6, 20)
	damage = libtcod.random_get_int(None, 5, 10)
	returned_object = obj_Actor(x, y, ASSETS.S_SCROLL, "Scroll", "Lightning Scroll", item = com_Item(use_function = cast_lightning, use_func_helper = (max_range, damage)))	
	GAME.current_objects.append(returned_object)
	return returned_object

def gen_fireball_scroll(coords):
	x, y = coords
	max_range = libtcod.random_get_int(None, 6, 20)
	damage = libtcod.random_get_int(None, 5, 10)
	radius = libtcod.random_get_int(None, 1, 5)
	returned_object = obj_Actor(x, y, ASSETS.S_SCROLL, "Scroll", "Fireball Scroll", item = com_Item(use_function = cast_fireball, use_func_helper = (max_range, radius, damage)))	
	GAME.current_objects.append(returned_object)
	return returned_object

def gen_confusion_scroll(coords):
	x, y = coords
	duration = libtcod.random_get_int(None, 1, 6)
	returned_object = obj_Actor(x, y, ASSETS.S_SCROLL, "Scroll", "Confusion Scroll", item = com_Item(use_function = cast_confusion, use_func_helper = duration))	
	GAME.current_objects.append(returned_object)
	return returned_object

def gen_weapon_sword(coords):
	x, y = coords
	bonus = libtcod.random_get_int(None, 1, 4)
	returned_object = obj_Actor(x, y, ASSETS.S_SWORD, "Weapon", "+" + str(bonus) + " Sword", equipment = com_Equipment(atk_bonus = bonus, slot = "main_hand"))
	GAME.current_objects.append(returned_object)
	return returned_object

def gen_armour_shield(coords):
	x, y = coords
	bonus = libtcod.random_get_int(None, 1, 4)
	returned_object = obj_Actor(x, y, ASSETS.S_SHIELD, "Armour", "+" + str(bonus) + " Shield", equipment = com_Equipment(def_bonus = bonus, slot = "off_hand"))
	GAME.current_objects.append(returned_object)
	return returned_object

#enemies
def gen_player(coords):
	player = obj_Actor(1, 1, ASSETS.A_PLAYER, "Elf", "Player", creature = com_Creature("Arion", base_atk = 2), container = com_Container())
	return player

def gen_undead(coords, forced_range = (1, 100)):
	global GAME
	r_min, r_max = forced_range
	random_enemy = libtcod.random_get_int(None, r_min, r_max)
	if random_enemy <= 90:
		gen_zombie(coords)
	else:
		gen_zogre(coords)


def gen_zombie(coords):
	x, y = coords
	creature_name = libtcod.namegen_generate("Fantasy female")
	returned_object = obj_Actor(x, y, ASSETS.A_ZOMBIE, "Undead", "Zombie", creature = com_Creature(creature_name, death_function = death_monster), ai = com_AI_zombie())
	GAME.current_objects.append(returned_object)
	return returned_object

def gen_zogre(coords):
	x, y = coords
	creature_name = libtcod.namegen_generate("Celtic male")
	returned_object = obj_Actor(x, y, ASSETS.A_ZOGRE, "Undead", "Zogre", creature = com_Creature(creature_name, hp = 15, base_atk = 5, base_def = 1, death_function = death_monster), ai = com_AI_zombie())
	GAME.current_objects.append(returned_object)
	return returned_object


#GAME FUNCTIONS

def game_main_loop():
	#In this function, we loop the main game
	global FOV_CALCULATE
	game_quit = False
	wait_timer = 0.0
	while not game_quit:
		player_action = "no-action"
		#handles player input
		map_calculate_fov()
		if not PLAYER.ai:
			player_action = handle_player_input()
		else:
			if CLOCK.get_fps() > 0.0:
				wait_timer += 1/CLOCK.get_fps()
				if wait_timer >= 1:
					wait_timer = 0.0
					player_action = "controlled"
					FOV_CALCULATE = True
			

		if player_action == "QUIT":
			game_quit = True
		if player_action != "no-action":
			for obj in GAME.current_objects:
				if obj.ai:
					obj.ai.take_Turn()
			#calculates the FOV
			map_calculate_fov()

		CLOCK.tick(constants.FPS_LIMIT)
		#draw the game
		map_calculate_fov()
		draw_game()
		pygame.display.flip()

	#TODO quit the game
	pygame.quit()
	exit()

def game_initialize():
	"""This functions initiatlizes the main window in pygame"""
	global SURFACE_MAIN, GAME, PLAYER, FOV_CALCULATE, CLOCK, ASSETS

	pygame.init()
	pygame.key.set_repeat(555, 85)	

	CLOCK = pygame.time.Clock()

	SURFACE_MAIN = pygame.display.set_mode((constants.GAME_WIDTH, constants.GAME_HEIGHT))

	FOV_CALCULATE = True

	GAME = obj_Game()

	ASSETS = struc_Assets()

	libtcod.namegen_parse("data\\namegen\\jice_celtic.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_fantasy.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_mesopotamian.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_norse.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_region.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_town.cfg")
	libtcod.namegen_parse("data\\namegen\\mignos_demon.cfg")
	libtcod.namegen_parse("data\\namegen\\mignos_dwarf.cfg")
	libtcod.namegen_parse("data\\namegen\\mignos_norse.cfg")
	libtcod.namegen_parse("data\\namegen\\mignos_standard.cfg")
	libtcod.namegen_parse("data\\namegen\\mignos_town.cfg")

	PLAYER = gen_player((1, 1))


	GAME.current_objects.append(PLAYER)
	
	gen_undead((15, 15))
	gen_undead((10, 15))
	gen_undead((10, 10))



	gen_item((1, 2))
	gen_item((2, 1))
	gen_item((2, 2))
	gen_item((3, 1))
	gen_item((3, 2))

def handle_player_input():
	global FOV_CALCULATE
	#get player input
	events_list = pygame.event.get()
	#TODO process player input
	for event in events_list:
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
			return "QUIT"
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				PLAYER.creature.move(0, -1)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_s:
				PLAYER.creature.move(0, 1)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_a:
				PLAYER.creature.move(-1, 0)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_d:
				PLAYER.creature.move(1, 0)
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_e:
				objects_at_player = map_objects_at_coords(PLAYER.x, PLAYER.y)
				for obj in objects_at_player:
					if obj.item:
						obj.item.pick_up(PLAYER)
			if event.key == pygame.K_f:
				if len(PLAYER.container.inventory) > 0:
					PLAYER.container.inventory[-1].item.drop(PLAYER.x, PLAYER.y)
			if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
				menu_pause()
			if event.key == pygame.K_g:
				menu_inventory()
			if event.key == pygame.K_v:
				print(menu_tile_select())
				return "player-looked"
			if event.key == pygame.K_SPACE:
				return "player_passed"
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				mouse_x, mouse_y = pygame.mouse.get_pos()
				PLAYER.move_towards(int(mouse_x/constants.CELL_WIDTH), int(mouse_y/constants.CELL_HEIGHT))
				FOV_CALCULATE = True
				return "player-moved"

			
	return "no-action"

def game_message(game_msg, msg_color = constants.COLOR_WHITE):
	GAME.message_history.append((game_msg, msg_color))


#EXECUTE GAME
if __name__ == "__main__":
	game_initialize()
	game_main_loop()