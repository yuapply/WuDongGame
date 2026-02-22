import pygame
import math
import random

import game_globals
from constants import (
    NEON_CYAN, WHITE,
    OBSTACLE_SQUARE, OBSTACLE_BIRD, OBSTACLE_TURTLE, OBSTACLE_MUSHROOM,
    OBSTACLE_MACHINEGUN, OBSTACLE_SHOTGUN, OBSTACLE_STEEL_BAR, OBSTACLE_XRAY_GUN,
    OBSTACLE_COLORS, OBSTACLE_GLOW_COLORS,
)


def draw_glow(surface, color, rect, radius=15, intensity=50):
    for i in range(3):
        r = radius + i * 6
        alpha = max(5, intensity - i * 15)
        glow_surface = pygame.Surface((rect.width + r * 2, rect.height + r * 2), pygame.SRCALPHA)
        glow_color = (*color, alpha)
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=r + 5)
        surface.blit(glow_surface, (rect.x - r, rect.y - r))


def draw_player(shape, color, x, y, size, glow_color=None, pulse=0, target_surface=None, orientation="vertical"):
    surf = target_surface if target_surface is not None else game_globals.screen

    if orientation == "horizontal":
        temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        draw_player_internal(shape, color, 0, 0, size, glow_color, pulse, temp_surf)
        rotated_surf = pygame.transform.rotate(temp_surf, -90)
        surf.blit(rotated_surf, (x, y))
        return

    draw_player_internal(shape, color, x, y, size, glow_color, pulse, surf)


def draw_player_internal(shape, color, x, y, size, glow_color=None, pulse=0, target_surface=None):
    surf = target_surface if target_surface is not None else game_globals.screen

    cx = x + size // 2
    cy = y + size // 2
    half = size // 2
    s = max(size / 40.0, 0.1)  # scale factor relative to default size 40

    if shape == "spaceship":
        # --- Advanced Sci-Fi Interceptor ---
        hull_pts = [
            (cx, y),
            (cx + int(10 * s), y + int(25 * s)),
            (cx + int(8 * s), y + size),
            (cx - int(8 * s), y + size),
            (cx - int(10 * s), y + int(25 * s)),
        ]
        pygame.draw.polygon(surf, color, hull_pts)

        ridge_color = tuple(min(255, c + 40) for c in color)
        pygame.draw.line(surf, ridge_color, (cx, y + int(5 * s)), (cx, y + size - int(5 * s)), max(1, int(2 * s)))

        wing_color = tuple(max(0, c - 30) for c in color)
        pygame.draw.polygon(surf, wing_color, [
            (cx - int(8 * s), y + int(15 * s)),
            (cx - int(22 * s), y + size - int(5 * s)),
            (cx - int(22 * s), y + size + int(2 * s)),
            (cx - int(8 * s), y + size - int(5 * s))
        ])
        pygame.draw.polygon(surf, wing_color, [
            (cx + int(8 * s), y + int(15 * s)),
            (cx + int(22 * s), y + size - int(5 * s)),
            (cx + int(22 * s), y + size + int(2 * s)),
            (cx + int(8 * s), y + size - int(5 * s))
        ])

        light_color = NEON_CYAN if (pulse % 0.4) > 0.2 else (255, 255, 255)
        pygame.draw.circle(surf, light_color, (cx - int(20 * s), y + size - int(2 * s)), max(1, int(2 * s)))
        pygame.draw.circle(surf, light_color, (cx + int(20 * s), y + size - int(2 * s)), max(1, int(2 * s)))

        cockpit_rect = (cx - int(4 * s), y + int(8 * s), int(8 * s), int(14 * s))
        pygame.draw.ellipse(surf, (30, 40, 60), cockpit_rect)
        pygame.draw.ellipse(surf, (100, 200, 255),
                            (cx - int(3 * s), y + int(10 * s), int(6 * s), int(5 * s)))

        engine_w = int(12 * s)
        flame_h = int((10 + math.sin(pulse * 10) * 5) * s)
        pygame.draw.rect(surf, (255, 100, 0), (cx - engine_w // 2, y + size, engine_w, flame_h // 2), border_radius=3)
        pygame.draw.rect(surf, (255, 255, 200), (cx - engine_w // 4, y + size, engine_w // 2, flame_h // 3), border_radius=2)

    elif shape == "aeroplane":
        # --- Light Ghost Gray Air Superiority Fighter ---
        BODY_LIGHT = (210, 215, 225)
        BODY_SHADE = (170, 175, 185)
        NOSE_CONE = (100, 105, 115)
        COCKPIT_GLASS = (20, 30, 45)

        pygame.draw.polygon(surf, NOSE_CONE, [(cx, y - int(8 * s)), (cx + int(3 * s), y), (cx - int(3 * s), y)])
        pygame.draw.rect(surf, BODY_LIGHT, (cx - int(4 * s), y, int(8 * s), size))

        pygame.draw.polygon(surf, (40, 45, 55), [
            (cx - int(4 * s), y + int(15 * s)), (cx - int(8 * s), y + int(18 * s)),
            (cx - int(8 * s), y + int(28 * s)), (cx - int(4 * s), y + int(25 * s))
        ])
        pygame.draw.polygon(surf, (40, 45, 55), [
            (cx + int(4 * s), y + int(15 * s)), (cx + int(8 * s), y + int(18 * s)),
            (cx + int(8 * s), y + int(28 * s)), (cx + int(4 * s), y + int(25 * s))
        ])

        pygame.draw.polygon(surf, BODY_SHADE, [
            (cx - int(4 * s), y + int(10 * s)),
            (cx - int(26 * s), y + size - int(8 * s)),
            (cx - int(26 * s), y + size - int(3 * s)),
            (cx - int(4 * s), y + size - int(6 * s))
        ])
        pygame.draw.polygon(surf, BODY_SHADE, [
            (cx + int(4 * s), y + int(10 * s)),
            (cx + int(26 * s), y + size - int(8 * s)),
            (cx + int(26 * s), y + size - int(3 * s)),
            (cx + int(4 * s), y + size - int(6 * s))
        ])

        pygame.draw.rect(surf, (240, 240, 240), (cx - int(27 * s), y + size - int(12 * s), int(2 * s), int(10 * s)))
        pygame.draw.rect(surf, (240, 240, 240), (cx + int(25 * s), y + size - int(12 * s), int(2 * s), int(10 * s)))

        pygame.draw.polygon(surf, BODY_SHADE, [(cx - int(4 * s), y + size - int(4 * s)), (cx - int(14 * s), y + size + int(6 * s)), (cx - int(4 * s), y + size)])
        pygame.draw.polygon(surf, BODY_SHADE, [(cx + int(4 * s), y + size - int(4 * s)), (cx + int(14 * s), y + size + int(6 * s)), (cx + int(4 * s), y + size)])

        pygame.draw.ellipse(surf, COCKPIT_GLASS, (cx - int(3 * s), y + int(4 * s), int(6 * s), int(16 * s)))
        pygame.draw.ellipse(surf, (100, 150, 200), (cx - int(2 * s), y + int(6 * s), int(2 * s), int(5 * s)))

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

        float_y = math.sin(pulse * 3) * 5 * s
        wing_flap = math.sin(pulse * 10) * 10 * s

        for side in [-1, 1]:
            pygame.draw.ellipse(surf, (255, 200, 0), (
                cx + (8 * s * side) - (5 * s if side == 1 else 0),
                y + (20 * s) + float_y + wing_flap,
                10 * s, 15 * s
            ))

        pygame.draw.ellipse(surf, BODY_GREEN, (cx - 15 * s, y + 15 * s + float_y, 30 * s, 35 * s))
        pygame.draw.ellipse(surf, BELLY_YELLOW, (cx - 10 * s, y + 25 * s + float_y, 20 * s, 22 * s))

        tail_pts = [(cx - 10 * s, y + 45 * s + float_y), (cx, y + 55 * s + float_y), (cx + 10 * s, y + 45 * s + float_y)]
        pygame.draw.lines(surf, BODY_GREEN, False, tail_pts, int(8 * s))

        head_rect = (cx - 18 * s, y - 5 * s + float_y, 36 * s, 30 * s)
        pygame.draw.ellipse(surf, BODY_GREEN, head_rect)

        pygame.draw.circle(surf, EYE_WHITE, (int(cx - 8 * s), int(y + 8 * s + float_y)), int(6 * s))
        pygame.draw.circle(surf, EYE_WHITE, (int(cx + 8 * s), int(y + 8 * s + float_y)), int(6 * s))
        pygame.draw.circle(surf, (0, 0, 0), (int(cx - 8 * s), int(y + 8 * s + float_y)), int(3 * s))
        pygame.draw.circle(surf, (0, 0, 0), (int(cx + 8 * s), int(y + 8 * s + float_y)), int(3 * s))
        pygame.draw.circle(surf, EYE_WHITE, (int(cx - 9 * s), int(y + 7 * s + float_y)), int(1.5 * s))
        pygame.draw.circle(surf, EYE_WHITE, (int(cx + 7 * s), int(y + 7 * s + float_y)), int(1.5 * s))

        pygame.draw.circle(surf, BELLY_YELLOW, (int(cx - 12 * s), int(y - 2 * s + float_y)), int(4 * s))
        pygame.draw.circle(surf, BELLY_YELLOW, (int(cx + 12 * s), int(y - 2 * s + float_y)), int(4 * s))


def draw_obstacle(obstacle_type, x, y, size, glow_color=None, pulse=0, time_offset=0, orientation="vertical"):
    screen = game_globals.screen
    color = OBSTACLE_COLORS[obstacle_type]

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
        cx, cy = x + size // 2, y + size // 2
        angle = time_offset * 3 % 360
        radius = size // 3
        pygame.draw.circle(screen, (130, 10, 10), (cx, cy), radius + 2)
        pygame.draw.circle(screen, color, (cx, cy), radius)
        for deg in range(0, 360, 45):
            spike_rad = math.radians(deg + angle)
            sx = cx + int(math.cos(spike_rad) * (radius + size // 6))
            sy = cy + int(math.sin(spike_rad) * (radius + size // 6))
            pygame.draw.circle(screen, (130, 10, 10), (sx, sy), max(2, size // 10))
        center_pulse = abs(math.sin(time_offset * 0.15))
        center_r = max(2, int(size // 8 + center_pulse * 2))
        pygame.draw.circle(screen, (255, 200, 200), (cx, cy), center_r)

    elif obstacle_type == OBSTACLE_BIRD:
        cx, cy = x + size // 2, y + size // 2
        s = size / 55.0
        bolt_color = (250, 204, 21)
        bright_color = (254, 240, 138)
        points = [
            (cx + int(1 * s), cy - int(18 * s)),
            (cx - int(9 * s), cy + int(2 * s)),
            (cx + int(0 * s), cy + int(2 * s)),
            (cx - int(1 * s), cy + int(18 * s)),
            (cx + int(9 * s), cy - int(2 * s)),
            (cx + int(0 * s), cy - int(2 * s)),
        ]
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
        cx, cy = x + size // 2, y + size // 2
        s = size / 40.0
        bob = math.sin(time_offset * 0.05) * 2 * s

        leg_color = (120, 190, 120)
        leg_outline = (60, 120, 60)
        fl_x, fl_y = int(cx - 10 * s), int(cy + 8 * s + bob)
        pygame.draw.ellipse(screen, leg_color, (fl_x, fl_y, int(8 * s), int(10 * s)))
        pygame.draw.ellipse(screen, leg_outline, (fl_x, fl_y, int(8 * s), int(10 * s)), max(1, int(s)))
        fr_x, fr_y = int(cx + 2 * s), int(cy + 8 * s + bob)
        pygame.draw.ellipse(screen, leg_color, (fr_x, fr_y, int(8 * s), int(10 * s)))
        pygame.draw.ellipse(screen, leg_outline, (fr_x, fr_y, int(8 * s), int(10 * s)), max(1, int(s)))
        for lx in [fl_x, fr_x]:
            for t in range(3):
                tx = lx + int((1 + t * 3) * s)
                ty = int(cy + 16 * s + bob)
                pygame.draw.circle(screen, leg_color, (tx, ty), max(1, int(1.5 * s)))

        shell_color = (100, 180, 80)
        shell_dark = (70, 140, 55)
        shell_outline = (50, 100, 40)
        shell_w, shell_h = int(26 * s), int(20 * s)
        shell_x = int(cx - 13 * s)
        shell_y = int(cy - 10 * s + bob)
        pygame.draw.ellipse(screen, shell_color, (shell_x, shell_y, shell_w, shell_h))
        pygame.draw.ellipse(screen, shell_outline, (shell_x, shell_y, shell_w, shell_h), max(1, int(1.5 * s)))
        rim_rect = (shell_x + int(2 * s), int(cy + 5 * s + bob), shell_w - int(4 * s), int(5 * s))
        pygame.draw.ellipse(screen, shell_dark, rim_rect)
        pygame.draw.ellipse(screen, shell_outline, rim_rect, max(1, int(s)))
        hex_cx, hex_cy = int(cx), int(cy - 4 * s + bob)
        hex_r = int(5 * s)
        hex_pts = [(hex_cx + int(hex_r * math.cos(math.radians(60 * i - 30))),
                     hex_cy + int(hex_r * 0.8 * math.sin(math.radians(60 * i - 30)))) for i in range(6)]
        pygame.draw.polygon(screen, shell_dark, hex_pts, max(1, int(s)))
        for angle_deg in [0, 72, 144, 216, 288]:
            px = hex_cx + int(7 * s * math.cos(math.radians(angle_deg)))
            py = hex_cy + int(5 * s * math.sin(math.radians(angle_deg)))
            mini_r = int(3 * s)
            mini_pts = [(px + int(mini_r * math.cos(math.radians(72 * i))),
                          py + int(mini_r * 0.7 * math.sin(math.radians(72 * i)))) for i in range(5)]
            pygame.draw.polygon(screen, shell_dark, mini_pts, max(1, int(s)))

        neck_x = int(cx + 10 * s)
        neck_y = int(cy - 2 * s + bob)
        neck_w, neck_h = int(8 * s), int(10 * s)
        pygame.draw.ellipse(screen, leg_color, (neck_x, neck_y, neck_w, neck_h))
        pygame.draw.ellipse(screen, leg_outline, (neck_x, neck_y, neck_w, neck_h), max(1, int(s)))
        for si in range(3):
            sy = neck_y + int((2 + si * 3) * s)
            pygame.draw.line(screen, shell_dark, (neck_x + int(1 * s), sy), (neck_x + neck_w - int(1 * s), sy), max(1, int(s)))

        head_x = int(cx + 14 * s + bob)
        head_y = int(cy - 8 * s + bob)
        head_r = int(8 * s)
        pygame.draw.circle(screen, leg_color, (head_x, head_y), head_r)
        pygame.draw.circle(screen, leg_outline, (head_x, head_y), head_r, max(1, int(1.5 * s)))

        eye_r = max(2, int(3 * s))
        pupil_r = max(1, int(1.5 * s))
        le_x, le_y = int(head_x - 2 * s), int(head_y - 3 * s)
        pygame.draw.circle(screen, (255, 255, 255), (le_x, le_y), eye_r)
        pygame.draw.circle(screen, (30, 30, 30), (le_x + int(0.5 * s), le_y), pupil_r)
        pygame.draw.circle(screen, (255, 255, 255), (le_x + int(1 * s), le_y - int(1 * s)), max(1, int(0.8 * s)))
        pygame.draw.circle(screen, leg_outline, (le_x, le_y), eye_r, max(1, int(s)))
        re_x, re_y = int(head_x + 4 * s), int(head_y - 3 * s)
        pygame.draw.circle(screen, (255, 255, 255), (re_x, re_y), eye_r)
        pygame.draw.circle(screen, (30, 30, 30), (re_x + int(0.5 * s), re_y), pupil_r)
        pygame.draw.circle(screen, (255, 255, 255), (re_x + int(1 * s), re_y - int(1 * s)), max(1, int(0.8 * s)))
        pygame.draw.circle(screen, leg_outline, (re_x, re_y), eye_r, max(1, int(s)))

        smile_rect = pygame.Rect(int(head_x - 3 * s), int(head_y - 1 * s), int(8 * s), int(6 * s))
        pygame.draw.arc(screen, (50, 80, 50), smile_rect, math.radians(200), math.radians(340), max(1, int(1.5 * s)))

    elif obstacle_type == OBSTACLE_MUSHROOM:
        inset = size // 5
        mx = x + inset
        ms = size - inset * 2
        bounce = abs(int(math.sin(time_offset * 0.2) * 2))
        my = y + inset - bounce
        cap_h = ms // 2 + 2
        stem_w = ms // 3
        stem_h = ms // 3 + bounce
        stem_rect = pygame.Rect(mx + ms // 2 - stem_w // 2, my + cap_h - 2, stem_w, stem_h)
        pygame.draw.rect(screen, (220, 215, 200), stem_rect, border_radius=3)
        pygame.draw.rect(screen, (200, 200, 190), stem_rect, 2, border_radius=3)
        cap_rect = pygame.Rect(mx + 1, my, ms - 2, cap_h)
        pygame.draw.ellipse(screen, (220, 38, 38), cap_rect)
        pygame.draw.ellipse(screen, (252, 165, 165), cap_rect, max(1, ms // 16))
        pygame.draw.circle(screen, WHITE, (mx + ms // 3, my + cap_h // 3), max(2, ms // 10))
        pygame.draw.circle(screen, WHITE, (mx + ms * 2 // 3, my + cap_h // 3 + 2), max(2, ms // 12))

    elif obstacle_type == OBSTACLE_MACHINEGUN:
        cx = x + size // 2
        bullet_w = max(4, size // 6)
        bullet_h = max(10, size * 2 // 5)
        gap = bullet_w + 2
        for i in range(3):
            bx = cx - gap + i * gap - bullet_w // 2
            bounce = int(math.sin(time_offset * 0.3 + i * 0.5) * 4)
            by = y + size // 2 - bullet_h // 2 + bounce
            bullet_rect = pygame.Rect(bx, by, bullet_w, bullet_h)
            pygame.draw.rect(screen, (234, 88, 12), bullet_rect, border_radius=bullet_w)
            highlight_rect = pygame.Rect(bx, by, bullet_w, bullet_h // 2)
            pygame.draw.rect(screen, (253, 224, 71), highlight_rect, border_radius=bullet_w)
            pygame.draw.rect(screen, (254, 215, 170), bullet_rect, 1, border_radius=bullet_w)

    elif obstacle_type == OBSTACLE_SHOTGUN:
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
        if orientation == "vertical":
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
        else:
            bar_width = 12
            bar_height = size
            bar_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(screen, (80, 85, 95), bar_rect, border_radius=3)
            pygame.draw.rect(screen, color, (x + 2, y + 2, bar_width - 4, bar_height - 4), border_radius=2)
            highlight_rect = pygame.Rect(x + 3, y + 4, 3, bar_height - 8)
            pygame.draw.rect(screen, (180, 190, 200), highlight_rect, border_radius=1)
            pygame.draw.rect(screen, glow_color, bar_rect, 2, border_radius=3)
            for i in range(3):
                bolt_x = x + bar_width // 2
                bolt_y = y + bar_height // 4 + i * bar_height // 4
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
    screen = game_globals.screen
    cx, cy = x + size // 2, y + size // 2
    half = size // 2
    s = size / 100.0
    pulse = math.sin(time_offset * 0.1)

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
        color = (100, 150, 255)
        pygame.draw.rect(screen, color, (x, y, size, size), border_radius=10)
        pygame.draw.rect(screen, (20, 20, 40), (int(x + 10 * s), int(y + 20 * s), int(80 * s), int(30 * s)))
        eye_color = (255, 0, 0) if pulse > 0 else (150, 0, 0)
        pygame.draw.circle(screen, eye_color, (int(x + 30 * s), int(y + 35 * s)), int(8 * s))
        pygame.draw.circle(screen, eye_color, (int(x + 70 * s), int(y + 35 * s)), int(8 * s))

    elif level == 2:
        color = (200, 150, 255)
        alpha = int(150 + pulse * 50)
        ghost_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(ghost_surf, (*color, alpha), (0, 0, size, int(size * 0.8)))
        for i in range(3):
            wx = i * (size // 3)
            pygame.draw.circle(ghost_surf, (*color, alpha), (wx + size // 6, int(size * 0.8)), size // 6)
        screen.blit(ghost_surf, (x, y))
        pygame.draw.circle(screen, (0, 0, 0), (int(cx - 15 * s), int(cy - 10 * s)), int(5 * s))
        pygame.draw.circle(screen, (0, 0, 0), (int(cx + 15 * s), int(cy - 10 * s)), int(5 * s))

    elif level == 3:
        color = (255, 140, 0)
        pygame.draw.circle(screen, color, (cx, cy), size // 2)
        pygame.draw.polygon(screen, color, [(x, int(y + 20 * s)), (int(x + 30 * s), y), (int(x + 40 * s), int(y + 30 * s))])
        pygame.draw.polygon(screen, color, [(x + size, int(y + 20 * s)), (int(x + size - 30 * s), y), (int(x + size - 40 * s), int(y + 30 * s))])
        for i in range(3):
            pygame.draw.line(screen, (0, 0, 0), (int(cx - 20 * s), int(y + 40 * s + i * 10 * s)),
                             (int(cx + 20 * s), int(y + 40 * s + i * 10 * s)), 3)

    elif level == 4:
        color = (50, 255, 100)
        pygame.draw.ellipse(screen, color, (int(x + 20 * s), y, int(60 * s), size))
        pygame.draw.ellipse(screen, (0, 0, 0), (int(x + 25 * s), int(y + 20 * s), int(20 * s), int(35 * s)))
        pygame.draw.ellipse(screen, (0, 0, 0), (int(x + 55 * s), int(y + 20 * s), int(20 * s), int(35 * s)))
        pygame.draw.arc(screen, (200, 255, 200),
                        pygame.Rect(int(cx - 20 * s), int(cy + 10 * s), int(40 * s), int(30 * s)),
                        0, math.pi, 4)

    elif level == 5:
        pygame.draw.polygon(screen, (40, 0, 80), [(cx, y), (x, y + size), (x + size, y + size)])
        pygame.draw.circle(screen, (220, 180, 150), (cx, int(cy + 20 * s)), int(25 * s))
        pygame.draw.circle(screen, (0, 255, 0), (int(cx - 10 * s), int(cy + 15 * s)), 4)
        pygame.draw.circle(screen, (0, 255, 0), (int(cx + 10 * s), int(cy + 15 * s)), 4)

    elif level == 6:
        pygame.draw.ellipse(screen, (255, 255, 255), (x, int(y + 20 * s), size, int(60 * s)))
        iris_r = int(20 * s + pulse * 5 * s)
        pygame.draw.circle(screen, (255, 0, 0), (cx, cy), iris_r)
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), iris_r // 2)

    elif level == 7:
        pygame.draw.circle(screen, (240, 240, 240), (cx, int(cy - 10 * s)), int(40 * s))
        pygame.draw.rect(screen, (240, 240, 240),
                         (int(cx - 25 * s), int(cy + 20 * s), int(50 * s), int(25 * s)), border_radius=5)
        pygame.draw.circle(screen, (0, 100, 255), (int(cx - 15 * s), int(cy)), int(10 * s))
        pygame.draw.circle(screen, (0, 100, 255), (int(cx + 15 * s), int(cy)), int(10 * s))

    elif level == 8:
        color = (150, 255, 0)
        for i in range(5):
            bx = cx + math.cos(time_offset * 0.1 + i) * 30 * s
            by = cy + math.sin(time_offset * 0.1 + i) * 20 * s
            pygame.draw.circle(screen, color, (int(bx), int(by)), int(20 * s))
        pygame.draw.ellipse(screen, color, (int(x + 10 * s), int(y + 20 * s), int(80 * s), int(60 * s)))

    elif level == 9:
        color = (200, 30, 30)
        pygame.draw.polygon(screen, color, [(cx, y), (x, cy), (cx, y + size), (x + size, cy)])
        pygame.draw.line(screen, (255, 200, 100), (int(cx - 10 * s), int(y + 10 * s)), (x, int(y - 10 * s)), 5)
        pygame.draw.line(screen, (255, 200, 100), (int(cx + 10 * s), int(y + 10 * s)), (x + size, int(y - 10 * s)), 5)
        pygame.draw.line(screen, (255, 255, 0), (int(cx - 15 * s), int(cy - 5 * s)), (int(cx - 5 * s), int(cy - 5 * s)), 3)
        pygame.draw.line(screen, (255, 255, 0), (int(cx + 15 * s), int(cy - 5 * s)), (int(cx + 5 * s), int(cy - 5 * s)), 3)

    elif level >= 10:
        angle = time_offset * 0.05
        points = []
        for i in range(6):
            px = cx + math.cos(angle + i * math.pi / 3) * 50 * s
            py = cy + math.sin(angle + i * math.pi / 3) * 50 * s
            points.append((px, py))
        pygame.draw.polygon(screen, (255, 215, 0), points, 3)
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), int(15 * s + pulse * 10 * s))


def draw_boss_projectile(x, y, size, time_offset, level=1, indestructible=False):
    """Draw boss projectile (circle block)."""
    screen = game_globals.screen
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

    if indestructible:
        glow_color = (255, 255, 255)
        color = (255, 100, 100)

    pulse = 2 + math.sin(time_offset * 0.2) * 1
    gs = pygame.Surface((size + pulse * 4, size + pulse * 4), pygame.SRCALPHA)
    pygame.draw.circle(gs, (*glow_color, 80), (size // 2 + pulse * 2, size // 2 + pulse * 2), size // 2 + pulse)
    screen.blit(gs, (x - pulse * 2, y - pulse * 2))

    pygame.draw.circle(screen, color, (x + size // 2, y + size // 2), size // 2)

    inner_color = tuple(max(0, c - 50) for c in color)
    pygame.draw.circle(screen, inner_color, (x + size // 2, y + size // 2), size // 3)

    if indestructible:
        pygame.draw.circle(screen, (255, 255, 255), (x + size // 2, y + size // 2), size // 2, 2)


def draw_boss_health_bar(x, y, width, height, health, max_health, level=1):
    """Draw boss health bar."""
    screen = game_globals.screen
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

    bg_rect = pygame.Rect(x, y, width, height)
    bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (20, 20, 40, 200), bg_rect, border_radius=10)
    screen.blit(bg_surface, (x, y))

    pygame.draw.rect(screen, boss_color, bg_rect, 2, border_radius=10)

    health_width = int((health / max_health) * (width - 8))
    if health_width > 0:
        fill_rect = pygame.Rect(x + 4, y + 4, health_width, height - 8)
        if health > max_health * 0.5:
            health_color = (100, 200, 100)
        elif health > max_health * 0.25:
            health_color = (200, 180, 50)
        else:
            health_color = (200, 50, 50)
        pygame.draw.rect(screen, health_color, fill_rect, border_radius=6)

    boss_text = game_globals.font_small.render(f"LVL {level}: {boss_name}", True, boss_color)
    screen.blit(boss_text, (x + 10, y + 7))

    health_text = game_globals.font_small.render(f"{health}/{max_health}", True, (200, 200, 255))
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
            half_t = trail_size // 2 + 2
            diamond = [(half_t, 2), (trail_size + 2, half_t), (half_t, trail_size + 2), (2, half_t)]
            pygame.draw.polygon(ts_surf, (*color, alpha), diamond)
        elif shape == "aeroplane":
            pygame.draw.ellipse(ts_surf, (*color, alpha), (2, 2, trail_size, trail_size))
        elif shape == "dragon":
            pygame.draw.circle(ts_surf, (*color, alpha), (trail_size // 2 + 2, trail_size // 2 + 2), trail_size // 2)

        surface.blit(ts_surf, (int(tx), int(ty)))
