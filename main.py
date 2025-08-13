import pygame
from code.enemies import *
from code.block import *
from code.collectible import *
from code.ground import *
from code.player import *
from code.spritesheets import *
from code.config import *
from code.collectibles import *
from code.gun_boost import *
from code.bonus_points import *
import sys
import random

class Game:
    def __init__(self):
        pygame.init()
        self.points = 0
        # sistema de kills e coletáveis
        self.enemies_killed = 0
        self.kills_for_collectible = 10  
        self.collectible_types = ['heart', 'gun', 'points'] # tipos disponiveis!
            
        self.collectible_weights = [50, 25, 25]  # 50% heart, 25% gun, 25% points
        self.guns_collected = 0
        self.player_health = 4  # Vida máxima
        self.max_health = 4
        self.game_over_flag = False

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

        self.character_spritesheet = Spritesheets('assets/images/character.png')
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
                
                if column == 'G':
                    Gun_boost(self, j, i)
                
                if column == 'O':
                    Bonus_points(self, j, i)

    def new(self):
        self.playing = True
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.col = pygame.sprite.LayeredUpdates()
        self.gun = pygame.sprite.LayeredUpdates()
        self.point_boost = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        self.enemy_bullets = pygame.sprite.LayeredUpdates()  
        self.special_collectibles = pygame.sprite.LayeredUpdates()

        self.create_tilemap()
        self.find_spawn_points()  
    # jogador toma dano
    def take_damage(self):
        if self.player_health > 0:
            self.player_health -= 1
            
            if self.player_health <= 0:
                self.game_over_flag = True
    # desenha a barra de vida
    def draw_health_bar(self):
    
        # Posição da barra de vida
        bar_x = 10
        bar_y = 90
        bar_width = 200
        bar_height = 20
        
        # Fundo da barra (cinza)
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, GRAY, background_rect)
        pygame.draw.rect(self.screen, WHITE, background_rect, 2)
        
        # Barra de vida (verde/amarelo/vermelho baseado na vida)
        health_percentage = self.player_health / self.max_health
        health_width = int(bar_width * health_percentage)
        
        if health_percentage > 0.6:
            health_color = GREEN
        elif health_percentage > 0.3:
            health_color = (255, 255, 0)  # Amarelo
        else:
            health_color = RED
        
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            pygame.draw.rect(self.screen, health_color, health_rect)
        
        # Texto da vida
        health_text = f"Vida: {self.player_health}/{self.max_health}"
        text_surface = self.font.render(health_text, True, WHITE)
        self.screen.blit(text_surface, (bar_x + bar_width + 10, bar_y - 5))
    # encontra as portas/entradas específicas do mapa
    def find_spawn_points(self):
        self.spawn_points = []
        
        map_height = len(tilemap)
        map_width = len(tilemap[0]) if tilemap else 0
        
        # verifica borda superior (primeira linha)
  
        for col in range(map_width):
            if tilemap[0][col] == '.':
                # encontrou uma abertura na borda superior
                self.spawn_points.append((col * TILESIZE, 0))
               
      
        # verifica borda inferior (última linha)

        for col in range(map_width):
            if tilemap[map_height-1][col] == '.':
                # Encontrou uma abertura na borda inferior
                self.spawn_points.append((col * TILESIZE, (map_height-1) * TILESIZE))
         
        
        # Verifica borda esquerda (primeira coluna)
     
        for row in range(map_height):
            if tilemap[row][0] == '.':
                # Encontrou uma abertura na borda esquerda
                self.spawn_points.append((0, row * TILESIZE))
           
        
        # Verifica borda direita (última coluna)
    
        for row in range(map_height):
            if tilemap[row][map_width-1] == '.':
                # Encontrou uma abertura na borda direita
                self.spawn_points.append(((map_width-1) * TILESIZE, row * TILESIZE))
         
        # se ainda não encontrou portas, vamos procurar por aberturas próximas às bordas
        if len(self.spawn_points) == 0:
            self.find_near_border_openings()
        
        # se ainda assim não encontrou, adiciona pontos manuais
        if len(self.spawn_points) == 0:
   
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
             
        
        # verifica penúltima linha (próximo à borda inferior)
        if map_height > 2:
            for col in range(map_width):
                if tilemap[map_height-2][col] == '.' and col < map_width:
                    if tilemap[map_height-1][col] == '.':
                        self.spawn_points.append((col * TILESIZE, (map_height-2) * TILESIZE))
               
        # Verifica segunda coluna (próximo à borda esquerda)
        if map_width > 1:
            for row in range(map_height):
                if tilemap[row][1] == '.':
                    if tilemap[row][0] == '.':
                        self.spawn_points.append((TILESIZE, row * TILESIZE))
        
        # Verifica penúltima coluna (próximo à borda direita)
        if map_width > 2:
            for row in range(map_height):
                if tilemap[row][map_width-2] == '.':
                    if tilemap[row][map_width-1] == '.':
                        self.spawn_points.append(((map_width-2) * TILESIZE, row * TILESIZE))
             
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
        for offset in range(-1, 2):  
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
    # checa se deveria spawnar um coletável
    def check_collectible_spawn(self):
        if self.enemies_killed >= self.kills_for_collectible:
            if self.spawn_random_collectible():
                self.enemies_killed = 0  # reseta o contador
    
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
        
        return free_count >= 3  
    # registra arma coletada
    def add_gun_collected(self):
        self.guns_collected += 1
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
 
            return True
        except Exception as e:

            return False
    # loop que checa os eventos
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    action = self.pause_menu()
                    if action == "quit":
                        self.playing = False
                        self.running = False
                    elif action == "menu":
                        self.playing = False
                    elif action == "continue":
                        pass
    # atualização de sprites
    def update(self):
        
        self.all_sprites.update()
        # aqui é chamado o sistema de spawn dos sprites(inimigos)
        self.handle_enemy_spawning()
        self.check_collectible_spawn()
        if self.game_over_flag:
            self.playing = False
    #registra as kills
    def register_enemy_kill(self):
        """Registra morte de inimigo e verifica spawn de coletável"""
        self.enemies_killed += 1
        print(f"Enemy killed! Total: {self.enemies_killed}")  # debug
        
        # verifica imediatamente se deve spawnar
        if self.enemies_killed >= self.kills_for_collectible:
            print(f"Spawning collectible after {self.enemies_killed} kills!")  # debug
            if self.spawn_random_collectible():
                self.enemies_killed = 0
                print("Kill counter reset!")  # debug   

    def spawn_random_collectible(self):
        # escolhe tipo aleatório
        collectible_type = random.choices(self.collectible_types, weights=self.collectible_weights)[0]  
        
        # encontra posição válida no mapa
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            map_width = len(tilemap[0]) if tilemap else 0
            map_height = len(tilemap)
            
            x = random.randint(1, map_width - 2)
            y = random.randint(1, map_height - 2)
            
            # verifica se é espaço livre
            if tilemap[y][x] == '.':
                # verifica se não há sprites na posição
                pos_occupied = False
                test_rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
                
                for sprite in self.all_sprites:
                    if (hasattr(sprite, 'rect') and 
                        sprite.rect.colliderect(test_rect) and 
                        not isinstance(sprite, Ground)):
                        pos_occupied = True
                        break
                
                if not pos_occupied:
                    # spawna o coletável baseado no tipo
                    if collectible_type == 'heart':
                        Collectible(self, x, y)
                    elif collectible_type == 'gun':
                        Gun_boost(self, x, y)
                    elif collectible_type == 'points':
                        Bonus_points(self, x, y)
                    
                    return True
            
            attempts += 1 

        return False
    # função q desenha todos os sprites e scoreboard
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        # Scoreboard
        scoreboard = f"Pontos: {self.points}"
        text = self.font.render(scoreboard, True, WHITE)
        self.screen.blit(text, (10, 10))
        # progresso para o proximo coletável
        remaining = self.kills_for_collectible - self.enemies_killed
        progress_text = f"Próximo coletável: {remaining} kills"
        progress_surface = self.font.render(progress_text, True, (200, 200, 0))
        self.screen.blit(progress_surface, (10, 35))
        # texto para armas
        guns_text = f"Armas: {self.guns_collected}"
        guns_surface = self.font.render(guns_text, True, (0, 255, 255))  # cor ciano
        self.screen.blit(guns_surface, (10, 60))
        # chama a função de barra de vidaa
        self.draw_health_bar()
        
        self.clock.tick(FPS)
        pygame.display.set_caption("BitCinFireshoot")
        imagem = pygame.image.load("assets/images/single.png")
        pygame.display.set_icon(imagem)
        pygame.display.update()
        
    # chamado quando um inimigo morre
    def enemy_killed(self):
        
        self.enemies_killed += 1
        
        # verifica se deve spawnar um coletável especial
  
    def add_points(self, amount):
        self.points += amount
    
    def add_life(self, amount):
        self.player_health += amount
        
    def main(self):
        # loop principal
        while self.playing:
            self.events()
            self.update()
            self.draw()
        if self.game_over_flag:
            self.playing = False
        self.running = False
    # jogador pausa
    def pause_menu(self):
        # só essas por enqnt
        menu_options = ["Continuar", "Voltar ao Menu", "Sair"]
        selected_index = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_index == 0:
                            return "continue"
                        elif selected_index == 1:
                            return "menu"
                        elif selected_index == 2:
                            return "quit"

            # fundo escuro semi-transparente
            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            # título
            title_text = self.font.render("PAUSADO", True, WHITE)
            title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
            self.screen.blit(title_text, title_rect)

            # opções
            for i, option in enumerate(menu_options):
                if i == selected_index:
                    color = RED
                    prefix = "> "
                else:
                    color = WHITE
                    prefix = "  "
                option_text = self.font.render(prefix + option, True, color)
                option_rect = option_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + i * 40))
                self.screen.blit(option_text, option_rect)

            pygame.display.update()
            pygame.display.set_caption("BitCinFireshoot")
            imagem = pygame.image.load("assets/images/single.png")
            pygame.display.set_icon(imagem)
            self.clock.tick(FPS)
    # jogador morre
    def game_over(self):
        if not self.game_over_flag:
            return None  # Nenhum game over ocorreu

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # resetando as variáveis
                        self.points = 0
                        self.enemies_killed = 0
                        self.guns_collected = 0
                        return "restart"
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"
            
            # Tela de fundo
            self.screen.fill(BLACK)

            # título Game Over
            game_over_text = self.font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
            self.screen.blit(game_over_text, game_over_rect)

            # pontuação final
            score_text = self.font.render(f"SCORE FINAL: {self.points}", True, WHITE)
            score_rect = score_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, score_rect)

            # instruções
            restart_text = self.font.render("Pressione SPACE para jogar novamente", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

            quit_text = self.font.render("Pressione ESC para sair", True, GRAY)
            quit_rect = quit_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 80))
            self.screen.blit(quit_text, quit_rect)
            
            pygame.display.update()
            pygame.display.set_caption("BitCinFireshoot")
            imagem = pygame.image.load("assets/images/single.png")
            pygame.display.set_icon(imagem)
            self.clock.tick(FPS)
            # reiniciando as variáveis
            self.player_health = 4  # Vida máxima
            self.max_health = 4
            self.game_over_flag = False
            
    def intro_screen(self):
        # tenta carregar as imagens
        try:
            background_image = pygame.image.load('assets/images/apenascomece.png').convert()
            background_image = pygame.transform.scale(background_image, (WIN_WIDTH, WIN_HEIGHT))
        except pygame.error as e:
            print(f"Erro ao carregar a imagem de fundo: {e}")
            background_image = None
        # opções do menu(só essas, por enquanto)
        menu_options = ["Iniciar Jogo", "Sair"]
        # indice selecionado(nesse caso, indice das opções)
        selected_index = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_index == 0:  # Iniciar Jogo
                            return True
                        elif selected_index == 1:  # Sair
                            return False
                        
            if background_image:
                self.screen.blit(background_image, (0, 0))
            else:
                # Se a imagem falhou ao carregar, preenche a tela com preto
                self.screen.fill(BLACK)

            # Título
            title_text = self.font.render("BitCin Fireshoot", True, WHITE)
            title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
            self.screen.blit(title_text, title_rect)

            # Opções do menu
            for i, option in enumerate(menu_options):
                if i == selected_index:
                    color = RED
                    prefix = "> "
                else:
                    color = WHITE
                    prefix = "  "

                option_text = self.font.render(prefix + option, True, color)
                option_rect = option_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + i * 40))
                self.screen.blit(option_text, option_rect)

            pygame.display.update()
            pygame.display.set_caption("BitCinFireshoot")
            imagem = pygame.image.load("assets/images/single.png")
            pygame.display.set_icon(imagem)
            self.clock.tick(FPS)
g = Game()

while True:
    if not g.intro_screen():
        break

    g.new()
    g.main()
    action = g.game_over()
pygame.quit()
sys.exit()