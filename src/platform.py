import pygame
import random
from src.constants import BROWN, MOVING_PLATFORM_SPEED, GRAVITY, SHRINK_DELAY, SHRINK_SPEED, MIN_PLATFORM_WIDTH, ORANGE
from src.constants import load_image

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, color=BROWN):
        super().__init__()
        self.image = pygame.Surface((width, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class MovingPlatform(Platform):
    def __init__(self, x, y, width, move_distance, horizontal=True, color=BROWN):
        super().__init__(x, y, width, color)
        self.start_x = x
        self.start_y = y
        self.move_distance = move_distance
        self.horizontal = horizontal
        self.speed = MOVING_PLATFORM_SPEED
        self.original_speed = MOVING_PLATFORM_SPEED
        
    def update(self):
        if self.horizontal:
            self.rect.x += self.speed
            if self.rect.x > self.start_x + self.move_distance or self.rect.x < self.start_x:
                self.speed *= -1
        else:
            self.rect.y += self.speed
            if self.rect.y > self.start_y + self.move_distance or self.rect.y < self.start_y:
                self.speed *= -1

class ShrinkingPlatform(Platform):
    def __init__(self, x, y, width, color=(255, 100, 0)):  # Orange-red color
        super().__init__(x, y, width, color)
        self.original_width = width
        self.current_width = width
        self.is_shrinking = False
        self.shrink_timer = 0
        self.player_touched = False
        
    def update(self):
        if self.player_touched:
            self.shrink_timer += 1
            
            # Start shrinking after delay
            if self.shrink_timer > SHRINK_DELAY and self.current_width > MIN_PLATFORM_WIDTH:
                self.is_shrinking = True
                self.current_width -= SHRINK_SPEED
                
                # Create new image with reduced width
                self.image = pygame.Surface((self.current_width, 10))
                self.image.fill((255, int(100 * (self.current_width / self.original_width)), 0))  # Change color as it shrinks
                
                # Keep platform centered while shrinking
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center
    
    def reset(self):
        """Reset the platform to its original state"""
        self.current_width = self.original_width
        self.is_shrinking = False
        self.shrink_timer = 0
        self.player_touched = False
        self.image = pygame.Surface((self.original_width, 10))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(x=self.rect.x, y=self.rect.y)

class FallingPlatform(Platform):
    def __init__(self, x, y, width, color=(200, 100, 50)):  # Brown-red color
        super().__init__(x, y, width, color)
        self.velocity_y = 0
        self.player_touched = False
        self.fall_delay = 15  # Frames before platform starts falling
        self.fall_timer = 0
        self.start_y = y
        
    def update(self):
        if self.player_touched:
            self.fall_timer += 1
            
            # Start falling after delay
            if self.fall_timer > self.fall_delay:
                self.velocity_y += GRAVITY * 0.5
                self.rect.y += self.velocity_y
    
    def reset(self):
        """Reset the platform to its original state"""
        self.rect.y = self.start_y
        self.velocity_y = 0
        self.player_touched = False
        self.fall_timer = 0 