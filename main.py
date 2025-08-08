import pygame
from code.sprites import *
from code.config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption('Bitcin da Pradaria')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(r'assets\fonts\BreatheFireIii-PKLOB.ttf', 22)
        self.running = True

        self.character_spritesheet = Spritesheets('assets\images\character.png')
        self.terrain_spritesheet = Spritesheets(r'assets\images\terrain.png')
    
    def create_tilemap(self):
        for i, row in enumerate(tilemap):
            
            for j, column in enumerate(row):
                Ground(self, j, i)
                
                if column == "B":
                    Block(self, j, i)
                
                if column == "P":
                    Player(self, j, i)
    
    def new(self):
        #* a new game starts
        self.playing = True
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        
        self.create_tilemap()
    
    def events(self):
        #* game loop events
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
    
    def update(self):
        #* game loop updates
        self.all_sprites.update()
    
    def draw(self):
        #* game loop draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        
        pygame.display.update()
    
    def main(self):
        #* game loop
        
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