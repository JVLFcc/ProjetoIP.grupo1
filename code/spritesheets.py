import pygame
from code.config import *

class Spritesheets:
    def __init__(self, file):
        super().__init__()
        
        self.sheet = pygame.image.load(file).convert()
    
    def get_sprite(self, x, y, width, height):
        
        sprite = pygame.Surface([width, height])
        
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        
        return sprite