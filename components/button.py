import pygame
from config import LIGHT_PINK, BORDER_PINK, BLACK

def draw_filled_button(screen, x, y, w, h, text, font_size=42):
    rect = pygame.Rect(x, y, w, h)
    radius = max(18, min(w, h) // 4)
    pygame.draw.rect(screen, LIGHT_PINK, rect, border_radius=radius)

    font = pygame.font.SysFont("arial", font_size, bold=True)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect


def draw_outline_button(screen, x, y, w, h, text, font_size=42):
    rect = pygame.Rect(x, y, w, h)
    radius = max(18, min(w, h) // 4)
    pygame.draw.rect(screen, BORDER_PINK, rect, width=max(3, w // 60), border_radius=radius)

    font = pygame.font.SysFont("arial", font_size, bold=True)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect