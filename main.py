# main.py

import pygame
import sys
import random

# Importações explícitas e claras. Sem mais linhas amarelas aqui!
from src.config import *
from src.spritesheets import Spritesheets
from src.player_animated import PlayerAnimated # Importando diretamente
from src.block import Block
from src.ground import Ground
from src.enemies import Enemy, SmartEnemy, ShootingEnemy
from src.collectible import Collectible
from src.gun_boost import Gun_boost
from src.bonus_points import Bonus_points
from src.decoration import Decoration

# NOTA: Não precisamos mais importar Player, Bullet, ou Animations aqui,
# pois eles são usados por outras classes, e não diretamente no main.py.
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
        try:
            self.font = pygame.font.Font('assets/fonts/BreatheFireIii-PKLOB.ttf', 22)
        except Exception:
            # fallback to default system font
            self.font = pygame.font.SysFont(None, 22)

        self.running = True
        # do sistema de spawn
        self.spawn_points = []
        self.last_spawn = 0
        self.spawn_cooldown = 3000  # 3 segundos entre spawns
        self.max_enemies = 10  # máximo de inimigos na tela

        # --- CORREÇÃO APLICADA AQUI ---
        # Carrega o único tileset que vamos usar para o cenário
        self.terrain_spritesheet = Spritesheets('assets/images/tileset.png')
        # Pré-carrega os tiles de decoração para usar depois
        self.floor_decoration_images = []
        # Pega o tile de pedrinhas (x=32)
        self.floor_decoration_images.append(self.terrain_spritesheet.get_sprite(32, 0, TILESIZE, TILESIZE))
        # Pega o tile de rocha (x=64)
        self.floor_decoration_images.append(self.terrain_spritesheet.get_sprite(64, 0, TILESIZE, TILESIZE))
        # Pega o tile de mato seco (x=96)
        self.floor_decoration_images.append(self.terrain_spritesheet.get_sprite(96, 0, TILESIZE, TILESIZE))

    def add_floor_decorations(self):
        """ Percorre o mapa e adiciona decorações aleatórias nos espaços de chão. """
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                # Apenas coloca decoração em espaços vazios ('.')
                if column == '.':
                    # Chance de 20% de colocar uma decoração
                    if random.random() < 0.20:
                        # Escolhe uma das imagens de decoração que pré-carregamos
                        deco_image = random.choice(self.floor_decoration_images)
                        Decoration(self, j, i, deco_image)

    def create_tilemap(self):
        # Lógica correta para um jogo Top-Down
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                # Sempre cria o chão de areia base por baixo
                Ground(self, j, i)
                
                # Cria cercas, jogador, etc. por cima
                if column == "B":
                    Block(self, j, i)
                elif column == "P":
                    self.player = PlayerAnimated(self, j, i)
                
                # Cria coletáveis iniciais
                elif column == "C": Collectible(self, j, i)
                elif column == 'G': Gun_boost(self, j, i)
                elif column == 'O': Bonus_points(self, j, i)

        self.add_floor_decorations()

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
        bar_x = 10
        bar_y = 90
        bar_width = 200
        bar_height = 20
        
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, GRAY, background_rect)
        pygame.draw.rect(self.screen, WHITE, background_rect, 2)
        
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
        
        health_text = f"Vida: {self.player_health}/{self.max_health}"
        text_surface = self.font.render(health_text, True, WHITE)
        self.screen.blit(text_surface, (bar_x + bar_width + 10, bar_y - 5))

    def find_spawn_points(self):
        self.spawn_points = []
        map_height = len(tilemap)
        map_width = len(tilemap[0]) if tilemap else 0

        for col in range(map_width):
            if tilemap[0][col] == '.':
                self.spawn_points.append((col * TILESIZE, 0))
        
        for col in range(map_width):
            if tilemap[map_height - 1][col] == '.':
                self.spawn_points.append((col * TILESIZE, (map_height - 1) * TILESIZE))

        for row in range(map_height):
            if tilemap[row][0] == '.':
                self.spawn_points.append((0, row * TILESIZE))
        
        for row in range(map_height):
            if tilemap[row][map_width - 1] == '.':
                self.spawn_points.append(((map_width - 1) * TILESIZE, row * TILESIZE))

        if len(self.spawn_points) == 0:
            self.find_near_border_openings()
        
        if len(self.spawn_points) == 0:
            self.add_manual_spawn_points(map_width, map_height)

    def find_near_border_openings(self):
        map_height = len(tilemap)
        map_width = len(tilemap[0]) if tilemap else 0
        
        if map_height > 1:
            for col in range(map_width):
                if tilemap[1][col] == '.' and col < map_width:
                    if tilemap[0][col] == '.':
                        self.spawn_points.append((col * TILESIZE, TILESIZE))
        
        if map_height > 2:
            for col in range(map_width):
                if tilemap[map_height - 2][col] == '.' and col < map_width:
                    if tilemap[map_height - 1][col] == '.':
                        self.spawn_points.append((col * TILESIZE, (map_height - 2) * TILESIZE))
        
        if map_width > 1:
            for row in range(map_height):
                if tilemap[row][1] == '.':
                    if tilemap[row][0] == '.':
                        self.spawn_points.append((TILESIZE, row * TILESIZE))
        
        if map_width > 2:
            for row in range(map_height):
                if tilemap[row][map_width - 2] == '.':
                    if tilemap[row][map_width - 1] == '.':
                        self.spawn_points.append(((map_width - 2) * TILESIZE, row * TILESIZE))

    def add_manual_spawn_points(self, map_width, map_height):
        possible_points = []
        mid_col = map_width // 2
        for offset in range(-2, 3):
            col = mid_col + offset
            if 0 <= col < map_width:
                possible_points.append((col * TILESIZE, 0))
        
        for offset in range(-2, 3):
            col = mid_col + offset
            if 0 <= col < map_width:
                possible_points.append((col * TILESIZE, (map_height - 1) * TILESIZE))
        
        mid_row = map_height // 2
        for offset in range(-1, 2):
            row = mid_row + offset
            if 0 <= row < map_height:
                possible_points.append((0, row * TILESIZE))
                possible_points.append(((map_width - 1) * TILESIZE, row * TILESIZE))
        
        for x, y in possible_points:
            grid_x = x // TILESIZE
            grid_y = y // TILESIZE
            
            if (0 <= grid_y < map_height and 
                0 <= grid_x < map_width and 
                tilemap[grid_y][grid_x] != 'B'):
                self.spawn_points.append((x, y))

    def check_collectible_spawn(self):
        if self.enemies_killed >= self.kills_for_collectible:
            if self.spawn_random_collectible():
                self.enemies_killed = 0

    def add_gun_collected(self):
        self.guns_collected += 1

    def handle_enemy_spawning(self):
        current_enemies = len(self.enemies)
        
        if self.points < 100:
            target_cooldown = 3000
            target_max_enemies = 5
        elif self.points < 300:
            target_cooldown = 2500
            target_max_enemies = 8
        elif self.points < 600:
            target_cooldown = 1000
            target_max_enemies = 12
        else:
            target_cooldown = 500
            target_max_enemies = 15
        
        if self.spawn_cooldown > target_cooldown:
            self.spawn_cooldown = max(target_cooldown, self.spawn_cooldown - 50)
        self.max_enemies = target_max_enemies
        
        if current_enemies < self.max_enemies:
            now = pygame.time.get_ticks()
            if now - self.last_spawn > self.spawn_cooldown:
                if self.spawn_enemy():
                    self.last_spawn = now

    def spawn_enemy(self):
        if not self.spawn_points:
            return False
        
        spawn_x, spawn_y = random.choice(self.spawn_points)
        grid_x = spawn_x // TILESIZE
        grid_y = spawn_y // TILESIZE
        
        if (0 <= grid_y < len(tilemap) and 
            0 <= grid_x < len(tilemap[grid_y]) and 
            tilemap[grid_y][grid_x] == 'B'):
            return False
        
        try:
            enemy_types = [Enemy, SmartEnemy, ShootingEnemy]
            weights = [50, 30, 20]
            enemy_type = random.choices(enemy_types, weights=weights)[0]
            
            # ################################################################ #
            # AQUI ESTÁ A MUDANÇA PRINCIPAL: O if/else foi removido.           #
            # Agora, qualquer inimigo sorteado é criado da mesma forma simples.#
            # ################################################################ #

            enemy_type(self, grid_x, grid_y)

            return True
        except Exception as e:
            return False

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

    def update(self):
        self.all_sprites.update()
        self.handle_enemy_spawning()
        self.check_collectible_spawn()
        if self.game_over_flag:
            self.playing = False

    def register_enemy_kill(self):
        self.enemies_killed += 1
        if self.enemies_killed >= self.kills_for_collectible:
            if self.spawn_random_collectible():
                self.enemies_killed = 0

    def spawn_random_collectible(self):
        collectible_type = random.choices(self.collectible_types, weights=self.collectible_weights)[0]
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            map_width = len(tilemap[0]) if tilemap else 0
            map_height = len(tilemap)
            
            x = random.randint(1, map_width - 2)
            y = random.randint(1, map_height - 2)
            
            if tilemap[y][x] == '.':
                pos_occupied = False
                test_rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
                
                for sprite in self.all_sprites:
                    if (hasattr(sprite, 'rect') and 
                        sprite.rect.colliderect(test_rect) and 
                        not isinstance(sprite, Ground)):
                        pos_occupied = True
                        break
                
                if not pos_occupied:
                    if collectible_type == 'heart':
                        Collectible(self, x, y)
                    elif collectible_type == 'gun':
                        Gun_boost(self, x, y)
                    elif collectible_type == 'points':
                        Bonus_points(self, x, y)
                    
                    return True
            
            attempts += 1
        return False

    def draw(self):
        # Cor de fundo de areia que combina com os tiles
        self.screen.fill((201, 169, 101)) 
        
        # Desenha todos os sprites (chão, cercas, jogador, etc.) por cima
        self.all_sprites.draw(self.screen)
        
        # O resto do seu código de UI (placar, vida, etc.)
        scoreboard = f"Pontos: {self.points}"
        text = self.font.render(scoreboard, True, BLACK) # Use BLACK para o texto contrastar com a areia
        self.screen.blit(text, (10, 10))
        
        remaining = self.kills_for_collectible - self.enemies_killed
        progress_text = f"Próximo coletável: {remaining} kills"
        progress_surface = self.font.render(progress_text, True, (100, 100, 0)) # Cor mais escura
        self.screen.blit(progress_surface, (10, 35))
        
        guns_text = f"Armas: {self.guns_collected}"
        guns_surface = self.font.render(guns_text, True, (0, 100, 100)) # Cor mais escura
        self.screen.blit(guns_surface, (10, 60))
        
        self.draw_health_bar()
        
        self.clock.tick(FPS)
        pygame.display.update()

    def add_points(self, amount):
        self.points += amount
    
    def add_life(self, amount):
        self.player_health = min(self.max_health, self.player_health + amount)

    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        if self.game_over_flag:
            self.playing = False

    def pause_menu(self):
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

            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            title_text = self.font.render("PAUSADO", True, WHITE)
            title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
            self.screen.blit(title_text, title_rect)

            for i, option in enumerate(menu_options):
                color = RED if i == selected_index else WHITE
                prefix = "> " if i == selected_index else "  "
                option_text = self.font.render(prefix + option, True, color)
                option_rect = option_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + i * 40))
                self.screen.blit(option_text, option_rect)

            pygame.display.update()
            self.clock.tick(FPS)

    def game_over(self):
        if not self.game_over_flag:
            return None

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player_health = self.max_health
                        self.game_over_flag = False
                        return "restart"
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"
            
            self.screen.fill(BLACK)
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 100))
            self.screen.blit(game_over_text, game_over_rect)

            score_text = self.font.render(f"SCORE FINAL: {self.points}", True, WHITE)
            score_rect = score_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, score_rect)

            restart_text = self.font.render("Pressione SPACE para jogar novamente", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
            
            quit_text = self.font.render("Pressione ESC para sair", True, GRAY)
            quit_rect = quit_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 80))
            self.screen.blit(quit_text, quit_rect)
            
            pygame.display.update()
            self.clock.tick(FPS)

   # Em main.py, substitua sua função intro_screen por esta:

    def intro_screen(self):
        # --- 1. Carregar todas as imagens do menu ---
        try:
            background_image = pygame.image.load('assets/images/apenascomece.png').convert()
            background_image = pygame.transform.scale(background_image, (WIN_WIDTH, WIN_HEIGHT))
            
            path_ui = 'assets/images/ui/'
            img_iniciar_normal = pygame.image.load(path_ui + 'botao_iniciar_normal.png').convert_alpha()
            img_iniciar_selecionado = pygame.image.load(path_ui + 'botao_iniciar_selecionado.png').convert_alpha()
            img_sair_normal = pygame.image.load(path_ui + 'botao_sair_normal.png').convert_alpha()
            img_sair_selecionado = pygame.image.load(path_ui + 'botao_sair_selecionado.png').convert_alpha()
            img_seletor = pygame.image.load(path_ui + 'seletor_bala.png').convert_alpha()

            # --- AJUSTE 1: AUMENTAR A ESCALA DOS BOTÕES ---
            # Você pode mudar este número. 1.2 = 20% maior, 1.5 = 50% maior, etc.
            fator_escala = 1.2 
            
            # Pega o tamanho original para calcular o novo tamanho
            largura_original, altura_original = img_iniciar_normal.get_size()
            nova_largura = int(largura_original * fator_escala)
            nova_altura = int(altura_original * fator_escala)
            
            # Redimensiona todas as imagens dos botões
            img_iniciar_normal = pygame.transform.scale(img_iniciar_normal, (nova_largura, nova_altura))
            img_iniciar_selecionado = pygame.transform.scale(img_iniciar_selecionado, (nova_largura, nova_altura))
            img_sair_normal = pygame.transform.scale(img_sair_normal, (nova_largura, nova_altura))
            img_sair_selecionado = pygame.transform.scale(img_sair_selecionado, (nova_largura, nova_altura))

        except pygame.error as e:
            print(f"Erro ao carregar imagens do menu: {e}")
            return True # Permite que o jogo continue mesmo com erro

        menu_options = ["Iniciar Jogo", "Sair"] 
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
                        if selected_index == 0: return True
                        elif selected_index == 1: return False
            
            # Desenha o fundo
            self.screen.blit(background_image, (0, 0))

            # --- AJUSTE 2: REMOÇÃO DO TÍTULO ---
            # As linhas que desenhavam "BitCin Fireshoot" foram comentadas com '#'
            # Se um dia quiser o título de volta, é só remover os '#' abaixo.
            # title_text = self.font.render("BitCin Fireshoot", True, WHITE)
            # title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 4))
            # self.screen.blit(title_text, title_rect)

            # --- AJUSTE 3: NOVAS POSIÇÕES DOS BOTÕES ---
            # A posição Y foi aumentada para descer os botões.
            # WIN_HEIGHT // 2 + 80 os coloca mais para baixo do centro.
            pos_iniciar_y = WIN_HEIGHT // 2 + 80
            # A distância entre eles também foi aumentada para 100 pixels.
            pos_sair_y = pos_iniciar_y + 100 
            
            # Desenha o botão de Iniciar Jogo
            if selected_index == 0:
                btn_iniciar_img = img_iniciar_selecionado
            else:
                btn_iniciar_img = img_iniciar_normal
            rect_iniciar = btn_iniciar_img.get_rect(center=(WIN_WIDTH // 2, pos_iniciar_y))
            self.screen.blit(btn_iniciar_img, rect_iniciar)
            
            # Desenha o botão de Sair
            if selected_index == 1:
                btn_sair_img = img_sair_selecionado
            else:
                btn_sair_img = img_sair_normal
            rect_sair = btn_sair_img.get_rect(center=(WIN_WIDTH // 2, pos_sair_y))
            self.screen.blit(btn_sair_img, rect_sair)

            # Desenha o seletor (a bala) ao lado do botão selecionado
            if selected_index == 0:
                rect_selecionado = rect_iniciar
            else:
                rect_selecionado = rect_sair
            
            rect_seletor = img_seletor.get_rect(center=(rect_selecionado.left - 40, rect_selecionado.centery))
            self.screen.blit(img_seletor, rect_seletor)

            pygame.display.update()
            self.clock.tick(FPS)

# Loop principal do Jogo
g = Game()
while g.running:
    if not g.intro_screen():
        break
    
    # Reinicia o estado do jogo para uma nova partida
    g.new()
    g.main()
    
    # Lida com o que acontece após o fim do jogo (game over ou volta ao menu)
    action = g.game_over()
    if action == "quit":
        break
    elif action == "restart":
        # Reseta variáveis para um novo jogo
        g.points = 0
        g.enemies_killed = 0
        g.guns_collected = 0
        continue # Volta para o início do loop 'while g.running'

pygame.quit()
sys.exit()