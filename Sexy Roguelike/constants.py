import pygame
import libtcodpy as libtcod

#initializes pygame
pygame.init()

#MAP VARS
MAP_WIDTH = 30
MAP_HEIGHT = 30

#game sizes
CELL_WIDTH = 16
CELL_HEIGHT = 16
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

#game colors
COLOR_DEFAULT_BG = COLOR_GREY

#Message Defaults
NUM_MESSAGES = 4