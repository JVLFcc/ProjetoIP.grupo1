import pygame
from code.config import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        super().__init__()
        self.game = game
        self._layer = BULLET_LAYER  
        self.groups = self.game.all_sprites, self.game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = 6
        self.height = 6
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((255, 255, 0))  
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.speed = 8
        self.direction = direction
        
        # calculando velocidade pra cada direção 
        self.dx, self.dy = self.get_direction_vector(direction)

    def get_direction_vector(self, direction):
        # retorna vetor de movimento baseado na direção
        vectors = {
            'up': (0, -self.speed),
            'down': (0, self.speed),
            'left': (-self.speed, 0),
            'right': (self.speed, 0),
            'up_left': (-self.speed * 0.707, -self.speed * 0.707), 
            'up_right': (self.speed * 0.707, -self.speed * 0.707),
            'down_left': (-self.speed * 0.707, self.speed * 0.707),
            'down_right': (self.speed * 0.707, self.speed * 0.707)
        }
        return vectors.get(direction, (0, 0))

    def update(self):
        # move a bala
        self.rect.x += self.dx
        self.rect.y += self.dy

        # remove bala se ela sair da tela 
        if (self.rect.right < 0 or self.rect.left > WIN_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > WIN_HEIGHT):
            self.kill()
        
        # colisão com blocos
        if pygame.sprite.spritecollideany(self, self.game.blocks):
            self.kill()
        
        # colisão com inimigos 
        hit_enemies = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if hit_enemies:
            self.kill()
            # adiciona pontos por matar inimigos
            for enemy in hit_enemies:
                self.game.add_points(50)
                self.game.register_enemy_kill()