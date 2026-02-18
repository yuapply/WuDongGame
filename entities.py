import pygame
import random

import game_globals
from constants import (
    NEON_CYAN, NEON_PINK, NEON_BLUE, PRIMARY_COLOR, PRIMARY_GLOW,
    PRIMARY_HOVER, WHITE,
)


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
            txt = game_globals.font_popup.render(self.text, True, self.color)
            txt_surface = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
            txt_surface.blit(txt, (0, 0))
            txt_surface.set_alpha(alpha)
            surface.blit(txt_surface, (int(self.x), int(self.y)))

    def is_alive(self):
        return self.lifetime > 0


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


class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY_COLOR,
                 hover_color=PRIMARY_HOVER, text_color=WHITE, radius=16, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.font = font or game_globals.font_normal
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

        btn_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (15, 15, 30, 200), btn_surface.get_rect(), border_radius=self.radius)
        surface.blit(btn_surface, (scaled_rect.x, scaled_rect.y))

        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) or self.is_selected else self.color

        border_width = 2 if not self.is_selected else 3
        pygame.draw.rect(surface, color, scaled_rect, border_width, border_radius=self.radius)

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
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (10, 12, 25, 180), panel_surface.get_rect(), border_radius=20)
        surface.blit(panel_surface, (self.rect.x, self.rect.y))

        pygame.draw.rect(surface, (50, 60, 120), self.rect, 1, border_radius=20)

        if self.title:
            title_surf = game_globals.font_menu_section.render(self.title, True, (160, 170, 220))
            surface.blit(title_surf, (self.rect.x + 20, self.rect.y + 12))
