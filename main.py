import pygame
import random
import math
import json
import os

pygame.init()

VERTICAL = (400, 600)
HORIZONTAL = (800, 500)

WIDTH, HEIGHT = VERTICAL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WU DONG Running")

# --- Dark Neon Color Palette ---
BG_TOP = (8, 8, 20)
BG_BOTTOM = (15, 20, 40)
BG_TOP_GAME = (8, 8, 20)
BG_BOTTOM_GAME = (10, 15, 35)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 80)
DARK_GRAY = (200, 200, 220)
LIGHT_GRAY = (30, 30, 50)

PRIMARY_COLOR = (99, 102, 241)
PRIMARY_HOVER = (129, 140, 248)
PRIMARY_GLOW = (139, 92, 246)
SUCCESS_COLOR = (16, 185, 129)
WARNING_COLOR = (245, 158, 11)
DANGER_COLOR = (239, 68, 68)

NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 0, 200)
NEON_BLUE = (80, 120, 255)

PLAYER_COLORS = {
    "spaceship": (99, 102, 241),
    "aeroplane": (16, 185, 129),
    "dragon": (245, 158, 11)
}

PLAYER_GLOW_COLORS = {
    "spaceship": (167, 139, 250),
    "aeroplane": (52, 211, 153),
    "dragon": (251, 191, 36)
}

# Obstacle types
OBSTACLE_SQUARE = "square"
OBSTACLE_BIRD = "bird"
OBSTACLE_TURTLE = "turtle"
OBSTACLE_MUSHROOM = "mushroom"
OBSTACLE_MACHINEGUN = "machinegun"
OBSTACLE_SHOTGUN = "shotgun"
OBSTACLE_STEEL_BAR = "steel_bar"
OBSTACLE_XRAY_GUN = "xray_gun"

OBSTACLE_COLORS = {
    OBSTACLE_SQUARE: (220, 38, 38),
    OBSTACLE_BIRD: (250, 204, 21),
    OBSTACLE_TURTLE: (96, 165, 250),
    OBSTACLE_MUSHROOM: (239, 68, 68),
    OBSTACLE_MACHINEGUN: (234, 88, 12),
    OBSTACLE_SHOTGUN: (168, 85, 247),
    OBSTACLE_STEEL_BAR: (120, 130, 150),
    OBSTACLE_XRAY_GUN: (0, 200, 255),
}

OBSTACLE_GLOW_COLORS = {
    OBSTACLE_SQUARE: (248, 113, 113),
    OBSTACLE_BIRD: (254, 240, 138),
    OBSTACLE_TURTLE: (147, 197, 253),
    OBSTACLE_MUSHROOM: (252, 165, 165),
    OBSTACLE_MACHINEGUN: (253, 186, 116),
    OBSTACLE_SHOTGUN: (216, 180, 254),
    OBSTACLE_STEEL_BAR: (180, 190, 210),
    OBSTACLE_XRAY_GUN: (100, 230, 255),
}

# Fonts
font_title = pygame.font.Font(None, 48)
font_header = pygame.font.Font(None, 36)
font_menu_section = pygame.font.Font(None, 28)
font_normal = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 22)
font_popup = pygame.font.Font(None, 32)

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
ENTER_NAME = "enter_name"
LEADERBOARD = "leaderboard"
LEVEL_TRANSITION = "level_transition"
BOSS_DEFEATED = "boss_defeated"

# --- Score persistence ---
SCORES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.json")


def load_scores():
    try:
        with open(SCORES_FILE, "r") as f:
            scores = json.load(f)
        scores = [s for s in scores if isinstance(s, dict) and "name" in s and "score" in s]
        scores.sort(key=lambda s: s["score"], reverse=True)
        return scores[:10]
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return []


def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)


def is_high_score(score):
    scores = load_scores()
    if len(scores) < 10:
        return True
    return score > scores[-1]["score"]

# --- Cached surfaces (generated once per resolution) ---
_cached_gradients = {}
_cached_scanlines = {}


def get_cached_gradient(width, height, top_color, bottom_color):
    key = (width, height, top_color, bottom_color)
    if key not in _cached_gradients:
        _cached_gradients[key] = create_gradient_surface(width, height, top_color, bottom_color)
    return _cached_gradients[key]


def get_scanline_overlay(width, height):
    key = (width, height)
    if key not in _cached_scanlines:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 3):
            pygame.draw.line(surf, (0, 0, 0, 25), (0, y), (width, y))
        _cached_scanlines[key] = surf
    return _cached_scanlines[key]


class Particle:
    def __init__(self, x, y, color, size, velocity_x, velocity_y, lifetime=60, glow=False):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.original_size = size
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.glow = glow
        self.alpha = 255

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_x *= 0.98
        self.velocity_y *= 0.98
        self.lifetime -= 1
        self.alpha = int((self.lifetime / self.max_lifetime) * 255)
        self.size = self.original_size * (self.lifetime / self.max_lifetime)

    def draw(self, surface):
        if self.lifetime > 0 and self.size > 0.5:
            sz = max(1, int(self.size))
            if self.glow:
                gs = sz * 4
                glow_surface = pygame.Surface((gs, gs), pygame.SRCALPHA)
                glow_color = (*self.color, int(self.alpha * 0.3))
                pygame.draw.circle(glow_surface, glow_color, (gs // 2, gs // 2), gs // 2)
                surface.blit(glow_surface, (int(self.x - gs // 2), int(self.y - gs // 2)))

            ps = sz * 2
            particle_surface = pygame.Surface((ps, ps), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, self.alpha), (sz, sz), sz)
            surface.blit(particle_surface, (int(self.x - sz), int(self.y - sz)))

    def is_alive(self):
        return self.lifetime > 0


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10, size=5, glow=False, spread=3):
        for _ in range(count):
            velocity_x = random.uniform(-spread, spread)
            velocity_y = random.uniform(-spread, spread)
            particle = Particle(x, y, color, size, velocity_x, velocity_y, glow=glow)
            self.particles.append(particle)

    def update(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


# --- Score Popup System ---
class ScorePopup:
    def __init__(self, x, y, text, color=(255, 255, 100)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 40
        self.max_lifetime = 40

    def update(self):
        self.y -= 1.5
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int((self.lifetime / self.max_lifetime) * 255)
            txt = font_popup.render(self.text, True, self.color)
            txt_surface = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
            txt_surface.blit(txt, (0, 0))
            txt_surface.set_alpha(alpha)
            surface.blit(txt_surface, (int(self.x), int(self.y)))

    def is_alive(self):
        return self.lifetime > 0


# --- Parallax Background ---
class ParallaxBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.stars = [(random.randint(0, width), random.randint(0, height),
                       random.uniform(0.5, 2.0), random.randint(100, 200)) for _ in range(80)]
        self.grid_offset = 0.0
        self.floor_offset = 0.0

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.stars = [(random.randint(0, width), random.randint(0, height),
                       random.uniform(0.5, 2.0), random.randint(100, 200)) for _ in range(80)]

    def update(self, speed_factor=1.0):
        self.grid_offset += 0.5 * speed_factor
        self.floor_offset += 2.0 * speed_factor

    def draw(self, surface, orientation="vertical"):
        # Layer 1: Stars (slow)
        for sx, sy, sz, sa in self.stars:
            alpha = min(255, int(sa * 0.7))
            brightness = min(255, int(150 + sz * 50))
            color = (brightness, brightness, min(255, brightness + 40), alpha)
            star_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            r = max(1, int(sz))
            pygame.draw.circle(star_surf, color, (2, 2), r)
            surface.blit(star_surf, (int(sx), int(sy)))

        # Layer 2: Grid lines (medium speed)
        grid_size = 50
        grid_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        offset = int(self.grid_offset) % grid_size

        if orientation == "vertical":
            for x in range(0, self.width + grid_size, grid_size):
                pygame.draw.line(grid_surf, (40, 60, 120, 25), (x, 0), (x, self.height), 1)
            for y in range(-grid_size, self.height + grid_size, grid_size):
                pygame.draw.line(grid_surf, (40, 60, 120, 25), (0, y + offset), (self.width, y + offset), 1)
        else:
            for y in range(0, self.height + grid_size, grid_size):
                pygame.draw.line(grid_surf, (40, 60, 120, 25), (0, y), (self.width, y), 1)
            for x in range(-grid_size, self.width + grid_size, grid_size):
                pygame.draw.line(grid_surf, (40, 60, 120, 25), (x - offset, 0), (x - offset, self.height), 1)

        surface.blit(grid_surf, (0, 0))

        # Layer 3: Floor markers (fast)
        floor_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        floor_offset = int(self.floor_offset) % 30

        if orientation == "vertical":
            ground_y = self.height - 60
            for i in range(0, self.width + 30, 30):
                x = (i + floor_offset) % (self.width + 30)
                alpha = max(10, 40 - abs(x - self.width // 2) // 8)
                pygame.draw.line(floor_surf, (60, 80, 150, alpha), (x, ground_y), (x, self.height), 1)
        else:
            ground_x = 30
            for i in range(0, self.height + 30, 30):
                y = (i + floor_offset) % (self.height + 30)
                alpha = max(10, 40 - abs(y - self.height // 2) // 8)
                pygame.draw.line(floor_surf, (60, 80, 150, alpha), (0, y), (ground_x, y), 1)

        surface.blit(floor_surf, (0, 0))


# --- Menu Floating Particles ---
class MenuParticle:
    def __init__(self, width, height):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.size = random.uniform(1.5, 4.0)
        self.color = random.choice([NEON_CYAN, NEON_PINK, NEON_BLUE, PRIMARY_COLOR, PRIMARY_GLOW])
        self.alpha = random.randint(40, 120)
        self.width = width
        self.height = height

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0:
            self.x = self.width
        elif self.x > self.width:
            self.x = 0
        if self.y < 0:
            self.y = self.height
        elif self.y > self.height:
            self.y = 0

    def draw(self, surface):
        sz = max(1, int(self.size))
        s = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, min(255, self.alpha)), (sz * 2, sz * 2), sz * 2)
        surface.blit(s, (int(self.x - sz * 2), int(self.y - sz * 2)))
        s2 = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        pygame.draw.circle(s2, (*self.color, min(255, self.alpha + 60)), (sz, sz), sz)
        surface.blit(s2, (int(self.x - sz), int(self.y - sz)))


def create_gradient_surface(width, height, top_color, bottom_color):
    if height <= 0 or width <= 0:
        return pygame.Surface((max(width, 1), max(height, 1)))
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient


class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, text_color=WHITE, radius=16, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.font = font or font_normal
        self.is_selected = False
        self.scale = 1.0
        self.target_scale = 1.0

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.05 if is_hovered or self.is_selected else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, surface):
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )

        # Dark panel background
        btn_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (15, 15, 30, 200), btn_surface.get_rect(), border_radius=self.radius)
        surface.blit(btn_surface, (scaled_rect.x, scaled_rect.y))

        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) or self.is_selected else self.color

        # Neon border
        border_width = 2 if not self.is_selected else 3
        pygame.draw.rect(surface, color, scaled_rect, border_width, border_radius=self.radius)

        # Glow on selected
        if self.is_selected:
            glow_surf = pygame.Surface((scaled_width + 8, scaled_height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, 40), glow_surf.get_rect(), border_radius=self.radius + 4)
            surface.blit(glow_surf, (scaled_rect.x - 4, scaled_rect.y - 4))

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)


class SectionPanel:
    def __init__(self, x, y, width, height, title=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title

    def draw(self, surface):
        # Dark semi-transparent panel
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (10, 12, 25, 180), panel_surface.get_rect(), border_radius=20)
        surface.blit(panel_surface, (self.rect.x, self.rect.y))

        # Neon border
        pygame.draw.rect(surface, (50, 60, 120), self.rect, 1, border_radius=20)

        if self.title:
            title_surf = font_menu_section.render(self.title, True, (160, 170, 220))
            surface.blit(title_surf, (self.rect.x + 20, self.rect.y + 12))


def draw_glow(surface, color, rect, radius=15, intensity=50):
    for i in range(3):
        r = radius + i * 6
        alpha = max(5, intensity - i * 15)
        glow_surface = pygame.Surface((rect.width + r * 2, rect.height + r * 2), pygame.SRCALPHA)
        glow_color = (*color, alpha)
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=r + 5)
        surface.blit(glow_surface, (rect.x - r, rect.y - r))


def draw_player(shape, color, x, y, size, glow_color=None, pulse=0, target_surface=None):
    surf = target_surface if target_surface is not None else screen

    pass  # No outer container/glow for player

    cx = x + size // 2
    cy = y + size // 2
    half = size // 2
    s = max(size / 40.0, 0.1)  # scale factor relative to default size 40

    if shape == "spaceship":
        # --- Advanced Sci-Fi Interceptor ---
        # Main Hull (Tapered sleek body)
        hull_pts = [
            (cx, y),                                # Nose
            (cx + int(10 * s), y + int(25 * s)),    # Right mid
            (cx + int(8 * s), y + size),            # Right aft
            (cx - int(8 * s), y + size),            # Left aft
            (cx - int(10 * s), y + int(25 * s)),    # Left mid
        ]
        pygame.draw.polygon(surf, color, hull_pts)
        
        # Central Ridge (Adds depth)
        ridge_color = tuple(min(255, c + 40) for c in color)
        pygame.draw.line(surf, ridge_color, (cx, y + int(5 * s)), (cx, y + size - int(5 * s)), max(1, int(2 * s)))

        # Swept Wings
        wing_color = tuple(max(0, c - 30) for c in color)
        # Left Wing
        pygame.draw.polygon(surf, wing_color, [
            (cx - int(8 * s), y + int(15 * s)),
            (cx - int(22 * s), y + size - int(5 * s)),
            (cx - int(22 * s), y + size + int(2 * s)),
            (cx - int(8 * s), y + size - int(5 * s))
        ])
        # Right Wing
        pygame.draw.polygon(surf, wing_color, [
            (cx + int(8 * s), y + int(15 * s)),
            (cx + int(22 * s), y + size - int(5 * s)),
            (cx + int(22 * s), y + size + int(2 * s)),
            (cx + int(8 * s), y + size - int(5 * s))
        ])

        # Wing Lights (Small neon dots)
        light_color = NEON_CYAN if (pulse % 0.4) > 0.2 else (255, 255, 255)
        pygame.draw.circle(surf, light_color, (cx - int(20 * s), y + size - int(2 * s)), max(1, int(2 * s)))
        pygame.draw.circle(surf, light_color, (cx + int(20 * s), y + size - int(2 * s)), max(1, int(2 * s)))

        # Cockpit (Glassy look)
        cockpit_rect = (cx - int(4 * s), y + int(8 * s), int(8 * s), int(14 * s))
        pygame.draw.ellipse(surf, (30, 40, 60), cockpit_rect)  # Base
        pygame.draw.ellipse(surf, (100, 200, 255),
                            (cx - int(3 * s), y + int(10 * s), int(6 * s), int(5 * s)))  # Shine

        # Engine Thruster (Flickering Core)
        engine_w = int(12 * s)
        flame_h = int((10 + math.sin(pulse * 10) * 5) * s)
        # Outer Glow
        pygame.draw.rect(surf, (255, 100, 0), (cx - engine_w//2, y + size, engine_w, flame_h // 2), border_radius=3)
        # Inner Core
        pygame.draw.rect(surf, (255, 255, 200), (cx - engine_w//4, y + size, engine_w // 2, flame_h // 3), border_radius=2)

    elif shape == "aeroplane":
        # --- Light Ghost Gray Air Superiority Fighter ---
        # Define the realistic light palette
        BODY_LIGHT = (210, 215, 225)      # Main Light Gray
        BODY_SHADE = (170, 175, 185)      # Shaded Gray for wings
        NOSE_CONE = (100, 105, 115)       # Darker radar nose
        COCKPIT_GLASS = (20, 30, 45)      # Deep canopy
        
        # 1. Main Fuselage
        # Nose cone
        pygame.draw.polygon(surf, NOSE_CONE, [(cx, y - int(8 * s)), (cx + int(3 * s), y), (cx - int(3 * s), y)])
        # Main body
        pygame.draw.rect(surf, BODY_LIGHT, (cx - int(4 * s), y, int(8 * s), size))

        # 2. Air Intakes (Slanted for realism)
        pygame.draw.polygon(surf, (40, 45, 55), [
            (cx - int(4 * s), y + int(15 * s)), (cx - int(8 * s), y + int(18 * s)), 
            (cx - int(8 * s), y + int(28 * s)), (cx - int(4 * s), y + int(25 * s))
        ])
        pygame.draw.polygon(surf, (40, 45, 55), [
            (cx + int(4 * s), y + int(15 * s)), (cx + int(8 * s), y + int(18 * s)), 
            (cx + int(8 * s), y + int(28 * s)), (cx + int(4 * s), y + int(25 * s))
        ])

        # 3. Main Wings (Light Ghost Gray with Shading)
        # Left Wing
        pygame.draw.polygon(surf, BODY_SHADE, [
            (cx - int(4 * s), y + int(10 * s)),   # Leading edge extension
            (cx - int(26 * s), y + size - int(8 * s)), # Wing tip
            (cx - int(26 * s), y + size - int(3 * s)), # Wing tip back
            (cx - int(4 * s), y + size - int(6 * s))   # Root back
        ])
        # Right Wing
        pygame.draw.polygon(surf, BODY_SHADE, [
            (cx + int(4 * s), y + int(10 * s)),
            (cx + int(26 * s), y + size - int(8 * s)),
            (cx + int(26 * s), y + size - int(3 * s)),
            (cx + int(4 * s), y + size - int(6 * s))
        ])

        # 4. Wing-tip Missiles (White Sidewinders)
        pygame.draw.rect(surf, (240, 240, 240), (cx - int(27 * s), y + size - int(12 * s), int(2 * s), int(10 * s)))
        pygame.draw.rect(surf, (240, 240, 240), (cx + int(25 * s), y + size - int(12 * s), int(2 * s), int(10 * s)))

        # 5. Rear Horizontal Stabilizers
        pygame.draw.polygon(surf, BODY_SHADE, [(cx - int(4 * s), y + size - int(4 * s)), (cx - int(14 * s), y + size + int(6 * s)), (cx - int(4 * s), y + size)])
        pygame.draw.polygon(surf, BODY_SHADE, [(cx + int(4 * s), y + size - int(4 * s)), (cx + int(14 * s), y + size + int(6 * s)), (cx + int(4 * s), y + size)])

        # 6. Cockpit Bubble (With highlight)
        pygame.draw.ellipse(surf, COCKPIT_GLASS, (cx - int(3 * s), y + int(4 * s), int(6 * s), int(16 * s)))
        pygame.draw.ellipse(surf, (100, 150, 200), (cx - int(2 * s), y + int(6 * s), int(2 * s), int(5 * s)))

        # 7. Engine Exhaust (Twin Blue Afterburners)
        afterburner_glow = (120, 230, 255) if (pulse % 0.3) > 0.15 else (80, 180, 255)
        pygame.draw.circle(surf, (60, 60, 70), (cx - int(2 * s), y + size), int(3 * s))
        pygame.draw.circle(surf, (60, 60, 70), (cx + int(2 * s), y + size), int(3 * s))
        
        flame_len = int((6 + math.sin(pulse * 12) * 4) * s)
        pygame.draw.line(surf, afterburner_glow, (cx - int(2 * s), y + size), (cx - int(2 * s), y + size + flame_len), 2)
        pygame.draw.line(surf, afterburner_glow, (cx + int(2 * s), y + size), (cx + int(2 * s), y + size + flame_len), 2)

    elif shape == "dragon":
        # --- Friendly Forest Dragon ---
        BODY_GREEN = (100, 220, 60)
        BELLY_YELLOW = (255, 255, 150)
        EYE_WHITE = (255, 255, 255)
        
        # Gentle floating animation
        float_y = math.sin(pulse * 3) * 5 * s
        wing_flap = math.sin(pulse * 10) * 10 * s
        
        # 1. Small Fluttery Wings
        for side in [-1, 1]:
            pygame.draw.ellipse(surf, (255, 200, 0), (
                cx + (8 * s * side) - (5 * s if side == 1 else 0), 
                y + (20 * s) + float_y + wing_flap, 
                10 * s, 15 * s
            ))

        # 2. Chubby Body
        pygame.draw.ellipse(surf, BODY_GREEN, (cx - 15*s, y + 15*s + float_y, 30*s, 35*s))
        # Pale Belly
        pygame.draw.ellipse(surf, BELLY_YELLOW, (cx - 10*s, y + 25*s + float_y, 20*s, 22*s))

        # 3. Rounded Tail
        tail_pts = [(cx - 10*s, y + 45*s + float_y), (cx, y + 55*s + float_y), (cx + 10*s, y + 45*s + float_y)]
        pygame.draw.lines(surf, BODY_GREEN, False, tail_pts, int(8*s))

        # 4. Big Head
        head_rect = (cx - 18*s, y - 5*s + float_y, 36*s, 30*s)
        pygame.draw.ellipse(surf, BODY_GREEN, head_rect)

        # 5. Friendly Eyes (The "Cute" Secret)
        # White part
        pygame.draw.circle(surf, EYE_WHITE, (int(cx - 8*s), int(y + 8*s + float_y)), int(6*s))
        pygame.draw.circle(surf, EYE_WHITE, (int(cx + 8*s), int(y + 8*s + float_y)), int(6*s))
        # Pupils
        pygame.draw.circle(surf, (0, 0, 0), (int(cx - 8*s), int(y + 8*s + float_y)), int(3*s))
        pygame.draw.circle(surf, (0, 0, 0), (int(cx + 8*s), int(y + 8*s + float_y)), int(3*s))
        # Eye Sparkle (tiny white dot)
        pygame.draw.circle(surf, EYE_WHITE, (int(cx - 9*s), int(y + 7*s + float_y)), int(1.5*s))
        pygame.draw.circle(surf, EYE_WHITE, (int(cx + 7*s), int(y + 7*s + float_y)), int(1.5*s))

        # 6. Little Nubs (Horns)
        pygame.draw.circle(surf, BELLY_YELLOW, (int(cx - 12*s), int(y - 2*s + float_y)), int(4*s))
        pygame.draw.circle(surf, BELLY_YELLOW, (int(cx + 12*s), int(y - 2*s + float_y)), int(4*s))


def draw_obstacle(obstacle_type, x, y, size, glow_color=None, pulse=0, time_offset=0):
    color = OBSTACLE_COLORS[obstacle_type]

    # Only draw outer container/glow for OBSTACLE_SQUARE
    if glow_color and obstacle_type == OBSTACLE_SQUARE:
        pulse_size = 2 + math.sin(pulse) * 1.5
        glow_rect = pygame.Rect(x - pulse_size, y - pulse_size, size + pulse_size * 2, size + pulse_size * 2)
        for i in range(3):
            r = 8 + i * 4
            alpha = max(5, 35 - i * 10)
            gs = pygame.Surface((glow_rect.width + r * 2, glow_rect.height + r * 2), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*glow_color, alpha), gs.get_rect(), border_radius=r + 3)
            screen.blit(gs, (glow_rect.x - r, glow_rect.y - r))

    if obstacle_type == OBSTACLE_SQUARE:
        # HAZARD - Spiked Mine: rotating red circle with spikes
        cx, cy = x + size // 2, y + size // 2
        angle = time_offset * 3 % 360
        radius = size // 3
        # Main circle body with dark border
        pygame.draw.circle(screen, (130, 10, 10), (cx, cy), radius + 2)
        pygame.draw.circle(screen, color, (cx, cy), radius)
        # Spikes around the circle (8 directions)
        for deg in range(0, 360, 45):
            spike_rad = math.radians(deg + angle)
            sx = cx + int(math.cos(spike_rad) * (radius + size // 6))
            sy = cy + int(math.sin(spike_rad) * (radius + size // 6))
            pygame.draw.circle(screen, (130, 10, 10), (sx, sy), max(2, size // 10))
        # Pulsing center light
        center_pulse = abs(math.sin(time_offset * 0.15))
        center_r = max(2, int(size // 8 + center_pulse * 2))
        pygame.draw.circle(screen, (255, 200, 200), (cx, cy), center_r)

    elif obstacle_type == OBSTACLE_BIRD:
        # SPEED UP - Lightning Bolt (drawn smaller within hitbox)
        cx, cy = x + size // 2, y + size // 2
        s = size / 55.0
        bolt_color = (250, 204, 21)
        bright_color = (254, 240, 138)
        # Lightning bolt shape
        points = [
            (cx + int(1 * s), cy - int(18 * s)),
            (cx - int(9 * s), cy + int(2 * s)),
            (cx + int(0 * s), cy + int(2 * s)),
            (cx - int(1 * s), cy + int(18 * s)),
            (cx + int(9 * s), cy - int(2 * s)),
            (cx + int(0 * s), cy - int(2 * s)),
        ]
        # Brightness pulse glow
        brightness_pulse = abs(math.sin(time_offset * 0.2))
        if brightness_pulse > 0.3:
            glow_surf = pygame.Surface((size + 10, size + 10), pygame.SRCALPHA)
            glow_alpha = int(brightness_pulse * 80)
            pygame.draw.polygon(glow_surf, (*bolt_color, glow_alpha),
                                [(p[0] - x + 5, p[1] - y + 5) for p in points])
            screen.blit(glow_surf, (x - 5, y - 5))
        pygame.draw.polygon(screen, bolt_color, points)
        pygame.draw.polygon(screen, bright_color, points, max(1, int(s)))

    elif obstacle_type == OBSTACLE_TURTLE:
        # SLOW DOWN - Cute cartoon turtle matching reference image
        cx, cy = x + size // 2, y + size // 2
        s = size / 40.0
        bob = math.sin(time_offset * 0.05) * 2 * s

        # --- Front legs (behind body) ---
        leg_color = (120, 190, 120)
        leg_outline = (60, 120, 60)
        # Front-left leg
        fl_x, fl_y = int(cx - 10 * s), int(cy + 8 * s + bob)
        pygame.draw.ellipse(screen, leg_color, (fl_x, fl_y, int(8 * s), int(10 * s)))
        pygame.draw.ellipse(screen, leg_outline, (fl_x, fl_y, int(8 * s), int(10 * s)), max(1, int(s)))
        # Front-right leg
        fr_x, fr_y = int(cx + 2 * s), int(cy + 8 * s + bob)
        pygame.draw.ellipse(screen, leg_color, (fr_x, fr_y, int(8 * s), int(10 * s)))
        pygame.draw.ellipse(screen, leg_outline, (fr_x, fr_y, int(8 * s), int(10 * s)), max(1, int(s)))
        # Toes (small circles at bottom of each leg)
        for lx in [fl_x, fr_x]:
            for t in range(3):
                tx = lx + int((1 + t * 3) * s)
                ty = int(cy + 16 * s + bob)
                pygame.draw.circle(screen, leg_color, (tx, ty), max(1, int(1.5 * s)))

        # --- Shell (dome shape) ---
        shell_color = (100, 180, 80)
        shell_dark = (70, 140, 55)
        shell_outline = (50, 100, 40)
        shell_w, shell_h = int(26 * s), int(20 * s)
        shell_x = int(cx - 13 * s)
        shell_y = int(cy - 10 * s + bob)
        # Main shell dome
        pygame.draw.ellipse(screen, shell_color, (shell_x, shell_y, shell_w, shell_h))
        pygame.draw.ellipse(screen, shell_outline, (shell_x, shell_y, shell_w, shell_h), max(1, int(1.5 * s)))
        # Shell rim (bottom edge stripe)
        rim_rect = (shell_x + int(2 * s), int(cy + 5 * s + bob), shell_w - int(4 * s), int(5 * s))
        pygame.draw.ellipse(screen, shell_dark, rim_rect)
        pygame.draw.ellipse(screen, shell_outline, rim_rect, max(1, int(s)))
        # Shell pattern - hexagonal/pentagon shapes
        # Center hexagon
        hex_cx, hex_cy = int(cx), int(cy - 4 * s + bob)
        hex_r = int(5 * s)
        hex_pts = [(hex_cx + int(hex_r * math.cos(math.radians(60 * i - 30))),
                     hex_cy + int(hex_r * 0.8 * math.sin(math.radians(60 * i - 30)))) for i in range(6)]
        pygame.draw.polygon(screen, shell_dark, hex_pts, max(1, int(s)))
        # Surrounding smaller shapes
        for angle_deg in [0, 72, 144, 216, 288]:
            px = hex_cx + int(7 * s * math.cos(math.radians(angle_deg)))
            py = hex_cy + int(5 * s * math.sin(math.radians(angle_deg)))
            mini_r = int(3 * s)
            mini_pts = [(px + int(mini_r * math.cos(math.radians(72 * i))),
                          py + int(mini_r * 0.7 * math.sin(math.radians(72 * i)))) for i in range(5)]
            pygame.draw.polygon(screen, shell_dark, mini_pts, max(1, int(s)))

        # --- Neck (with stripes, connecting head to shell) ---
        neck_x = int(cx + 10 * s)
        neck_y = int(cy - 2 * s + bob)
        neck_w, neck_h = int(8 * s), int(10 * s)
        pygame.draw.ellipse(screen, leg_color, (neck_x, neck_y, neck_w, neck_h))
        pygame.draw.ellipse(screen, leg_outline, (neck_x, neck_y, neck_w, neck_h), max(1, int(s)))
        # Neck stripes
        for si in range(3):
            sy = neck_y + int((2 + si * 3) * s)
            pygame.draw.line(screen, shell_dark, (neck_x + int(1 * s), sy), (neck_x + neck_w - int(1 * s), sy), max(1, int(s)))

        # --- Head (large, round, cute) ---
        head_x = int(cx + 14 * s + bob)
        head_y = int(cy - 8 * s + bob)
        head_r = int(8 * s)
        pygame.draw.circle(screen, leg_color, (head_x, head_y), head_r)
        pygame.draw.circle(screen, leg_outline, (head_x, head_y), head_r, max(1, int(1.5 * s)))

        # Eyes (big, expressive)
        eye_r = max(2, int(3 * s))
        pupil_r = max(1, int(1.5 * s))
        # Left eye
        le_x, le_y = int(head_x - 2 * s), int(head_y - 3 * s)
        pygame.draw.circle(screen, (255, 255, 255), (le_x, le_y), eye_r)
        pygame.draw.circle(screen, (30, 30, 30), (le_x + int(0.5 * s), le_y), pupil_r)
        pygame.draw.circle(screen, (255, 255, 255), (le_x + int(1 * s), le_y - int(1 * s)), max(1, int(0.8 * s)))
        pygame.draw.circle(screen, leg_outline, (le_x, le_y), eye_r, max(1, int(s)))
        # Right eye
        re_x, re_y = int(head_x + 4 * s), int(head_y - 3 * s)
        pygame.draw.circle(screen, (255, 255, 255), (re_x, re_y), eye_r)
        pygame.draw.circle(screen, (30, 30, 30), (re_x + int(0.5 * s), re_y), pupil_r)
        pygame.draw.circle(screen, (255, 255, 255), (re_x + int(1 * s), re_y - int(1 * s)), max(1, int(0.8 * s)))
        pygame.draw.circle(screen, leg_outline, (re_x, re_y), eye_r, max(1, int(s)))

        # Smile (curved line)
        smile_rect = pygame.Rect(int(head_x - 3 * s), int(head_y - 1 * s), int(8 * s), int(6 * s))
        pygame.draw.arc(screen, (50, 80, 50), smile_rect, math.radians(200), math.radians(340), max(1, int(1.5 * s)))

    elif obstacle_type == OBSTACLE_MUSHROOM:
        # SHRINK - Mushroom: red cap with white dots, cream stem (drawn smaller)
        inset = size // 5
        mx = x + inset
        ms = size - inset * 2
        bounce = abs(int(math.sin(time_offset * 0.2) * 2))
        my = y + inset - bounce
        cap_h = ms // 2 + 2
        stem_w = ms // 3
        stem_h = ms // 3 + bounce
        # Stem
        stem_rect = pygame.Rect(mx + ms // 2 - stem_w // 2, my + cap_h - 2, stem_w, stem_h)
        pygame.draw.rect(screen, (220, 215, 200), stem_rect, border_radius=3)
        pygame.draw.rect(screen, (200, 200, 190), stem_rect, 2, border_radius=3)
        # Red cap dome
        cap_rect = pygame.Rect(mx + 1, my, ms - 2, cap_h)
        pygame.draw.ellipse(screen, (220, 38, 38), cap_rect)
        pygame.draw.ellipse(screen, (252, 165, 165), cap_rect, max(1, ms // 16))
        # White dots on cap
        pygame.draw.circle(screen, WHITE, (mx + ms // 3, my + cap_h // 3), max(2, ms // 10))
        pygame.draw.circle(screen, WHITE, (mx + ms * 2 // 3, my + cap_h // 3 + 2), max(2, ms // 12))

    elif obstacle_type == OBSTACLE_MACHINEGUN:
        # TRIPLE SHOT - Three bouncing bullet shapes
        cx = x + size // 2
        bullet_w = max(4, size // 6)
        bullet_h = max(10, size * 2 // 5)
        gap = bullet_w + 2
        for i in range(3):
            bx = cx - gap + i * gap - bullet_w // 2
            bounce = int(math.sin(time_offset * 0.3 + i * 0.5) * 4)
            by = y + size // 2 - bullet_h // 2 + bounce
            bullet_rect = pygame.Rect(bx, by, bullet_w, bullet_h)
            # Bullet body (orange)
            pygame.draw.rect(screen, (234, 88, 12), bullet_rect, border_radius=bullet_w)
            # Top highlight (yellow)
            highlight_rect = pygame.Rect(bx, by, bullet_w, bullet_h // 2)
            pygame.draw.rect(screen, (253, 224, 71), highlight_rect, border_radius=bullet_w)
            # Border
            pygame.draw.rect(screen, (254, 215, 170), bullet_rect, 1, border_radius=bullet_w)

    elif obstacle_type == OBSTACLE_SHOTGUN:
        # SHOTGUN - Same triple-bullet icon but in purple
        cx = x + size // 2
        bullet_w = max(4, size // 6)
        bullet_h = max(10, size * 2 // 5)
        gap = bullet_w + 2
        for i in range(3):
            bx = cx - gap + i * gap - bullet_w // 2
            bounce = int(math.sin(time_offset * 0.3 + i * 0.5) * 4)
            by = y + size // 2 - bullet_h // 2 + bounce
            bullet_rect = pygame.Rect(bx, by, bullet_w, bullet_h)
            pygame.draw.rect(screen, (168, 85, 247), bullet_rect, border_radius=bullet_w)
            highlight_rect = pygame.Rect(bx, by, bullet_w, bullet_h // 2)
            pygame.draw.rect(screen, (216, 180, 254), highlight_rect, border_radius=bullet_w)
            pygame.draw.rect(screen, (232, 210, 255), bullet_rect, 1, border_radius=bullet_w)

    elif obstacle_type == OBSTACLE_STEEL_BAR:
        bar_width = size
        bar_height = 12
        bar_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(screen, (80, 85, 95), bar_rect, border_radius=3)
        pygame.draw.rect(screen, color, (x + 2, y + 2, bar_width - 4, bar_height - 4), border_radius=2)
        highlight_rect = pygame.Rect(x + 4, y + 3, bar_width - 8, 3)
        pygame.draw.rect(screen, (180, 190, 200), highlight_rect, border_radius=1)
        pygame.draw.rect(screen, glow_color, bar_rect, 2, border_radius=3)
        for i in range(3):
            bolt_x = x + bar_width // 4 + i * bar_width // 4
            bolt_y = y + bar_height // 2
            pygame.draw.circle(screen, (60, 65, 75), (bolt_x, bolt_y), 3)
            pygame.draw.circle(screen, (100, 105, 115), (bolt_x, bolt_y), 2)

    elif obstacle_type == OBSTACLE_XRAY_GUN:
        cx, cy = x + size // 2, y + size // 2
        s = size / 40.0
        pulse_brightness = abs(math.sin(time_offset * 0.15))
        
        xray_glow_color = (100, 230, 255)
        
        for i in range(3):
            glow_r = int((12 + i * 6) * s)
            glow_alpha = int((60 - i * 15) * pulse_brightness + 30)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*xray_glow_color, glow_alpha), (glow_r, glow_r), glow_r)
            screen.blit(glow_surf, (cx - glow_r, cy - glow_r))
        
        pygame.draw.polygon(screen, color, [
            (cx, y + int(5 * s)),
            (cx + int(12 * s), cy),
            (cx, y + size - int(5 * s)),
            (cx - int(12 * s), cy)
        ])
        
        inner_color = (150, 230, 255)
        pygame.draw.polygon(screen, inner_color, [
            (cx, y + int(10 * s)),
            (cx + int(6 * s), cy),
            (cx, y + size - int(10 * s)),
            (cx - int(6 * s), cy)
        ])
        
        core_brightness = int(180 + 75 * pulse_brightness)
        pygame.draw.circle(screen, (core_brightness, min(core_brightness + 20, 255), 255), (cx, cy), int(4 * s))


def draw_xray_beam(surface, start_x, start_y, orientation, width, height, time_offset):
    if orientation == "vertical":
        if start_y <= 0:
            return
        beam_width = 20
        beam_surf = pygame.Surface((beam_width, start_y), pygame.SRCALPHA)
        for i in range(start_y):
            alpha = int(150 - (i / start_y) * 80)
            wave = int(math.sin((i + time_offset * 3) * 0.1) * 3)
            inner_alpha = int(200 - (i / start_y) * 100)
            pygame.draw.line(beam_surf, (100, 200, 255, alpha), (0, i), (beam_width, i))
            pygame.draw.line(beam_surf, (200, 240, 255, inner_alpha), (beam_width // 2 - 3 + wave, i), (beam_width // 2 + 3 + wave, i))
        surface.blit(beam_surf, (start_x - beam_width // 2, 0))
    else:
        beam_length = width - start_x
        if beam_length <= 0:
            return
        beam_height = 15
        beam_surf = pygame.Surface((beam_length, beam_height), pygame.SRCALPHA)
        for i in range(beam_length):
            alpha = int(150 - (i / beam_length) * 80)
            wave = int(math.sin((i + time_offset * 3) * 0.1) * 2)
            inner_alpha = int(200 - (i / beam_length) * 100)
            pygame.draw.line(beam_surf, (100, 200, 255, alpha), (i, 0), (i, beam_height))
            pygame.draw.line(beam_surf, (200, 240, 255, inner_alpha), (i, beam_height // 2 - 2 + wave), (i, beam_height // 2 + 2 + wave))
        surface.blit(beam_surf, (start_x, start_y - beam_height // 2))


def draw_speed_lines(surface, width, height, orientation, speed, time_offset):
    """Draw faint speed lines that scale with game speed."""
    line_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    intensity = min(60, int(speed * 8))
    if intensity < 10:
        return

    for _ in range(int(speed * 3)):
        if orientation == "vertical":
            lx = random.randint(0, width)
            ly = random.randint(0, height)
            length = random.randint(10, 30 + int(speed * 5))
            pygame.draw.line(line_surf, (100, 150, 255, intensity), (lx, ly), (lx, ly + length), 1)
        else:
            lx = random.randint(0, width)
            ly = random.randint(0, height)
            length = random.randint(10, 30 + int(speed * 5))
            pygame.draw.line(line_surf, (100, 150, 255, intensity), (lx, ly), (lx - length, ly), 1)

    surface.blit(line_surf, (0, 0))


def draw_boss(x, y, size, health, max_health, time_offset, level=1):
    """Draws one of 10 unique bosses based on the current level."""
    cx, cy = x + size // 2, y + size // 2
    half = size // 2
    s = size / 100.0
    pulse = math.sin(time_offset * 0.1)

    # Common glow effect
    boss_glow_configs = {
        1: (129, 140, 248), 2: (216, 180, 254), 3: (251, 146, 60),
        4: (248, 113, 113), 5: (74, 222, 128), 6: (110, 231, 183),
        7: (255, 255, 255), 8: (250, 204, 21), 9: (99, 102, 241),
        10: (255, 250, 205),
    }
    boss_glow = boss_glow_configs.get(level, boss_glow_configs[1])
    pulse_size = 3 + pulse * 2
    glow_rect = pygame.Rect(x - pulse_size, y - pulse_size, size + pulse_size * 2, size + pulse_size * 2)
    for i in range(4):
        r = 15 + i * 6
        alpha = max(5, 50 - i * 12)
        gs = pygame.Surface((glow_rect.width + r * 2, glow_rect.height + r * 2), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*boss_glow, alpha), gs.get_rect(), border_radius=r + 5)
        screen.blit(gs, (glow_rect.x - r, glow_rect.y - r))

    if level == 1:
        # ROBOT (Mecha-Sentinel)
        color = (100, 150, 255)
        pygame.draw.rect(screen, color, (x, y, size, size), border_radius=10)
        # Visor
        pygame.draw.rect(screen, (20, 20, 40), (int(x + 10 * s), int(y + 20 * s), int(80 * s), int(30 * s)))
        # Pulsing red eyes
        eye_color = (255, 0, 0) if pulse > 0 else (150, 0, 0)
        pygame.draw.circle(screen, eye_color, (int(x + 30 * s), int(y + 35 * s)), int(8 * s))
        pygame.draw.circle(screen, eye_color, (int(x + 70 * s), int(y + 35 * s)), int(8 * s))

    elif level == 2:
        # GHOST (Neon Phantom)
        color = (200, 150, 255)
        alpha = int(150 + pulse * 50)
        ghost_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(ghost_surf, (*color, alpha), (0, 0, size, int(size * 0.8)))
        # Wavy bottom
        for i in range(3):
            wx = i * (size // 3)
            pygame.draw.circle(ghost_surf, (*color, alpha), (wx + size // 6, int(size * 0.8)), size // 6)
        screen.blit(ghost_surf, (x, y))
        # Dark hollow eyes
        pygame.draw.circle(screen, (0, 0, 0), (int(cx - 15 * s), int(cy - 10 * s)), int(5 * s))
        pygame.draw.circle(screen, (0, 0, 0), (int(cx + 15 * s), int(cy - 10 * s)), int(5 * s))

    elif level == 3:
        # TIGER (Cyber-Beast)
        color = (255, 140, 0)
        pygame.draw.circle(screen, color, (cx, cy), size // 2)
        # Ears
        pygame.draw.polygon(screen, color, [(x, int(y + 20 * s)), (int(x + 30 * s), y), (int(x + 40 * s), int(y + 30 * s))])
        pygame.draw.polygon(screen, color, [(x + size, int(y + 20 * s)), (int(x + size - 30 * s), y), (int(x + size - 40 * s), int(y + 30 * s))])
        # Black stripes
        for i in range(3):
            pygame.draw.line(screen, (0, 0, 0), (int(cx - 20 * s), int(y + 40 * s + i * 10 * s)),
                             (int(cx + 20 * s), int(y + 40 * s + i * 10 * s)), 3)

    elif level == 4:
        # ALIEN (Insectoid Overlord)
        color = (50, 255, 100)
        # Long oval head
        pygame.draw.ellipse(screen, color, (int(x + 20 * s), y, int(60 * s), size))
        # Large black almond eyes
        pygame.draw.ellipse(screen, (0, 0, 0), (int(x + 25 * s), int(y + 20 * s), int(20 * s), int(35 * s)))
        pygame.draw.ellipse(screen, (0, 0, 0), (int(x + 55 * s), int(y + 20 * s), int(20 * s), int(35 * s)))
        # Mandibles
        pygame.draw.arc(screen, (200, 255, 200),
                        pygame.Rect(int(cx - 20 * s), int(cy + 10 * s), int(40 * s), int(30 * s)),
                        0, math.pi, 4)

    elif level == 5:
        # WITCH (Void Hag)
        # Hat (triangle)
        pygame.draw.polygon(screen, (40, 0, 80), [(cx, y), (x, y + size), (x + size, y + size)])
        # Face
        pygame.draw.circle(screen, (220, 180, 150), (cx, int(cy + 20 * s)), int(25 * s))
        # Glowing green eyes
        pygame.draw.circle(screen, (0, 255, 0), (int(cx - 10 * s), int(cy + 15 * s)), 4)
        pygame.draw.circle(screen, (0, 255, 0), (int(cx + 10 * s), int(cy + 15 * s)), 4)

    elif level == 6:
        # EYE (The Watcher)
        # White sclera
        pygame.draw.ellipse(screen, (255, 255, 255), (x, int(y + 20 * s), size, int(60 * s)))
        # Red iris (pulsing size)
        iris_r = int(20 * s + pulse * 5 * s)
        pygame.draw.circle(screen, (255, 0, 0), (cx, cy), iris_r)
        # Black pupil
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), iris_r // 2)

    elif level == 7:
        # SKULL (Plasma Lich)
        # Cranium
        pygame.draw.circle(screen, (240, 240, 240), (cx, int(cy - 10 * s)), int(40 * s))
        # Jaw
        pygame.draw.rect(screen, (240, 240, 240),
                         (int(cx - 25 * s), int(cy + 20 * s), int(50 * s), int(25 * s)), border_radius=5)
        # Blue fire eyes
        pygame.draw.circle(screen, (0, 100, 255), (int(cx - 15 * s), int(cy)), int(10 * s))
        pygame.draw.circle(screen, (0, 100, 255), (int(cx + 15 * s), int(cy)), int(10 * s))

    elif level == 8:
        # SLIME (Toxic Blob)
        color = (150, 255, 0)
        # Animated bubbles
        for i in range(5):
            bx = cx + math.cos(time_offset * 0.1 + i) * 30 * s
            by = cy + math.sin(time_offset * 0.1 + i) * 20 * s
            pygame.draw.circle(screen, color, (int(bx), int(by)), int(20 * s))
        # Main body blob
        pygame.draw.ellipse(screen, color, (int(x + 10 * s), int(y + 20 * s), int(80 * s), int(60 * s)))

    elif level == 9:
        # DRAGON (Ancient Wyrm)
        color = (200, 30, 30)
        # Diamond-shaped head
        pygame.draw.polygon(screen, color, [(cx, y), (x, cy), (cx, y + size), (x + size, cy)])
        # Golden horns
        pygame.draw.line(screen, (255, 200, 100), (int(cx - 10 * s), int(y + 10 * s)), (x, int(y - 10 * s)), 5)
        pygame.draw.line(screen, (255, 200, 100), (int(cx + 10 * s), int(y + 10 * s)), (x + size, int(y - 10 * s)), 5)
        # Yellow slit eyes
        pygame.draw.line(screen, (255, 255, 0), (int(cx - 15 * s), int(cy - 5 * s)), (int(cx - 5 * s), int(cy - 5 * s)), 3)
        pygame.draw.line(screen, (255, 255, 0), (int(cx + 15 * s), int(cy - 5 * s)), (int(cx + 5 * s), int(cy - 5 * s)), 3)

    elif level >= 10:
        # THE CORE (Final God) - Rotating hexagon with pulsing center
        angle = time_offset * 0.05
        points = []
        for i in range(6):
            px = cx + math.cos(angle + i * math.pi / 3) * 50 * s
            py = cy + math.sin(angle + i * math.pi / 3) * 50 * s
            points.append((px, py))
        pygame.draw.polygon(screen, (255, 215, 0), points, 3)
        # Pulsing white core
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), int(15 * s + pulse * 10 * s))


def draw_boss_projectile(x, y, size, time_offset, level=1):
    """Draw boss projectile (circle block)."""
    boss_configs = {
        1: {"color": (100, 150, 255), "glow": (129, 140, 248)},
        2: {"color": (200, 150, 255), "glow": (216, 180, 254)},
        3: {"color": (255, 140, 0), "glow": (251, 146, 60)},
        4: {"color": (50, 255, 100), "glow": (100, 255, 150)},
        5: {"color": (40, 0, 80), "glow": (100, 50, 150)},
        6: {"color": (255, 0, 0), "glow": (248, 113, 113)},
        7: {"color": (0, 100, 255), "glow": (100, 180, 255)},
        8: {"color": (150, 255, 0), "glow": (200, 255, 100)},
        9: {"color": (200, 30, 30), "glow": (255, 100, 100)},
        10: {"color": (255, 215, 0), "glow": (255, 250, 205)},
    }
    
    config = boss_configs.get(level, boss_configs[1])
    color = config["color"]
    glow_color = config["glow"]
    
    # Glow
    pulse = 2 + math.sin(time_offset * 0.2) * 1
    gs = pygame.Surface((size + pulse * 4, size + pulse * 4), pygame.SRCALPHA)
    pygame.draw.circle(gs, (*glow_color, 80), (size // 2 + pulse * 2, size // 2 + pulse * 2), size // 2 + pulse)
    screen.blit(gs, (x - pulse * 2, y - pulse * 2))
    
    # Main circle
    pygame.draw.circle(screen, color, (x + size // 2, y + size // 2), size // 2)
    
    # Inner pattern
    inner_color = tuple(max(0, c - 50) for c in color)
    pygame.draw.circle(screen, inner_color, (x + size // 2, y + size // 2), size // 3)


def draw_boss_health_bar(x, y, width, height, health, max_health, level=1):
    """Draw boss health bar."""
    boss_configs = {
        1: {"name": "MECHA-SENTINEL", "color": (100, 150, 255)},
        2: {"name": "NEON PHANTOM", "color": (200, 150, 255)},
        3: {"name": "CYBER-BEAST", "color": (255, 140, 0)},
        4: {"name": "INSECTOID", "color": (50, 255, 100)},
        5: {"name": "VOID HAG", "color": (40, 0, 80)},
        6: {"name": "THE WATCHER", "color": (255, 0, 0)},
        7: {"name": "PLASMA LICH", "color": (0, 100, 255)},
        8: {"name": "TOXIC BLOB", "color": (150, 255, 0)},
        9: {"name": "ANCIENT WYRM", "color": (200, 30, 30)},
        10: {"name": "THE CORE", "color": (255, 215, 0)},
    }
    
    config = boss_configs.get(level, boss_configs[1])
    boss_name = config["name"]
    boss_color = config["color"]
    
    # Background
    bg_rect = pygame.Rect(x, y, width, height)
    bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (20, 20, 40, 200), bg_rect, border_radius=10)
    screen.blit(bg_surface, (x, y))
    
    # Border
    pygame.draw.rect(screen, boss_color, bg_rect, 2, border_radius=10)
    
    # Health fill
    health_width = int((health / max_health) * (width - 8))
    if health_width > 0:
        fill_rect = pygame.Rect(x + 4, y + 4, health_width, height - 8)
        # Color gradient based on health
        if health > max_health * 0.5:
            health_color = (100, 200, 100)
        elif health > max_health * 0.25:
            health_color = (200, 180, 50)
        else:
            health_color = (200, 50, 50)
        pygame.draw.rect(screen, health_color, fill_rect, border_radius=6)
    
    # Boss label
    boss_text = font_small.render(f"LVL {level}: {boss_name}", True, boss_color)
    screen.blit(boss_text, (x + 10, y + 7))
    
    # Health text
    health_text = font_small.render(f"{health}/{max_health}", True, (200, 200, 255))
    screen.blit(health_text, (x + width - health_text.get_width() - 10, y + 7))


def draw_player_trail(surface, trail, shape, color, glow_color):
    """Draw fading trail copies behind the player."""
    n = len(trail)
    for i, (tx, ty, ts) in enumerate(trail):
        ratio = (i + 1) / n
        alpha = int(ratio * 80)
        trail_size = max(4, int(ts * (0.3 + ratio * 0.5)))
        ts_surf = pygame.Surface((trail_size + 4, trail_size + 4), pygame.SRCALPHA)

        if shape == "spaceship":
            # Diamond / rhombus silhouette
            half_t = trail_size // 2 + 2
            diamond = [(half_t, 2), (trail_size + 2, half_t), (half_t, trail_size + 2), (2, half_t)]
            pygame.draw.polygon(ts_surf, (*color, alpha), diamond)
        elif shape == "aeroplane":
            # Small ellipse
            pygame.draw.ellipse(ts_surf, (*color, alpha), (2, 2, trail_size, trail_size))
        elif shape == "dragon":
            # Small circle (body segment)
            pygame.draw.circle(ts_surf, (*color, alpha), (trail_size // 2 + 2, trail_size // 2 + 2), trail_size // 2)

        surface.blit(ts_surf, (int(tx), int(ty)))


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
        1: {"blocks": 1, "base_speed": 3, "spawn_rate": 60, "name": "Easy"},
        2: {"blocks": 2, "base_speed": 4, "spawn_rate": 50, "name": "Medium"},
        3: {"blocks": 3, "base_speed": 5, "spawn_rate": 40, "name": "Hard"}
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
                            reset_screen(selected_orientation)
                            parallax.resize(WIDTH, HEIGHT)
                            _cached_gradients.clear()
                            _cached_scanlines.clear()
                            if selected_orientation == "vertical":
                                player_x = WIDTH // 2
                                player_y = HEIGHT - 100
                            else:
                                player_x = 50
                                player_y = HEIGHT // 2
                            obstacles = []
                            score = 0
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
                        reset_screen("vertical")
                        parallax.resize(WIDTH, HEIGHT)
                        _cached_gradients.clear()
                        _cached_scanlines.clear()
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
                            reset_screen("vertical")
                            parallax.resize(WIDTH, HEIGHT)
                            _cached_gradients.clear()
                            _cached_scanlines.clear()
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

            # Title glow layers
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
                # Draw small role preview icon inside each button (left side)
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
                        # Boss mode: spawn projectiles and occasional machinegun
                        boss_attack_timer += 1
                        boss_pattern_timer += 1
                        
                        # Change pattern periodically
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
                            obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN, OBSTACLE_STEEL_BAR, OBSTACLE_XRAY_GUN], weights=obstacle_weights)[0]
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
                        # Boss mode: spawn projectiles and occasional machinegun
                        boss_attack_timer += 1
                        boss_pattern_timer += 1
                        
                        # Change pattern periodically
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
                            obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN, OBSTACLE_STEEL_BAR, OBSTACLE_XRAY_GUN], weights=obstacle_weights)[0]
                            if obs_type == OBSTACLE_SQUARE:
                                obs_sz = random.choice([30, 40, 50, 60])
                            elif obs_type == OBSTACLE_STEEL_BAR:
                                min_width = WIDTH // 5
                                max_width = WIDTH // 3
                                obs_sz = random.randint(min_width, max_width)
                            else:
                                obs_sz = obstacle_size
                            obstacle_y = random.randint(0, HEIGHT - 12)
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
                    enemy_rect = pygame.Rect(obstacle[0], obstacle[1], obs_sz, 12)
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
                            obs_rect = pygame.Rect(obs[0], obs[1], obs[3], 12)
                        
                        if xray_beam_rect.colliderect(obs_rect):
                            level_obstacles_destroyed += 1
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
                        
                        # Get boss color for particles
                        boss_configs = {
                            1: (100, 150, 255),
                            2: (200, 150, 255),
                            3: (255, 140, 0),
                            4: (50, 255, 100),
                            5: (40, 0, 80),
                            6: (255, 0, 0),
                            7: (0, 100, 255),
                            8: (150, 255, 0),
                            9: (200, 30, 30),
                            10: (255, 215, 0),
                        }
                        boss_color = boss_configs.get(current_level, boss_configs[1])
                        
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
                
                # Blue bullets for all roles - bigger size
                # Outer blue glow
                glow_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (0, 150, 255, 100), (12, 12), 12)
                screen.blit(glow_surf, (bx - 12, by - 12))

                # Inner bright core
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

            draw_player(selected_role, PLAYER_COLORS[selected_role], int(player_x + size_offset + shake_offset_x), int(player_y + size_offset + shake_offset_y), int(player_size), PLAYER_GLOW_COLORS[selected_role], time_offset * 0.15)

            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0] + shake_offset_x), int(obstacle[1] + shake_offset_y), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset)

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
                score = int(elapsed_seconds * 10)

            # --- Dark neon HUD ---
            status_y = 15

            # Score pill
            score_bg = pygame.Surface((120, 40), pygame.SRCALPHA)
            pygame.draw.rect(score_bg, (10, 10, 25, 180), score_bg.get_rect(), border_radius=12)
            pygame.draw.rect(score_bg, (*PRIMARY_COLOR, 100), score_bg.get_rect(), 1, border_radius=12)
            screen.blit(score_bg, (10, status_y))

            score_text = font_header.render(f"{score}", True, (200, 210, 255))
            screen.blit(score_text, (20, status_y + 8))

            # Speed pill
            speed_bg = pygame.Surface((100, 35), pygame.SRCALPHA)
            pygame.draw.rect(speed_bg, (10, 10, 25, 180), speed_bg.get_rect(), border_radius=10)
            pygame.draw.rect(speed_bg, (60, 80, 140, 100), speed_bg.get_rect(), 1, border_radius=10)
            screen.blit(speed_bg, (140, status_y + 2))

            speed_text = font_normal.render(f"{round(current_speed, 1)}x", True, (160, 180, 230))
            screen.blit(speed_text, (150, status_y + 7))

            # Level pill
            level_bg = pygame.Surface((90, 35), pygame.SRCALPHA)
            pygame.draw.rect(level_bg, (10, 10, 25, 180), level_bg.get_rect(), border_radius=10)
            pygame.draw.rect(level_bg, (*WARNING_COLOR, 100), level_bg.get_rect(), 1, border_radius=10)
            screen.blit(level_bg, (250, status_y + 2))

            level_text = font_normal.render(f"LVL {current_level}", True, (255, 200, 120))
            screen.blit(level_text, (260, status_y + 7))

            # Level timer
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
                draw_obstacle(obstacle[2], int(obstacle[0]), int(obstacle[1]), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset)
            
            draw_player_trail(screen, player_trail, selected_role, PLAYER_COLORS[selected_role], PLAYER_GLOW_COLORS[selected_role])
            draw_player(selected_role, PLAYER_COLORS[selected_role], int(player_x + (original_player_size - player_size) // 2), int(player_y + (original_player_size - player_size) // 2), int(player_size), PLAYER_GLOW_COLORS[selected_role], time_offset * 0.15)
            
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
            
            # Success border
            pygame.draw.rect(screen, SUCCESS_COLOR, panel_rect, 2, border_radius=24)
            draw_glow(screen, SUCCESS_COLOR, panel_rect, 20, 25)
            
            # Level complete text
            level_complete_text = font_header.render(f"LEVEL {current_level} COMPLETE!", True, SUCCESS_COLOR)
            screen.blit(level_complete_text, (WIDTH // 2 - level_complete_text.get_width() // 2, panel_rect.y + 25))
            
            # Stats
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
            
            # Countdown
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
                draw_obstacle(obstacle[2], int(obstacle[0]), int(obstacle[1]), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset)
            
            draw_player_trail(screen, player_trail, selected_role, PLAYER_COLORS[selected_role], PLAYER_GLOW_COLORS[selected_role])
            draw_player(selected_role, PLAYER_COLORS[selected_role], int(player_x + (original_player_size - player_size) // 2), int(player_y + (original_player_size - player_size) // 2), int(player_size), PLAYER_GLOW_COLORS[selected_role], time_offset * 0.15)
            
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
            
            # Victory border
            pygame.draw.rect(screen, SUCCESS_COLOR, panel_rect, 2, border_radius=24)
            draw_glow(screen, SUCCESS_COLOR, panel_rect, 20, 25)
            
            # Boss defeated text
            boss_configs = {
                1: "MECHA-SENTINEL",
                2: "NEON PHANTOM",
                3: "CYBER-BEAST",
                4: "INSECTOID",
                5: "VOID HAG",
                6: "THE WATCHER",
                7: "PLASMA LICH",
                8: "TOXIC BLOB",
                9: "ANCIENT WYRM",
                10: "THE CORE",
            }
            boss_name = boss_configs.get(current_level, "BOSS")
            boss_defeated_text = font_header.render(f"{boss_name} DEFEATED!", True, SUCCESS_COLOR)
            screen.blit(boss_defeated_text, (WIDTH // 2 - boss_defeated_text.get_width() // 2, panel_rect.y + 25))
            
            # Stats
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
            
            # Countdown
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

            # Speed lines still visible but fading
            draw_speed_lines(screen, WIDTH, HEIGHT, selected_orientation, max(0, current_speed * 0.5), time_offset)

            # Draw remaining obstacles with shake
            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0] + shake_offset_x), int(obstacle[1] + shake_offset_y), obstacle[3], OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset)

            particle_system.draw(screen)

            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 10, 160))
            screen.blit(overlay, (0, 0))

            # Animated game over panel (scale-in)
            game_over_timer = min(game_over_timer + 1, GAME_OVER_ANIM_FRAMES)
            anim_progress = game_over_timer / GAME_OVER_ANIM_FRAMES
            # Ease out
            anim_scale = 1.0 - (1.0 - anim_progress) ** 3

            panel_w = int(320 * anim_scale)
            panel_h = int(380 * anim_scale)
            if panel_w > 10 and panel_h > 10:
                panel_rect = pygame.Rect(WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2, panel_w, panel_h)

                # Dark panel
                panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(panel_surface, (10, 10, 25, 230), panel_surface.get_rect(), border_radius=24)
                screen.blit(panel_surface, (panel_rect.x, panel_rect.y))

                # Neon danger border
                pygame.draw.rect(screen, DANGER_COLOR, panel_rect, 2, border_radius=24)
                draw_glow(screen, DANGER_COLOR, panel_rect, 20, 25)

                if anim_progress > 0.5:
                    text_alpha = int(min(255, (anim_progress - 0.5) * 2 * 255))

                    game_over_text = font_title.render("GAME OVER", True, DANGER_COLOR)
                    go_surface = pygame.Surface(game_over_text.get_size(), pygame.SRCALPHA)
                    go_surface.blit(game_over_text, (0, 0))
                    go_surface.set_alpha(text_alpha)
                    screen.blit(go_surface, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 110))

                    # Score bg
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

            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 10, 180))
            screen.blit(overlay, (0, 0))

            # Panel
            panel_w, panel_h = 320, 280
            panel_rect = pygame.Rect(WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2, panel_w, panel_h)
            panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (10, 10, 25, 230), panel_surface.get_rect(), border_radius=24)
            screen.blit(panel_surface, (panel_rect.x, panel_rect.y))
            pygame.draw.rect(screen, WARNING_COLOR, panel_rect, 2, border_radius=24)
            draw_glow(screen, WARNING_COLOR, panel_rect, 20, 25)

            # Title
            title_text = font_header.render("NEW HIGH SCORE!", True, WARNING_COLOR)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, panel_rect.y + 20))

            # Score display
            score_text = font_title.render(str(score), True, (220, 220, 240))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, panel_rect.y + 60))

            # Input label
            label_text = font_normal.render("Enter your name:", True, (160, 170, 220))
            screen.blit(label_text, (WIDTH // 2 - label_text.get_width() // 2, panel_rect.y + 120))

            # Input field
            input_w, input_h = 240, 40
            input_rect = pygame.Rect(WIDTH // 2 - input_w // 2, panel_rect.y + 155, input_w, input_h)
            input_surf = pygame.Surface((input_w, input_h), pygame.SRCALPHA)
            pygame.draw.rect(input_surf, (5, 5, 15, 220), input_surf.get_rect(), border_radius=10)
            screen.blit(input_surf, (input_rect.x, input_rect.y))
            pygame.draw.rect(screen, NEON_CYAN, input_rect, 1, border_radius=10)

            # Text + cursor
            display_name = player_name
            if (name_cursor_blink // 30) % 2 == 0:
                display_name += "|"
            name_surf = font_header.render(display_name, True, WHITE)
            screen.blit(name_surf, (input_rect.x + 10, input_rect.y + 7))

            # Submit button
            submit_name_button.rect.y = panel_rect.y + 210
            submit_name_button.update()
            submit_name_button.draw(screen)

        elif game_state == LEADERBOARD:
            # Dark background with parallax
            parallax.update(0.2)
            # (parallax already drawn above before event handling)

            for mp in menu_particles:
                mp.update()
                mp.draw(screen)

            # Title
            glow_pulse = 0.5 + 0.5 * math.sin(time_offset * 0.05)
            title_text = font_title.render("LEADERBOARD", True, WARNING_COLOR)
            glow_surface = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
            glow_surface.blit(title_text, (0, 0))
            glow_surface.set_alpha(int(180 + glow_pulse * 75))
            screen.blit(glow_surface, (WIDTH // 2 - title_text.get_width() // 2, 25))

            # Load scores
            current_scores = load_scores()

            # Table panel
            table_w, table_h = min(360, WIDTH - 40), 380
            table_rect = pygame.Rect(WIDTH // 2 - table_w // 2, 75, table_w, table_h)
            table_surf = pygame.Surface((table_w, table_h), pygame.SRCALPHA)
            pygame.draw.rect(table_surf, (10, 12, 25, 200), table_surf.get_rect(), border_radius=20)
            screen.blit(table_surf, (table_rect.x, table_rect.y))
            pygame.draw.rect(screen, (50, 60, 120), table_rect, 1, border_radius=20)

            # Header row
            header_y = table_rect.y + 10
            rank_header = font_small.render("#", True, (120, 140, 180))
            name_header = font_small.render("NAME", True, (120, 140, 180))
            score_header = font_small.render("SCORE", True, (120, 140, 180))
            screen.blit(rank_header, (table_rect.x + 15, header_y))
            screen.blit(name_header, (table_rect.x + 50, header_y))
            screen.blit(score_header, (table_rect.x + table_w - 80, header_y))

            # Divider
            pygame.draw.line(screen, (50, 60, 120), (table_rect.x + 10, header_y + 22),
                             (table_rect.x + table_w - 10, header_y + 22), 1)

            # Entries
            for i in range(10):
                row_y = header_y + 30 + i * 33
                if i < len(current_scores):
                    entry = current_scores[i]
                    is_highlighted = (entry["name"] == last_saved_score_name and
                                      entry["score"] == score and last_saved_score_name != "")

                    if is_highlighted:
                        # Glow highlight
                        highlight_surf = pygame.Surface((table_w - 20, 28), pygame.SRCALPHA)
                        glow_a = int(40 + 20 * math.sin(time_offset * 0.1))
                        pygame.draw.rect(highlight_surf, (*SUCCESS_COLOR, glow_a),
                                         highlight_surf.get_rect(), border_radius=6)
                        screen.blit(highlight_surf, (table_rect.x + 10, row_y - 2))

                    # Rank color
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
                    # Empty slot
                    empty_text = font_small.render(f"{i + 1}.  ---", True, (60, 70, 100))
                    screen.blit(empty_text, (table_rect.x + 15, row_y + 2))

            # Buttons
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
