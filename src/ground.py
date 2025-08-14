import pygame
from .config import *

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        super().__init__(self.game.all_sprites)

        # Pega o primeiro tile (areia limpa) do tileset na posição (x=0, y=0)
        self.image = self.game.terrain_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE