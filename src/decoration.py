# code/decoration.py

import pygame
from .config import *

class Decoration(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image):
        self.game = game
        # Uma camada acima do chão, mas abaixo do jogador
        self._layer = GROUND_LAYER + 1 
        super().__init__(self.game.all_sprites)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE