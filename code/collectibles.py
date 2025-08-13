import pygame
import math
import random

from code.config import *


class SpecialCollectible(pygame.sprite.Sprite):
    def __init__(self, game, x, y, collectible_type, milestone):
        super().__init__()
        
        self.game = game
        self._layer = COLLEC_LAYER + 1  # Fica acima dos coletáveis normais
        self.groups = self.game.all_sprites, self.game.col, self.game.special_collectibles
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.collectible_type = collectible_type
        self.milestone = milestone
        
        # Sistema de animação/pulsação
        self.pulse_timer = 0
        self.base_size = TILESIZE
        self.pulse_strength = 4
        
        # Define propriedades baseadas no tipo
        self.setup_collectible_properties()
        
        # Cria a imagem base
        self.create_image()
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Efeito visual de aparição
        self.spawn_timer = 0
        self.fully_spawned = False

    def setup_collectible_properties(self):
        """Define cor, pontos e efeito baseado no tipo de coletável"""
        collectible_data = {
            'power_up': {
                'color': (0, 255, 255),    # Ciano
                'points': 100,
                'effect': 'faster_shooting'
            },
            'health_pack': {
                'color': (0, 255, 0),      # Verde
                'points': 75,
                'effect': 'restore_health'
            },
            'speed_boost': {
                'color': (255, 255, 0),    # Amarelo
                'points': 150,
                'effect': 'speed_boost'
            },
            'mega_power': {
                'color': (255, 0, 255),    # Magenta
                'points': 300,
                'effect': 'mega_bullets'
            },
            'shield': {
                'color': (0, 100, 255),    # Azul
                'points': 200,
                'effect': 'temporary_shield'
            },
            'golden_heart': {
                'color': (255, 215, 0),    # Dourado
                'points': 500,
                'effect': 'golden_bonus'
            }
        }
        
        data = collectible_data.get(self.collectible_type, collectible_data['power_up'])
        self.color = data['color']
        self.points_value = data['points']
        self.effect = data['effect']

    def create_image(self):
        """Cria a imagem do coletável com efeitos visuais"""
        self.image = pygame.Surface([self.width, self.height])
        self.image.set_colorkey(BLACK)
        
        # Desenha uma forma baseada no tipo
        if self.collectible_type == 'power_up':
            # Estrela para power-up
            self.draw_star()
        elif self.collectible_type == 'health_pack':
            # Cruz para saúde
            self.draw_cross()
        elif self.collectible_type == 'speed_boost':
            # Setas para velocidade
            self.draw_arrows()
        elif self.collectible_type == 'mega_power':
            # Diamante para mega power
            self.draw_diamond()
        elif self.collectible_type == 'shield':
            # Escudo
            self.draw_shield()
        elif self.collectible_type == 'golden_heart':
            # Coração dourado
            self.draw_heart()

    def draw_star(self):
        """Desenha uma estrela"""
        center_x, center_y = self.width // 2, self.height // 2
        radius = min(self.width, self.height) // 3
        
        # Desenha um círculo como base
        pygame.draw.circle(self.image, self.color, (center_x, center_y), radius)
        # Adiciona pontos da estrela
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            end_x = center_x + math.cos(angle) * (radius + 5)
            end_y = center_y + math.sin(angle) * (radius + 5)
            pygame.draw.line(self.image, self.color, (center_x, center_y), (end_x, end_y), 3)

    def draw_cross(self):
        """Desenha uma cruz de saúde"""
        center_x, center_y = self.width // 2, self.height // 2
        size = min(self.width, self.height) // 3
        
        # Cruz vertical
        pygame.draw.rect(self.image, self.color, 
                        (center_x - size//4, center_y - size, size//2, size*2))
        # Cruz horizontal
        pygame.draw.rect(self.image, self.color, 
                        (center_x - size, center_y - size//4, size*2, size//2))

    def draw_arrows(self):
        """Desenha setas para velocidade"""
        center_x, center_y = self.width // 2, self.height // 2
        
        # Círculo base
        pygame.draw.circle(self.image, self.color, (center_x, center_y), 
                          min(self.width, self.height) // 3, 3)
        
        # Setas apontando para fora
        for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
            start_x = center_x + math.cos(angle) * 8
            start_y = center_y + math.sin(angle) * 8
            end_x = center_x + math.cos(angle) * 15
            end_y = center_y + math.sin(angle) * 15
            pygame.draw.line(self.image, self.color, (start_x, start_y), (end_x, end_y), 2)

    def draw_diamond(self):
        """Desenha um diamante"""
        center_x, center_y = self.width // 2, self.height // 2
        size = min(self.width, self.height) // 3
        
        points = [
            (center_x, center_y - size),      # topo
            (center_x + size, center_y),      # direita
            (center_x, center_y + size),      # baixo
            (center_x - size, center_y)       # esquerda
        ]
        pygame.draw.polygon(self.image, self.color, points)

    def draw_shield(self):
        """Desenha um escudo"""
        center_x, center_y = self.width // 2, self.height // 2
        radius = min(self.width, self.height) // 3
        
        # Escudo oval
        pygame.draw.ellipse(self.image, self.color, 
                           (center_x - radius, center_y - radius, 
                            radius * 2, int(radius * 1.5)))

    def draw_heart(self):
        """Desenha um coração"""
        center_x, center_y = self.width // 2, self.height // 2
        size = min(self.width, self.height) // 4
        
        # Dois círculos para o topo do coração
        pygame.draw.circle(self.image, self.color, 
                          (center_x - size//2, center_y - size//2), size//2)
        pygame.draw.circle(self.image, self.color, 
                          (center_x + size//2, center_y - size//2), size//2)
        
        # Triângulo para a parte inferior
        points = [
            (center_x - size, center_y),
            (center_x + size, center_y),
            (center_x, center_y + size)
        ]
        pygame.draw.polygon(self.image, self.color, points)

    def update(self):
        """Atualização com efeitos visuais"""
        self.pulse_timer += 1
        
        # Efeito de pulsação
        if self.pulse_timer % 30 == 0:  # Pulsa a cada 30 frames
            self.create_image()
            
            # Muda ligeiramente o tamanho
            pulse_offset = math.sin(self.pulse_timer * 0.1) * self.pulse_strength
            new_size = self.base_size + int(pulse_offset)
            
            if new_size != self.width:
                old_center = self.rect.center
                self.width = new_size
                self.height = new_size
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                self.rect = self.image.get_rect()
                self.rect.center = old_center
        
        # Efeito de aparição gradual
        if not self.fully_spawned:
            self.spawn_timer += 1
            if self.spawn_timer > 30:  # 30 frames para aparecer completamente
                self.fully_spawned = True

    def get_collected(self, player):
        """Chamado quando o coletável é coletado"""
        print(f"Coletável especial coletado: {self.collectible_type} (+{self.points_value} pontos)")
        
        # Adiciona pontos
        self.game.add_points(self.points_value)
        
        # Aplica efeito especial
        self.apply_effect(player)
        
        # Remove o coletável
        self.kill()

    def apply_effect(self, player):
        """Aplica o efeito especial do coletável"""
        if self.effect == 'faster_shooting':
            # Reduz cooldown de tiro pela metade por 10 segundos
            player.shoot_cooldown = max(50, player.shoot_cooldown // 2)
            print("Tiro mais rápido ativado!")
            
        elif self.effect == 'restore_health':
            # Se você implementar sistema de vida, pode restaurar aqui
            print("Vida restaurada!")
            
        elif self.effect == 'speed_boost':
            # Aumenta velocidade do player (você precisaria modificar PLAYER_SPEED)
            print("Velocidade aumentada!")
            
        elif self.effect == 'mega_bullets':
            # Poderia fazer balas maiores/mais poderosas
            print("Mega balas ativadas!")
            
        elif self.effect == 'temporary_shield':
            # Poderia implementar invencibilidade temporária
            print("Escudo temporário ativado!")
            
        elif self.effect == 'golden_bonus':
            # Bonus extra de pontos
            self.game.add_points(500)  # Bonus extra
            print("Bonus dourado! +500 pontos extras!")