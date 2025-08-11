import pygame
from code.config import *
from code.bullet import *

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