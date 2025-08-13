import pygame
import math
import random

from code.config import ENEMY_LAYER, BULLET_LAYER, TILESIZE, WIN_WIDTH, WIN_HEIGHT
from code.player import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        
        self.game = game
        self._layer = ENEMY_LAYER  
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        # posição
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        
        # tamanho
        self.width = TILESIZE
        self.height = TILESIZE
        
        # velocidade
        self.speed = 1  
        
        # Carrega a imagem
        self.image = pygame.image.load("assets/images/skeleton_transparent.png").convert_alpha()

        # Redimensiona para caber no tile
        self.image = pygame.transform.scale(self.image, (self.width*1.5, self.height*1.5))
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        self.health = 1  # morre com 1 tiro

    def update(self):
        self.move_towards_player()
        self.check_collision_with_player()

    def move_towards_player(self):
        # Move o inimigo em direção ao player
        # encontra o player
        player = None
        for sprite in self.game.all_sprites:
            if isinstance(sprite, Player):
                player = sprite
                break
        
        if not player:
            return
        
        # calcula direção para o player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        
        # normaliza o movimento (evita velocidade maior nas diagonais)
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
        
        # move em direção ao player
        old_x = self.rect.x
        old_y = self.rect.y
        
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        # evita atravessar paredes
        if pygame.sprite.spritecollideany(self, self.game.blocks):
            self.rect.x = old_x
            self.rect.y = old_y

    def check_collision_with_player(self):
        # verifica colisão com o player
        player_hit = pygame.sprite.spritecollide(self, self.game.all_sprites, False)
        for sprite in player_hit:
            if isinstance(sprite, Player):
                self.game.take_damage()  
                # por enquanto, o inimigo morre ao tocar o player(acho q vai continuar assim)
                self.kill()
                

    def take_damage(self, damage=1):
        # recebe dano
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True  # morreu
        return False  # ainda vivo

# inimigo mais inteligente que pode contornar obstáculos
class SmartEnemy(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.stuck_counter = 0
        # sistema de pathfinding simples
        self.target_x = self.rect.x
        self.target_y = self.rect.y

        self.image = pygame.image.load("assets\images\inimigo_inteligente.png").convert_alpha()  
        self.image = pygame.transform.scale(self.image, (self.width*1.5, self.height*1.5))

        self.speed = 0.8
        self.health = 2 

    def move_towards_player(self):
        # Movimento mais inteligente
        # encontra o player
        player = None
        for sprite in self.game.all_sprites:
            if isinstance(sprite, Player):
                player = sprite
                break
        
        if not player:
            return
        
        # se não conseguiu se mover por muito tempo, tenta uma direção aleatória
        if self.stuck_counter > 30:
            self.target_x = self.rect.x + random.randint(-50, 50)
            self.target_y = self.rect.y + random.randint(-50, 50)
            self.stuck_counter = 0
        else:
            # normalmente move em direção ao player
            self.target_x = player.rect.centerx
            self.target_y = player.rect.centery
        
        # calcula direção
        dx = self.target_x - self.rect.centerx
        dy = self.target_y - self.rect.centery
        
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
        
        # tenta mover
        old_x = self.rect.x
        old_y = self.rect.y
        
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        # se colidir com parede
        if pygame.sprite.spritecollideany(self, self.game.blocks):
            self.rect.x = old_x
            self.rect.y = old_y
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0

# inimigo que atira
class ShootingEnemy(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.image = pygame.image.load("assets/images/ghost_transparent.png").convert_alpha()  
        self.image = pygame.transform.scale(self.image, (self.width*1.5, self.height*1.5))
        self.speed = 0.5  # velocidade desse inimigo
        self.health = 3
        
        # sistema de tiro
        self.last_shot = 0
        self.shoot_cooldown = 1000  # 1 segundo entre tiros // coloquei só por teste
        self.shoot_range = 1500  # alcance do tiro(mt alto)

    def update(self):
        self.move_towards_player()
        self.try_shoot_player()
        self.check_collision_with_player()

    def try_shoot_player(self):
        # lógica pra atirar no jogador quando ele tiver no alcançe(sempre então kkkkkk)
        # encontra o player
        player = None
        for sprite in self.game.all_sprites:
            if isinstance(sprite, Player):
                player = sprite
                break
        
        if not player:
            return
        
        # verifica se está no alcance
        distance = math.sqrt((player.rect.centerx - self.rect.centerx)**2 + 
                           (player.rect.centery - self.rect.centery)**2)
        
        if distance <= self.shoot_range:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_cooldown:
                # cria projétil inimigo
                bullet = EnemyBullet(self.game, self.rect.centerx, self.rect.centery, 
                                   player.rect.centerx, player.rect.centery)
                self.game.all_sprites.add(bullet)
                self.game.enemy_bullets.add(bullet)
                self.last_shot = now

# projétil do inimigo
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, game, start_x, start_y, target_x, target_y):
        super().__init__()
        self.game = game
        self._layer = BULLET_LAYER
        
        self.width = 6
        self.height = 6
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((255, 0, 0))  # Vermelho
        self.rect = self.image.get_rect()
        self.rect.centerx = start_x
        self.rect.centery = start_y
        
        self.speed = 3
        
        # calcula direção para o alvo
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # remove se sair da tela
        if (self.rect.right < 0 or self.rect.left > WIN_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > WIN_HEIGHT):
            self.kill()
        
        # colisão com paredes
        if pygame.sprite.spritecollideany(self, self.game.blocks):
            self.kill()
        
        # colisão com player
        for sprite in pygame.sprite.spritecollide(self, self.game.all_sprites, False):
            if isinstance(sprite, Player):
                self.game.take_damage()
                self.kill()
                break