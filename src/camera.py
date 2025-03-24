import pygame
from src.constants import SCREEN_WIDTH, CAMERA_SMOOTH_FACTOR

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.scroll_x = 0
        self.target_scroll_x = 0  # Target position for smooth scrolling
    
    def update(self, target):
        # Calculate target scroll position
        self.target_scroll_x = -target.rect.x + SCREEN_WIDTH // 2
        
        # Limit scrolling to world boundaries
        self.target_scroll_x = min(0, self.target_scroll_x)  # Stop scrolling at the left edge
        self.target_scroll_x = max(-(self.width - SCREEN_WIDTH), self.target_scroll_x)  # Right edge
        
        # Smooth scrolling - interpolate between current and target position
        self.scroll_x += (self.target_scroll_x - self.scroll_x) * CAMERA_SMOOTH_FACTOR
    
    def apply(self, entity):
        # Round scroll value to avoid pixel jittering
        scroll_x_rounded = round(self.scroll_x)
        return pygame.Rect(entity.rect.x + scroll_x_rounded, entity.rect.y, entity.rect.width, entity.rect.height)

    def apply_rect(self, rect):
        # Round scroll value to avoid pixel jittering
        scroll_x_rounded = round(self.scroll_x)
        return pygame.Rect(rect.x + scroll_x_rounded, rect.y, rect.width, rect.height) 