import pygame
import libtcodpy as libtcod

#initializes pygame
pygame.init()

#MAP VARS
MAP_WIDTH = 20
MAP_HEIGHT = 20

#game sizes
CELL_WIDTH = 32
CELL_HEIGHT = 32
GAME_WIDTH = MAP_WIDTH * CELL_WIDTH
GAME_HEIGHT = MAP_HEIGHT * CELL_HEIGHT

#FOV settings
FOV_ALGO = libtcod.FOV_BASIC
FOV_LIGHT_WALLS = True
SIGHT_RADIUS = 10

FPS_LIMIT = 60

#color definitions
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (100, 100, 100)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

#game colors
COLOR_DEFAULT_BG = COLOR_GREY

#Message Defaults
NUM_MESSAGES = 4


#fonts
FONT_DEBUG = pygame.font.Font("data/joystix.ttf", 16)
FONT_MESSAGES = pygame.font.Font("data/joystix.ttf", 12)
