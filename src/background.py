import pygame
import random
import math
from src.constants import (
    WORLD_WIDTH, SCREEN_HEIGHT, SKY_BLUE, WHITE, BROWN, 
    DARK_GREEN, BLACK
)
from src.constants import load_image

class Background:
    def __init__(self):
        self.image = load_image("background.png", WORLD_WIDTH, SCREEN_HEIGHT, SKY_BLUE)
        self.clouds = [
            {"x": random.randint(0, WORLD_WIDTH), "y": random.randint(50, 200), "speed": random.uniform(0.2, 0.5)}
            for _ in range(15)  # More clouds for a larger world
        ]
        self.cloud_img = load_image("cloud.png", 100, 50, WHITE)
        self.rect = pygame.Rect(0, 0, WORLD_WIDTH, SCREEN_HEIGHT)

    def update(self):
        for cloud in self.clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] > WORLD_WIDTH:
                cloud["x"] = -100
                cloud["y"] = random.randint(50, 200)

    def draw(self, surface, camera):
        # Draw the visible portion of the background
        visible_rect = camera.apply_rect(self.rect)
        surface.blit(self.image, visible_rect)
        
        # Draw clouds that are visible in the current view
        for cloud in self.clouds:
            cloud_rect = pygame.Rect(cloud["x"], cloud["y"], 100, 50)
            if visible_rect.x + camera.width > cloud_rect.x > visible_rect.x - 100:
                surface.blit(self.cloud_img, (cloud_rect.x + camera.scroll_x, cloud_rect.y))


class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y, size='medium'):
        super().__init__()
        self.size_map = {
            'small': (60, 80),
            'medium': (80, 120),
            'large': (100, 150)
        }
        width, height = self.size_map.get(size, (80, 120))
        self.image = self.create_tree_image(width, height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y  # Bottom of tree anchors at y
    
    def create_tree_image(self, width, height):
        img = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw trunk
        trunk_width = width // 4
        trunk_height = height // 2
        trunk_x = (width - trunk_width) // 2
        pygame.draw.rect(img, BROWN, (trunk_x, height - trunk_height, trunk_width, trunk_height))
        
        # Draw foliage (triangular for pine tree or circular for oak)
        foliage_type = random.choice(['pine', 'oak'])
        if foliage_type == 'pine':
            # Pine tree with multiple triangles
            for i in range(3):
                triangle_width = width - i * (width // 6)
                triangle_height = height // 2 - i * (height // 12)
                triangle_y = height - trunk_height - i * (height // 6)
                
                pygame.draw.polygon(img, DARK_GREEN, [
                    ((width - triangle_width) // 2, triangle_y),  # Top left
                    (width // 2, triangle_y - triangle_height),   # Top point
                    ((width + triangle_width) // 2, triangle_y)   # Top right
                ])
        else:
            # Oak tree with a big circle
            foliage_radius = width // 2
            pygame.draw.circle(img, DARK_GREEN, (width // 2, height - trunk_height - foliage_radius), foliage_radius)
        
        return img


class Bush(pygame.sprite.Sprite):
    def __init__(self, x, y, size='medium'):
        super().__init__()
        self.size_map = {
            'small': (40, 20),
            'medium': (60, 30),
            'large': (80, 40)
        }
        width, height = self.size_map.get(size, (60, 30))
        self.image = self.create_bush_image(width, height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y  # Bottom of bush anchors at y
    
    def create_bush_image(self, width, height):
        img = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw multiple circles of different shades of green for a bush effect
        num_circles = 5
        for _ in range(num_circles):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(height // 3, height // 2)
            green_shade = (0, random.randint(100, 180), 0)
            pygame.draw.circle(img, green_shade, (x, y), radius)
        
        return img


class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        width, height = 100, 50
        self.image = self.create_cloud_image(width, height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.uniform(0.2, 0.5)
    
    def create_cloud_image(self, width, height):
        img = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw multiple white circles for a cloud effect
        cloud_color = (250, 250, 250, 220)  # Slightly transparent white
        center_x = width // 2
        center_y = height // 2
        
        pygame.draw.circle(img, cloud_color, (center_x, center_y), height // 2)
        pygame.draw.circle(img, cloud_color, (center_x - width // 4, center_y), height // 2.5)
        pygame.draw.circle(img, cloud_color, (center_x + width // 4, center_y), height // 2.5)
        pygame.draw.circle(img, cloud_color, (center_x - width // 3, center_y - height // 4), height // 3)
        pygame.draw.circle(img, cloud_color, (center_x + width // 3, center_y - height // 4), height // 3)
        
        return img
    
    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WORLD_WIDTH:
            self.rect.right = 0 