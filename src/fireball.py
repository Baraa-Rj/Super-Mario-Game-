import pygame
from src.constants import load_image, ORANGE, RED, YELLOW

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=10):
        super().__init__()
        # Create fireball animation frames
        self.frames = [
            self.create_fireball_image(10, 10, 0),
            self.create_fireball_image(10, 10, 1),
            self.create_fireball_image(10, 10, 2),
            self.create_fireball_image(10, 10, 3)
        ]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.speed = speed
        self.animation_index = 0
        self.animation_timer = 0
        self.bounce_count = 0
        self.max_bounces = 3
        self.velocity_y = 0
        self.gravity = 0.3
        
    def create_fireball_image(self, width, height, frame):
        """Create a fireball animation frame"""
        img = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Different frames for animation
        if frame == 0:
            # Base fireball (circle)
            pygame.draw.circle(img, RED, (width//2, height//2), width//2)
            # Inner glow
            pygame.draw.circle(img, ORANGE, (width//2, height//2), width//3)
            # Center hot point
            pygame.draw.circle(img, YELLOW, (width//2, height//2), width//6)
        elif frame == 1:
            # Slightly different shape
            pygame.draw.circle(img, RED, (width//2, height//2), width//2)
            # Inner glow (shifted)
            pygame.draw.circle(img, ORANGE, (width//2 - 1, height//2), width//3)
            # Center hot point
            pygame.draw.circle(img, YELLOW, (width//2 - 1, height//2), width//6)
        elif frame == 2:
            # Another variation
            pygame.draw.circle(img, RED, (width//2, height//2), width//2)
            # Inner glow
            pygame.draw.circle(img, ORANGE, (width//2, height//2 + 1), width//3)
            # Center hot point (shifted)
            pygame.draw.circle(img, YELLOW, (width//2, height//2 + 1), width//6)
        else:
            # Final variation
            pygame.draw.circle(img, RED, (width//2, height//2), width//2)
            # Inner glow
            pygame.draw.circle(img, ORANGE, (width//2 + 1, height//2), width//3)
            # Center hot point
            pygame.draw.circle(img, YELLOW, (width//2 + 1, height//2), width//6)
        
        return img
        
    def update(self):
        # Move fireball horizontally
        self.rect.x += self.speed * self.direction
        
        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        
        # Animate fireball
        self.animation_timer += 1
        if self.animation_timer > 3:  # Fast animation
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            self.image = self.frames[self.animation_index]
            
    def bounce(self):
        """Make the fireball bounce when hitting the ground"""
        if self.bounce_count < self.max_bounces:
            self.velocity_y = -5  # Bounce upward
            self.bounce_count += 1
            return True
        else:
            return False  # Too many bounces, should be removed
        
    def check_platform_collision(self, platforms):
        """Check for collision with platforms"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Only bounce if hitting the top of a platform and moving downward
                if self.velocity_y > 0 and self.rect.bottom < platform.rect.bottom + 10:
                    self.rect.bottom = platform.rect.top
                    return self.bounce()  # Bounce and check if should continue
                # If hitting side of platform, fireball should be removed
                elif (self.rect.right > platform.rect.left and self.rect.left < platform.rect.left) or \
                     (self.rect.left < platform.rect.right and self.rect.right > platform.rect.right):
                    return False  # Hit side of platform, should be removed
        
        # Check if hitting the ground
        if self.rect.bottom > pygame.display.get_surface().get_height() - 10:
            self.rect.bottom = pygame.display.get_surface().get_height() - 10
            return self.bounce()  # Bounce and check if should continue
            
        return True  # No collision or bounce successful 