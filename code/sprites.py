import pygame
from code.config import *
from code.enemies import *
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

        self.last_shot = 0
        self.shoot_cooldown = 200  

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown:

            start_x = self.rect.centerx
            start_y = self.rect.centery
            bullet = Bullet(self.game, start_x, start_y, self.facing)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)
            
           
            self.last_shot = now

    def update(self):
        self.movement()
        
        old_x = self.rect.x
        old_y = self.rect.y
        
        self.rect.x += self.x_change
        self.rect.y += self.y_change
        
        if pygame.sprite.spritecollideany(self, self.game.blocks):
            self.rect.x = old_x
            self.rect.y = old_y
        
        # lida com a colisão dos coletáveis
            
        collected_items = pygame.sprite.spritecollide(self, self.game.col, True)
        
        if collected_items:
            for item in collected_items:
                self.game.add_points(10)
            
            
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
        
        # tiro
        shoot_direction = self.get_shoot_direction(keys)
        if shoot_direction:
            self.shoot_in_direction(shoot_direction)

    def get_shoot_direction(self, keys):
        shoot_x = 0
        shoot_y = 0
        
        # Verifica teclas de seta
        if keys[pygame.K_LEFT]:
            shoot_x = -1
        if keys[pygame.K_RIGHT]:
            shoot_x = 1
        if keys[pygame.K_UP]:
            shoot_y = -1
        if keys[pygame.K_DOWN]:
            shoot_y = 1
        
        # se nenhuma seta foi pressionada e tals
        if shoot_x == 0 and shoot_y == 0:
            return None
        
        # retorna direção como string
        if shoot_x == -1 and shoot_y == -1:
            return 'up_left'
        elif shoot_x == 0 and shoot_y == -1:
            return 'up'
        elif shoot_x == 1 and shoot_y == -1:
            return 'up_right'
        elif shoot_x == -1 and shoot_y == 0:
            return 'left'
        elif shoot_x == 1 and shoot_y == 0:
            return 'right'
        elif shoot_x == -1 and shoot_y == 1:
            return 'down_left'
        elif shoot_x == 0 and shoot_y == 1:
            return 'down'
        elif shoot_x == 1 and shoot_y == 1:
            return 'down_right'

    def shoot_in_direction(self, direction):
        # atira na direção especificada pelas setas
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown:
            start_x = self.rect.centerx
            start_y = self.rect.centery
            bullet = Bullet(self.game, start_x, start_y, direction)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)
            self.last_shot = now



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

class Collectible(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()

        self.game = game
        self._layer = COLLEC_LAYER
        
        self.groups = self.game.all_sprites, self.game.col
        
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        self.width = TILESIZE
        self.height = TILESIZE 

        image_to_load = pygame.image.load('assets\images\heart.png')
    
        self.image = pygame.Surface([self.width, self.height])
        scaled_image = pygame.transform.scale(image_to_load, (self.width, self.height))
        scaled_image = scaled_image.convert_alpha()
        self.image.set_colorkey(BLACK)
        self.image.blit(scaled_image, (0, 0))
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

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

