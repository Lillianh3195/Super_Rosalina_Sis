import pygame as pg
import sys, time
from pygame.math import Vector2 as vector

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 704
TILE_SIZE = 16
ANIMATION_SPEED = 6
BG_COLOR = (80, 136, 160) 

Z_LAYERS = {
    'bg': 0,
    'bg details': 1,
    'main': 2,
    'fg': 3
}