import pygame
import random
import sys
import time

# Inicialização do pygame
pygame.init()

# Janela
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rolagem de Dado")

# Fonte
font = pygame.font.SysFont(None, 150)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Função para desenhar o dado
def draw_dice(value):
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (100, 100, 200, 200), 5)
    text = font.render(str(value), True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

# Função para simular rolagem
def roll_dice_animation():
    for _ in range(20):  # número de frames da rolagem
        value = random.randint(1, 6)
        draw_dice(value)
        pygame.time.delay(50 + _ * 3)  # aumenta o delay para simular desaceleração
    return value

# Estado inicial
dice_value = 1
draw_dice(dice_value)

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Rola o dado ao apertar espaço ou clicar
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            dice_value = roll_dice_animation()

        if event.type == pygame.MOUSEBUTTONDOWN:
            dice_value = roll_dice_animation()

# Encerra
pygame.quit()
sys.exit()