import pygame
from config import *
import sys

# Adicione este método à classe Game, substituindo o método intro_screen existente:

def intro_screen(self):
    """Tela inicial simples do jogo"""
    intro_running = True
    
    while intro_running:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    intro_running = False  # Inicia o jogo
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Desenha a tela
        self.screen.fill(BLACK)
        
        # Título do jogo
        title_text = self.font.render("BitCin da Pradaria", True, WHITE)
        title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Instruções básicas
        start_text = self.font.render("Pressione ESPAÇO para iniciar", True, WHITE)
        start_rect = start_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
        self.screen.blit(start_text, start_rect)
        
        # Controles
        controls_text = self.font.render("WASD: Mover | Setas: Atirar | ESC: Sair", True, GRAY)
        controls_rect = controls_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 50))
        self.screen.blit(controls_text, controls_rect)
        
        pygame.display.update()
        self.clock.tick(FPS)