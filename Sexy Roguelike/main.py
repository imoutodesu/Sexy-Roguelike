#modules
import libtcodpy as libtcod
import pygame
import textwrap
import pickle
import gzip
import math
import random
import sys
import datetime
import os


#game files
import constants
import dungeonGenerationAlgorithms as dGA

#STRUCTURES

class struc_Tile:
	def __init__(self, walkable, blocks_fov = None):
		#creates map tiles
		self.walkable = walkable
		self.explored = False
		if blocks_fov == None:
			self.blocks_fov = not self.walkable
		else:
			self.blocks_fov = self.blocks_fov


class struc_Assets:
	"""All of the assets in the game"""
	def __init__(self):
		self.load_assets()
		self.sound_adjust()
	
	def load_assets(self):
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
		self.tile_sheet = obj_SpriteSheet("data/DawnLike/Objects/Tile.png")
		self.potion_sheet = obj_SpriteSheet("data/DawnLike/Items/Potion.png")

		#animations
		self.A_PLAYER = self.player0_sheet.get_image(0, 7, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_PLAYER += self.player1_sheet.get_image(0, 7, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOMBIE = self.undead0_sheet.get_image(5, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOMBIE += self.undead1_sheet.get_image(5, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOGRE = self.undead0_sheet.get_image(7, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.A_ZOGRE += self.undead1_sheet.get_image(7, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))


		#sprites
		self.S_RIBS = self.flesh_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_SWORD = self.med_wep_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_SHIELD = self.shield_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_SCROLL = self.scroll_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_HEALTH_POTION = self.potion_sheet.get_image(0, 0, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))

		self.S_STAIRS_UP =  self.tile_sheet.get_image(4, 3, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_STAIRS_DOWN = self.tile_sheet.get_image(6, 3, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))

		self.S_FLOOR = self.floor_sheet.get_image(1, 7, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_FLOOR_EXPLORED = self.floor_sheet.get_image(1, 10, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))


		self.S_WALL = self.wall_sheet.get_image(3, 3, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))
		self.S_WALL_EXPLORED = self.wall_sheet.get_image(3, 6, 16, 16, (constants.CELL_WIDTH, constants.CELL_HEIGHT))

		#used by actors to convret a string into an animation
		self.animation_dict = {
		#animations
		"A_PLAYER" : self.A_PLAYER,
		"A_ZOMBIE" : self.A_ZOMBIE,
		"A_ZOGRE" : self.A_ZOGRE,

		#sprites
		"S_RIBS" : self.S_RIBS,
		"S_SWORD" : self.S_SWORD,
		"S_SHIELD" : self.S_SHIELD,
		"S_SCROLL" : self.S_SCROLL,
		"S_HEALTH_POTION": self.S_HEALTH_POTION,
		"S_STAIRS_UP" : self.S_STAIRS_UP,
		"S_STAIRS_DOWN" : self.S_STAIRS_DOWN
		}


		#audio
		self.sound_list = []
		#music
		self.music_menu = "data/audio/Beethoven_Virus_8-Bit_Remix.mp3"
		#sound effects
		self.sound_hit = self.add_sound("data/audio/Hit_Hurt.wav") 
		self.sound_explode = self.add_sound("data/audio/Explosion.wav")
		self.sound_lightning = self.add_sound("data/audio/Explosion7.wav")
		self.sound_confuse = self.add_sound("data/audio/Powerup.wav")
	
	def add_sound(self, path):
		new_sound = pygame.mixer.Sound(path)
		self.sound_list.append(new_sound)
		return new_sound

	def sound_adjust(self):
		for sound in self.sound_list:
			sound.set_volume(PREFERENCES.vol_sound)
		pygame.mixer.music.set_volume(PREFERENCES.vol_music)

class struc_Preferences:
	def __init__(self):
		self.vol_sound = 0.5
		self.vol_music = 0.5





#OBJECTS
class obj_Actor:
	def __init__(self,
				x, y,
				animation_key,
				object_type,
				object_name,
				animation_speed = 1.0,
				creature = None,
				ai = None,
				container = None,
				item = None,
				equipment = None,
				stairs = None,
				state = None):
		
		self.x = x #map address not pixel address
		self.y = y
		self.animation_key = animation_key
		self.animation = ASSETS.animation_dict[self.animation_key] #list of images
		self.animation_speed = animation_speed/1.0 #in seconds
		#animation flicker speed
		self.flicker_speed = self.animation_speed/len(self.animation)
		self.flicker_timer = 0.0
		self.sprite_image = 0

		self.object_type = object_type
		self.object_name = object_name
		self.state = state
		
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
		
		self.stairs = stairs
		if stairs:
			self.stairs.owner = self
	
	@property
	def display_name(self):
		"""
		determines the display name of a creature
		"""
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
				SURFACE_MAP.blit(self.animation[0], (self.x*constants.CELL_WIDTH, self.y*constants.CELL_HEIGHT))
			elif len(self.animation) > 1:
				if CLOCK.get_fps() > 0.0:
					self.flicker_timer += 1/CLOCK.get_fps()
				if self.flicker_timer >= self.flicker_speed:
					self.flicker_timer = 0.0
					if self.sprite_image >= (len(self.animation)-1):
						self.sprite_image = 0
					else:
						self.sprite_image +=1
				SURFACE_MAP.blit(self.animation[self.sprite_image], (self.x*constants.CELL_WIDTH, self.y*constants.CELL_HEIGHT))

	def distance_to(self, x, y):
		"""
		determines the distance between an the actor and a point on the map
		"""
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
		self.creature.move((dx, dy))

	def animation_destroy(self):
		self.animation = None

	def animation_init(self):
		self.animation = ASSETS.animation_dict[self.animation_key]

class obj_Game:
	def __init__(self):
		self.current_objects = []
		self.message_history = []
		self.past_maps = []
		self.future_maps = []
		self.current_map, self.current_rooms = map_create()

	def next_map(self):
		global FOV_CALCULATE
		FOV_CALCULATE = True
		if len(self.future_maps) == 0:
			for obj in self.current_objects:
				obj.animation_destroy()
			self.past_maps.append((PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects))
			self.current_objects= [PLAYER]
			PLAYER.animation_init()
			self.current_map, self.current_rooms = map_create()
			map_place_objects(self.current_rooms)
		else:
			for obj in self.current_objects:
				obj.animation_destroy()
				if obj.container:
					for item in obj.container.inventory:
						item.animation_destroy()
			self.past_maps.append((PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects))
			self.current_objects= [PLAYER]
			PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects = self.future_maps[-1]
			for obj in self.current_objects:
				obj.animation_init()
				if obj.container:
					for item in obj.container.inventory:
						item.animation_init()
			map_make_fov(self.current_map)
			del self.future_maps[-1]
	def last_map(self):
		global FOV_CALCULATE
		FOV_CALCULATE = True
		if len(self.past_maps) != 0:
			for obj in self.current_objects:
				obj.animation_destroy()
				if obj.container:
					for item in obj.container.inventory:
						item.animation_destroy()
			self.future_maps.append((PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects))
			self.current_objects= [PLAYER]
			PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects = self.past_maps[-1]
			for obj in self.current_objects:
				obj.animation_init()
				if obj.container:
					for item in obj.container.inventory:
						item.animation_init()
			map_make_fov(self.current_map)
			del self.past_maps[-1]
		else:
			pass


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

class obj_Room:
	''' 
	This is a rectangle that lives on the map
	'''

	def __init__(self, coords, size):
		self.x1, self.y1 = coords
		self.w, self.h = size

		self.x2 = self.x1 + self.w
		self.y2 = self.y1 + self.h

	@property
	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2

		return (center_x, center_y)

	def intersects(self, other):

		# return True if other obj intersects with this one
		objects_intersect = (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

		return objects_intersect
	
class obj_Camera:
	def __init__(self):
		self.width = constants.CAM_WIDTH
		self.height = constants.CAM_HEIGHT
		self.x, self.y = (0, 0)

	def update(self, target_center, update_speed = 1):
		global PLAYER
		t_x, t_y = target_center
		target_x = t_x * constants.CELL_WIDTH + (constants.CELL_WIDTH/2)
		target_y = t_y * constants.CELL_HEIGHT + (constants.CELL_HEIGHT/2)
		distance_x, distance_y = self.map_dist((target_x, target_y))
		self.x += int(distance_x * update_speed)
		self.y += int(distance_y * update_speed)


	@property
	def rectangle(self):
		pos_rect = pygame.Rect((0, 0), (self.width, self.height))
		pos_rect.center = (self.x, self.y)
		return pos_rect

	@property
	def map_address(self):
		map_x = self.x/constants.CELL_WIDTH
		map_y = self.y/constans.CELL_HEIGHT

	def win_to_map(self, coords):
		tar_x, tar_y = coords
		#convert window coords to distance from camera
		cam_dx, cam_dy = self.cam_dist((tar_x, tar_y))
		#distance from camera converted to a map coordinate
		map_x = self.x + cam_dx
		map_y = self.y + cam_dy
		return map_x, map_y

	#gets the distance from the camera center to an object on the map
	def map_dist(self, coords):
		new_x, new_y = coords
		dist_x = new_x - self.x
		dist_y = new_y - self.y
		return (dist_x, dist_y)
	#gets the pixel distance from the center of the camera
	def cam_dist(self, coords):
		window_x, window_y = coords
		dist_x = window_x - self.width/2
		dist_y = window_y - self.height/2
		return (dist_x, dist_y)
	
	

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

	def move(self, coords):
		dx, dy = coords
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
		if damage_dealt > 0:
			pygame.mixer.Sound.play(ASSETS.sound_hit)

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
		# self.stackable = stackable
		# if self.stackable:
		# 	@property
		# 	def quantity(self):
		# 		if self.current_container:
		# 			for item in current_container.inventory:
		# 				if item.item == self
			
	#pick up item
	def pick_up(self, actor):
		if actor.container:
			if actor.container.volume + self.volume > actor.container.max_volume:
				if actor == PLAYER:
					game_message("Not enough room.", constants.COLOR_WHITE)
			else:
				if actor == PLAYER:
					game_message("Picking up", constants.COLOR_WHITE)
				actor.container.inventory.append(self.owner)
				GAME.current_objects.remove(self.owner)
				self.current_container = actor.container
					
	#drop item
	def drop(self, new_x, new_y):
		if self.owner.equipment:
			self.owner.equipment.unequip()
		GAME.current_objects.insert(1, self.owner)
		if self.current_container != None:
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
		all_equipped_items = self.owner.item.current_container.equipped_items
		for item in all_equipped_items:
			if item.equipment.slot == self.slot:
				if self.owner.item.current_container.owner == PLAYER:
					game_message("That slot is occupied!", constants.COLOR_RED)
				return
		self.equipped = True
		if self.owner.item.current_container.owner == PLAYER:
			game_message("Item equipped")
	def unequip(self):
		self.equipped = False
		if self.owner.item.current_container == PLAYER.container:
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
		total_volume = 0
		if self.inventory:
			object_volumes = [obj.item.volume for obj in self.inventory]
			for volume in object_volumes:
				total_volume += volume
		return total_volume
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
		x = libtcod.random_get_int(0, -1, 1)
		y = libtcod.random_get_int(0, -1, 1)
		if x == 0 and y == 0:
			self.owner.creature.attack(TARGET = self.owner)
		else:
			self.owner.creature.move((x, y))
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

class com_Stairs:
	def __init__(self, downwards = True):
		self.downwards = downwards
	def use(self):
		if self.downwards:
			GAME.next_map()
		else:
			GAME.last_map()


#DEATH FUNCTIONS
def death_monster(monster):
	game_message(monster.creature.name_instance + " the " + monster.object_name + " has been slain!", constants.COLOR_WHITE)
	if monster.container:
		if len(monster.container.inventory) > 0:
			for thing in monster.container.inventory:
				thing.item.drop(monster.x, monster.y)
	monster.creature = None
	monster.ai = None
	monster.animation_key = "S_RIBS"
	monster.animation = ASSETS.animation_dict[monster.animation_key]
	monster.object_type = "Corpse"
	monster.object_name += " Corpse"
	monster.item = com_Item()
	monster.item.owner = monster

def death_player_hardcore(player):
	player.state = "DEAD"
	SURFACE_MAIN.fill(constants.COLOR_BLACK)
	draw_text(SURFACE_MAIN,"YOU DIED!",(constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2), constants.COLOR_RED, font = constants.FONT_TITLE, center = True)
	pygame.display.update()
	pygame.time.wait(5000)




#MAP
def map_create():
	#generates a blank map
	new_map = [[struc_Tile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range (0, constants.MAP_WIDTH)]
	#generate new room
	list_of_rooms = []
	for i in range(0, 10):
		w = libtcod.random_get_int(0, 2, 10)
		h = libtcod.random_get_int(0, 2, 10)
		x = libtcod.random_get_int(0, 2, constants.MAP_WIDTH - w - 2)
		y = libtcod.random_get_int(0, 2, constants.MAP_HEIGHT - h - 2)
		new_room = obj_Room((x, y), (w, h))
		#checks interference
		failed = False
		for other_room in list_of_rooms:
			if new_room.intersects(other_room):
				failed = True
				break
		#if not, create new room
		if not failed:
			map_place_room(new_map, new_room)
			current_center = new_room.center
			if len(list_of_rooms) != 0:
				previous_center = list_of_rooms[-1].center
				#dig tunnels
				map_create_tunnels(current_center, previous_center, new_map)
			list_of_rooms.append(new_room)
	map_make_fov(new_map)
	return (new_map, list_of_rooms)

def map_place_objects(room_list):
	for room in room_list:
		if room == room_list[0]:
			PLAYER.x, PLAYER.y = room_list[0].center
			if len(GAME.past_maps) > 0:
				gen_stairs(room_list[0].center, False)
		num_of_objects = libtcod.random_get_int(0, 0, 4)
		if num_of_objects > 0:
			for obj in range(num_of_objects):
				obj_x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
				obj_y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
				item_or_enemy = libtcod.random_get_int(0,0,1)
				if item_or_enemy == 0:
					gen_item((obj_x, obj_y))
				else:
					if not map_creature_check(obj_x, obj_y):
						gen_undead((obj_x, obj_y))
					else:
						gen_item((obj_x, obj_y))
	gen_stairs(room_list[-1].center, True)
		



def map_place_room(new_map, placed_room):
	# set all tiles within a rectangle to 0
	for x in range(placed_room.x1, placed_room.x2):
		for y in range(placed_room.y1, placed_room.y2):
			new_map[x][y].walkable = True

def map_create_tunnels(room1_center, room2_center, used_map):
	x1, y1 = room1_center
	x2, y2 = room2_center
	coin_flip = (libtcod.random_get_int(0, 0, 1) == 1)
	if coin_flip:
		for x in range(min(x1, x2), max(x1, x2)+1):
			used_map[x][y1].walkable = True
		for y in range(min(y1, y2), max(y1, y2)+1):
			used_map[x2][y].walkable = True
	else:
		for y in range(min(y1, y2), max(y1, y2)+1):
			used_map[x1][y].walkable = True
		for x in range(min(x1, x2), max(x1, x2)+1):
			used_map[x][y2].walkable = True
		
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
	#finds a line betweeen two points, and returns a list of tiles in the line
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
	#finds a circle centered on a point on the map and returns all of the tiles in the circle
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
	#draws all of the objects that appear on the screen during normal play
	global SURFACE_MAIN, SURFACE_MAP, CAMERA
	#Clear the surface
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)
	#updates the camera
	CAMERA.update((PLAYER.x, PLAYER.y))
	#draw the map
	draw_map(GAME.current_map)
	#draw the character
	for obj in GAME.current_objects:
		obj.draw()
	SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)

	draw_debug()
	draw_messages()

def draw_map(map_to_draw):
	#draws the map
	for x in range(0, constants.MAP_WIDTH):
		for y in range(0, constants.MAP_HEIGHT):

			is_visible = libtcod.map_is_in_fov(FOV_MAP, x, y)

			if is_visible:

				map_to_draw[x][y].explored = True

				if map_to_draw[x][y].walkable == False:
					#draw wall
					SURFACE_MAP.blit(ASSETS.S_WALL[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
				else:
					#draw floor
					SURFACE_MAP.blit(ASSETS.S_FLOOR[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
			elif map_to_draw[x][y].explored:
				if map_to_draw[x][y].walkable == False:
					#draw wall
					SURFACE_MAP.blit(ASSETS.S_WALL_EXPLORED[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
				else:
					#draw floor
					SURFACE_MAP.blit(ASSETS.S_FLOOR_EXPLORED[0], (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

def draw_debug():
	#displayss an fps counter
	draw_text(SURFACE_MAIN, "FPS: " + str(int(CLOCK.get_fps())), (0, 0), constants.COLOR_WHITE, constants.COLOR_BLACK)

def draw_messages():
	#draws a log of all of the messages in the game
	if len(GAME.message_history) <= constants.NUM_MESSAGES:
		to_draw = GAME.message_history
	else:
		to_draw = GAME.message_history[-constants.NUM_MESSAGES:]

	text_height = helper_text_height(constants.FONT_MESSAGES)
	start_y = (CAMERA.height-(constants.NUM_MESSAGES*text_height))

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
	#this function draws a square at coords, somtimes with a text symbol marking it
	x, y = coords
	new_x = x*constants.CELL_WIDTH
	new_y = y*constants.CELL_HEIGHT
	new_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))

	new_surface.fill(tile_color)
	new_surface.set_alpha(tile_alpha)
	if mark:
		draw_text(new_surface, mark, (constants.CELL_WIDTH/2, constants.CELL_HEIGHT/2), constants.COLOR_BLACK, font = constants.FONT_CURSOR_TEXT, center = True)
	
	SURFACE_MAP.blit(new_surface, (new_x, new_y))

#HELPERS

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

def helper_scroll_down(selected_line, starting_line, ending_line, max_lines, print_list):
	if selected_line == None or selected_line >= (len(print_list)) or selected_line >= ending_line-1:
		if selected_line != None and selected_line >= ending_line-1 and selected_line <= (len(print_list)-2):
			starting_line += 1
			selected_line += 1
			if max_lines < len(print_list):
				max_lines += 1
		else:
			selected_line = 0
			if starting_line != 0:
				starting_line = 0
				max_lines = 14
	else:
		selected_line += 1
	return (selected_line, starting_line, max_lines)

def helper_scroll_up(selected_line, starting_line, ending_line, max_lines, print_list):
	if selected_line == None or selected_line == 0 or selected_line <= starting_line:
		if selected_line != None and selected_line <= starting_line and selected_line > 0:
			starting_line -= 1
			selected_line -= 1
			if max_lines > 14:
				max_lines -= 1
			else:
				starting_line = 0
				max_lines = 13
		else:
			selected_line = len(print_list)-1
			max_lines = len(print_list)
			if (len(print_list)) > 14:
				starting_line = max_lines-14
			else:
				max_lines = len(print_list)
	else:
		selected_line -= 1
	return (selected_line, starting_line, max_lines)



#UI
class ui_button:
	def __init__(self, surface, button_text, size, coords, box_color_mouseover = constants.COLOR_GREEN, box_color_default = constants.COLOR_BLUE, text_color_mouseover = constants.COLOR_BLACK, text_color_default = constants.COLOR_WHITE):
		self.surface = surface
		self.button_text = button_text
		self.size = size
		self.coords = coords
		self.c_box_mo = box_color_mouseover
		self.c_box_def = box_color_default
		self.c_box_cur = self.c_box_def
		self.c_text_mo = text_color_mouseover
		self.c_text_def = text_color_default
		self.c_text_cur = self.c_text_def
		self.rect = pygame.Rect(coords, size)
		self.rect.center = coords

	def update(self, player_input):
		mouse_pos, events_list = player_input
		mouse_x, mouse_y = mouse_pos
		mouse_clicked = False

		mouse_over = (mouse_x >= self.rect.left and mouse_x <= self.rect.right and mouse_y >= self.rect.top and mouse_y <= self.rect.bottom)
		
		if mouse_over:
			self.c_box_cur = self.c_box_mo
			self.c_text_cur = self.c_text_mo
		else:
			self.c_box_cur = self.c_box_def
			self.c_text_cur = self.c_text_def

		for event in events_list:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					mouse_clicked = True

		if mouse_over and mouse_clicked:
			return True
		else:
			return False

		
	def draw(self):
		pygame.draw.rect(self.surface, self.c_box_cur, self.rect)
		draw_text(self.surface, self.button_text, self.coords, self.c_text_cur, center = True)

class ui_slider:
	def __init__(self, surface, size, coords, parameter_value = 0.50):
		self.surface = surface
		self.size = size
		self.current_value = parameter_value
		self.bg_rect = pygame.Rect(coords, size)
		self.bg_rect.center = coords
		self.guard_rect = pygame.Rect(self.bg_rect.left-4, self.bg_rect.top-4,self.bg_rect.width+8,self.bg_rect.height+8)
		self.fg_rect = pygame.Rect((self.bg_rect.topleft), (int(self.bg_rect.width*self.current_value),self.bg_rect.height))
		self.grip_tab = pygame.Rect(self.fg_rect.topright,(4, self.bg_rect.height))

	def update(self, player_input):
		mouse_pos, events_list = player_input
		mouse_x, mouse_y = mouse_pos
		mouse_down = pygame.mouse.get_pressed()[0] == 1

		mouse_over = (mouse_x >= self.bg_rect.left and mouse_x <= self.bg_rect.right and mouse_y >= self.bg_rect.top and mouse_y <= self.bg_rect.bottom)
		
		for event in events_list:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					mouse_clicked = True
		if mouse_over and mouse_down:
			self.current_value = (mouse_x - self.bg_rect.left)/self.bg_rect.width
			self.fg_rect.width = self.bg_rect.width*self.current_value
			self.grip_tab.topleft = self.fg_rect.topright
			return self.current_value
		else:
			return self.current_value

		
	def draw(self):
		pygame.draw.rect(self.surface, constants.COLOR_DEFAULT_BG, self.guard_rect)
		pygame.draw.rect(self.surface, constants.COLOR_BLUE, self.bg_rect)
		pygame.draw.rect(self.surface, constants.COLOR_GREEN, self.fg_rect)
		pygame.draw.rect(self.surface, constants.COLOR_BLACK, self.grip_tab)

#MENUS
def menu_main():
	game_initialize()
	menu_running = True

	title_y = constants.CAM_HEIGHT/2 - 40
	title_text = "Sexy Roguelike"
	build = "INDEV 2.0"
	new_game_button = ui_button(SURFACE_MAIN, "New Game", (150, 35), (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2+20))
	load_game_button = ui_button(SURFACE_MAIN, "Load Game", (150, 35), (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2+60))
	options_button = ui_button(SURFACE_MAIN, "Options", (150, 35), (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2+100))
	quit_button = ui_button(SURFACE_MAIN, "Quit", (150, 35), (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2+140))
	pygame.mixer.music.load(ASSETS.music_menu)
	pygame.mixer.music.play(-1)
	while menu_running == True:
		SURFACE_MAIN.fill(constants.COLOR_BLACK)
		
		mouse_pos = pygame.mouse.get_pos()
		menu_events = pygame.event.get()
		game_input = (mouse_pos, menu_events)
		for event in menu_events:
			if event.type == pygame.QUIT:
				menu_running = False
		if new_game_button.update(game_input):
			pygame.mixer.music.stop()
			game_start()
		if load_game_button.update(game_input):
			pygame.mixer.music.stop()
			game_continue()
		if quit_button.update(game_input):
			game_exit()
		if options_button.update(game_input):
			menu_main_options()

		draw_text(SURFACE_MAIN, title_text, (constants.CAM_WIDTH/2, title_y), constants.COLOR_WHITE, font = constants.FONT_TITLE, center = True)
		draw_text(SURFACE_MAIN, build, (0, 0), constants.COLOR_WHITE, font = constants.FONT_MESSAGES)
		new_game_button.draw()
		load_game_button.draw()
		options_button.draw()
		quit_button.draw()
		pygame.display.flip()
		
	game_exit()
				
def menu_main_options():
	options_menu_surface = pygame.Surface((constants.CAM_WIDTH, constants.CAM_HEIGHT))
	options_menu_rect = pygame.Rect((0,0), (constants.CAM_WIDTH, constants.CAM_HEIGHT))
	options_menu_rect.center = (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2)
	menu_open = True
	return_button = ui_button(options_menu_surface, "Return", (150, 35), (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2+20))
	sound_slider = ui_slider(options_menu_surface, (150, 35), (constants.CAM_WIDTH/2+150, constants.CAM_HEIGHT/2+60), parameter_value = PREFERENCES.vol_sound)
	music_slider = ui_slider(options_menu_surface, (150, 35), (constants.CAM_WIDTH/2+150, constants.CAM_HEIGHT/2+100), parameter_value = PREFERENCES.vol_music)
	sound_check = False
	while menu_open:
		mouse_pos = pygame.mouse.get_pos()
		menu_events = pygame.event.get()
		game_input = (mouse_pos, menu_events)
		for event in menu_events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					menu_open = False
			if event.type == pygame.QUIT:
				game_exit()
				menu_open = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					prev_vol_s = PREFERENCES.vol_sound
					sound_check = True
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					if sound_check and prev_vol_s != PREFERENCES.vol_sound:
						pygame.mixer.Sound.play(ASSETS.sound_confuse)
		if return_button.update(game_input):
			break
		options_menu_surface.fill(constants.COLOR_BLACK)
		return_button.draw()
		sound_slider.draw()
		draw_text(options_menu_surface, "Sound", (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2+60), constants.COLOR_WHITE, font = constants.FONT_MESSAGES, center = True)
		music_slider.draw()
		draw_text(options_menu_surface, "Music", (constants.CAM_WIDTH/2, constants.CAM_HEIGHT/2+100), constants.COLOR_WHITE, font = constants.FONT_MESSAGES, center = True)
		PREFERENCES.vol_sound = sound_slider.update(game_input)
		PREFERENCES.vol_music = music_slider.update(game_input)
		ASSETS.sound_adjust()
		SURFACE_MAIN.blit(options_menu_surface, (0,0))
		pygame.display.update()


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
			elif event.type == pygame.QUIT:
				game_exit()
		draw_text(SURFACE_MAIN, menu_text, ((CAMERA.width/2)-text_width/2, (CAMERA.height/2)-text_height/2), constants.COLOR_WHITE, constants.COLOR_BLACK)
		pygame.display.flip()
		CLOCK.tick(constants.FPS_LIMIT)

def menu_inventory(target_inv):
	inv_Open = True
	menu_width = 216
	menu_height = 216
	menu_x = (CAMERA.width/2) - menu_width/2
	menu_y = (CAMERA.height/2) - menu_height/2
	starting_line = 0
	menu_font = constants.FONT_MESSAGES
	menu_text_height = helper_text_height(menu_font)
	max_lines = 14
	local_inventory_surface = pygame.Surface((menu_width, menu_height))
	selected_line = None
	while inv_Open:
		#clear the menu
		local_inventory_surface.fill(constants.COLOR_BLACK)
		#register changes
		print_list = [obj.display_name for obj in target_inv]
		inventory_events = pygame.event.get()
		mouse_x, mouse_y = pygame.mouse.get_pos()
		rel_mouse_x = mouse_x - menu_x
		rel_mouse_y = mouse_y - menu_y
		
		mouse_in_window = menu_width > rel_mouse_x > 0  and menu_height > rel_mouse_y > 0

		if (pygame.mouse.get_rel() != (0, 0)) and mouse_in_window:
			selected_line = int(rel_mouse_y/menu_text_height)
			selected_line += starting_line

		for event in inventory_events:
			if event.type == pygame.QUIT:
				game_exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_g or event.key == pygame.K_ESCAPE:
					inv_Open = False
				if event.key == pygame.K_s:
					selected_line, starting_line, max_lines = helper_scroll_down(selected_line, starting_line, ending_line, max_lines, print_list)
				if event.key == pygame.K_w:
					selected_line, starting_line, max_lines = helper_scroll_up(selected_line, starting_line, ending_line, max_lines, print_list)
				if event.key == pygame.K_e and len(print_list) > 0:
					if selected_line == None:
						selected_line = 0
					if selected_line > len(print_list) - 1:
						selected_line = len(print_list) - 1
					if target_inv == PLAYER.container.inventory:
						if not target_inv[selected_line].equipment:
							inv_Open = False
						target_inv[selected_line].item.use()
					else:
						target_inv[selected_line].item.pick_up(PLAYER)
						target_inv.pop(selected_line)
						if len(target_inv) == 0:
							inv_Open = False
				if event.key == pygame.K_f and len(print_list) > 0:
					if selected_line == None:
						selected_line = 0
					if selected_line > len(print_list) - 1:
						selected_line = len(print_list) - 1
					if target_inv == PLAYER.container.inventory:
						target_inv[selected_line].item.drop(PLAYER.x, PLAYER.y)
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					if mouse_in_window and selected_line <= (len(print_list)-1):
						inv_Open = False
						target_inv[selected_line].item.use()
		
		#draw menu
		if len(print_list) < max_lines:
			ending_line = len(print_list)
		else:
			ending_line = max_lines
		for line in range(starting_line, ending_line):
			if line == selected_line:
				draw_text(local_inventory_surface, print_list[line], (0, 0+((line-starting_line)*menu_text_height)), constants.COLOR_WHITE, constants.COLOR_GREY, menu_font)
			else:
				draw_text(local_inventory_surface, print_list[line], (0, 0+((line-starting_line)*menu_text_height)), constants.COLOR_WHITE, constants.COLOR_BLACK, menu_font)
	
		#display menu
		draw_game()
		SURFACE_MAIN.blit(local_inventory_surface, ((menu_x), (menu_y)))
		CLOCK.tick(constants.FPS_LIMIT)
		pygame.display.flip()

def menu_tile_select(coords_origin = None, max_range = None, radius = None, penetrate_walls = True, pierce_creature = True):
	menu_Open = True
	if coords_origin:
		map_coords_x, map_coords_y = coords_origin
	else:
		map_coords_x, map_coords_y = (PLAYER.x, PLAYER.y)
	while menu_Open:
		inspect_events = pygame.event.get()
		#get mouse position and speed. Sets the target map coordinates based on mouse position if the mouse moves.
		if pygame.mouse.get_rel() != (0, 0):
			mouse_x, mouse_y = pygame.mouse.get_pos()
			pxl_map_x, pxl_map_y = CAMERA.win_to_map((mouse_x, mouse_y))
			map_coords_x = int(pxl_map_x/constants.CELL_WIDTH)
			map_coords_y = int(pxl_map_y/constants.CELL_HEIGHT)

		for event in inspect_events:
			if event.type == pygame.QUIT:
				game_exit()
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
				if event.button == 3:
					return (valid_tiles[-1])
					menu_Open = False
				elif event.button == 1:
					print(valid_tiles)

		
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


		#Clear the surface
		SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
		SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)
		#updates the camera
		CAMERA.update((PLAYER.x, PLAYER.y))
		#draw the map
		draw_map(GAME.current_map)
		#draw the characters
		for obj in GAME.current_objects:
			obj.draw()


		for (tile_x, tile_y) in valid_tiles:
			if (tile_x, tile_y) == (map_coords_x, map_coords_y):
				draw_inspect_rect((tile_x, tile_y), tile_color = constants.COLOR_WHITE, mark = "X")
			else:
				draw_inspect_rect((tile_x, tile_y), tile_color = constants.COLOR_WHITE)
		if radius:
			if not valid_tiles:
				valid_tiles.append(coords_origin)
			area_effect = map_find_radius(valid_tiles[-1], radius)
			for (tile_x, tile_y) in area_effect:
				draw_inspect_rect((tile_x, tile_y))
		
		
		SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)


		draw_debug()
		draw_messages()
		
		pygame.display.flip()
		
		CLOCK.tick(constants.FPS_LIMIT)
		
		
	
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
	pygame.mixer.Sound.play(ASSETS.sound_lightning)
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
	pygame.mixer.Sound.play(ASSETS.sound_explode)
	return "cast"

def cast_confusion(caster, duration = 5):
	point_selected = menu_tile_select()
	if point_selected == None:
		return "cancelled"
	tile_x, tile_y = point_selected
	target = map_creature_check(tile_x, tile_y)
	if target:
		old_ai = target.ai
		target.ai = com_AI_Confused(old_ai = old_ai, num_turns = duration)
		target.ai.owner = target
		game_message("The creature's eyes glaze over.", msg_color = constants.COLOR_GREEN)
		pygame.mixer.Sound.play(ASSETS.sound_confuse)
		return "confused"
	else:
		return "cancelled"

#GENERATORS

#items
def gen_item(coords, forced_range = (1, 12)):
	global GAME
	r_min, r_max = forced_range
	generated_item = libtcod.random_get_int(0, r_min, r_max)
	new_item = None
	if generated_item == 1 or generated_item == 2:
		new_item = gen_lightning_scroll(coords)
	elif generated_item == 3 or generated_item == 4:
		new_item = gen_fireball_scroll(coords)
	elif generated_item == 5 or generated_item == 6:
		new_item = gen_confusion_scroll(coords)
	elif generated_item == 7 or generated_item == 8:
		new_item = gen_weapon_sword(coords)
	elif generated_item == 9 or generated_item == 10:
		new_item = gen_armour_shield(coords)
	elif generated_item == 11 or generated_item == 12:
		new_item = gen_healing_potion(coords)
	return new_item

def gen_lightning_scroll(coords):
	x, y = coords
	max_range = libtcod.random_get_int(0, 6, 20)
	damage = libtcod.random_get_int(0, 5, 10)
	returned_object = obj_Actor(x, y, "S_SCROLL", "Scroll", "Lightning Scroll", item = com_Item(use_function = cast_lightning, use_func_helper = (max_range, damage)))	
	GAME.current_objects.insert(1, returned_object)
	return returned_object

def gen_fireball_scroll(coords):
	x, y = coords
	max_range = libtcod.random_get_int(0, 6, 20)
	damage = libtcod.random_get_int(0, 5, 10)
	radius = libtcod.random_get_int(0, 1, 5)
	returned_object = obj_Actor(x, y, "S_SCROLL", "Scroll", "Fireball Scroll", item = com_Item(use_function = cast_fireball, use_func_helper = (max_range, radius, damage)))	
	GAME.current_objects.insert(1, returned_object)
	return returned_object

def gen_confusion_scroll(coords):
	x, y = coords
	duration = libtcod.random_get_int(0, 1, 6)
	returned_object = obj_Actor(x, y, "S_SCROLL", "Scroll", "Confusion Scroll", item = com_Item(use_function = cast_confusion, use_func_helper = duration))	
	GAME.current_objects.insert(1, returned_object)
	return returned_object

def gen_healing_potion(coords):
	x, y = coords
	healing = libtcod.random_get_int(0, 2, 10)
	returned_object = obj_Actor(x, y, "S_HEALTH_POTION", "Potion", "Healing Potion", item = com_Item(use_function = cast_heal, use_func_helper = healing))
	GAME.current_objects.insert(1, returned_object)
	return returned_object	

def gen_weapon_sword(coords):
	x, y = coords
	bonus = libtcod.random_get_int(0, 1, 4)
	returned_object = obj_Actor(x, y, "S_SWORD", "Weapon", "+" + str(bonus) + " Sword", equipment = com_Equipment(atk_bonus = bonus, slot = "main_hand"))
	GAME.current_objects.insert(1, returned_object)
	return returned_object

def gen_armour_shield(coords):
	x, y = coords
	bonus = libtcod.random_get_int(0, 1, 4)
	returned_object = obj_Actor(x, y, "S_SHIELD", "Armour", "+" + str(bonus) + " Shield", equipment = com_Equipment(def_bonus = bonus, slot = "off_hand"))
	GAME.current_objects.insert(1, returned_object)
	return returned_object


#characters
def gen_player(coords):
	global PLAYER, GAME
	x, y = coords
	player_container = com_Container
	PLAYER = obj_Actor(x, y, "A_PLAYER", "Elf", "Player", creature = com_Creature("Arion", base_atk = 2, death_function = death_player_hardcore), container = player_container())
	GAME.current_objects.append(PLAYER)
	return PLAYER

def gen_undead(coords, forced_range = (1, 100)):
	global GAME
	r_min, r_max = forced_range
	random_enemy = libtcod.random_get_int(0, r_min, r_max)
	if random_enemy <= 90:
		gen_zombie(coords)
	else:
		gen_zogre(coords)

def gen_zombie(coords):
	x, y = coords
	sex_gen = libtcod.random_get_int(0, 0, 1)
	if sex_gen == 0:
		gender = "female"
	else:
		gender = "male"
	creature_name = libtcod.namegen_generate("Fantasy %s" % gender)
	
	num_carried_items = libtcod.random_get_int(0, -3, 5)
	carried_items = []
	if num_carried_items > 0:
		for item in range(num_carried_items):
			carried_items.append(gen_item((x, y), (1, 11)))
	returned_object = obj_Actor(x, y, "A_ZOMBIE", "Undead", "Zombie", creature = com_Creature(creature_name, death_function = death_monster), ai = com_AI_zombie(), container = com_Container(inventory = carried_items))
	for thing in carried_items:
		GAME.current_objects.remove(thing)
	for thing in returned_object.container.inventory:
		thing.item.current_container = returned_object.container
		if thing.equipment:
			thing.equipment.equip()
	GAME.current_objects.insert(1, returned_object)
	return returned_object

def gen_zogre(coords):
	x, y = coords
	sex_gen = libtcod.random_get_int(0, 1, 10)
	if sex_gen == 1:
		gender = "female"
	else:
		gender = "male"
	creature_name = libtcod.namegen_generate("Celtic %s" % gender)
	returned_object = obj_Actor(x, y, "A_ZOGRE", "Undead", "Zogre", creature = com_Creature(creature_name, hp = 15, base_atk = 5, base_def = 1, death_function = death_monster), ai = com_AI_zombie())
	GAME.current_objects.insert(1, returned_object)
	return returned_object

#decorum
def gen_stairs(coords, downwards):
	global GAME
	x, y = coords
	if downwards:
		stairs_com = com_Stairs(True)
		stairs = obj_Actor(x, y, "S_STAIRS_DOWN", "Stairs", "Stairs Down", stairs = stairs_com)
		GAME.current_objects.insert(0, stairs)
		return stairs
	else:
		stairs_com = com_Stairs(False)
		stairs = obj_Actor(x, y, "S_STAIRS_UP", "Stairs", "Stairs Up", stairs = stairs_com)
		GAME.current_objects.insert(0, stairs)
		return stairs



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

		if PLAYER.state is "DEAD":
			pygame.mixer.music.load(ASSETS.music_menu)
			pygame.mixer.music.play(-1)
			game_quit = True

		CLOCK.tick(constants.FPS_LIMIT)
		#draw the game
		map_calculate_fov()
		draw_game()
		pygame.display.flip()

	

def game_initialize():
	"""This functions initiatlizes the main window in pygame"""
	global SURFACE_MAIN, SURFACE_MAP, PLAYER, FOV_CALCULATE, CLOCK, ASSETS, CAMERA, PREFERENCES

	pygame.init()
	pygame.key.set_repeat(555, 85)	

	libtcod.namegen_parse("data\\namegen\\jice_celtic.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_fantasy.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_mesopotamian.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_norse.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_region.cfg")
	libtcod.namegen_parse("data\\namegen\\jice_town.cfg")
	libtcod.namegen_parse("data\\namegen\\mingos_demon.cfg")
	libtcod.namegen_parse("data\\namegen\\mingos_dwarf.cfg")
	libtcod.namegen_parse("data\\namegen\\mingos_norse.cfg")
	libtcod.namegen_parse("data\\namegen\\mingos_standard.cfg")
	libtcod.namegen_parse("data\\namegen\\mingos_town.cfg")

	CLOCK = pygame.time.Clock()

	CAMERA = obj_Camera()

	SURFACE_MAIN = pygame.display.set_mode((CAMERA.width, CAMERA.height))

	SURFACE_MAP = pygame.Surface((constants.GAME_WIDTH, constants.GAME_HEIGHT))

	FOV_CALCULATE = True
	try:
		load_preferences()
		print("Preferences Loaded")
	except:
		PREFERENCES = struc_Preferences()
		print("Preferences generated")
	ASSETS = struc_Assets()

def game_new():
	global GAME
	GAME = obj_Game()
	gen_player((0,0))
	map_place_objects(GAME.current_rooms)

def handle_player_input():
	global FOV_CALCULATE
	#get player input
	events_list = pygame.event.get()
	#TODO process player input
	for event in events_list:
		if event.type == pygame.QUIT:
			game_exit()
			return "QUIT"
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				PLAYER.creature.move((0, -1))
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_s:
				PLAYER.creature.move((0, 1))
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_a:
				PLAYER.creature.move((-1, 0))
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_d:
				PLAYER.creature.move((1, 0))
				FOV_CALCULATE = True
				return "player-moved"
			if event.key == pygame.K_e:
				objects_at_player = map_objects_at_coords(PLAYER.x, PLAYER.y)
				items_at_player = []
				for obj in objects_at_player:
					if obj.item:
						items_at_player.append(obj)
				if len(items_at_player) > 0:
					menu_inventory(items_at_player)
				else:
					for obj in objects_at_player:
						if obj.stairs:
							obj.stairs.use()
				
			if event.key == pygame.K_f:
				if len(PLAYER.container.inventory) > 0:
					PLAYER.container.inventory[-1].item.drop(PLAYER.x, PLAYER.y)
			if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
				menu_pause()
			if event.key == pygame.K_g:
				menu_inventory(PLAYER.container.inventory)
			if event.key == pygame.K_v:
				print(menu_tile_select())
				return "player-looked"
			if event.key == pygame.K_SPACE:
				return "player_passed"
			if event.key == pygame.K_l:
				GAME.next_map()
			if event.key == pygame.K_o:
				GAME.last_map()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 3:
				mouse_x, mouse_y = pygame.mouse.get_pos()
				pxl_map_x, pxl_map_y = CAMERA.win_to_map((mouse_x, mouse_y))
				map_coords_x = int(pxl_map_x/constants.CELL_WIDTH)
				map_coords_y = int(pxl_map_y/constants.CELL_HEIGHT)
				PLAYER.move_towards(map_coords_x, map_coords_y)
				FOV_CALCULATE = True
				return "player-moved"

			
	return "no-action"

def game_message(game_msg, msg_color = constants.COLOR_WHITE):
	text_width = helper_text_width(constants.FONT_MESSAGES)
	max_chars = CAMERA.width//text_width
	wrapped_text = textwrap.wrap(game_msg, max_chars)
	for msg in wrapped_text:
		GAME.message_history.append((msg, msg_color))

def save_game():
	for obj in GAME.current_objects:
		obj.animation_destroy()
		if obj.container:
			for item in obj.container.inventory:
				item.animation_destroy()
	#open a new empty shelve (possibly overwriting an old one) to write the game data
	with gzip.open('data\save_data\savegame', 'wb') as file:
		pickle.dump([GAME, PLAYER], file)
		print("game saved")
	file.close()
def preferences_save():
	with gzip.open('data\save_data\preferences', 'wb') as file:
		pickle.dump(PREFERENCES, file)
		print("preferences saved")
	file.close()

def load_game():
	global GAME, PLAYER
	with gzip.open('data\save_data\savegame', 'rb') as file:
		GAME, PLAYER = pickle.load(file)
	map_make_fov(GAME.current_map)
	for obj in GAME.current_objects:
		obj.animation_init()
		if obj.container:
			for item in obj.container.inventory:
				item.animation_init()
def load_preferences():
	global PREFERENCES
	
	with gzip.open('data\save_data\preferences', 'rb') as file:
		PREFERENCES = pickle.load(file)
def game_continue():
	try:
		load_game()
	except:
	 	game_new()
	game_main_loop()
def game_start():
	game_new()
	game_main_loop()

def game_exit():
	try:
		save_game()
	except:
		pass
	try:
		preferences_save()
	except:
		pass
	pygame.quit()
	exit()

#EXECUTE GAME
if __name__ == "__main__":
	menu_main()