import pygame
import random
import sys

# Inicializa o pygame
pygame.init()

# Tamanho da janela
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dado 2D")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonte
font = pygame.font.SysFont(None, 72)

# Posições dos pontos do dado
def draw_dice(value):
    screen.fill(WHITE)
    center = (WIDTH // 2, HEIGHT // 2)
    radius = 15
    offset = 60

    # Define posições relativas
    positions = {
        1: [(0, 0)],
        2: [(-offset, -offset), (offset, offset)],
        3: [(-offset, -offset), (0, 0), (offset, offset)],
        4: [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)],
        5: [(-offset, -offset), (offset, -offset), (0, 0), (-offset, offset), (offset, offset)],
        6: [(-offset, -offset), (offset, -offset), (-offset, 0), (offset, 0), (-offset, offset), (offset, offset)],
    }

    # Desenha um quadrado para o dado
    pygame.draw.rect(screen, BLACK, (100, 100, 200, 200), 5)

    # Desenha os pontos
    for dx, dy in positions[value]:
        x = center[0] + dx
        y = center[1] + dy
        pygame.draw.circle(screen, BLACK, (x, y), radius)

    pygame.display.flip()

# Estado inicial
dice_value = 1
draw_dice(dice_value)

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Rola o dado ao apertar espaço ou clicar com o mouse
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            dice_value = random.randint(1, 6)
            draw_dice(dice_value)

        if event.type == pygame.MOUSEBUTTONDOWN:
            dice_value = random.randint(1, 6)
            draw_dice(dice_value)

# Encerra o pygame
pygame.quit()
sys.exit()