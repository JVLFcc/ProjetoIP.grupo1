# code/spritesheets.py (VERSÃO CORRIGIDA)

import pygame

class Spritesheets:
    def __init__(self, file):
        # Carrega a imagem usando .convert_alpha() para manter a transparência
        try:
            self.sheet = pygame.image.load(file).convert_alpha()
        except pygame.error as e:
            print(f"Não foi possível carregar a spritesheet: {file}")
            raise SystemExit(e)

    def get_sprite(self, x, y, width, height):
        """ Recorta um sprite da folha. """
        
        # Cria uma nova superfície em branco com as dimensões desejadas
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Copia o pedaço da spritesheet para a nova superfície
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        
        return sprite