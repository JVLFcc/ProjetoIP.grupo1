# code/player.py (VERSÃO CORRIGIDA E FINAL)

import pygame
from src.config import *
from src.bullet import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER 
        self.groups = self.game.all_sprites
        
        super().__init__(self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        # --- AQUI ESTÁ A CORREÇÃO PRINCIPAL ---
        # A largura é baseada no TILESIZE, mas a altura deve ser a altura real
        # do seu sprite de personagem, que é 48, e não 32.
        self.width = TILESIZE
        self.height = 48  # <-- MUDANÇA CRÍTICA AQUI!
        
        self.x_change = 0
        self.y_change = 0
        
        self.facing = 'down'
        self.normal_speed = PLAYER_SPEED
        self.slow_speed = PLAYER_SLOW_SPEED
        self.current_speed = self.normal_speed
        
        # Esta imagem é apenas um placeholder, então não importa muito.
        # O importante é que o self.rect seja criado com o tamanho correto.
        self.image = pygame.Surface((self.width, self.height))
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.last_shot = 0
        self.shoot_cooldown = 500
        self.shooting = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown:
            self.shooting = True
            start_x = self.rect.centerx
            start_y = self.rect.centery
            bullet = Bullet(self.game, start_x, start_y, self.facing)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)
            self.last_shot = now

    def update(self):
        self.shooting = False
        self.movement()
        
        old_x = self.rect.x
        old_y = self.rect.y
        
        self.rect.x += self.x_change
        self.rect.y += self.y_change
        
        if pygame.sprite.spritecollideany(self, self.game.blocks):
            self.rect.x = old_x
            self.rect.y = old_y
        
        collected_items = pygame.sprite.spritecollide(self, self.game.col, True)
        collected_gun = pygame.sprite.spritecollide(self, self.game.gun, True)
        bonus_points = pygame.sprite.spritecollide(self, self.game.point_boost, True)
        
        if collected_items:
            for item in collected_items:
                if self.game.player_health < 4:
                    self.game.add_life(1)

        if collected_gun:
            for item in collected_gun:
                self.shoot_cooldown = 100
                self.game.add_gun_collected() 
        
        if bonus_points:
            self.game.add_points(500)
            
        self.x_change = 0
        self.y_change = 0
    
    def movement(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.current_speed = self.slow_speed
        else:
            self.current_speed = self.normal_speed
    
        if keys[pygame.K_a]:
            self.x_change -= self.current_speed
            self.facing = 'left'
        
        if keys[pygame.K_d]:
            self.x_change += self.current_speed
            self.facing = 'right'
        
        if keys[pygame.K_w]:
            self.y_change -= self.current_speed
            self.facing = 'up'
        
        if keys[pygame.K_s]:
            self.y_change += self.current_speed
            self.facing = 'down'
        
        shoot_direction = self.get_shoot_direction(keys)
        if shoot_direction:
            self.shoot_in_direction(shoot_direction)

    def get_shoot_direction(self, keys):
        shoot_x, shoot_y = 0, 0
        
        if keys[pygame.K_LEFT]: shoot_x = -1
        if keys[pygame.K_RIGHT]: shoot_x = 1
        if keys[pygame.K_UP]: shoot_y = -1
        if keys[pygame.K_DOWN]: shoot_y = 1
        
        if shoot_x == 0 and shoot_y == 0:
            return None
        
        # Lógica para converter direções em strings...
        if shoot_x == -1 and shoot_y == -1: return 'up_left'
        elif shoot_x == 0 and shoot_y == -1: return 'up'
        elif shoot_x == 1 and shoot_y == -1: return 'up_right'
        elif shoot_x == -1 and shoot_y == 0: return 'left'
        elif shoot_x == 1 and shoot_y == 0: return 'right'
        elif shoot_x == -1 and shoot_y == 1: return 'down_left'
        elif shoot_x == 0 and shoot_y == 1: return 'down'
        elif shoot_x == 1 and shoot_y == 1: return 'down_right'
        
    def shoot_in_direction(self, direction):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown:
            self.shooting = True
            
            start_x = self.rect.centerx
            start_y = self.rect.centery
            bullet = Bullet(self.game, start_x, start_y, direction)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)
            self.last_shot = now