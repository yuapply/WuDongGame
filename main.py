import pygame
import random
import math

import game_globals
from constants import (
    BG_TOP, BG_BOTTOM, PRIMARY_COLOR, PRIMARY_HOVER, PRIMARY_GLOW,
    SUCCESS_COLOR, WARNING_COLOR, DANGER_COLOR, NEON_CYAN, WHITE,
    PLAYER_COLORS, PLAYER_GLOW_COLORS,
    OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MUSHROOM,
    OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN, OBSTACLE_STEEL_BAR, OBSTACLE_XRAY_GUN,
    OBSTACLE_COLORS, OBSTACLE_GLOW_COLORS,
    MENU, PLAYING, GAME_OVER, ENTER_NAME, LEADERBOARD, LEVEL_TRANSITION, BOSS_DEFEATED,
)
from scores import load_scores, save_scores, is_high_score
from cache import get_cached_gradient, get_scanline_overlay, clear_caches
from entities import (
    ParticleSystem, ScorePopup, ParallaxBackground, MenuParticle, Button, SectionPanel,
)
from drawing import (
    draw_glow, draw_player, draw_obstacle, draw_xray_beam, draw_speed_lines,
    draw_boss, draw_boss_projectile, draw_boss_health_bar, draw_player_trail,
)
from game_globals import (
    font_title, font_header, font_menu_section, font_normal, font_small, font_popup,
)


def main():
    # Bind display globals as local variables; rebind after any reset_screen() call
    screen = game_globals.screen
    WIDTH = game_globals.WIDTH
    HEIGHT = game_globals.HEIGHT

    selected_difficulty = 1
    selected_role = "spaceship"
    selected_orientation = "vertical"

    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    player_size = 30
    original_player_size = 30
    obstacles = []
    obstacle_size = 40
    spawn_timer = 0
    score = 0
    bonus_score = 0
    start_ticks = 0
    base_speed = 0
    current_speed = 0
    spawn_interval = 0
    current_level = 1
    level_start_ticks = 0
    LEVEL_DURATION = 45000

    # Level transition stats
    level_obstacles_passed = 0
    level_obstacles_destroyed = 0
    level_start_obstacle_count = 0

    # Transition state
    transition_start_ticks = 0
    COUNTDOWN_DURATION = 3000

    speed_boost_timer = 0
    speed_slow_timer = 0
    BOOST_DURATION = 5000
    SLOW_DURATION = 5000
    machinegun_timer = 0
    MACHINEGUN_DURATION = 10000
    shotgun_timer = 0
    SHOTGUN_DURATION = 10000
    XRAY_DURATION = 10000
    xray_timer = 0
    shotgun_cooldown = 0
    bullets = []
    bullet_cooldown = 0

    particle_system = ParticleSystem()
    score_popups = []

    # Player trail
    player_trail = []
    TRAIL_LENGTH = 15

    # Screen shake
    shake_intensity = 0.0
    shake_decay = 0.85

    # Game over animation
    game_over_timer = 0
    GAME_OVER_ANIM_FRAMES = 20

    # Leaderboard state
    player_name = ""
    leaderboard_from = MENU
    name_cursor_blink = 0
    qualifies_for_leaderboard = False
    last_saved_score_name = ""

    # Parallax
    parallax = ParallaxBackground(WIDTH, HEIGHT)

    # Menu particles
    menu_particles = [MenuParticle(WIDTH, HEIGHT) for _ in range(30)]

    # Last score for popup tracking
    last_obstacle_count = 0

    # Boss state
    BOSS_TRIGGER_TIME = 45000
    boss_active = False
    boss_health = 0
    boss_max_health = 200 + (current_level - 1) * 50
    boss_size = 120
    boss_x = 0
    boss_y = 0
    boss_projectiles = []
    boss_attack_timer = 0
    boss_attack_interval = 8
    boss_pattern_timer = 0
    boss_current_pattern = 0
    boss_direction = 1
    boss_speed = 2

    # Boss attack patterns
    BOSS_PATTERNS = ["tight_spread", "wide_spread", "random_scatter", "line"]

    difficulty_settings = {
        1: {"blocks": 1, "base_speed": 3, "spawn_rate": 60, "name": "Easy", "steel_bar_weight": 12},
        2: {"blocks": 2, "base_speed": 4, "spawn_rate": 50, "name": "Medium", "steel_bar_weight": 8},
        3: {"blocks": 3, "base_speed": 5, "spawn_rate": 40, "name": "Hard", "steel_bar_weight": 4}
    }

    obstacle_weights = [55, 6, 6, 4, 3, 12, 4]

    orient_buttons = [
        Button(60, 135, WIDTH // 2 - 80, 35, "Vertical", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 12),
        Button(WIDTH // 2 + 10, 135, WIDTH // 2 - 80, 35, "Horizontal", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 12)
    ]

    diff_buttons = [
        Button(55, 245, 90, 45, "Easy", SUCCESS_COLOR, (52, 211, 153), WHITE, 12),
        Button(165, 245, 110, 45, "Medium", WARNING_COLOR, (251, 191, 36), WHITE, 12),
        Button(295, 245, 60, 45, "Hard", DANGER_COLOR, (248, 113, 113), WHITE, 12)
    ]

    role_buttons = [
        Button(65, 370, 75, 40, "Ship", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 10, font_small),
        Button(170, 370, 75, 40, "Plane", SUCCESS_COLOR, (52, 211, 153), WHITE, 10, font_small),
        Button(275, 370, 75, 40, "Dragon", WARNING_COLOR, (251, 191, 36), WHITE, 10, font_small)
    ]

    start_button = Button(WIDTH // 2 - 100, 460, 200, 55, "PLAY", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 18)
    scores_menu_button = Button(WIDTH // 2 - 100, 525, 200, 45, "SCORES", WARNING_COLOR, (251, 191, 36), WHITE, 14)
    help_button = Button(WIDTH // 2 - 50, 575, 100, 22, "? Help", (30, 80, 130), (60, 130, 190), WHITE, 8, font_small)
    restart_button = Button(WIDTH // 2 - 100, 320, 200, 50, "RESTART", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 14)
    menu_button = Button(WIDTH // 2 - 100, 380, 200, 50, "MENU", (100, 116, 139), (148, 163, 184), WHITE, 14)
    save_score_button = Button(WIDTH // 2 - 100, 440, 200, 50, "SAVE SCORE", SUCCESS_COLOR, (52, 211, 153), WHITE, 14)
    scores_gameover_button = Button(WIDTH // 2 - 100, 440, 200, 50, "SCORES", WARNING_COLOR, (251, 191, 36), WHITE, 14)
    submit_name_button = Button(WIDTH // 2 - 80, 0, 160, 45, "SUBMIT", SUCCESS_COLOR, (52, 211, 153), WHITE, 14)
    leaderboard_back_button = Button(WIDTH // 2 - 100, 0, 200, 50, "BACK", (100, 116, 139), (148, 163, 184), WHITE, 14)
    leaderboard_menu_button = Button(WIDTH // 2 - 100, 0, 200, 50, "MENU", (100, 116, 139), (148, 163, 184), WHITE, 14)
    leaderboard_restart_button = Button(WIDTH // 2 - 100, 0, 200, 50, "RESTART", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 14)

    clock = pygame.time.Clock()
    running = True
    game_state = MENU
    show_help = False
    time_offset = 0

    while running:
        time_offset += 1

        # --- Screen shake offset ---
        shake_offset_x, shake_offset_y = 0, 0
        if shake_intensity > 0.5:
            shake_offset_x = int(random.uniform(-shake_intensity, shake_intensity))
            shake_offset_y = int(random.uniform(-shake_intensity, shake_intensity))
            shake_intensity *= shake_decay

        # --- Background ---
        bg = get_cached_gradient(WIDTH, HEIGHT, BG_TOP, BG_BOTTOM)
        screen.blit(bg, (0, 0))

        if game_state == MENU:
            parallax.update(0.3)
            parallax.draw(screen, selected_orientation)
        elif game_state == PLAYING:
            parallax.update(current_speed * 0.3 if current_speed else 0.5)
            parallax.draw(screen, selected_orientation)
        else:
            parallax.draw(screen, selected_orientation)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == MENU:
                    if show_help:
                        show_help = False
                    else:
                        for i, btn in enumerate(orient_buttons):
                            if btn.is_clicked():
                                selected_orientation = "vertical" if i == 0 else "horizontal"

                        for i, btn in enumerate(diff_buttons):
                            if btn.is_clicked():
                                selected_difficulty = i + 1

                        roles = ["spaceship", "aeroplane", "dragon"]
                        for i, btn in enumerate(role_buttons):
                            if btn.is_clicked():
                                selected_role = roles[i]

                        if help_button.is_clicked():
                            show_help = True

                        if start_button.is_clicked():
                            game_globals.reset_screen(selected_orientation)
                            screen = game_globals.screen
                            WIDTH = game_globals.WIDTH
                            HEIGHT = game_globals.HEIGHT
                            parallax.resize(WIDTH, HEIGHT)
                            clear_caches()
                            if selected_orientation == "vertical":
                                player_x = WIDTH // 2
                                player_y = HEIGHT - 100
                            else:
                                player_x = 50
                                player_y = HEIGHT // 2
                            obstacles = []
                            score = 0
                            bonus_score = 0
                            start_ticks = pygame.time.get_ticks()
                            level_start_ticks = pygame.time.get_ticks()
                            current_level = 1
                            spawn_timer = 0
                            current_speed = 0
                            speed_boost_timer = 0
                            speed_slow_timer = 0

                            machinegun_timer = 0
                            shotgun_timer = 0
                            xray_timer = 0
                            shotgun_cooldown = 0
                            bullets = []
                            bullet_cooldown = 0
                            player_size = original_player_size
                            particle_system = ParticleSystem()
                            player_trail = []
                            score_popups = []
                            last_obstacle_count = 0
                            shake_intensity = 0
                            game_over_timer = 0
                            level_obstacles_passed = 0
                            level_obstacles_destroyed = 0
                            transition_start_ticks = 0
                            player_name = ""
                            boss_active = False
                            boss_health = 0
                            boss_projectiles = []
                            boss_attack_timer = 0
                            boss_pattern_timer = 0
                            boss_current_pattern = 0
                            boss_direction = 1
                            game_state = PLAYING

                        if scores_menu_button.is_clicked():
                            leaderboard_from = MENU
                            last_saved_score_name = ""
                            game_state = LEADERBOARD

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
                            bonus_score = 0
                            start_ticks = pygame.time.get_ticks()
                            level_start_ticks = pygame.time.get_ticks()
                            current_level = 1
                            spawn_timer = 0
                            current_speed = 0
                        speed_boost_timer = 0
                        speed_slow_timer = 0

                        machinegun_timer = 0
                        shotgun_timer = 0
                        xray_timer = 0
                        shotgun_cooldown = 0
                        bullets = []
                        bullet_cooldown = 0
                        player_size = original_player_size
                        particle_system = ParticleSystem()
                        player_trail = []
                        score_popups = []
                        last_obstacle_count = 0
                        shake_intensity = 0
                        game_over_timer = 0
                        level_obstacles_passed = 0
                        level_obstacles_destroyed = 0
                        transition_start_ticks = 0
                        player_name = ""
                        boss_active = False
                        boss_health = 0
                        boss_projectiles = []
                        boss_attack_timer = 0
                        boss_pattern_timer = 0
                        boss_current_pattern = 0
                        boss_direction = 1
                        game_state = PLAYING
                    elif menu_button.is_clicked():
                        game_globals.reset_screen("vertical")
                        screen = game_globals.screen
                        WIDTH = game_globals.WIDTH
                        HEIGHT = game_globals.HEIGHT
                        parallax.resize(WIDTH, HEIGHT)
                        clear_caches()
                        menu_particles = [MenuParticle(WIDTH, HEIGHT) for _ in range(30)]
                        player_trail = []
                        score_popups = []
                        shake_intensity = 0
                        game_over_timer = 0
                        game_state = MENU
                    elif qualifies_for_leaderboard and save_score_button.is_clicked():
                        player_name = ""
                        name_cursor_blink = 0
                        game_state = ENTER_NAME
                    elif not qualifies_for_leaderboard and scores_gameover_button.is_clicked():
                        leaderboard_from = GAME_OVER
                        last_saved_score_name = ""
                        game_state = LEADERBOARD

                elif game_state == ENTER_NAME:
                    if submit_name_button.is_clicked():
                        final_name = player_name.strip() if player_name.strip() else "???"
                        scores_list = load_scores()
                        scores_list.append({"name": final_name, "score": score})
                        scores_list.sort(key=lambda s: s["score"], reverse=True)
                        scores_list = scores_list[:10]
                        save_scores(scores_list)
                        last_saved_score_name = final_name
                        qualifies_for_leaderboard = False
                        leaderboard_from = GAME_OVER
                        game_state = LEADERBOARD

                elif game_state == LEADERBOARD:
                    if leaderboard_from == MENU:
                        if leaderboard_back_button.is_clicked():
                            game_state = MENU
                    else:
                        if leaderboard_menu_button.is_clicked():
                            game_globals.reset_screen("vertical")
                            screen = game_globals.screen
                            WIDTH = game_globals.WIDTH
                            HEIGHT = game_globals.HEIGHT
                            parallax.resize(WIDTH, HEIGHT)
                            clear_caches()
                            menu_particles = [MenuParticle(WIDTH, HEIGHT) for _ in range(30)]
                            player_trail = []
                            score_popups = []
                            shake_intensity = 0
                            game_over_timer = 0
                            game_state = MENU
                        elif leaderboard_restart_button.is_clicked():
                            if selected_orientation == "vertical":
                                player_x = WIDTH // 2
                                player_y = HEIGHT - 100
                            else:
                                player_x = 50
                                player_y = HEIGHT // 2
                            obstacles = []
                            score = 0
                            bonus_score = 0
                            start_ticks = pygame.time.get_ticks()
                            level_start_ticks = pygame.time.get_ticks()
                            current_level = 1
                            spawn_timer = 0
                            current_speed = 0
                            speed_boost_timer = 0
                            speed_slow_timer = 0

                            machinegun_timer = 0
                            shotgun_timer = 0
                            shotgun_cooldown = 0
                            bullets = []
                            bullet_cooldown = 0
                            player_size = original_player_size
                            particle_system = ParticleSystem()
                            player_trail = []
                            score_popups = []
                            last_obstacle_count = 0
                            shake_intensity = 0
                            game_over_timer = 0
                            level_obstacles_passed = 0
                            level_obstacles_destroyed = 0
                            transition_start_ticks = 0
                            player_name = ""
                        boss_active = False
                        boss_health = 0
                        boss_projectiles = []
                        boss_attack_timer = 0
                        boss_pattern_timer = 0
                        boss_current_pattern = 0
                        boss_direction = 1
                        game_state = PLAYING

            if event.type == pygame.KEYDOWN and game_state == ENTER_NAME:
                if event.key == pygame.K_RETURN:
                    final_name = player_name.strip() if player_name.strip() else "???"
                    scores_list = load_scores()
                    scores_list.append({"name": final_name, "score": score})
                    scores_list.sort(key=lambda s: s["score"], reverse=True)
                    scores_list = scores_list[:10]
                    save_scores(scores_list)
                    last_saved_score_name = final_name
                    qualifies_for_leaderboard = False
                    leaderboard_from = GAME_OVER
                    game_state = LEADERBOARD
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    char = event.unicode
                    if char and len(player_name) < 12 and (char.isalnum() or char == " "):
                        player_name += char

        if game_state == MENU:
            for btn in orient_buttons + diff_buttons + role_buttons + [start_button, scores_menu_button, help_button]:
                btn.update()

            # Menu floating particles
            for mp in menu_particles:
                mp.update()
                mp.draw(screen)

            # Glowing pulsing title
            title_text = "WU DONG Running"
            glow_pulse = 0.5 + 0.5 * math.sin(time_offset * 0.05)
            glow_alpha = int(30 + glow_pulse * 40)

            for i in range(3):
                glow_surf = font_title.render(title_text, True, PRIMARY_GLOW)
                glow_surface = pygame.Surface(glow_surf.get_size(), pygame.SRCALPHA)
                glow_surface.blit(glow_surf, (0, 0))
                glow_surface.set_alpha(glow_alpha - i * 10)
                screen.blit(glow_surface, (WIDTH // 2 - glow_surf.get_width() // 2 + random.randint(-1, 1),
                                           30 + random.randint(-1, 1)))

            title = font_title.render(title_text, True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 32))

            orient_panel = SectionPanel(30, 100, WIDTH - 60, 80, "Orientation")
            diff_panel = SectionPanel(30, 205, WIDTH - 60, 100, "Difficulty")
            role_panel = SectionPanel(30, 330, WIDTH - 60, 95, "Player")

            orient_panel.draw(screen)
            diff_panel.draw(screen)
            role_panel.draw(screen)

            for i, btn in enumerate(orient_buttons):
                btn.is_selected = (selected_orientation == ("vertical" if i == 0 else "horizontal"))
                btn.draw(screen)

            for i, btn in enumerate(diff_buttons):
                btn.is_selected = (selected_difficulty == i + 1)
                btn.draw(screen)

            roles = ["spaceship", "aeroplane", "dragon"]
            role_colors_list = [PLAYER_COLORS["spaceship"], PLAYER_COLORS["aeroplane"], PLAYER_COLORS["dragon"]]
            for i, btn in enumerate(role_buttons):
                btn.is_selected = (selected_role == roles[i])
                btn.draw(screen)
                preview_size = 16
                preview_x = btn.rect.x + 3
                preview_y = btn.rect.centery - preview_size // 2
                draw_player(roles[i], role_colors_list[i], preview_x, preview_y,
                            preview_size, pulse=time_offset * 0.15)

            start_button.draw(screen)
            scores_menu_button.draw(screen)
            help_button.draw(screen)

            if show_help:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, WIDTH, HEIGHT))
                screen.blit(overlay, (0, 0))

                panel_x, panel_y = 25, 80
                panel_w, panel_h = WIDTH - 50, 420
                panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                pygame.draw.rect(panel_surf, (10, 15, 35, 230), (0, 0, panel_w, panel_h), border_radius=14)
                pygame.draw.rect(panel_surf, PRIMARY_COLOR, (0, 0, panel_w, panel_h), 2, border_radius=14)
                screen.blit(panel_surf, (panel_x, panel_y))

                title_surf = font_header.render("Obstacle Guide", True, WHITE)
                screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, panel_y + 14))

                ox = panel_x + 20
                oy = panel_y + 55
                items = [
                    (OBSTACLE_SQUARE,    24, "Square  — Game Over",   (180, 190, 210)),
                    (OBSTACLE_BIRD,      24, "Bird    — Speed Up",    (96, 165, 250)),
                    (OBSTACLE_TURTLE,    24, "Turtle  — Slow Down",   (52, 211, 153)),
                    (OBSTACLE_MACHINEGUN,24, "Gun     — Machine Gun", (255, 160, 80)),
                    (OBSTACLE_SHOTGUN,   24, "Shotgun — Spread Fire", (168, 85, 247)),
                    (OBSTACLE_XRAY_GUN,  24, "X-Ray   — Beam Attack", (100, 230, 255)),
                ]
                for obs_type, obs_size, label, color in items:
                    draw_obstacle(obs_type, ox + obs_size // 2, oy + obs_size // 2, obs_size,
                                  OBSTACLE_GLOW_COLORS[obs_type], time_offset=time_offset)
                    screen.blit(font_small.render(label, True, color), (ox + obs_size + 10, oy + 3))
                    oy += 38

                oy += 6
                draw_obstacle(OBSTACLE_STEEL_BAR, ox + 30, oy + 12, 60,
                              OBSTACLE_GLOW_COLORS[OBSTACLE_STEEL_BAR], time_offset=time_offset)
                screen.blit(font_small.render("Steel Bar — Barrier", True, (180, 190, 210)), (ox + 74, oy + 3))
                oy += 38

                oy += 8
                if selected_orientation == "vertical":
                    ctrl = font_small.render("Controls: Left / Right arrow to move", True, (120, 140, 180))
                else:
                    ctrl = font_small.render("Controls: Up / Down arrow to move", True, (120, 140, 180))
                screen.blit(ctrl, (WIDTH // 2 - ctrl.get_width() // 2, oy))

                close_hint = font_small.render("Click anywhere to close", True, (80, 100, 140))
                screen.blit(close_hint, (WIDTH // 2 - close_hint.get_width() // 2, panel_y + panel_h - 24))

        elif game_state == PLAYING:
            particle_system.update()

            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - start_ticks) / 1000

            level_elapsed = current_time - level_start_ticks

            # Boss trigger logic
            if not boss_active and level_elapsed >= BOSS_TRIGGER_TIME:
                boss_active = True
                boss_max_health = 200 + (current_level - 1) * 50
                boss_health = boss_max_health
                boss_projectiles = []
                boss_attack_timer = 0
                boss_pattern_timer = 0
                boss_current_pattern = 0
                boss_direction = 1
                if selected_orientation == "vertical":
                    boss_x = (WIDTH - boss_size) // 2
                    boss_y = 120
                else:
                    boss_x = WIDTH - boss_size - 20
                    boss_y = (HEIGHT - boss_size) // 2

            if boss_active:
                if selected_orientation == "vertical":
                    boss_x += boss_speed * boss_direction
                    if boss_x <= 0:
                        boss_x = 0
                        boss_direction = 1
                    elif boss_x >= WIDTH - boss_size:
                        boss_x = WIDTH - boss_size
                        boss_direction = -1
                else:
                    boss_y += boss_speed * boss_direction
                    if boss_y <= 0:
                        boss_y = 0
                        boss_direction = 1
                    elif boss_y >= HEIGHT - boss_size:
                        boss_y = HEIGHT - boss_size
                        boss_direction = -1

            # Boss defeated check
            if boss_active and boss_health <= 0:
                boss_active = False
                transition_start_ticks = current_time
                game_state = BOSS_DEFEATED

            if level_elapsed >= LEVEL_DURATION and not boss_active:
                transition_start_ticks = current_time
                game_state = LEVEL_TRANSITION

            settings = difficulty_settings[selected_difficulty]
            base_speed = settings["base_speed"] + (level_elapsed / 1000 * 0.1)

            if speed_boost_timer > 0:
                speed_boost_timer -= clock.get_time()
                current_speed = base_speed * 1.5
            elif speed_slow_timer > 0:
                speed_slow_timer -= clock.get_time()
                current_speed = base_speed * 0.5
            else:
                current_speed = base_speed

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
                    if boss_active:
                        boss_attack_timer += 1
                        boss_pattern_timer += 1

                        if boss_pattern_timer >= 180:
                            boss_pattern_timer = 0
                            boss_current_pattern = random.randint(0, len(BOSS_PATTERNS) - 1)

                        if boss_attack_timer >= boss_attack_interval:
                            boss_attack_timer = 0
                            pattern = BOSS_PATTERNS[boss_current_pattern]

                            num_projectiles = random.randint(3, 6)

                            if pattern == "tight_spread":
                                for i in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    speed = random.uniform(3, 7)
                                    spread_range = 120
                                    offset = -spread_range // 2 + (spread_range * i // (num_projectiles - 1)) if num_projectiles > 1 else 0
                                    boss_projectiles.append([boss_x + boss_size // 2 - proj_size // 2 + offset, boss_y + boss_size, proj_size, speed])

                            elif pattern == "wide_spread":
                                for i in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    speed = random.uniform(3, 7)
                                    spread_range = 200
                                    offset = -spread_range // 2 + (spread_range * i // (num_projectiles - 1)) if num_projectiles > 1 else 0
                                    boss_projectiles.append([boss_x + boss_size // 2 - proj_size // 2 + offset, boss_y + boss_size, proj_size, speed])

                            elif pattern == "random_scatter":
                                for _ in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    offset = random.randint(-140, 140)
                                    speed = random.uniform(3, 8)
                                    boss_projectiles.append([boss_x + boss_size // 2 - proj_size // 2 + offset, boss_y + boss_size, proj_size, speed])

                            elif pattern == "line":
                                for i in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    speed = random.uniform(4, 7)
                                    offset_x = random.randint(-30, 30)
                                    boss_projectiles.append([boss_x + boss_size // 2 - proj_size // 2 + offset_x, boss_y + boss_size + i * 25, proj_size, speed])

                        # Occasionally spawn gun power-ups
                        if random.random() < 0.1:
                            mg_x = random.randint(0, WIDTH - obstacle_size)
                            gun_type = random.choice([OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN])
                            obstacles.append([mg_x, -obstacle_size, gun_type, obstacle_size])
                    else:
                        # Normal mode
                        for _ in range(settings["blocks"]):
                            current_weights = obstacle_weights.copy()
                            current_weights[5] = settings["steel_bar_weight"]
                            obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN, OBSTACLE_STEEL_BAR, OBSTACLE_XRAY_GUN], weights=current_weights)[0]
                            if obs_type == OBSTACLE_SQUARE:
                                obs_sz = random.choice([30, 40, 50, 60])
                            elif obs_type == OBSTACLE_STEEL_BAR:
                                min_width = WIDTH // 5
                                max_width = WIDTH // 3
                                obs_sz = random.randint(min_width, max_width)
                            else:
                                obs_sz = obstacle_size
                            obstacle_x = random.randint(0, WIDTH - obs_sz)
                            obstacles.append([obstacle_x, -obs_sz, obs_type, obs_sz])

                prev_count = len(obstacles)
                for obstacle in obstacles:
                    obs_speed = current_speed
                    if boss_active and obstacle[2] in (OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN):
                        obs_speed = settings["base_speed"]
                    obstacle[1] += obs_speed

                obstacles = [obs for obs in obstacles if obs[1] < HEIGHT]
                passed = prev_count - len(obstacles)
                if passed > 0:
                    level_obstacles_passed += passed
                    if len(score_popups) < 5:
                        score_popups.append(ScorePopup(player_x, player_y - 30, f"+{passed * 10}"))

                # Update boss projectiles
                for proj in boss_projectiles[:]:
                    proj[1] += proj[3]
                    if proj[1] > HEIGHT:
                        boss_projectiles.remove(proj)

            else:
                if keys[pygame.K_UP] and player_y > 0:
                    player_y -= 5
                if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
                    player_y += 5

                spawn_timer += 1
                if spawn_timer >= spawn_interval:
                    spawn_timer = 0
                    if boss_active:
                        boss_attack_timer += 1
                        boss_pattern_timer += 1

                        if boss_pattern_timer >= 180:
                            boss_pattern_timer = 0
                            boss_current_pattern = random.randint(0, len(BOSS_PATTERNS) - 1)

                        if boss_attack_timer >= boss_attack_interval:
                            boss_attack_timer = 0
                            pattern = BOSS_PATTERNS[boss_current_pattern]

                            num_projectiles = random.randint(3, 6)

                            if pattern == "tight_spread":
                                for i in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    speed = random.uniform(3, 7)
                                    spread_range = 120
                                    offset = -spread_range // 2 + (spread_range * i // (num_projectiles - 1)) if num_projectiles > 1 else 0
                                    boss_projectiles.append([boss_x - proj_size, boss_y + boss_size // 2 - proj_size // 2 + offset, proj_size, speed])

                            elif pattern == "wide_spread":
                                for i in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    speed = random.uniform(3, 7)
                                    spread_range = 200
                                    offset = -spread_range // 2 + (spread_range * i // (num_projectiles - 1)) if num_projectiles > 1 else 0
                                    boss_projectiles.append([boss_x - proj_size, boss_y + boss_size // 2 - proj_size // 2 + offset, proj_size, speed])

                            elif pattern == "random_scatter":
                                for _ in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    offset = random.randint(-140, 140)
                                    speed = random.uniform(3, 8)
                                    boss_projectiles.append([boss_x - proj_size, boss_y + boss_size // 2 - proj_size // 2 + offset, proj_size, speed])

                            elif pattern == "line":
                                for i in range(num_projectiles):
                                    proj_size = random.randint(18, 35)
                                    speed = random.uniform(4, 7)
                                    offset_y = random.randint(-30, 30)
                                    boss_projectiles.append([boss_x - proj_size - i * 25, boss_y + boss_size // 2 - proj_size // 2 + offset_y, proj_size, speed])

                        # Occasionally spawn gun power-ups
                        if random.random() < 0.1:
                            mg_y = random.randint(0, HEIGHT - obstacle_size)
                            gun_type = random.choice([OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN])
                            obstacles.append([WIDTH, mg_y, gun_type, obstacle_size])
                    else:
                        # Normal mode
                        for _ in range(settings["blocks"]):
                            current_weights = obstacle_weights.copy()
                            current_weights[5] = settings["steel_bar_weight"]
                            obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN, OBSTACLE_STEEL_BAR, OBSTACLE_XRAY_GUN], weights=current_weights)[0]
                            if obs_type == OBSTACLE_SQUARE:
                                obs_sz = random.choice([30, 40, 50, 60])
                            elif obs_type == OBSTACLE_STEEL_BAR:
                                min_width = HEIGHT // 5
                                max_width = HEIGHT // 3
                                obs_sz = random.randint(min_width, max_width)
                            else:
                                obs_sz = obstacle_size
                            obstacle_y = random.randint(0, HEIGHT - obs_sz if obs_type == OBSTACLE_STEEL_BAR else HEIGHT - 12)
                            obstacles.append([WIDTH, obstacle_y, obs_type, obs_sz])

                prev_count = len(obstacles)
                for obstacle in obstacles:
                    obs_speed = current_speed
                    if boss_active and obstacle[2] in (OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN):
                        obs_speed = settings["base_speed"]
                    obstacle[0] -= obs_speed

                obstacles = [obs for obs in obstacles if obs[0] > -obstacle_size]
                passed = prev_count - len(obstacles)
                if passed > 0:
                    level_obstacles_passed += passed
                    if len(score_popups) < 5:
                        score_popups.append(ScorePopup(player_x + player_size, player_y, f"+{passed * 10}"))

                # Update boss projectiles
                for proj in boss_projectiles[:]:
                    proj[0] -= proj[3]
                    if proj[0] < -50:
                        boss_projectiles.remove(proj)

            size_offset = (original_player_size - player_size) // 2
            player_rect = pygame.Rect(player_x + size_offset, player_y + size_offset, player_size, player_size)

            # Update player trail
            player_trail.append((player_x + size_offset, player_y + size_offset, player_size))
            if len(player_trail) > TRAIL_LENGTH:
                player_trail.pop(0)

            for obstacle in obstacles[:]:
                obs_type = obstacle[2]
                obs_sz = obstacle[3]
                if obs_type == OBSTACLE_BIRD:
                    hitbox_inset = obs_sz // 4
                    enemy_rect = pygame.Rect(obstacle[0] + hitbox_inset, obstacle[1] + hitbox_inset,
                                             obs_sz - hitbox_inset * 2, obs_sz - hitbox_inset * 2)
                elif obs_type == OBSTACLE_STEEL_BAR:
                    if selected_orientation == "vertical":
                        enemy_rect = pygame.Rect(obstacle[0], obstacle[1], obs_sz, 12)
                    else:
                        enemy_rect = pygame.Rect(obstacle[0], obstacle[1], 12, obs_sz)
                else:
                    enemy_rect = pygame.Rect(obstacle[0], obstacle[1], obs_sz, obs_sz)

                if player_rect.colliderect(enemy_rect):
                    center_x = enemy_rect.centerx
                    center_y = enemy_rect.centery

                    if obs_type == OBSTACLE_SQUARE or obs_type == OBSTACLE_STEEL_BAR:
                        particle_system.emit(center_x, center_y, DANGER_COLOR, count=25, size=8, glow=True, spread=6)
                        shake_intensity = 15.0
                        game_over_timer = 0
                        qualifies_for_leaderboard = is_high_score(score)
                        game_state = GAME_OVER
                        break
                    elif obs_type == OBSTACLE_BIRD:
                        particle_system.emit(center_x, center_y, (59, 130, 246), count=15, size=6, glow=True, spread=4)
                        speed_boost_timer = BOOST_DURATION
                        speed_slow_timer = 0
                        obstacles.remove(obstacle)
                    elif obs_type == OBSTACLE_TURTLE:
                        particle_system.emit(center_x, center_y, (16, 185, 129), count=15, size=6, glow=True, spread=4)
                        speed_slow_timer = SLOW_DURATION
                        speed_boost_timer = 0
                        obstacles.remove(obstacle)
                    elif obs_type == OBSTACLE_MACHINEGUN:
                        particle_system.emit(center_x, center_y, (255, 100, 30), count=15, size=6, glow=True, spread=4)
                        machinegun_timer = MACHINEGUN_DURATION
                        shotgun_timer = 0
                        xray_timer = 0
                        obstacles.remove(obstacle)
                    elif obs_type == OBSTACLE_SHOTGUN:
                        particle_system.emit(center_x, center_y, (168, 85, 247), count=15, size=6, glow=True, spread=4)
                        shotgun_timer = SHOTGUN_DURATION
                        machinegun_timer = 0
                        xray_timer = 0
                        obstacles.remove(obstacle)
                    elif obs_type == OBSTACLE_XRAY_GUN:
                        particle_system.emit(center_x, center_y, (100, 230, 255), count=15, size=6, glow=True, spread=4)
                        xray_timer = XRAY_DURATION
                        machinegun_timer = 0
                        shotgun_timer = 0
                        obstacles.remove(obstacle)

            # Boss projectile collision with player
            for proj in boss_projectiles[:]:
                proj_rect = pygame.Rect(proj[0], proj[1], proj[2], proj[2])
                if player_rect.colliderect(proj_rect):
                    particle_system.emit(proj_rect.centerx, proj_rect.centery, DANGER_COLOR, count=20, size=6, glow=True, spread=5)
                    shake_intensity = 10.0
                    game_over_timer = 0
                    qualifies_for_leaderboard = is_high_score(score)
                    game_state = GAME_OVER
                    break

            # --- Machinegun bullet logic ---
            dt = clock.get_time()
            if machinegun_timer > 0:
                machinegun_timer -= dt
                bullet_cooldown -= dt
                if bullet_cooldown <= 0:
                    bullet_cooldown = 150
                    bcx = player_x + size_offset + player_size // 2
                    bcy = player_y + size_offset + player_size // 2
                    if selected_orientation == "vertical":
                        bullets.append([bcx, bcy, 0, -10])
                    else:
                        bullets.append([bcx, bcy, 10, 0])

            # --- Shotgun bullet logic ---
            if shotgun_timer > 0:
                shotgun_timer -= dt
                shotgun_cooldown -= dt
                if shotgun_cooldown <= 0:
                    shotgun_cooldown = 250
                    bcx = player_x + size_offset + player_size // 2
                    bcy = player_y + size_offset + player_size // 2
                    speed = 10
                    for angle_deg in [-30, -15, 0, 15, 30]:
                        if selected_orientation == "vertical":
                            angle_rad = math.radians(angle_deg)
                            vx = speed * math.sin(angle_rad)
                            vy = -speed * math.cos(angle_rad)
                        else:
                            angle_rad = math.radians(angle_deg)
                            vx = speed * math.cos(angle_rad)
                            vy = speed * math.sin(angle_rad)
                        bullets.append([bcx, bcy, vx, vy])

            # --- X-ray gun logic ---
            if xray_timer > 0:
                xray_timer -= dt
                xray_cx = player_x + size_offset + player_size // 2
                xray_cy = player_y + size_offset + player_size // 2

                if selected_orientation == "vertical":
                    xray_beam_rect = pygame.Rect(xray_cx - 10, 0, 20, xray_cy)
                else:
                    xray_beam_rect = pygame.Rect(xray_cx, xray_cy - 7, WIDTH - xray_cx, 14)

                for obs in obstacles[:]:
                    obs_type = obs[2]
                    if obs_type in (OBSTACLE_SQUARE, OBSTACLE_STEEL_BAR):
                        if obs_type == OBSTACLE_SQUARE:
                            obs_rect = pygame.Rect(obs[0], obs[1], obs[3], obs[3])
                        else:
                            if selected_orientation == "vertical":
                                obs_rect = pygame.Rect(obs[0], obs[1], obs[3], 12)
                            else:
                                obs_rect = pygame.Rect(obs[0], obs[1], 12, obs[3])

                        if xray_beam_rect.colliderect(obs_rect):
                            level_obstacles_destroyed += 1
                            bonus_score += 15
                            cx_hit = obs_rect.centerx
                            cy_hit = obs_rect.centery
                            particle_system.emit(cx_hit, cy_hit, (100, 200, 255), count=10, size=5, glow=True, spread=3)
                            score_popups.append(ScorePopup(cx_hit, cy_hit - 20, "+15", (100, 230, 255)))
                            obstacles.remove(obs)

                if boss_active:
                    boss_rect = pygame.Rect(boss_x, boss_y, boss_size, boss_size)
                    if xray_beam_rect.colliderect(boss_rect):
                        boss_health -= 0.5
                        particle_system.emit(boss_rect.centerx, boss_rect.centery, (100, 230, 255), count=3, size=3, glow=True, spread=2)

            # Update bullets
            bullets_to_remove = []
            for b in bullets:
                b[0] += b[2]
                b[1] += b[3]
                if b[1] < -10 or b[1] > HEIGHT + 10 or b[0] < -10 or b[0] > WIDTH + 10:
                    bullets_to_remove.append(b)
            for b in bullets_to_remove:
                if b in bullets:
                    bullets.remove(b)

            # Bullet vs OBSTACLE_SQUARE collision
            bullets_hit = []
            obs_hit = []
            for b in bullets:
                for obs in obstacles:
                    if obs in obs_hit:
                        continue
                    if obs[2] == OBSTACLE_SQUARE:
                        obs_rect = pygame.Rect(obs[0], obs[1], obs[3], obs[3])
                        bullet_rect = pygame.Rect(b[0] - 4, b[1] - 4, 8, 8)
                        if bullet_rect.colliderect(obs_rect):
                            bullets_hit.append(b)
                            obs_hit.append(obs)
                            level_obstacles_destroyed += 1
                            bonus_score += 20
                            cx_hit = obs_rect.centerx
                            cy_hit = obs_rect.centery
                            particle_system.emit(cx_hit, cy_hit, (255, 150, 50), count=12, size=5, glow=True, spread=4)
                            score_popups.append(ScorePopup(cx_hit, cy_hit - 20, "+20", (255, 200, 80)))
                            shake_intensity = max(shake_intensity, 3.0)
                            break

            # Bullet vs boss projectile collision
            if boss_active:
                for b in bullets[:]:
                    bullet_rect = pygame.Rect(b[0] - 4, b[1] - 4, 8, 8)
                    for proj in boss_projectiles[:]:
                        proj_rect = pygame.Rect(proj[0], proj[1], proj[2], proj[2])
                        if bullet_rect.colliderect(proj_rect):
                            if b in bullets:
                                bullets.remove(b)
                            boss_projectiles.remove(proj)
                            particle_system.emit(proj_rect.centerx, proj_rect.centery, (255, 200, 100), count=10, size=4, glow=True, spread=3)
                            break

            # Bullet vs boss collision
            if boss_active:
                boss_rect = pygame.Rect(boss_x, boss_y, boss_size, boss_size)
                for b in bullets[:]:
                    bullet_rect = pygame.Rect(b[0] - 4, b[1] - 4, 8, 8)
                    if bullet_rect.colliderect(boss_rect):
                        bullets.remove(b)
                        boss_health -= 1
                        cx_hit = bullet_rect.centerx
                        cy_hit = bullet_rect.centery

                        boss_hit_colors = {
                            1: (100, 150, 255), 2: (200, 150, 255), 3: (255, 140, 0),
                            4: (50, 255, 100), 5: (40, 0, 80), 6: (255, 0, 0),
                            7: (0, 100, 255), 8: (150, 255, 0), 9: (200, 30, 30),
                            10: (255, 215, 0),
                        }
                        boss_color = boss_hit_colors.get(current_level, boss_hit_colors[1])

                        particle_system.emit(cx_hit, cy_hit, boss_color, count=8, size=4, glow=True, spread=3)
                        shake_intensity = max(shake_intensity, 2.0)

            for b in bullets_hit:
                if b in bullets:
                    bullets.remove(b)
            for o in obs_hit:
                if o in obstacles:
                    obstacles.remove(o)

            # Draw bullets
            for b in bullets:
                bx = int(b[0] + shake_offset_x)
                by = int(b[1] + shake_offset_y)

                glow_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (0, 150, 255, 100), (12, 12), 12)
                screen.blit(glow_surf, (bx - 12, by - 12))

                core_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(core_surf, (100, 200, 255, 200), (8, 8), 6)
                pygame.draw.circle(core_surf, (200, 230, 255, 255), (8, 8), 4)
                screen.blit(core_surf, (bx - 8, by - 8))

            # Draw X-ray beam
            if xray_timer > 0:
                xray_cx = int(player_x + size_offset + player_size // 2)
                xray_cy = int(player_y + size_offset + player_size // 2)
                draw_xray_beam(screen, xray_cx, xray_cy, selected_orientation, WIDTH, HEIGHT, time_offset)

            # Speed lines
            draw_speed_lines(screen, WIDTH, HEIGHT, selected_orientation, current_speed, time_offset)

            # Player trail
            draw_player_trail(screen, player_trail, selected_role, PLAYER_COLORS[selected_role], PLAYER_GLOW_COLORS[selected_role])

            draw_player(selected_role, PLAYER_COLORS[selected_role], int(player_x + size_offset + shake_offset_x), int(player_y + size_offset + shake_offset_y), int(player_size), PLAYER_GLOW_COLORS[selected_role], time_offset * 0.15, None, selected_orientation)

            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0] + shake_offset_x), int(obstacle[1] + shake_offset_y), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset, selected_orientation)

            # Draw boss and boss projectiles if active
            if boss_active:
                draw_boss(boss_x + shake_offset_x, boss_y + shake_offset_y, boss_size, boss_health, boss_max_health, time_offset, current_level)
                for proj in boss_projectiles:
                    draw_boss_projectile(int(proj[0] + shake_offset_x), int(proj[1] + shake_offset_y), proj[2], time_offset, current_level)
                draw_boss_health_bar(10, 60, WIDTH - 20, 35, boss_health, boss_max_health, current_level)

            particle_system.draw(screen)

            # Score popups
            for sp in score_popups[:]:
                sp.update()
                sp.draw(screen)
            score_popups = [sp for sp in score_popups if sp.is_alive()]

            if not boss_active:
                score = int(elapsed_seconds * 10) + bonus_score

            # --- Dark neon HUD ---
            status_y = 15

            score_bg = pygame.Surface((120, 40), pygame.SRCALPHA)
            pygame.draw.rect(score_bg, (10, 10, 25, 180), score_bg.get_rect(), border_radius=12)
            pygame.draw.rect(score_bg, (*PRIMARY_COLOR, 100), score_bg.get_rect(), 1, border_radius=12)
            screen.blit(score_bg, (10, status_y))

            score_text = font_header.render(f"{score}", True, (200, 210, 255))
            screen.blit(score_text, (20, status_y + 8))

            speed_bg = pygame.Surface((100, 35), pygame.SRCALPHA)
            pygame.draw.rect(speed_bg, (10, 10, 25, 180), speed_bg.get_rect(), border_radius=10)
            pygame.draw.rect(speed_bg, (60, 80, 140, 100), speed_bg.get_rect(), 1, border_radius=10)
            screen.blit(speed_bg, (140, status_y + 2))

            speed_text = font_normal.render(f"{round(current_speed, 1)}x", True, (160, 180, 230))
            screen.blit(speed_text, (150, status_y + 7))

            level_bg = pygame.Surface((90, 35), pygame.SRCALPHA)
            pygame.draw.rect(level_bg, (10, 10, 25, 180), level_bg.get_rect(), border_radius=10)
            pygame.draw.rect(level_bg, (*WARNING_COLOR, 100), level_bg.get_rect(), 1, border_radius=10)
            screen.blit(level_bg, (250, status_y + 2))

            level_text = font_normal.render(f"LVL {current_level}", True, (255, 200, 120))
            screen.blit(level_text, (260, status_y + 7))

            level_time_left = max(0, (LEVEL_DURATION - level_elapsed) / 1000)
            timer_bg = pygame.Surface((110, 35), pygame.SRCALPHA)
            pygame.draw.rect(timer_bg, (10, 10, 25, 180), timer_bg.get_rect(), border_radius=10)
            pygame.draw.rect(timer_bg, (*SUCCESS_COLOR, 100), timer_bg.get_rect(), 1, border_radius=10)
            screen.blit(timer_bg, (350, status_y + 2))

            timer_color = (120, 240, 160) if level_time_left > 10 else (255, 150, 150)
            timer_text = font_normal.render(f"{int(level_time_left)}s", True, timer_color)
            screen.blit(timer_text, (360, status_y + 7))

        elif game_state == LEVEL_TRANSITION:
            particle_system.update()

            transition_elapsed = pygame.time.get_ticks() - transition_start_ticks

            # Continue showing game state (frozen)
            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0]), int(obstacle[1]), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset, selected_orientation)

            draw_player_trail(screen, player_trail, selected_role, PLAYER_COLORS[selected_role], PLAYER_GLOW_COLORS[selected_role])
            draw_player(selected_role, PLAYER_COLORS[selected_role], int(player_x + (original_player_size - player_size) // 2), int(player_y + (original_player_size - player_size) // 2), int(player_size), PLAYER_GLOW_COLORS[selected_role], time_offset * 0.15, None, selected_orientation)

            particle_system.draw(screen)

            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay_alpha = int(min(180, transition_elapsed * 0.1))
            overlay.fill((0, 0, 10, overlay_alpha))
            screen.blit(overlay, (0, 0))

            # Panel showing level stats
            panel_w, panel_h = 320, 350
            panel_rect = pygame.Rect(WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2, panel_w, panel_h)

            panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (10, 10, 25, 230), panel_surface.get_rect(), border_radius=24)
            screen.blit(panel_surface, (panel_rect.x, panel_rect.y))

            pygame.draw.rect(screen, SUCCESS_COLOR, panel_rect, 2, border_radius=24)
            draw_glow(screen, SUCCESS_COLOR, panel_rect, 20, 25)

            level_complete_text = font_header.render(f"LEVEL {current_level} COMPLETE!", True, SUCCESS_COLOR)
            screen.blit(level_complete_text, (WIDTH // 2 - level_complete_text.get_width() // 2, panel_rect.y + 25))

            stats_start_y = panel_rect.y + 80
            line_height = 40

            stat_names = ["Obstacles Passed:", "Obstacles Destroyed:"]
            stat_values = [level_obstacles_passed, level_obstacles_destroyed]
            stat_colors = [(100, 200, 255), (255, 180, 100)]

            for i, (name, value, color) in enumerate(zip(stat_names, stat_values, stat_colors)):
                name_text = font_normal.render(name, True, (150, 160, 190))
                screen.blit(name_text, (panel_rect.x + 30, stats_start_y + i * line_height))

                value_text = font_header.render(str(value), True, color)
                screen.blit(value_text, (panel_rect.right - 30 - value_text.get_width(), stats_start_y + i * line_height))

            countdown_remaining = COUNTDOWN_DURATION - transition_elapsed
            if countdown_remaining > 0:
                countdown_num = math.ceil(countdown_remaining / 1000)
                if countdown_num > 0:
                    countdown_scale = 1.0 + (1.0 - countdown_remaining / COUNTDOWN_DURATION) * 0.3
                    countdown_text = font_title.render(str(countdown_num), True, SUCCESS_COLOR)

                    cw = int(countdown_text.get_width() * countdown_scale)
                    ch = int(countdown_text.get_height() * countdown_scale)

                    if countdown_num > 0:
                        scaled_countdown = pygame.transform.scale(countdown_text, (cw, ch))
                        screen.blit(scaled_countdown, (WIDTH // 2 - cw // 2, stats_start_y + len(stat_names) * line_height + 20))
            else:
                # Start next level
                current_level += 1
                level_start_ticks = pygame.time.get_ticks()
                level_obstacles_passed = 0
                level_obstacles_destroyed = 0
                obstacles = []
                game_state = PLAYING

        elif game_state == BOSS_DEFEATED:
            particle_system.update()

            transition_elapsed = pygame.time.get_ticks() - transition_start_ticks

            # Continue showing game state (frozen)
            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0]), int(obstacle[1]), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset, selected_orientation)

            draw_player_trail(screen, player_trail, selected_role, PLAYER_COLORS[selected_role], PLAYER_GLOW_COLORS[selected_role])
            draw_player(selected_role, PLAYER_COLORS[selected_role], int(player_x + (original_player_size - player_size) // 2), int(player_y + (original_player_size - player_size) // 2), int(player_size), PLAYER_GLOW_COLORS[selected_role], time_offset * 0.15, None, selected_orientation)

            particle_system.draw(screen)

            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay_alpha = int(min(180, transition_elapsed * 0.1))
            overlay.fill((0, 0, 10, overlay_alpha))
            screen.blit(overlay, (0, 0))

            # Panel showing boss defeat stats
            panel_w, panel_h = 320, 350
            panel_rect = pygame.Rect(WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2, panel_w, panel_h)

            panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (10, 10, 25, 230), panel_surface.get_rect(), border_radius=24)
            screen.blit(panel_surface, (panel_rect.x, panel_rect.y))

            pygame.draw.rect(screen, SUCCESS_COLOR, panel_rect, 2, border_radius=24)
            draw_glow(screen, SUCCESS_COLOR, panel_rect, 20, 25)

            boss_name_configs = {
                1: "MECHA-SENTINEL", 2: "NEON PHANTOM", 3: "CYBER-BEAST",
                4: "INSECTOID", 5: "VOID HAG", 6: "THE WATCHER",
                7: "PLASMA LICH", 8: "TOXIC BLOB", 9: "ANCIENT WYRM", 10: "THE CORE",
            }
            boss_name = boss_name_configs.get(current_level, "BOSS")
            boss_defeated_text = font_header.render(f"{boss_name} DEFEATED!", True, SUCCESS_COLOR)
            screen.blit(boss_defeated_text, (WIDTH // 2 - boss_defeated_text.get_width() // 2, panel_rect.y + 25))

            stats_start_y = panel_rect.y + 80
            line_height = 40

            stat_names = ["Obstacles Passed:", "Obstacles Destroyed:"]
            stat_values = [level_obstacles_passed, level_obstacles_destroyed]
            stat_colors = [(100, 200, 255), (255, 180, 100)]

            for i, (name, value, color) in enumerate(zip(stat_names, stat_values, stat_colors)):
                name_text = font_normal.render(name, True, (150, 160, 190))
                screen.blit(name_text, (panel_rect.x + 30, stats_start_y + i * line_height))

                value_text = font_header.render(str(value), True, color)
                screen.blit(value_text, (panel_rect.right - 30 - value_text.get_width(), stats_start_y + i * line_height))

            countdown_remaining = COUNTDOWN_DURATION - transition_elapsed
            if countdown_remaining > 0:
                countdown_num = math.ceil(countdown_remaining / 1000)
                if countdown_num > 0:
                    countdown_scale = 1.0 + (1.0 - countdown_remaining / COUNTDOWN_DURATION) * 0.3
                    countdown_text = font_title.render(str(countdown_num), True, SUCCESS_COLOR)

                    cw = int(countdown_text.get_width() * countdown_scale)
                    ch = int(countdown_text.get_height() * countdown_scale)

                    if countdown_num > 0:
                        scaled_countdown = pygame.transform.scale(countdown_text, (cw, ch))
                        screen.blit(scaled_countdown, (WIDTH // 2 - cw // 2, stats_start_y + len(stat_names) * line_height + 20))
            else:
                # Start next level
                current_level += 1
                level_start_ticks = pygame.time.get_ticks()
                level_obstacles_passed = 0
                level_obstacles_destroyed = 0
                obstacles = []
                boss_projectiles = []
                boss_active = False
                boss_attack_timer = 0
                boss_pattern_timer = 0
                boss_current_pattern = 0
                boss_direction = 1
                game_state = PLAYING

        elif game_state == GAME_OVER:
            particle_system.update()

            draw_speed_lines(screen, WIDTH, HEIGHT, selected_orientation, max(0, current_speed * 0.5), time_offset)

            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0] + shake_offset_x), int(obstacle[1] + shake_offset_y), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset, selected_orientation)

            particle_system.draw(screen)

            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 10, 160))
            screen.blit(overlay, (0, 0))

            # Animated game over panel (scale-in)
            game_over_timer = min(game_over_timer + 1, GAME_OVER_ANIM_FRAMES)
            anim_progress = game_over_timer / GAME_OVER_ANIM_FRAMES
            anim_scale = 1.0 - (1.0 - anim_progress) ** 3

            panel_w = int(320 * anim_scale)
            panel_h = int(380 * anim_scale)
            if panel_w > 10 and panel_h > 10:
                panel_rect = pygame.Rect(WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2, panel_w, panel_h)

                panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(panel_surface, (10, 10, 25, 230), panel_surface.get_rect(), border_radius=24)
                screen.blit(panel_surface, (panel_rect.x, panel_rect.y))

                pygame.draw.rect(screen, DANGER_COLOR, panel_rect, 2, border_radius=24)
                draw_glow(screen, DANGER_COLOR, panel_rect, 20, 25)

                if anim_progress > 0.5:
                    text_alpha = int(min(255, (anim_progress - 0.5) * 2 * 255))

                    game_over_text = font_title.render("GAME OVER", True, DANGER_COLOR)
                    go_surface = pygame.Surface(game_over_text.get_size(), pygame.SRCALPHA)
                    go_surface.blit(game_over_text, (0, 0))
                    go_surface.set_alpha(text_alpha)
                    screen.blit(go_surface, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 110))

                    score_panel = pygame.Surface((180, 45), pygame.SRCALPHA)
                    pygame.draw.rect(score_panel, (239, 68, 68, 40), score_panel.get_rect(), border_radius=12)
                    score_panel.set_alpha(text_alpha)
                    screen.blit(score_panel, (WIDTH // 2 - 90, HEIGHT // 2 - 50))

                    score_label = font_header.render(f"Score: {score}", True, (220, 220, 240))
                    sl_surface = pygame.Surface(score_label.get_size(), pygame.SRCALPHA)
                    sl_surface.blit(score_label, (0, 0))
                    sl_surface.set_alpha(text_alpha)
                    screen.blit(sl_surface, (WIDTH // 2 - score_label.get_width() // 2, HEIGHT // 2 - 42))

                    diff_name = difficulty_settings[selected_difficulty]["name"]
                    diff_text = font_normal.render(f"Difficulty: {diff_name}", True, (150, 160, 190))
                    dt_surface = pygame.Surface(diff_text.get_size(), pygame.SRCALPHA)
                    dt_surface.blit(diff_text, (0, 0))
                    dt_surface.set_alpha(text_alpha)
                    screen.blit(dt_surface, (WIDTH // 2 - diff_text.get_width() // 2, HEIGHT // 2 - 5))

                    level_text = font_normal.render(f"Level Reached: {current_level}", True, (255, 200, 120))
                    lt_surface = pygame.Surface(level_text.get_size(), pygame.SRCALPHA)
                    lt_surface.blit(level_text, (0, 0))
                    lt_surface.set_alpha(text_alpha)
                    screen.blit(lt_surface, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 + 20))

                if anim_progress >= 1.0:
                    restart_button.rect.y = HEIGHT // 2 + 40
                    menu_button.rect.y = HEIGHT // 2 + 100
                    restart_button.update()
                    menu_button.update()
                    restart_button.draw(screen)
                    menu_button.draw(screen)

                    if qualifies_for_leaderboard:
                        save_score_button.rect.y = HEIGHT // 2 + 160
                        save_score_button.update()
                        save_score_button.draw(screen)
                    else:
                        scores_gameover_button.rect.y = HEIGHT // 2 + 160
                        scores_gameover_button.update()
                        scores_gameover_button.draw(screen)

        elif game_state == ENTER_NAME:
            name_cursor_blink += 1

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 10, 180))
            screen.blit(overlay, (0, 0))

            panel_w, panel_h = 320, 280
            panel_rect = pygame.Rect(WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2, panel_w, panel_h)
            panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (10, 10, 25, 230), panel_surface.get_rect(), border_radius=24)
            screen.blit(panel_surface, (panel_rect.x, panel_rect.y))
            pygame.draw.rect(screen, WARNING_COLOR, panel_rect, 2, border_radius=24)
            draw_glow(screen, WARNING_COLOR, panel_rect, 20, 25)

            title_text = font_header.render("NEW HIGH SCORE!", True, WARNING_COLOR)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, panel_rect.y + 20))

            score_text = font_title.render(str(score), True, (220, 220, 240))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, panel_rect.y + 60))

            label_text = font_normal.render("Enter your name:", True, (160, 170, 220))
            screen.blit(label_text, (WIDTH // 2 - label_text.get_width() // 2, panel_rect.y + 120))

            input_w, input_h = 240, 40
            input_rect = pygame.Rect(WIDTH // 2 - input_w // 2, panel_rect.y + 155, input_w, input_h)
            input_surf = pygame.Surface((input_w, input_h), pygame.SRCALPHA)
            pygame.draw.rect(input_surf, (5, 5, 15, 220), input_surf.get_rect(), border_radius=10)
            screen.blit(input_surf, (input_rect.x, input_rect.y))
            pygame.draw.rect(screen, NEON_CYAN, input_rect, 1, border_radius=10)

            display_name = player_name
            if (name_cursor_blink // 30) % 2 == 0:
                display_name += "|"
            name_surf = font_header.render(display_name, True, WHITE)
            screen.blit(name_surf, (input_rect.x + 10, input_rect.y + 7))

            submit_name_button.rect.y = panel_rect.y + 210
            submit_name_button.update()
            submit_name_button.draw(screen)

        elif game_state == LEADERBOARD:
            parallax.update(0.2)

            for mp in menu_particles:
                mp.update()
                mp.draw(screen)

            glow_pulse = 0.5 + 0.5 * math.sin(time_offset * 0.05)
            title_text = font_title.render("LEADERBOARD", True, WARNING_COLOR)
            glow_surface = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
            glow_surface.blit(title_text, (0, 0))
            glow_surface.set_alpha(int(180 + glow_pulse * 75))
            screen.blit(glow_surface, (WIDTH // 2 - title_text.get_width() // 2, 25))

            current_scores = load_scores()

            table_w, table_h = min(360, WIDTH - 40), 380
            table_rect = pygame.Rect(WIDTH // 2 - table_w // 2, 75, table_w, table_h)
            table_surf = pygame.Surface((table_w, table_h), pygame.SRCALPHA)
            pygame.draw.rect(table_surf, (10, 12, 25, 200), table_surf.get_rect(), border_radius=20)
            screen.blit(table_surf, (table_rect.x, table_rect.y))
            pygame.draw.rect(screen, (50, 60, 120), table_rect, 1, border_radius=20)

            header_y = table_rect.y + 10
            rank_header = font_small.render("#", True, (120, 140, 180))
            name_header = font_small.render("NAME", True, (120, 140, 180))
            score_header = font_small.render("SCORE", True, (120, 140, 180))
            screen.blit(rank_header, (table_rect.x + 15, header_y))
            screen.blit(name_header, (table_rect.x + 50, header_y))
            screen.blit(score_header, (table_rect.x + table_w - 80, header_y))

            pygame.draw.line(screen, (50, 60, 120), (table_rect.x + 10, header_y + 22),
                             (table_rect.x + table_w - 10, header_y + 22), 1)

            for i in range(10):
                row_y = header_y + 30 + i * 33
                if i < len(current_scores):
                    entry = current_scores[i]
                    is_highlighted = (entry["name"] == last_saved_score_name and
                                      entry["score"] == score and last_saved_score_name != "")

                    if is_highlighted:
                        highlight_surf = pygame.Surface((table_w - 20, 28), pygame.SRCALPHA)
                        glow_a = int(40 + 20 * math.sin(time_offset * 0.1))
                        pygame.draw.rect(highlight_surf, (*SUCCESS_COLOR, glow_a),
                                         highlight_surf.get_rect(), border_radius=6)
                        screen.blit(highlight_surf, (table_rect.x + 10, row_y - 2))

                    if i == 0:
                        rank_color = (255, 215, 0)
                    elif i == 1:
                        rank_color = (192, 192, 210)
                    elif i == 2:
                        rank_color = (205, 127, 50)
                    else:
                        rank_color = (160, 170, 210)

                    text_color = (220, 240, 220) if is_highlighted else (200, 210, 230)

                    rank_text = font_normal.render(str(i + 1), True, rank_color)
                    name_text = font_normal.render(entry["name"][:12], True, text_color)
                    score_text = font_normal.render(str(entry["score"]), True, text_color)
                    screen.blit(rank_text, (table_rect.x + 15, row_y))
                    screen.blit(name_text, (table_rect.x + 50, row_y))
                    screen.blit(score_text, (table_rect.x + table_w - 80, row_y))
                else:
                    empty_text = font_small.render(f"{i + 1}.  ---", True, (60, 70, 100))
                    screen.blit(empty_text, (table_rect.x + 15, row_y + 2))

            btn_y = table_rect.y + table_h + 15
            if leaderboard_from == MENU:
                leaderboard_back_button.rect.y = btn_y
                leaderboard_back_button.update()
                leaderboard_back_button.draw(screen)
            else:
                leaderboard_restart_button.rect.y = btn_y
                leaderboard_menu_button.rect.y = btn_y + 55
                leaderboard_restart_button.update()
                leaderboard_menu_button.update()
                leaderboard_restart_button.draw(screen)
                leaderboard_menu_button.draw(screen)

        # --- CRT Scanline Overlay ---
        scanlines = get_scanline_overlay(WIDTH, HEIGHT)
        screen.blit(scanlines, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
