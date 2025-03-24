import pygame
import random
import math
from src.constants import ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_SPEED, GRAVITY, SCREEN_HEIGHT, GREEN, PURPLE, RED
from src.constants import load_image

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create animation frames
        self.frames = [
            load_image("enemy_walk1.png", ENEMY_WIDTH, ENEMY_HEIGHT, RED),
            load_image("enemy_walk2.png", ENEMY_WIDTH, ENEMY_HEIGHT, RED)
        ]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.direction = -1
        self.animation_index = 0
        self.animation_timer = 0
        self.spotted_player = False
        self.on_ground = False
        self.move_range = 150
        self.start_x = x
        self.speed = ENEMY_SPEED
        
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        # Move horizontally
        if self.spotted_player:
            # Move faster if player spotted
            self.rect.x += self.direction * (self.speed * 1.5)
        else:
            self.rect.x += self.direction * self.speed
            
        # Animate enemy
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            
            # Flip the image based on direction
            if self.direction > 0:
                self.image = pygame.transform.flip(self.frames[self.animation_index], True, False)
            else:
                self.image = self.frames[self.animation_index]
    
    def detect_player(self, player, camera):
        # Only chase player if within visible range
        player_screen_x = player.rect.x - camera.scroll_x
        enemy_screen_x = self.rect.x - camera.scroll_x
        
        if abs(player_screen_x - enemy_screen_x) < 300 and abs(player.rect.y - self.rect.y) < 100:
            self.spotted_player = True
            # Change direction to face player
            self.direction = 1 if player.rect.x > self.rect.x else -1
        else:
            self.spotted_player = False
            
    def check_platform_edge(self, platforms):
        # Look ahead to see if we're about to walk off an edge
        test_rect = self.rect.copy()
        test_rect.x += self.direction * 10
        test_rect.y += 10
        
        on_platform = False
        for platform in platforms:
            if platform.rect.colliderect(test_rect):
                on_platform = True
                break
        
        # If we're about to walk off an edge, turn around
        if not on_platform and not self.spotted_player:
            self.direction *= -1
            # Move away from edge
            self.rect.x += self.direction * 10

class PatrollingEnemy(Enemy):
    def __init__(self, x, y, patrol_points=None):
        super().__init__(x, y)
        self.frames = [
            load_image("enemy_walk1.png", ENEMY_WIDTH, ENEMY_HEIGHT, PURPLE),
            load_image("enemy_walk2.png", ENEMY_WIDTH, ENEMY_HEIGHT, PURPLE)
        ]
        self.image = self.frames[0]
        
        # Patrol path
        if patrol_points:
            self.patrol_points = patrol_points
        else:
            # Default patrol between start point and some distance away
            self.patrol_points = [(x, y), (x + 200, y)]
            
        self.current_point = 0
        self.speed = ENEMY_SPEED * 1.2  # Faster than regular enemies
        self.chase_speed = ENEMY_SPEED * 1.8  # Even faster when chasing
        self.detection_range = 350  # Wider detection range
        self.can_jump = True  # Can jump to reach the player
        self.jump_cooldown = 0
        self.max_jump_cooldown = 60  # Frames between jumps
    
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        if self.spotted_player:
            # Move faster when chasing
            self.rect.x += self.direction * self.chase_speed
            
            # Update jump cooldown
            if self.jump_cooldown > 0:
                self.jump_cooldown -= 1
        else:
            # Regular patrol movement - move towards current patrol point
            target = self.patrol_points[self.current_point]
            
            # Calculate direction to target
            if target[0] > self.rect.x:
                self.direction = 1
            else:
                self.direction = -1
                
            # Move towards target
            self.rect.x += self.direction * self.speed
            
            # Check if we've reached the target point
            if abs(self.rect.x - target[0]) < 10:
                # Move to next point
                self.current_point = (self.current_point + 1) % len(self.patrol_points)
        
        # Animate enemy
        self.animation_timer += 1
        if self.animation_timer > 8:  # Faster animation
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            
            # Flip the image based on direction
            if self.direction > 0:
                self.image = pygame.transform.flip(self.frames[self.animation_index], True, False)
            else:
                self.image = self.frames[self.animation_index]
    
    def detect_player(self, player, camera):
        # Check if player is in detection range
        dist_x = abs(player.rect.x - self.rect.x)
        dist_y = abs(player.rect.y - self.rect.y)
        
        if dist_x < self.detection_range and dist_y < 150:
            self.spotted_player = True
            # Change direction to face player
            self.direction = 1 if player.rect.x > self.rect.x else -1
            
            # Jump if player is above and we can jump
            if player.rect.y < self.rect.y - 20 and self.on_ground and self.can_jump and self.jump_cooldown == 0:
                self.velocity_y = -10  # Jump
                self.jump_cooldown = self.max_jump_cooldown
        else:
            self.spotted_player = False
    
    def check_platform_edge(self, platforms):
        # Look ahead to see if we're about to walk off an edge
        test_rect = self.rect.copy()
        test_rect.x += self.direction * 10
        test_rect.y += 10
        
        on_platform = False
        for platform in platforms:
            if platform.rect.colliderect(test_rect):
                on_platform = True
                break
        
        # If we're about to walk off an edge and not chasing player, turn around
        if not on_platform and not self.spotted_player:
            self.direction *= -1
            # Move away from edge
            self.rect.x += self.direction * 10 