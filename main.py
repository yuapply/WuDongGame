import pygame
import random

pygame.init()

VERTICAL = (400, 600)
HORIZONTAL = (800, 500)

WIDTH, HEIGHT = VERTICAL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WU DONG Running")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (240, 240, 240)

PRIMARY_COLOR = (70, 130, 180)
PRIMARY_HOVER = (100, 160, 210)
SUCCESS_COLOR = (60, 179, 113)
WARNING_COLOR = (255, 140, 0)
DANGER_COLOR = (220, 20, 60)

PLAYER_COLORS = {
    "square": (70, 130, 180),
    "circle": (60, 179, 113),
    "triangle": (255, 140, 0)
}

# Obstacle types
OBSTACLE_SQUARE = "square"
OBSTACLE_BIRD = "bird"
OBSTACLE_TURTLE = "turtle"
OBSTACLE_MUSHROOM = "mushroom"

OBSTACLE_COLORS = {
    OBSTACLE_SQUARE: (220, 20, 60),
    OBSTACLE_BIRD: (30, 144, 255),
    OBSTACLE_TURTLE: (34, 139, 34),
    OBSTACLE_MUSHROOM: (50, 205, 50),
}

# Fonts
font_title = pygame.font.Font(None, 52)
font_header = pygame.font.Font(None, 32)
font_normal = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 20)

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, text_color=WHITE, radius=12):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.is_selected = False
        
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (0, 0, 0, 30), shadow_rect, border_radius=self.radius)
        
        color = self.hover_color if is_hovered or self.is_selected else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.radius)
        
        border_color = WHITE if is_hovered else (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=self.radius)
        
        text_surf = font_normal.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

class SectionPanel:
    def __init__(self, x, y, width, height, title=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        
    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, border_radius=16)
        pygame.draw.rect(surface, GRAY, self.rect, 2, border_radius=16)
        
        if self.title:
            title_surf = font_header.render(self.title, True, DARK_GRAY)
            surface.blit(title_surf, (self.rect.x + 15, self.rect.y + 10))

def draw_player(shape, color, x, y, size):
    if shape == "square":
        pygame.draw.rect(screen, color, (x, y, size, size), border_radius=6)
    elif shape == "circle":
        pygame.draw.circle(screen, color, (x + size // 2, y + size // 2), size // 2)
    elif shape == "triangle":
        points = [
            (x + size // 2, y),
            (x, y + size),
            (x + size, y + size)
        ]
        pygame.draw.polygon(screen, color, points)

def draw_obstacle(obstacle_type, x, y, size):
    color = OBSTACLE_COLORS[obstacle_type]
    
    if obstacle_type == OBSTACLE_SQUARE:
        pygame.draw.rect(screen, color, (x, y, size, size), border_radius=4)
    elif obstacle_type == OBSTACLE_BIRD:
        pygame.draw.ellipse(screen, color, (x, y + 5, size, size - 10))
        pygame.draw.ellipse(screen, (200, 200, 200), (x + size//4, y + 10, size//2, size//3))
    elif obstacle_type == OBSTACLE_TURTLE:
        pygame.draw.ellipse(screen, color, (x + 2, y, size - 4, size))
        pygame.draw.circle(screen, (100, 200, 100), (x + size//2, y - 3), 6)
    elif obstacle_type == OBSTACLE_MUSHROOM:
        pygame.draw.rect(screen, (245, 222, 179), (x + size//3, y + size//2, size//3, size//2), border_radius=3)
        pygame.draw.ellipse(screen, color, (x + 2, y, size - 4, size//2 + 5))

def reset_screen(orientation):
    global WIDTH, HEIGHT, screen
    if orientation == "vertical":
        WIDTH, HEIGHT = VERTICAL
    else:
        WIDTH, HEIGHT = HORIZONTAL
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

def main():
    global screen, WIDTH, HEIGHT
    
    selected_difficulty = 1
    selected_role = "square"
    selected_orientation = "vertical"
    
    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    player_size = 40
    original_player_size = 40
    obstacles = []
    obstacle_size = 40
    spawn_timer = 0
    score = 0
    start_ticks = 0
    base_speed = 0
    current_speed = 0
    spawn_interval = 0
    
    speed_boost_timer = 0
    speed_slow_timer = 0
    shrink_timer = 0
    BOOST_DURATION = 5000
    SLOW_DURATION = 5000
    SHRINK_DURATION = 10000
    
    difficulty_settings = {
        1: {"blocks": 1, "base_speed": 3, "spawn_rate": 60, "name": "Easy"},
        2: {"blocks": 2, "base_speed": 4, "spawn_rate": 50, "name": "Medium"},
        3: {"blocks": 3, "base_speed": 5, "spawn_rate": 40, "name": "Hard"}
    }
    
    obstacle_weights = [60, 12, 12, 16]
    
    # Buttons
    orient_buttons = [
        Button(60, 135, WIDTH // 2 - 80, 30, "Vertical", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 8),
        Button(WIDTH // 2 + 10, 135, WIDTH // 2 - 80, 30, "Horizontal", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 8)
    ]
    
    diff_buttons = [
        Button(55, 240, 90, 40, "Easy", SUCCESS_COLOR, (100, 200, 140), WHITE, 10),
        Button(165, 240, 110, 40, "Medium", WARNING_COLOR, (255, 170, 50), WHITE, 10),
        Button(295, 240, 60, 40, "Hard", DANGER_COLOR, (235, 60, 90), WHITE, 10)
    ]
    
    role_buttons = [
        Button(55, 365, 90, 45, "Square", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 10),
        Button(165, 365, 90, 45, "Circle", SUCCESS_COLOR, (100, 200, 140), WHITE, 10),
        Button(275, 365, 90, 45, "Triangle", WARNING_COLOR, (255, 170, 50), WHITE, 10)
    ]
    
    start_button = Button(WIDTH // 2 - 100, 450, 200, 55, "PLAY", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 15)
    restart_button = Button(WIDTH // 2 - 100, 330, 200, 50, "RESTART", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 12)
    menu_button = Button(WIDTH // 2 - 100, 400, 200, 50, "MENU", DARK_GRAY, (80, 80, 80), WHITE, 12)
    
    clock = pygame.time.Clock()
    running = True
    game_state = MENU
    
    while running:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == MENU:
                    for i, btn in enumerate(orient_buttons):
                        if btn.is_clicked():
                            selected_orientation = "vertical" if i == 0 else "horizontal"
                    
                    for i, btn in enumerate(diff_buttons):
                        if btn.is_clicked():
                            selected_difficulty = i + 1
                    
                    roles = ["square", "circle", "triangle"]
                    for i, btn in enumerate(role_buttons):
                        if btn.is_clicked():
                            selected_role = roles[i]
                    
                    if start_button.is_clicked():
                        reset_screen(selected_orientation)
                        if selected_orientation == "vertical":
                            player_x = WIDTH // 2
                            player_y = HEIGHT - 100
                        else:
                            player_x = 50
                            player_y = HEIGHT // 2
                        obstacles = []
                        score = 0
                        start_ticks = pygame.time.get_ticks()
                        speed_boost_timer = 0
                        speed_slow_timer = 0
                        shrink_timer = 0
                        player_size = original_player_size
                        game_state = PLAYING
                
                elif game_state == GAME_OVER:
                    if restart_button.is_clicked():
                        if selected_orientation == "vertical":
                            player_x = WIDTH // 2
                            player_y = HEIGHT - 100
                        else:
                            player_x = 50
                            player_y = HEIGHT // 2
                        obstacles = []
                        score = 0
                        start_ticks = pygame.time.get_ticks()
                        speed_boost_timer = 0
                        speed_slow_timer = 0
                        shrink_timer = 0
                        player_size = original_player_size
                        game_state = PLAYING
                    elif menu_button.is_clicked():
                        reset_screen("vertical")
                        game_state = MENU
        
        if game_state == MENU:
            title_shadow = font_title.render("WU DONG Running", True, (180, 180, 180))
            screen.blit(title_shadow, (WIDTH // 2 - title_shadow.get_width() // 2 + 2, 32))
            
            title = font_title.render("WU DONG Running", True, DARK_GRAY)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
            
            orient_panel = SectionPanel(30, 100, WIDTH - 60, 70, "Orientation")
            diff_panel = SectionPanel(30, 200, WIDTH - 60, 90, "Difficulty")
            role_panel = SectionPanel(30, 320, WIDTH - 60, 100, "Player")
            
            orient_panel.draw(screen)
            diff_panel.draw(screen)
            role_panel.draw(screen)
            
            for i, btn in enumerate(orient_buttons):
                btn.is_selected = (selected_orientation == ("vertical" if i == 0 else "horizontal"))
                btn.draw(screen)
            
            for i, btn in enumerate(diff_buttons):
                btn.is_selected = (selected_difficulty == i + 1)
                btn.draw(screen)
            
            roles = ["square", "circle", "triangle"]
            for i, btn in enumerate(role_buttons):
                btn.is_selected = (selected_role == roles[i])
                btn.draw(screen)
            
            preview_x = WIDTH - 80
            preview_y = 365 + 22 - 20
            draw_player(selected_role, PLAYER_COLORS[selected_role], preview_x, preview_y, 40)
            
            # Block legend
            legend_y = 430
            legend_x = 55
            font_small_temp = pygame.font.Font(None, 18)
            
            draw_obstacle(OBSTACLE_SQUARE, legend_x, legend_y, 20)
            legend_text = font_small_temp.render("= Game Over", True, DARK_GRAY)
            screen.blit(legend_text, (legend_x + 25, legend_y + 2))
            
            draw_obstacle(OBSTACLE_BIRD, legend_x + 120, legend_y, 20)
            legend_text2 = font_small_temp.render("= Speed Up", True, (30, 144, 255))
            screen.blit(legend_text2, (legend_x + 145, legend_y + 2))
            
            draw_obstacle(OBSTACLE_TURTLE, legend_x + 220, legend_y, 20)
            legend_text3 = font_small_temp.render("= Slow", True, (34, 139, 34))
            screen.blit(legend_text3, (legend_x + 245, legend_y + 2))
            
            draw_obstacle(OBSTACLE_MUSHROOM, legend_x + 300, legend_y, 20)
            legend_text4 = font_small_temp.render("= Shrink", True, (50, 205, 50))
            screen.blit(legend_text4, (legend_x + 325, legend_y + 2))
            
            if selected_orientation == "vertical":
                control_hint = font_small.render("Controls: <- -> to move", True, (120, 120, 120))
            else:
                control_hint = font_small.render("Controls: ^ v to move", True, (120, 120, 120))
            screen.blit(control_hint, (WIDTH // 2 - control_hint.get_width() // 2, 520))
            
            start_button.draw(screen)
            
        elif game_state == PLAYING:
            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - start_ticks) / 1000
            
            settings = difficulty_settings[selected_difficulty]
            base_speed = settings["base_speed"] + (elapsed_seconds * 0.1)
            
            if speed_boost_timer > 0:
                speed_boost_timer -= clock.get_time()
                current_speed = base_speed * 1.5
            elif speed_slow_timer > 0:
                speed_slow_timer -= clock.get_time()
                current_speed = base_speed * 0.5
            else:
                current_speed = base_speed
            
            if shrink_timer > 0:
                shrink_timer -= clock.get_time()
                player_size = original_player_size * 0.6
            else:
                player_size = original_player_size
            
            spawn_interval = max(20, settings["spawn_rate"] - int(elapsed_seconds))
            
            keys = pygame.key.get_pressed()
            
            if selected_orientation == "vertical":
                if keys[pygame.K_LEFT] and player_x > 0:
                    player_x -= 5
                if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
                    player_x += 5
                
                spawn_timer += 1
                if spawn_timer >= spawn_interval:
                    spawn_timer = 0
                    for _ in range(settings["blocks"]):
                        obstacle_x = random.randint(0, WIDTH - obstacle_size)
                        obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MUSHROOM], weights=obstacle_weights)[0]
                        obstacles.append([obstacle_x, -obstacle_size, obs_type])
                
                for obstacle in obstacles:
                    obstacle[1] += current_speed
                
                obstacles = [obs for obs in obstacles if obs[1] < HEIGHT]
                
            else:
                if keys[pygame.K_UP] and player_y > 0:
                    player_y -= 5
                if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
                    player_y += 5
                
                spawn_timer += 1
                if spawn_timer >= spawn_interval:
                    spawn_timer = 0
                    for _ in range(settings["blocks"]):
                        obstacle_y = random.randint(0, HEIGHT - obstacle_size)
                        obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MUSHROOM], weights=obstacle_weights)[0]
                        obstacles.append([WIDTH, obstacle_y, obs_type])
                
                for obstacle in obstacles:
                    obstacle[0] -= current_speed
                
                obstacles = [obs for obs in obstacles if obs[0] > -obstacle_size]
            
            # Calculate center offset for smaller player
            size_offset = (original_player_size - player_size) // 2
            player_rect = pygame.Rect(player_x + size_offset, player_y + size_offset, player_size, player_size)
            
            for obstacle in obstacles:
                obs_type = obstacle[2]
                enemy_rect = pygame.Rect(obstacle[0], obstacle[1], obstacle_size, obstacle_size)
                
                if player_rect.colliderect(enemy_rect):
                    if obs_type == OBSTACLE_SQUARE:
                        game_state = GAME_OVER
                        break
                    elif obs_type == OBSTACLE_BIRD:
                        speed_boost_timer = BOOST_DURATION
                        speed_slow_timer = 0
                        obstacles.remove(obstacle)
                    elif obs_type == OBSTACLE_TURTLE:
                        speed_slow_timer = SLOW_DURATION
                        speed_boost_timer = 0
                        obstacles.remove(obstacle)
                    elif obs_type == OBSTACLE_MUSHROOM:
                        shrink_timer = SHRINK_DURATION
                        obstacles.remove(obstacle)
            
            # Draw player centered on position
            draw_player(selected_role, PLAYER_COLORS[selected_role], player_x + size_offset, player_y + size_offset, int(player_size))
            
            for obstacle in obstacles:
                draw_obstacle(obstacle[2], obstacle[0], obstacle[1], obstacle_size)
            
            score = int(elapsed_seconds * 10)
            
            status_y = 15
            score_text = font_normal.render(f"Score: {score}", True, DARK_GRAY)
            screen.blit(score_text, (15, status_y))
            
            speed_text = font_normal.render(f"Speed: {round(current_speed, 1)}", True, DARK_GRAY)
            screen.blit(speed_text, (15, status_y + 30))
            
            # Show active effects
            effect_x = WIDTH - 130
            effect_y = status_y
            if speed_boost_timer > 0:
                boost_text = font_small.render("SPEED UP!", True, (30, 144, 255))
                screen.blit(boost_text, (effect_x, effect_y))
                effect_y += 20
            elif speed_slow_timer > 0:
                slow_text = font_small.render("SLOW DOWN", True, (34, 139, 34))
                screen.blit(slow_text, (effect_x, effect_y))
                effect_y += 20
            
            if shrink_timer > 0:
                shrink_text = font_small.render("SHRINK!", True, (50, 205, 50))
                screen.blit(shrink_text, (effect_x, effect_y))
            
        elif game_state == GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            panel_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 120, 300, 240)
            pygame.draw.rect(screen, WHITE, panel_rect, border_radius=20)
            pygame.draw.rect(screen, DANGER_COLOR, panel_rect, 3, border_radius=20)
            
            game_over_text = font_title.render("GAME OVER", True, DANGER_COLOR)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 90))
            
            score_label = font_normal.render(f"Score: {score}", True, DARK_GRAY)
            screen.blit(score_label, (WIDTH // 2 - score_label.get_width() // 2, HEIGHT // 2 - 30))
            
            diff_name = difficulty_settings[selected_difficulty]["name"]
            diff_text = font_small.render(f"Difficulty: {diff_name}", True, GRAY)
            screen.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, HEIGHT // 2 + 5))
            
            restart_button.draw(screen)
            menu_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
