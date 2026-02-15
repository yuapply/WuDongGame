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

OBSTACLE_COLORS = {
    OBSTACLE_SQUARE: (239, 68, 68),
    OBSTACLE_BIRD: (59, 130, 246),
    OBSTACLE_TURTLE: (16, 185, 129),
    OBSTACLE_MUSHROOM: (34, 197, 94),
    OBSTACLE_MACHINEGUN: (255, 100, 30),
}

OBSTACLE_GLOW_COLORS = {
    OBSTACLE_SQUARE: (248, 113, 113),
    OBSTACLE_BIRD: (96, 165, 250),
    OBSTACLE_TURTLE: (52, 211, 153),
    OBSTACLE_MUSHROOM: (74, 222, 128),
    OBSTACLE_MACHINEGUN: (255, 160, 80),
}

# Fonts
font_title = pygame.font.Font(None, 64)
font_header = pygame.font.Font(None, 36)
font_normal = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 22)
font_popup = pygame.font.Font(None, 32)

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
ENTER_NAME = "enter_name"
LEADERBOARD = "leaderboard"

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
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient


class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, text_color=WHITE, radius=16):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
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

        text_surf = font_normal.render(self.text, True, self.text_color)
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
            title_surf = font_header.render(self.title, True, (160, 170, 220))
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

    if glow_color and target_surface is None:
        pulse_size = 3 + math.sin(pulse) * 2
        glow_rect = pygame.Rect(x - pulse_size, y - pulse_size, size + pulse_size * 2, size + pulse_size * 2)
        for i in range(4):
            r = 12 + i * 5
            alpha = max(5, 50 - i * 12)
            gs = pygame.Surface((glow_rect.width + r * 2, glow_rect.height + r * 2), pygame.SRCALPHA)
            if shape == "aeroplane":
                pygame.draw.ellipse(gs, (*glow_color, alpha), gs.get_rect())
            else:
                pygame.draw.rect(gs, (*glow_color, alpha), gs.get_rect(), border_radius=r + 5)
            surf.blit(gs, (glow_rect.x - r, glow_rect.y - r))

    cx = x + size // 2
    cy = y + size // 2
    half = size // 2
    s = max(size / 40.0, 0.1)  # scale factor relative to default size 40

    if shape == "spaceship":
        # --- Sleek rocket body ---
        body_pts = [
            (cx, y - int(4 * s)),                          # nose tip
            (cx + int(5 * s), y + int(6 * s)),             # upper right
            (cx + int(7 * s), y + int(16 * s)),            # mid right
            (cx + int(8 * s), y + int(28 * s)),            # lower right widest
            (cx + int(6 * s), y + size),                   # engine right
            (cx - int(6 * s), y + size),                   # engine left
            (cx - int(8 * s), y + int(28 * s)),            # lower left widest
            (cx - int(7 * s), y + int(16 * s)),            # mid left
            (cx - int(5 * s), y + int(6 * s)),             # upper left
        ]
        pygame.draw.polygon(surf, color, body_pts)

        # Hull panel lines for depth
        panel_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
        po = 10  # panel offset
        line_color = (*tuple(max(0, c - 35) for c in color), 100)
        pygame.draw.line(panel_surf, line_color,
                         (cx - x + po, y + int(10 * s) - y + po),
                         (cx - x + po, y + int(30 * s) - y + po), 1)
        pygame.draw.line(panel_surf, line_color,
                         (cx - x + po - int(5 * s), y + int(18 * s) - y + po),
                         (cx - x + po + int(5 * s), y + int(18 * s) - y + po), 1)
        pygame.draw.line(panel_surf, line_color,
                         (cx - x + po - int(6 * s), y + int(26 * s) - y + po),
                         (cx - x + po + int(6 * s), y + int(26 * s) - y + po), 1)
        surf.blit(panel_surf, (x - 10, y - 10))

        # Swept-back side fins with gradient shading
        darker = tuple(max(0, c - 50) for c in color)
        lighter = tuple(min(255, c + 20) for c in color)
        # Left fin
        fin_l = [
            (cx - int(8 * s), y + int(28 * s)),
            (cx - int(16 * s), y + size + int(4 * s)),
            (cx - int(10 * s), y + size + int(2 * s)),
            (cx - int(6 * s), y + size),
        ]
        pygame.draw.polygon(surf, darker, fin_l)
        # Right fin
        fin_r = [
            (cx + int(8 * s), y + int(28 * s)),
            (cx + int(16 * s), y + size + int(4 * s)),
            (cx + int(10 * s), y + size + int(2 * s)),
            (cx + int(6 * s), y + size),
        ]
        pygame.draw.polygon(surf, lighter, fin_r)

        # Engine nozzle - darker rectangle at bottom
        nozzle_w = int(10 * s)
        nozzle_h = int(4 * s)
        nozzle_color = tuple(max(0, c - 70) for c in color)
        pygame.draw.rect(surf, nozzle_color,
                         (cx - nozzle_w // 2, y + size - nozzle_h, nozzle_w, nozzle_h),
                         border_radius=max(1, int(s)))

        # Cockpit - bright oval window near the top with glint
        cockpit_w = max(2, int(8 * s))
        cockpit_h = max(3, int(12 * s))
        cockpit_y = y + int(8 * s)
        cockpit_surf = pygame.Surface((cockpit_w + 4, cockpit_h + 4), pygame.SRCALPHA)
        # Cockpit base
        pygame.draw.ellipse(cockpit_surf, (100, 180, 255, 180),
                            (2, 2, cockpit_w, cockpit_h))
        # Bright inner glint
        glint_w = max(1, cockpit_w // 2)
        glint_h = max(1, cockpit_h // 3)
        pygame.draw.ellipse(cockpit_surf, (200, 230, 255, 220),
                            (2 + cockpit_w // 4, 2 + int(1 * s), glint_w, glint_h))
        surf.blit(cockpit_surf, (cx - cockpit_w // 2 - 2, cockpit_y - 2))

        # Multi-layered animated thruster flame
        flame_flicker = math.sin(pulse * 6) * 3 + 5
        flame_len = int(flame_flicker * s) + int(6 * s)
        flame_w = int(12 * s)
        flame_surf = pygame.Surface((flame_w + 10, flame_len + 10), pygame.SRCALPHA)
        fo = 5  # flame offset
        # Outer flame (orange)
        outer_pts = [
            (fo + flame_w // 2 - int(5 * s), 0 + fo),
            (fo + flame_w // 2, flame_len + fo),
            (fo + flame_w // 2 + int(5 * s), 0 + fo),
        ]
        pygame.draw.polygon(flame_surf, (255, 120, 20, 150), outer_pts)
        # Inner flame (yellow)
        inner_len = int(flame_len * 0.65)
        inner_pts = [
            (fo + flame_w // 2 - int(3 * s), 0 + fo),
            (fo + flame_w // 2, inner_len + fo),
            (fo + flame_w // 2 + int(3 * s), 0 + fo),
        ]
        pygame.draw.polygon(flame_surf, (255, 220, 80, 200), inner_pts)
        # Core (white-hot)
        core_len = int(flame_len * 0.3)
        core_pts = [
            (fo + flame_w // 2 - int(1 * s), 0 + fo),
            (fo + flame_w // 2, core_len + fo),
            (fo + flame_w // 2 + int(1 * s), 0 + fo),
        ]
        pygame.draw.polygon(flame_surf, (255, 255, 220, 230), core_pts)
        surf.blit(flame_surf, (cx - flame_w // 2 - 5, y + size - fo))

    elif shape == "aeroplane":
        # --- Properly proportioned aeroplane ---
        # Fuselage - elongated cylinder-like body
        fuse_w = max(3, int(12 * s))
        fuse_h = size + int(4 * s)
        fuse_x = cx - fuse_w // 2
        fuse_y = y - int(2 * s)
        pygame.draw.ellipse(surf, color, (fuse_x, fuse_y, fuse_w, fuse_h))

        # Nose cone - rounded lighter front
        nose_w = max(2, int(8 * s))
        nose_h = max(3, int(8 * s))
        nose_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.ellipse(surf, nose_color,
                            (cx - nose_w // 2, y - int(3 * s), nose_w, nose_h))

        # Main swept-back wings extending well past body
        wing_color = tuple(min(255, c + 15) for c in color)
        wing_tip_color = tuple(min(255, c + 40) for c in color)
        wing_y = cy + int(2 * s)
        # Left wing
        wing_l = [
            (cx - int(2 * s), wing_y - int(2 * s)),
            (cx - int(20 * s), wing_y + int(6 * s)),
            (cx - int(18 * s), wing_y + int(8 * s)),
            (cx - int(2 * s), wing_y + int(3 * s)),
        ]
        pygame.draw.polygon(surf, wing_color, wing_l)
        # Left wing tip marking
        tip_l = [
            (cx - int(17 * s), wing_y + int(5 * s)),
            (cx - int(20 * s), wing_y + int(6 * s)),
            (cx - int(18 * s), wing_y + int(8 * s)),
            (cx - int(16 * s), wing_y + int(7 * s)),
        ]
        pygame.draw.polygon(surf, wing_tip_color, tip_l)
        # Right wing
        wing_r = [
            (cx + int(2 * s), wing_y - int(2 * s)),
            (cx + int(20 * s), wing_y + int(6 * s)),
            (cx + int(18 * s), wing_y + int(8 * s)),
            (cx + int(2 * s), wing_y + int(3 * s)),
        ]
        pygame.draw.polygon(surf, wing_color, wing_r)
        # Right wing tip marking
        tip_r = [
            (cx + int(17 * s), wing_y + int(5 * s)),
            (cx + int(20 * s), wing_y + int(6 * s)),
            (cx + int(18 * s), wing_y + int(8 * s)),
            (cx + int(16 * s), wing_y + int(7 * s)),
        ]
        pygame.draw.polygon(surf, wing_tip_color, tip_r)

        # Engine nacelles under wings
        nacelle_color = tuple(max(0, c - 40) for c in color)
        nacelle_r = max(1, int(3 * s))
        pygame.draw.circle(surf, nacelle_color,
                           (cx - int(12 * s), wing_y + int(5 * s)), nacelle_r)
        pygame.draw.circle(surf, nacelle_color,
                           (cx + int(12 * s), wing_y + int(5 * s)), nacelle_r)

        # Tail section - vertical stabilizer (tall fin)
        tail_color = tuple(max(0, c - 25) for c in color)
        # Vertical stabilizer
        vstab = [
            (cx, y + size - int(10 * s)),
            (cx - int(1 * s), y + size),
            (cx + int(1 * s), y + size),
        ]
        pygame.draw.polygon(surf, tail_color, vstab)
        # Horizontal stabilizers (small rear wings)
        hstab_l = [
            (cx - int(1 * s), y + size - int(4 * s)),
            (cx - int(10 * s), y + size),
            (cx - int(1 * s), y + size),
        ]
        hstab_r = [
            (cx + int(1 * s), y + size - int(4 * s)),
            (cx + int(10 * s), y + size),
            (cx + int(1 * s), y + size),
        ]
        pygame.draw.polygon(surf, tail_color, hstab_l)
        pygame.draw.polygon(surf, tail_color, hstab_r)

        # Cockpit windshield at the front
        cockpit_surf = pygame.Surface((int(8 * s), int(10 * s)), pygame.SRCALPHA)
        cw = max(2, int(6 * s))
        ch = max(3, int(8 * s))
        pygame.draw.ellipse(cockpit_surf, (180, 230, 255, 160), (1, 1, cw, ch))
        # Glint
        pygame.draw.ellipse(cockpit_surf, (220, 245, 255, 200),
                            (1 + cw // 4, 1, max(1, cw // 2), max(1, ch // 3)))
        surf.blit(cockpit_surf, (cx - cw // 2 - 1, y + int(1 * s)))

    elif shape == "dragon":
        # --- Detailed dragon with serpentine body ---
        segments = 8
        seg_positions = []
        for i in range(segments):
            t = i / (segments - 1)
            sx = cx + math.sin(t * math.pi * 2 + pulse * 2) * (size // 4)
            sy = y + size - t * size
            seg_positions.append((sx, sy))

        # Bat-like wings from upper body (segment 5-6 area)
        wing_seg = min(5, segments - 2)
        wing_x = seg_positions[wing_seg][0]
        wing_y_pos = seg_positions[wing_seg][1]
        wing_color = tuple(min(255, c + 10) for c in color)
        membrane_color = (*tuple(min(255, c + 30) for c in color), 80)
        wing_span = int(18 * s)
        wing_h = int(14 * s)

        wing_surf = pygame.Surface((size + int(40 * s), size + 20), pygame.SRCALPHA)
        wo = int(20 * s)  # wing offset for surface coordinates

        # Left wing - 3 bone segments with membrane
        lw_base = (wing_x - x + wo, wing_y_pos - y + 10)
        lw_tip1 = (wing_x - x + wo - wing_span, wing_y_pos - y + 10 - wing_h)
        lw_tip2 = (wing_x - x + wo - int(wing_span * 0.7), wing_y_pos - y + 10 - int(wing_h * 0.5))
        lw_tip3 = (wing_x - x + wo - int(wing_span * 0.4), wing_y_pos - y + 10 + int(3 * s))
        # Membrane fill
        membrane_pts = [lw_base, lw_tip1, lw_tip2, lw_tip3]
        pygame.draw.polygon(wing_surf, membrane_color, membrane_pts)
        # Bone lines
        bone_color = (*tuple(min(255, c + 50) for c in color), 180)
        pygame.draw.line(wing_surf, bone_color, lw_base, lw_tip1, max(1, int(s)))
        pygame.draw.line(wing_surf, bone_color, lw_base, lw_tip2, max(1, int(s)))
        pygame.draw.line(wing_surf, bone_color, lw_base, lw_tip3, max(1, int(s)))

        # Right wing
        rw_base = (wing_x - x + wo, wing_y_pos - y + 10)
        rw_tip1 = (wing_x - x + wo + wing_span, wing_y_pos - y + 10 - wing_h)
        rw_tip2 = (wing_x - x + wo + int(wing_span * 0.7), wing_y_pos - y + 10 - int(wing_h * 0.5))
        rw_tip3 = (wing_x - x + wo + int(wing_span * 0.4), wing_y_pos - y + 10 + int(3 * s))
        membrane_pts_r = [rw_base, rw_tip1, rw_tip2, rw_tip3]
        pygame.draw.polygon(wing_surf, membrane_color, membrane_pts_r)
        pygame.draw.line(wing_surf, bone_color, rw_base, rw_tip1, max(1, int(s)))
        pygame.draw.line(wing_surf, bone_color, rw_base, rw_tip2, max(1, int(s)))
        pygame.draw.line(wing_surf, bone_color, rw_base, rw_tip3, max(1, int(s)))

        surf.blit(wing_surf, (x - int(20 * s), y - 10))

        # Serpentine body with scaled segments tapering thick to thin
        for i in range(segments):
            t = i / (segments - 1)
            sx, sy = seg_positions[i]
            seg_r = max(2, int((size // 4) * (0.4 + 0.6 * (1 - t))))
            # Scale pattern with color variation
            base_shade = int(20 * math.sin(i * 1.5 + pulse))
            seg_color = tuple(max(0, min(255, c - int(25 * t) + base_shade)) for c in color)
            pygame.draw.circle(surf, seg_color, (int(sx), int(sy)), seg_r)
            # Overlapping scale highlight on upper half
            if seg_r > 3:
                scale_surf = pygame.Surface((seg_r * 2, seg_r * 2), pygame.SRCALPHA)
                highlight_color = (*tuple(min(255, c + 40) for c in color), 60)
                pygame.draw.arc(scale_surf, highlight_color,
                                (0, 0, seg_r * 2, seg_r * 2),
                                0.3, math.pi - 0.3, max(1, int(s)))
                surf.blit(scale_surf, (int(sx) - seg_r, int(sy) - seg_r))

        # Tapered tail ending in spade/arrow shape
        tail_x, tail_y = seg_positions[0]
        spade_size = max(2, int(5 * s))
        spade_pts = [
            (int(tail_x), int(tail_y) + int(4 * s)),
            (int(tail_x) - spade_size, int(tail_y) + spade_size + int(4 * s)),
            (int(tail_x), int(tail_y) + int(2 * s) + int(4 * s)),
            (int(tail_x) + spade_size, int(tail_y) + spade_size + int(4 * s)),
        ]
        spade_color = tuple(max(0, c - 30) for c in color)
        pygame.draw.polygon(surf, spade_color, spade_pts)

        # Small clawed limbs (from segments 2 and 4)
        limb_color = tuple(max(0, c - 40) for c in color)
        for li in [2, 4]:
            if li < segments:
                lx, ly = seg_positions[li]
                lr = max(2, int(3 * s))
                # Left leg
                pygame.draw.line(surf, limb_color,
                                 (int(lx) - lr, int(ly)),
                                 (int(lx) - lr - int(4 * s), int(ly) + int(5 * s)),
                                 max(1, int(s)))
                # Claw
                pygame.draw.line(surf, limb_color,
                                 (int(lx) - lr - int(4 * s), int(ly) + int(5 * s)),
                                 (int(lx) - lr - int(6 * s), int(ly) + int(4 * s)),
                                 max(1, int(s)))
                # Right leg
                pygame.draw.line(surf, limb_color,
                                 (int(lx) + lr, int(ly)),
                                 (int(lx) + lr + int(4 * s), int(ly) + int(5 * s)),
                                 max(1, int(s)))
                pygame.draw.line(surf, limb_color,
                                 (int(lx) + lr + int(4 * s), int(ly) + int(5 * s)),
                                 (int(lx) + lr + int(6 * s), int(ly) + int(4 * s)),
                                 max(1, int(s)))

        # Angular head with snout, jaw, and horns
        head_x = seg_positions[-1][0]
        head_y = seg_positions[-1][1]
        head_r = max(3, int(6 * s))

        # Head base (angular)
        head_pts = [
            (int(head_x), int(head_y) - int(8 * s)),        # top snout
            (int(head_x) + int(7 * s), int(head_y) - int(2 * s)),  # right cheek
            (int(head_x) + int(5 * s), int(head_y) + int(4 * s)),  # right jaw
            (int(head_x) - int(5 * s), int(head_y) + int(4 * s)),  # left jaw
            (int(head_x) - int(7 * s), int(head_y) - int(2 * s)),  # left cheek
        ]
        head_color = tuple(min(255, c + 15) for c in color)
        pygame.draw.polygon(surf, head_color, head_pts)

        # Horns
        horn_color = tuple(min(255, c + 60) for c in color)
        # Left horn
        pygame.draw.line(surf, horn_color,
                         (int(head_x) - int(5 * s), int(head_y) - int(3 * s)),
                         (int(head_x) - int(9 * s), int(head_y) - int(10 * s)),
                         max(1, int(1.5 * s)))
        # Right horn
        pygame.draw.line(surf, horn_color,
                         (int(head_x) + int(5 * s), int(head_y) - int(3 * s)),
                         (int(head_x) + int(9 * s), int(head_y) - int(10 * s)),
                         max(1, int(1.5 * s)))

        # Lower jaw (slightly open)
        jaw_pts = [
            (int(head_x) - int(4 * s), int(head_y) + int(4 * s)),
            (int(head_x), int(head_y) + int(8 * s)),
            (int(head_x) + int(4 * s), int(head_y) + int(4 * s)),
        ]
        jaw_color = tuple(max(0, c - 50) for c in color)
        pygame.draw.polygon(surf, jaw_color, jaw_pts)

        # Glowing eyes (red/orange with bright center)
        eye_r = max(1, int(2.5 * s))
        eye_glow_r = max(2, int(4 * s))
        for ex_offset in [-int(3 * s), int(3 * s)]:
            eye_cx = int(head_x) + ex_offset
            eye_cy = int(head_y) - int(2 * s)
            # Eye glow
            eye_glow_surf = pygame.Surface((eye_glow_r * 2, eye_glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow_surf, (255, 60, 20, 80),
                               (eye_glow_r, eye_glow_r), eye_glow_r)
            surf.blit(eye_glow_surf, (eye_cx - eye_glow_r, eye_cy - eye_glow_r))
            # Eye core
            pygame.draw.circle(surf, (255, 100, 30), (eye_cx, eye_cy), eye_r)
            # Bright pupil
            pygame.draw.circle(surf, (255, 220, 80), (eye_cx, eye_cy), max(1, eye_r // 2))

        # Fire breath - animated flame particles from the mouth
        flame_surf = pygame.Surface((int(20 * s), int(16 * s)), pygame.SRCALPHA)
        mouth_x = int(head_x)
        mouth_y = int(head_y) + int(7 * s)
        flame_len = int(6 * s + math.sin(pulse * 5) * 3 * s)
        # Outer fire
        fire_pts = [
            (int(10 * s), 0),
            (int(10 * s) - int(4 * s), flame_len),
            (int(10 * s) + int(4 * s), flame_len),
        ]
        pygame.draw.polygon(flame_surf, (255, 80, 20, 140), fire_pts)
        # Inner fire
        inner_fire = [
            (int(10 * s), 0),
            (int(10 * s) - int(2 * s), int(flame_len * 0.6)),
            (int(10 * s) + int(2 * s), int(flame_len * 0.6)),
        ]
        pygame.draw.polygon(flame_surf, (255, 200, 50, 180), inner_fire)
        surf.blit(flame_surf, (mouth_x - int(10 * s), mouth_y))


def draw_obstacle(obstacle_type, x, y, size, glow_color=None, pulse=0, time_offset=0):
    color = OBSTACLE_COLORS[obstacle_type]

    if glow_color:
        pulse_size = 2 + math.sin(pulse) * 1.5
        glow_rect = pygame.Rect(x - pulse_size, y - pulse_size, size + pulse_size * 2, size + pulse_size * 2)
        for i in range(3):
            r = 8 + i * 4
            alpha = max(5, 35 - i * 10)
            gs = pygame.Surface((glow_rect.width + r * 2, glow_rect.height + r * 2), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*glow_color, alpha), gs.get_rect(), border_radius=r + 3)
            screen.blit(gs, (glow_rect.x - r, glow_rect.y - r))

    if obstacle_type == OBSTACLE_SQUARE:
        # Rotation animation - draw rotated square
        angle = time_offset * 3 % 360
        cx, cy = x + size // 2, y + size // 2
        half = size // 2
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        corners = [(-half, -half), (half, -half), (half, half), (-half, half)]
        rotated = [(cx + px * cos_a - py * sin_a, cy + px * sin_a + py * cos_a) for px, py in corners]
        pygame.draw.polygon(screen, color, rotated)
        # Inner spinning detail
        inner_half = size // 4
        inner_corners = [(-inner_half, -inner_half), (inner_half, -inner_half),
                         (inner_half, inner_half), (-inner_half, inner_half)]
        inner_rotated = [(cx + px * cos_a - py * sin_a, cy + px * sin_a + py * cos_a) for px, py in inner_corners]
        pygame.draw.polygon(screen, tuple(max(0, c - 40) for c in color), inner_rotated)
    elif obstacle_type == OBSTACLE_BIRD:
        # Wing flap animation
        wing_offset = int(math.sin(time_offset * 0.3) * 6)
        pygame.draw.ellipse(screen, color, (x, y + 5, size, size - 10))
        # Left wing
        wing_points_l = [(x + 5, y + size // 2), (x - 5, y + size // 2 - 8 + wing_offset), (x + size // 3, y + size // 2)]
        pygame.draw.polygon(screen, tuple(min(255, c + 30) for c in color), wing_points_l)
        # Right wing
        wing_points_r = [(x + size - 5, y + size // 2), (x + size + 5, y + size // 2 - 8 + wing_offset), (x + size * 2 // 3, y + size // 2)]
        pygame.draw.polygon(screen, tuple(min(255, c + 30) for c in color), wing_points_r)
        # Eye
        pygame.draw.circle(screen, (220, 220, 255), (x + size // 2 + 2, y + size // 2 - 2), 3)
        pygame.draw.circle(screen, (20, 20, 20), (x + size // 2 + 2, y + size // 2 - 2), 1)
    elif obstacle_type == OBSTACLE_TURTLE:
        # Bobbing animation
        bob = int(math.sin(time_offset * 0.15) * 3)
        ty = y + bob
        pygame.draw.ellipse(screen, color, (x + 2, ty, size - 4, size))
        pygame.draw.ellipse(screen, tuple(max(0, c - 50) for c in color), (x + size // 3, ty + size // 4, size // 3, size // 2))
        pygame.draw.circle(screen, (80, 200, 80), (x + size // 2, ty - 3), 6)
    elif obstacle_type == OBSTACLE_MUSHROOM:
        # Bounce animation
        bounce = abs(int(math.sin(time_offset * 0.2) * 3))
        my = y - bounce
        pygame.draw.rect(screen, (200, 180, 140), (x + size // 3, my + size // 2, size // 3, size // 2 + bounce), border_radius=5)
        pygame.draw.ellipse(screen, color, (x + 2, my, size - 4, size // 2 + 5))
        pygame.draw.circle(screen, (240, 240, 240, 180), (x + size // 3, my + size // 4), 4)
        pygame.draw.circle(screen, (240, 240, 240, 180), (x + size * 2 // 3, my + size // 4), 3)
    elif obstacle_type == OBSTACLE_MACHINEGUN:
        # Gun body (rectangular)
        body_rect = (x + size // 4, y + size // 3, size // 2, size // 2)
        pygame.draw.rect(screen, color, body_rect, border_radius=3)
        # Barrel extending upward
        barrel_rect = (x + size // 2 - 3, y + 2, 6, size // 3)
        pygame.draw.rect(screen, tuple(min(255, c + 30) for c in color), barrel_rect)
        # Muzzle flash animation
        flash_intensity = abs(math.sin(time_offset * 0.4))
        if flash_intensity > 0.5:
            flash_size = int(4 + flash_intensity * 4)
            flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            flash_alpha = int(flash_intensity * 200)
            pygame.draw.circle(flash_surf, (255, 200, 50, flash_alpha), (flash_size, flash_size), flash_size)
            screen.blit(flash_surf, (x + size // 2 - flash_size, y + 2 - flash_size))
        # Handle / grip
        grip_rect = (x + size // 3, y + size * 3 // 4, size // 5, size // 4)
        pygame.draw.rect(screen, tuple(max(0, c - 60) for c in color), grip_rect, border_radius=2)


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
    machinegun_timer = 0
    MACHINEGUN_DURATION = 10000
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

    difficulty_settings = {
        1: {"blocks": 1, "base_speed": 3, "spawn_rate": 60, "name": "Easy"},
        2: {"blocks": 2, "base_speed": 4, "spawn_rate": 50, "name": "Medium"},
        3: {"blocks": 3, "base_speed": 5, "spawn_rate": 40, "name": "Hard"}
    }

    obstacle_weights = [60, 12, 12, 16, 10]

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
        Button(55, 370, 90, 50, "Ship", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 12),
        Button(165, 370, 90, 50, "Plane", SUCCESS_COLOR, (52, 211, 153), WHITE, 12),
        Button(275, 370, 90, 50, "Dragon", WARNING_COLOR, (251, 191, 36), WHITE, 12)
    ]

    start_button = Button(WIDTH // 2 - 100, 460, 200, 55, "PLAY", PRIMARY_COLOR, PRIMARY_HOVER, WHITE, 18)
    scores_menu_button = Button(WIDTH // 2 - 100, 525, 200, 45, "SCORES", WARNING_COLOR, (251, 191, 36), WHITE, 14)
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
                        speed_boost_timer = 0
                        speed_slow_timer = 0
                        shrink_timer = 0
                        machinegun_timer = 0
                        bullets = []
                        bullet_cooldown = 0
                        player_size = original_player_size
                        particle_system = ParticleSystem()
                        player_trail = []
                        score_popups = []
                        last_obstacle_count = 0
                        shake_intensity = 0
                        game_over_timer = 0
                        player_name = ""
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
                        speed_boost_timer = 0
                        speed_slow_timer = 0
                        shrink_timer = 0
                        machinegun_timer = 0
                        bullets = []
                        bullet_cooldown = 0
                        player_size = original_player_size
                        particle_system = ParticleSystem()
                        player_trail = []
                        score_popups = []
                        last_obstacle_count = 0
                        shake_intensity = 0
                        game_over_timer = 0
                        player_name = ""
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
                            speed_boost_timer = 0
                            speed_slow_timer = 0
                            shrink_timer = 0
                            machinegun_timer = 0
                            bullets = []
                            bullet_cooldown = 0
                            player_size = original_player_size
                            particle_system = ParticleSystem()
                            player_trail = []
                            score_popups = []
                            last_obstacle_count = 0
                            shake_intensity = 0
                            game_over_timer = 0
                            player_name = ""
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
            for btn in orient_buttons + diff_buttons + role_buttons + [start_button, scores_menu_button]:
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
            role_panel = SectionPanel(30, 330, WIDTH - 60, 110, "Player")

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
                preview_size = 20
                preview_x = btn.rect.x + 4
                preview_y = btn.rect.centery - preview_size // 2
                draw_player(roles[i], role_colors_list[i], preview_x, preview_y,
                            preview_size, pulse=time_offset * 0.15)

            legend_y = 470
            legend_x = 55

            draw_obstacle(OBSTACLE_SQUARE, legend_x, legend_y, 24, OBSTACLE_GLOW_COLORS[OBSTACLE_SQUARE], time_offset=time_offset)
            legend_text = font_small.render("= Game Over", True, (180, 190, 210))
            screen.blit(legend_text, (legend_x + 30, legend_y + 3))

            draw_obstacle(OBSTACLE_BIRD, legend_x + 140, legend_y, 24, OBSTACLE_GLOW_COLORS[OBSTACLE_BIRD], time_offset=time_offset)
            legend_text2 = font_small.render("= Speed Up", True, (96, 165, 250))
            screen.blit(legend_text2, (legend_x + 170, legend_y + 3))

            draw_obstacle(OBSTACLE_TURTLE, legend_x + 280, legend_y, 24, OBSTACLE_GLOW_COLORS[OBSTACLE_TURTLE], time_offset=time_offset)
            legend_text3 = font_small.render("= Slow", True, (52, 211, 153))
            screen.blit(legend_text3, (legend_x + 310, legend_y + 3))

            # Only show mushroom if wide enough
            if WIDTH > 450:
                draw_obstacle(OBSTACLE_MUSHROOM, legend_x + 390, legend_y, 24, OBSTACLE_GLOW_COLORS[OBSTACLE_MUSHROOM], time_offset=time_offset)
                legend_text4 = font_small.render("= Shrink", True, (74, 222, 128))
                screen.blit(legend_text4, (legend_x + 420, legend_y + 3))

            # Gun legend on second row
            legend_y2 = legend_y + 30
            draw_obstacle(OBSTACLE_MACHINEGUN, legend_x, legend_y2, 24, OBSTACLE_GLOW_COLORS[OBSTACLE_MACHINEGUN], time_offset=time_offset)
            legend_text5 = font_small.render("= Gun", True, (255, 160, 80))
            screen.blit(legend_text5, (legend_x + 30, legend_y2 + 3))

            if selected_orientation == "vertical":
                control_hint = font_small.render("Controls: < > to move", True, (120, 140, 180))
            else:
                control_hint = font_small.render("Controls: ^ v to move", True, (120, 140, 180))
            screen.blit(control_hint, (WIDTH // 2 - control_hint.get_width() // 2, 560))

            start_button.draw(screen)
            scores_menu_button.draw(screen)

        elif game_state == PLAYING:
            particle_system.update()

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
                        obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MUSHROOM, OBSTACLE_MACHINEGUN], weights=obstacle_weights)[0]
                        obstacles.append([obstacle_x, -obstacle_size, obs_type])

                prev_count = len(obstacles)
                for obstacle in obstacles:
                    obstacle[1] += current_speed

                obstacles = [obs for obs in obstacles if obs[1] < HEIGHT]
                passed = prev_count - len(obstacles)
                if passed > 0 and len(score_popups) < 5:
                    score_popups.append(ScorePopup(player_x, player_y - 30, f"+{passed * 10}"))

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
                        obs_type = random.choices([OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MUSHROOM, OBSTACLE_MACHINEGUN], weights=obstacle_weights)[0]
                        obstacles.append([WIDTH, obstacle_y, obs_type])

                prev_count = len(obstacles)
                for obstacle in obstacles:
                    obstacle[0] -= current_speed

                obstacles = [obs for obs in obstacles if obs[0] > -obstacle_size]
                passed = prev_count - len(obstacles)
                if passed > 0 and len(score_popups) < 5:
                    score_popups.append(ScorePopup(player_x + player_size, player_y, f"+{passed * 10}"))

            size_offset = (original_player_size - player_size) // 2
            player_rect = pygame.Rect(player_x + size_offset, player_y + size_offset, player_size, player_size)

            # Update player trail
            player_trail.append((player_x + size_offset, player_y + size_offset, player_size))
            if len(player_trail) > TRAIL_LENGTH:
                player_trail.pop(0)

            for obstacle in obstacles[:]:
                obs_type = obstacle[2]
                enemy_rect = pygame.Rect(obstacle[0], obstacle[1], obstacle_size, obstacle_size)

                if player_rect.colliderect(enemy_rect):
                    center_x = enemy_rect.centerx
                    center_y = enemy_rect.centery

                    if obs_type == OBSTACLE_SQUARE:
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
                    elif obs_type == OBSTACLE_MUSHROOM:
                        particle_system.emit(center_x, center_y, (34, 197, 94), count=15, size=6, glow=True, spread=4)
                        shrink_timer = SHRINK_DURATION
                        obstacles.remove(obstacle)
                    elif obs_type == OBSTACLE_MACHINEGUN:
                        particle_system.emit(center_x, center_y, (255, 100, 30), count=15, size=6, glow=True, spread=4)
                        machinegun_timer = MACHINEGUN_DURATION
                        obstacles.remove(obstacle)

            # --- Machinegun bullet logic ---
            dt = clock.get_time()
            if machinegun_timer > 0:
                machinegun_timer -= dt
                bullet_cooldown -= dt
                if bullet_cooldown <= 0:
                    bullet_cooldown = 150
                    bcx = player_x + size_offset + player_size // 2
                    bcy = player_y + size_offset + player_size // 2
                    bullets.append([bcx, bcy])

            # Update bullets
            bullets_to_remove = []
            for b in bullets:
                if selected_orientation == "vertical":
                    b[1] -= 10
                    if b[1] < -10:
                        bullets_to_remove.append(b)
                else:
                    b[0] += 10
                    if b[0] > WIDTH + 10:
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
                        obs_rect = pygame.Rect(obs[0], obs[1], obstacle_size, obstacle_size)
                        bullet_rect = pygame.Rect(b[0] - 4, b[1] - 4, 8, 8)
                        if bullet_rect.colliderect(obs_rect):
                            bullets_hit.append(b)
                            obs_hit.append(obs)
                            cx_hit = obs_rect.centerx
                            cy_hit = obs_rect.centery
                            particle_system.emit(cx_hit, cy_hit, (255, 150, 50), count=12, size=5, glow=True, spread=4)
                            score_popups.append(ScorePopup(cx_hit, cy_hit - 20, "+20", (255, 200, 80)))
                            shake_intensity = max(shake_intensity, 3.0)
                            break
            for b in bullets_hit:
                if b in bullets:
                    bullets.remove(b)
            for o in obs_hit:
                if o in obstacles:
                    obstacles.remove(o)

            # Draw bullets
            for b in bullets:
                # Glow
                glow_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 200, 50, 80), (8, 8), 8)
                screen.blit(glow_surf, (int(b[0] - 8 + shake_offset_x), int(b[1] - 8 + shake_offset_y)))
                # Core
                pygame.draw.circle(screen, (255, 220, 80), (int(b[0] + shake_offset_x), int(b[1] + shake_offset_y)), 3)

            # Speed lines
            draw_speed_lines(screen, WIDTH, HEIGHT, selected_orientation, current_speed, time_offset)

            # Player trail
            draw_player_trail(screen, player_trail, selected_role, PLAYER_COLORS[selected_role], PLAYER_GLOW_COLORS[selected_role])

            draw_player(selected_role, PLAYER_COLORS[selected_role], int(player_x + size_offset + shake_offset_x), int(player_y + size_offset + shake_offset_y), int(player_size), PLAYER_GLOW_COLORS[selected_role], time_offset * 0.15)

            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0] + shake_offset_x), int(obstacle[1] + shake_offset_y), obstacle_size, OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset)

            particle_system.draw(screen)

            # Score popups
            for sp in score_popups[:]:
                sp.update()
                sp.draw(screen)
            score_popups = [sp for sp in score_popups if sp.is_alive()]

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

            effect_x = WIDTH - 140
            effect_y = status_y
            if speed_boost_timer > 0:
                effect_bg = pygame.Surface((130, 28), pygame.SRCALPHA)
                pygame.draw.rect(effect_bg, (20, 50, 120, 200), effect_bg.get_rect(), border_radius=8)
                pygame.draw.rect(effect_bg, (96, 165, 250, 150), effect_bg.get_rect(), 1, border_radius=8)
                screen.blit(effect_bg, (effect_x, effect_y))
                boost_text = font_small.render("SPEED UP!", True, (150, 200, 255))
                screen.blit(boost_text, (effect_x + 10, effect_y + 4))
                effect_y += 35
            elif speed_slow_timer > 0:
                effect_bg = pygame.Surface((120, 28), pygame.SRCALPHA)
                pygame.draw.rect(effect_bg, (10, 60, 50, 200), effect_bg.get_rect(), border_radius=8)
                pygame.draw.rect(effect_bg, (52, 211, 153, 150), effect_bg.get_rect(), 1, border_radius=8)
                screen.blit(effect_bg, (effect_x, effect_y))
                slow_text = font_small.render("SLOW DOWN", True, (100, 230, 180))
                screen.blit(slow_text, (effect_x + 10, effect_y + 4))
                effect_y += 35

            if shrink_timer > 0:
                effect_bg = pygame.Surface((110, 28), pygame.SRCALPHA)
                pygame.draw.rect(effect_bg, (15, 50, 30, 200), effect_bg.get_rect(), border_radius=8)
                pygame.draw.rect(effect_bg, (74, 222, 128, 150), effect_bg.get_rect(), 1, border_radius=8)
                screen.blit(effect_bg, (effect_x, effect_y))
                shrink_text = font_small.render("SHRINK!", True, (120, 240, 160))
                screen.blit(shrink_text, (effect_x + 10, effect_y + 4))
                effect_y += 35

            if machinegun_timer > 0:
                effect_bg = pygame.Surface((140, 28), pygame.SRCALPHA)
                pygame.draw.rect(effect_bg, (80, 30, 10, 200), effect_bg.get_rect(), border_radius=8)
                pygame.draw.rect(effect_bg, (255, 160, 80, 150), effect_bg.get_rect(), 1, border_radius=8)
                screen.blit(effect_bg, (effect_x, effect_y))
                gun_text = font_small.render("MACHINE GUN!", True, (255, 180, 100))
                screen.blit(gun_text, (effect_x + 10, effect_y + 4))

        elif game_state == GAME_OVER:
            particle_system.update()

            # Speed lines still visible but fading
            draw_speed_lines(screen, WIDTH, HEIGHT, selected_orientation, max(0, current_speed * 0.5), time_offset)

            # Draw remaining obstacles with shake
            for obstacle in obstacles:
                draw_obstacle(obstacle[2], int(obstacle[0] + shake_offset_x), int(obstacle[1] + shake_offset_y), obstacle_size, OBSTACLE_GLOW_COLORS[obstacle[2]], time_offset * 0.1, time_offset)

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

                if anim_progress >= 1.0:
                    restart_button.rect.y = HEIGHT // 2 + 20
                    menu_button.rect.y = HEIGHT // 2 + 80
                    restart_button.update()
                    menu_button.update()
                    restart_button.draw(screen)
                    menu_button.draw(screen)

                    if qualifies_for_leaderboard:
                        save_score_button.rect.y = HEIGHT // 2 + 140
                        save_score_button.update()
                        save_score_button.draw(screen)
                    else:
                        scores_gameover_button.rect.y = HEIGHT // 2 + 140
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
