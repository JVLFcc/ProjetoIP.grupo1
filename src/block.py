import pygame
from .config import *

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        super().__init__(self.game.all_sprites, self.game.blocks)

        # Pega o quinto tile (cerca) do tileset na posição (x=128, y=0)
        self.image = self.game.terrain_spritesheet.get_sprite(128, 0, TILESIZE, TILESIZE)
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE