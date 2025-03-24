import pygame
import math
import random
from src.constants import (
    POWERUP_SIZE, GRAVITY, SCREEN_HEIGHT, 
    RED, WHITE, GOLD, YELLOW, ORANGE, GREEN, BLACK
)

class PowerUp(pygame.sprite.Sprite):
    """Base class for all power-ups"""
    def __init__(self, x, y, type_name):
        super().__init__()
        self.type = type_name
        self.animation_frames = self.create_animation_frames(type_name)
        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.on_ground = False
        self.animation_timer = 0
        self.animation_index = 0
        self.bob_offset = 0
        self.bob_direction = 1
        # Rotation for star powerup
        self.angle = 0
        
    def create_animation_frames(self, type_name):
        """Create multiple frames for each powerup type"""
        frames = []
        
        if type_name == "mushroom":
            # Create 4 frames for mushroom with slightly different spots
            for i in range(4):
                img = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
                # Cap
                pygame.draw.rect(img, RED, (0, POWERUP_SIZE//3, POWERUP_SIZE, POWERUP_SIZE*2//3))
                # Stem
                pygame.draw.rect(img, WHITE, (POWERUP_SIZE//4, 0, POWERUP_SIZE//2, POWERUP_SIZE//2))
                # Spots on cap (different for each frame)
                for j in range(3):
                    spot_x = random.randint(2, POWERUP_SIZE-6)
                    spot_y = random.randint(POWERUP_SIZE//3 + 2, POWERUP_SIZE-6)
                    spot_radius = random.randint(2, 4)
                    pygame.draw.circle(img, WHITE, (spot_x, spot_y), spot_radius)
                
                # Add eyes on the stem
                eye_y = POWERUP_SIZE//4
                pygame.draw.circle(img, BLACK, (POWERUP_SIZE//3, eye_y), 2)
                pygame.draw.circle(img, BLACK, (POWERUP_SIZE*2//3, eye_y), 2)
                
                frames.append(img)
                
        elif type_name == "star":
            # Create 4 frames for star with different colors/glows
            colors = [(255, 255, 0), (255, 240, 0), (255, 220, 0), (255, 200, 0)]
            
            for i in range(4):
                img = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
                
                # Draw star shape
                points = []
                for j in range(5):
                    # Outer points
                    angle_outer = math.pi/2 + j * 2*math.pi/5
                    x_outer = POWERUP_SIZE//2 + int(POWERUP_SIZE//2 * math.cos(angle_outer))
                    y_outer = POWERUP_SIZE//2 + int(POWERUP_SIZE//2 * math.sin(angle_outer))
                    points.append((x_outer, y_outer))
                    
                    # Inner points
                    angle_inner = angle_outer + math.pi/5
                    x_inner = POWERUP_SIZE//2 + int(POWERUP_SIZE//5 * math.cos(angle_inner))
                    y_inner = POWERUP_SIZE//2 + int(POWERUP_SIZE//5 * math.sin(angle_inner))
                    points.append((x_inner, y_inner))
                
                pygame.draw.polygon(img, colors[i], points)
                
                # Add sparkles (different for each frame)
                for _ in range(3):
                    spark_x = random.randint(5, POWERUP_SIZE-5)
                    spark_y = random.randint(5, POWERUP_SIZE-5)
                    pygame.draw.circle(img, WHITE, (spark_x, spark_y), 2)
                
                # Add central glow
                pygame.draw.circle(img, WHITE, (POWERUP_SIZE//2, POWERUP_SIZE//2), POWERUP_SIZE//10)
                
                frames.append(img)
            
        elif type_name == "flower":
            # Create 4 frames for flower with changing petals
            for i in range(4):
                img = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
                
                # Make stem
                pygame.draw.rect(img, GREEN, (POWERUP_SIZE//2 - 3, POWERUP_SIZE//2, 6, POWERUP_SIZE//2))
                
                # Center of flower
                pygame.draw.circle(img, YELLOW, (POWERUP_SIZE//2, POWERUP_SIZE//2), POWERUP_SIZE//4)
                
                # Petals - alternating colors and slightly different positions each frame
                offset = i * 2
                for j in range(6):
                    angle = j * math.pi/3 + (i * math.pi/12)  # Rotate slightly in each frame
                    distance = POWERUP_SIZE//3 + (i % 2) * 2  # Vary distance slightly
                    
                    x = POWERUP_SIZE//2 + int(distance * math.cos(angle))
                    y = POWERUP_SIZE//2 + int(distance * math.sin(angle))
                    
                    # Alternate between red, orange and a hint of green for the petals
                    if j % 3 == 0:
                        color = RED
                    elif j % 3 == 1:
                        color = ORANGE
                    else:
                        color = GREEN
                        
                    pygame.draw.circle(img, color, (x, y), POWERUP_SIZE//5)
                
                # Add face in the center
                face_y = POWERUP_SIZE//2
                # Eyes
                pygame.draw.circle(img, BLACK, (POWERUP_SIZE//2 - 5, face_y - 2), 2)
                pygame.draw.circle(img, BLACK, (POWERUP_SIZE//2 + 5, face_y - 2), 2)
                # Smile
                pygame.draw.arc(img, BLACK, 
                               (POWERUP_SIZE//2 - 5, face_y - 2, 10, 8),
                               0, math.pi, 2)
                
                frames.append(img)
        
        return frames
    
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY * 0.7  # Lighter than player
        self.rect.y += self.velocity_y
        
        # Ground collision
        if self.rect.bottom > SCREEN_HEIGHT - 10:
            self.rect.bottom = SCREEN_HEIGHT - 10
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
            
        # Bobbing animation when on ground
        if self.on_ground:
            self.animation_timer += 1
            if self.animation_timer > 5:
                self.animation_timer = 0
                self.bob_offset += self.bob_direction
                if abs(self.bob_offset) > 3:
                    self.bob_direction *= -1
                self.rect.y += self.bob_direction
        
        # Animate powerups
        self.animation_timer += 1
        if self.animation_timer > 8:  # Adjust for animation speed
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
            
            # For stars, rotate the image
            if self.type == "star":
                self.angle = (self.angle + 5) % 360
                rotated = pygame.transform.rotate(self.animation_frames[self.animation_index], self.angle)
                self.image = rotated
                # Reposition to keep centered
                orig_rect = self.rect.copy()
                self.rect = rotated.get_rect(center=orig_rect.center)
            else:
                self.image = self.animation_frames[self.animation_index]
    
    def check_platform_collision(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0 and self.rect.bottom < platform.rect.bottom + 10:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    break


class LifeIcon(pygame.sprite.Sprite):
    """Small icon representing a life in the UI"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        # Draw a small heart
        pygame.draw.polygon(self.image, RED, [
            (10, 3),  # Top center
            (3, 6),   # Left shoulder
            (1, 12),  # Left bottom
            (10, 18), # Bottom center
            (19, 12), # Right bottom
            (17, 6),  # Right shoulder
        ])
        # Add a slight shine to the heart
        pygame.draw.polygon(self.image, (255, 150, 150), [
            (7, 5),   # Upper left
            (4, 8),   # Middle left
            (8, 12),  # Lower middle
        ])
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 