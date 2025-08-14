# code/player_animated.py (VERSÃO MAIS SEGURA)

import pygame
from src.player import Player
from src.animations import AnimatedSprite
import os

class PlayerAnimated(Player):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        
        try:
            spritesheet_path = os.path.join("assets", "images", "sprites", "player_sheet.png")
            self.anim = AnimatedSprite(self, spritesheet_path, frame_w=32, frame_h=48, animations={
                'idle': [0, 1, 2, 3],
                'run': [6, 7, 8, 9, 10, 11],
                'shoot': [12, 13, 14, 15]
            }, fps=10)
            
            self.image = self.anim.get_image()
            self.rect = self.image.get_rect(center=self.rect.center)

        except Exception as e:
            print(f"ERRO CRÍTICO AO CARREGAR ANIMAÇÃO DO JOGADOR: {e}")
            # Se a animação falhar, cria uma imagem de placeholder para não quebrar o jogo
            self.image = pygame.Surface((32, 48))
            self.image.fill((255, 0, 255)) # Cor rosa choque para indicar erro
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            # Define self.anim como None para o update não quebrar
            self.anim = None

    def update(self):
        super().update()
        
        # Se self.anim falhou ao carregar, não faz nada de animação
        if not self.anim:
            return

        # Lógica de animação que já tínhamos
        if self.shooting:
            self.anim.set_animation('shoot')
        elif self.x_change != 0 or self.y_change != 0:
            self.anim.set_animation('run')
        else:
            self.anim.set_animation('idle')
            
        self.anim.update()
        self.image = self.anim.get_image()