import pygame
from code.config import *
import math
import random

class Spritesheets:
    def __init__(self, file):
        super().__init__()
        
        self.sheet = pygame.image.load(file).convert()
    
    def get_sprite(self, x, y, width, height):
        
        sprite = pygame.Surface([width, height])
        
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        
        return sprite

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        
        self.game = game
        self.layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.x_change = 0
        self.y_change = 0
        
        self.facing = 'down'
        
        self.image = self.game.character_spritesheet.get_sprite(3, 2, self.width, self.height)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update(self):
        self.movement()
        
        old_x = self.rect.x
        old_y = self.rect.y
        
        self.rect.x += self.x_change
        self.rect.y += self.y_change
        
        if pygame.sprite.spritecollideany(self, self.game.blocks):
            self.rect.x = old_x
            self.rect.y = old_y
        
        self.x_change = 0
        self.y_change = 0
    
    def movement(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a]:
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'
        
        if keys[pygame.K_d]:
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        
        if keys[pygame.K_w]:
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'
        
        if keys[pygame.K_s]:
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        
        self.game = game
        self._layer = BLOCK_LAYER
        
        self.groups = self.game.all_sprites, self.game.blocks
        
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        self.width = TILESIZE
        self.height = TILESIZE
        
        image_to_load = pygame.image.load('assets/images/rock_round.png')
        
        self.image = pygame.Surface([self.width, self.height])
        self.image.set_colorkey(BLACK)
        self.image.blit(image_to_load, (0, 0))
        
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        
        self.game = game
        self._layer = GROUND_LAYER
        
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.image = self.game.terrain_spritesheet.get_sprite(64, 352, self.width, self.height)
        
        self.rect = self.image.get_rect()
        
        self.rect.x = self.x
        self.rect.y = self.y
        