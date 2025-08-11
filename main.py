import pygame
from code.enemies import *
from code.sprites import *
from code.config import *
from code.collectibles import *
import sys
import random

class Game:
    def __init__(self):
        pygame.init()
        self.points = 0
        # sistema de kills e coletáveis
        self.enemies_killed = 0
        self.collectibles_spawned = {}  # dicionário para rastrear quais coletáveis já foram spawnados
        
        # definições dos coletáveis por kills
        self.collectible_milestones = {
            5: 'power_up',      # 5 kills = power-up (aumenta velocidade de tiro)
            10: 'health_pack',   # 10 kills = pack de vida
            15: 'speed_boost',   # 15 kills = boost de velocidade
            25: 'mega_power',    # 25 kills = mega power-up
            35: 'shield',        # 35 kills = escudo temporário
            50: 'golden_heart',  # 50 kills = coração dourado (muitos pontos)
        }

        self.bullets = pygame.sprite.Group()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('assets/fonts/BreatheFireIii-PKLOB.ttf', 22)
        self.running = True
        # do sistema de spawn
        self.spawn_points = []
        self.last_spawn = 0
        self.spawn_cooldown = 3000  # 3 segundos entre spawns
        self.max_enemies = 10  # máximo de inimigos na tela

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
        self.playing = True
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.col = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        self.enemy_bullets = pygame.sprite.LayeredUpdates()  
        self.special_collectibles = pygame.sprite.LayeredUpdates()

        self.create_tilemap()
        self.find_spawn_points()  
        
    def find_spawn_points(self):
        # encontra as portas/entradas específicas do mapa
        self.spawn_points = []
        
        map_height = len(tilemap)
        map_width = len(tilemap[0]) if tilemap else 0
        
        print("Analisando mapa para encontrar portas...")
        print(f"Dimensões do mapa: {map_width} x {map_height}")
        
        # verifica borda superior (primeira linha)
        print("Verificando borda superior...")
        for col in range(map_width):
            if tilemap[0][col] == '.':
                # encontrou uma abertura na borda superior
                self.spawn_points.append((col * TILESIZE, 0))
                print(f"Porta encontrada no topo: coluna {col}")
        
        # verifica borda inferior (última linha)
        print("Verificando borda inferior...")
        for col in range(map_width):
            if tilemap[map_height-1][col] == '.':
                # Encontrou uma abertura na borda inferior
                self.spawn_points.append((col * TILESIZE, (map_height-1) * TILESIZE))
                print(f"Porta encontrada embaixo: coluna {col}")
        
        # Verifica borda esquerda (primeira coluna)
        print("Verificando borda esquerda...")
        for row in range(map_height):
            if tilemap[row][0] == '.':
                # Encontrou uma abertura na borda esquerda
                self.spawn_points.append((0, row * TILESIZE))
                print(f"Porta encontrada à esquerda: linha {row}")
        
        # Verifica borda direita (última coluna)
        print("Verificando borda direita...")
        for row in range(map_height):
            if tilemap[row][map_width-1] == '.':
                # Encontrou uma abertura na borda direita
                self.spawn_points.append(((map_width-1) * TILESIZE, row * TILESIZE))
                print(f"Porta encontrada à direita: linha {row}")
        
        print(f"Total de portas encontradas: {len(self.spawn_points)}")
        
        # se ainda não encontrou portas, vamos procurar por aberturas próximas às bordas
        if len(self.spawn_points) == 0:
            print("Nenhuma porta nas bordas encontrada. Procurando aberturas próximas...")
            self.find_near_border_openings()
        
        # se ainda assim não encontrou, adiciona pontos manuais
        if len(self.spawn_points) == 0:
            print("Adicionando pontos de spawn manuais...")
            self.add_manual_spawn_points(map_width, map_height)
    # procura por aberturas uma célula para dentro das bordas
    def find_near_border_openings(self):
        
        map_height = len(tilemap)
        map_width = len(tilemap[0]) if tilemap else 0
        
        # verifica segunda linha (próximo à borda superior)
        if map_height > 1:
            for col in range(map_width):
                if tilemap[1][col] == '.' and col < map_width:
                    # verifica se tem caminho até a borda
                    if tilemap[0][col] == '.':
                        self.spawn_points.append((col * TILESIZE, TILESIZE))
                        print(f"Abertura próxima ao topo encontrada: coluna {col}")
        
        # verifica penúltima linha (próximo à borda inferior)
        if map_height > 2:
            for col in range(map_width):
                if tilemap[map_height-2][col] == '.' and col < map_width:
                    if tilemap[map_height-1][col] == '.':
                        self.spawn_points.append((col * TILESIZE, (map_height-2) * TILESIZE))
                        print(f"Abertura próxima ao fundo encontrada: coluna {col}")
        
        # Verifica segunda coluna (próximo à borda esquerda)
        if map_width > 1:
            for row in range(map_height):
                if tilemap[row][1] == '.':
                    if tilemap[row][0] == '.':
                        self.spawn_points.append((TILESIZE, row * TILESIZE))
                        print(f"Abertura próxima à esquerda encontrada: linha {row}")
        
        # Verifica penúltima coluna (próximo à borda direita)
        if map_width > 2:
            for row in range(map_height):
                if tilemap[row][map_width-2] == '.':
                    if tilemap[row][map_width-1] == '.':
                        self.spawn_points.append(((map_width-2) * TILESIZE, row * TILESIZE))
                        print(f"Abertura próxima à direita encontrada: linha {row}")
    # gera pontos típicos de spawn
    def add_manual_spawn_points(self, map_width, map_height):
        
        possible_points = []
        
        # entrada superior (meio-superior)
        mid_col = map_width // 2
        for offset in range(-2, 3):  # -2, -1, 0, 1, 2
            col = mid_col + offset
            if 0 <= col < map_width:
                possible_points.append((col * TILESIZE, 0))
        
        # entrada inferior (meio-inferior)
        for offset in range(-2, 3):
            col = mid_col + offset
            if 0 <= col < map_width:
                possible_points.append((col * TILESIZE, (map_height-1) * TILESIZE))
        
        # entradas laterais (meio das laterais)
        mid_row = map_height // 2
        for offset in range(-1, 2):  # -1, 0, 1
            row = mid_row + offset
            if 0 <= row < map_height:
                # Esquerda
                possible_points.append((0, row * TILESIZE))
                # Direita
                possible_points.append(((map_width-1) * TILESIZE, row * TILESIZE))
        
        # adiciona os pontos que não colidem com blocos
        for x, y in possible_points:
            grid_x = x // TILESIZE
            grid_y = y // TILESIZE
            
            if (0 <= grid_y < map_height and 
                0 <= grid_x < map_width and 
                tilemap[grid_y][grid_x] != 'B'):
                self.spawn_points.append((x, y))
                print(f"Ponto manual adicionado: ({grid_x}, {grid_y})")

    def check_free_space(self, row, col):
        # verifica se há espaço livre ao redor de uma posição
        free_count = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = row + di, col + dj
                if (0 <= ni < len(tilemap) and 
                    0 <= nj < len(tilemap[ni]) and 
                    tilemap[ni][nj] == '.'):
                    free_count += 1
        
        return free_count >= 3  # precisa de pelo menos 3 espaços livres ao redor
    # gerenciamento do spawn automatico de inimigos
    def handle_enemy_spawning(self):
        current_enemies = len(self.enemies)
        
        # sistema de fases baseado na pontuação
        if self.points < 100:
            # fase 1: spawn lento
            target_cooldown = 3000
            target_max_enemies = 5
        elif self.points < 300:
            # fase 2: spawn moderado
            target_cooldown = 2500
            target_max_enemies = 8
        elif self.points < 600:
            # fase 3: spawn rápido
            target_cooldown = 1000
            target_max_enemies = 12
        else:
            # fase 4+: spawn muito rápido
            target_cooldown = 500
            target_max_enemies = 15
        
        # ajusta gradualmente para os valores alvo
        if self.spawn_cooldown > target_cooldown:
            self.spawn_cooldown = max(target_cooldown, self.spawn_cooldown - 50)
        self.max_enemies = target_max_enemies
        
        # só spawna se não atingiu o limite máximo
        if current_enemies < self.max_enemies:
            now = pygame.time.get_ticks()
            if now - self.last_spawn > self.spawn_cooldown:
                if self.spawn_enemy():  # só atualiza se conseguiu spawnar
                    self.last_spawn = now
    # função que spawna inimigo em um lugar aleatório
    def spawn_enemy(self):
        
        if not self.spawn_points:
            print("Nenhum ponto de spawn disponível!")
            return False
        
        # escolhe um ponto de spawn aleatório
        spawn_x, spawn_y = random.choice(self.spawn_points)
        
        # converte para coordenadas de grid
        grid_x = spawn_x // TILESIZE
        grid_y = spawn_y // TILESIZE
        
        # verifica se a posição não está ocupada por um bloco
        if (0 <= grid_y < len(tilemap) and 
            0 <= grid_x < len(tilemap[grid_y]) and 
            tilemap[grid_y][grid_x] == 'B'):
            return False  # não spawna em cima de bloco
        
        try:
            # escolhe tipo de inimigo aleatório
            enemy_types = [Enemy, SmartEnemy, ShootingEnemy]
            # se quiserem mudar os pesos de spawn dos tipos de inimigo:

            weights = [50, 30, 20]  # 50 básico, 30% inteligente, 20% atirador
            
            enemy_type = random.choices(enemy_types, weights=weights)[0]
            enemy_type(self, grid_x, grid_y)
            print(f"Inimigo spawnou em ({grid_x}, {grid_y})")
            return True
        except Exception as e:
            print(f"Erro ao spawnar inimigo: {e}")
            return False
    # loop que checa os eventos
    def events(self):
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
    # atualização de sprites
    def update(self):
        
        self.all_sprites.update()
        # aqui é chamado o sistema de spawn dos sprites(inimigos)
        self.handle_enemy_spawning()
    # função q desenha todos os sprites 
    def draw(self):
        # e exibe scoreboard
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        
        # Scoreboard
        scoreboard = f"Pontos: {self.points}"
        text = self.font.render(scoreboard, True, WHITE)
        self.screen.blit(text, (10, 10))
        
        # contador de inimigos (pra debug)
        enemy_count = f"Inimigos: {len(self.enemies)}"
        enemy_text = self.font.render(enemy_count, True, WHITE)
        self.screen.blit(enemy_text, (10, 40)) 
        
        self.clock.tick(FPS)
        pygame.display.update()
    # chamado quando um inimigo morre
    def enemy_killed(self):
        
        self.enemies_killed += 1
        print(f"Inimigos mortos: {self.enemies_killed}")
        
        # verifica se deve spawnar um coletável especial
        self.check_collectible_spawn()
    # verifica se algum milestone foi atingido e spawna coletável
    def check_collectible_spawn(self):
        
        for kills_required, collectible_type in self.collectible_milestones.items():
            # se atingiu o milestone e ainda não spawnou este coletável
            if (self.enemies_killed >= kills_required and 
                kills_required not in self.collectibles_spawned):
                
                self.spawn_special_collectible(collectible_type, kills_required)
                self.collectibles_spawned[kills_required] = collectible_type
                print(f"Coletável especial spawnou: {collectible_type}")
    # Spawna um coletável especial em local aleatório 
    def spawn_special_collectible(self, collectible_type, milestone):
        
        # Encontra uma posição válida no mapa
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            # Escolhe uma posição aleatória no mapa
            map_width = len(tilemap[0]) if tilemap else 0
            map_height = len(tilemap)
            
            x = random.randint(1, map_width - 2)
            y = random.randint(1, map_height - 2)
            
            # Verifica se a posição é válida (não é bloco)
            if tilemap[y][x] == '.':
                # Verifica se não há outros sprites na posição
                pos_occupied = False
                test_rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
                
                for sprite in self.all_sprites:
                    if (hasattr(sprite, 'rect') and 
                        sprite.rect.colliderect(test_rect) and 
                        not isinstance(sprite, Ground)):
                        pos_occupied = True
                        break
                
                if not pos_occupied:
                    # Spawna o coletável especial
                    SpecialCollectible(self, x, y, collectible_type, milestone)
                    break
            
            attempts += 1
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