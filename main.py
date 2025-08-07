import pygame
from code.sprites import *
from code.config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.points = 0
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('assets/fonts/BreatheFireIii-PKLOB.ttf', 22)
        self.running = True

        self.character_spritesheet = Spritesheets('assets\images\character.png')
        self.terrain_spritesheet = Spritesheets('assets/images/terrain.png')
    
    def create_tilemap(self):
        for i, row in enumerate(tilemap):
            
            for j, column in enumerate(row):
                Ground(self, j, i)
                
                if column == "B":
                    Block(self, j, i)
                
                if column == "P":
                    Player(self, j, i)
                
                if column == "C":
                    Collectible(self, j, i)

    def new(self):
        #* a new game starts
        self.playing = True
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.col = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        
        self.create_tilemap()

    def events(self):
        # loop que checa os eventos
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
    
    def update(self):
        # atualização de sprites
        self.all_sprites.update()
    
    
    def draw(self):
        # função q desenha todos os sprites 
        # e exibe scoreboard
        scoreboard = f"Pontos: {self.points}"
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)

        text = self.font.render(scoreboard, True, True)
        self.screen.blit(text, (0,0))
        pygame.display.update()

    # função pra contabilização dos pontos
    def add_points(self, amount):
        self.points += amount
        
    def main(self):
        # loop principal
        
        while self.playing:
            self.events()
            self.update()
            self.draw()
        
        self.running = False
    
    def game_over(self):
        pass
    
    def intro_screen(self):
        pass

g = Game()
g.intro_screen()
g.new()

while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()