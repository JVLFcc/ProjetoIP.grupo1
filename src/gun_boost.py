import pygame
from src.config import *

class Gun_boost(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()

        self.game = game
        self._layer = COLLEC_LAYER
        
        self.groups = self.game.all_sprites, self.game.gun
        
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        self.width = TILESIZE
        self.height = TILESIZE 

        image_to_load = pygame.image.load('assets\images\gun_boost.jpg')
    
        self.image = pygame.Surface([self.width, self.height])
        scaled_image = pygame.transform.scale(image_to_load, (self.width, self.height))
        scaled_image = scaled_image.convert_alpha()
        self.image.set_colorkey(BLACK)
        self.image.blit(scaled_image, (0, 0))
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y