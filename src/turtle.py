import pygame
import random
from src.constants import ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_SPEED, GRAVITY, SCREEN_HEIGHT, WORLD_WIDTH
from src.constants import load_image

class Turtle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create animation frames
        self.frames_right = [
            load_image("turtle_walk1.png", ENEMY_WIDTH, ENEMY_HEIGHT, (0, 150, 0)),  # Darker green
            load_image("turtle_walk2.png", ENEMY_WIDTH, ENEMY_HEIGHT, (0, 150, 0))
        ]
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]
        self.shell_image = load_image("turtle_shell.png", ENEMY_WIDTH - 10, ENEMY_HEIGHT - 10, (150, 100, 50))  # Brown shell
        
        self.image = self.frames_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.animation_index = 0
        self.animation_timer = 0
        
        # Movement parameters
        self.start_x = x
        self.move_range = random.randint(100, 300)
        self.velocity_y = 0
        self.on_ground = False
        
        # Player detection
        self.spotted_player = False
        self.vision_range = 200
        self.platform_edge_detection = 20
        
        # Turtle specific properties
        self.in_shell = False
        self.shell_speed = 0
        self.shell_max_speed = 10
        self.shell_timer = 0
        self.shell_duration = 180  # 3 seconds at 60 FPS
        
    def update(self):
        # Animation timing
        self.animation_timer += 1
        if self.animation_timer > 8:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames_right)

        if not self.in_shell:
            # Normal movement
            # Apply gravity only if spotted player or already falling
            if self.spotted_player or not self.on_ground:
                self.velocity_y += GRAVITY
                self.rect.y += self.velocity_y

            # Update horizontal position
            self.rect.x += ENEMY_SPEED * self.direction * 0.7  # Turtles move slower

            # Update animation based on direction
            if self.direction > 0:
                self.image = self.frames_right[self.animation_index]
            else:
                self.image = self.frames_left[self.animation_index]
        else:
            # Shell state
            self.shell_timer += 1
            
            # Apply gravity
            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y
            
            # If shell is moving, it slides along the ground
            if self.shell_speed != 0:
                self.rect.x += self.shell_speed
                
                # Check if shell hits world boundaries
                if self.rect.left < 0:
                    self.rect.left = 0
                    self.shell_speed = abs(self.shell_speed)  # Bounce off left edge
                elif self.rect.right > WORLD_WIDTH:
                    self.rect.right = WORLD_WIDTH
                    self.shell_speed = -abs(self.shell_speed)  # Bounce off right edge
                
            # Come out of shell after timer expires if not moving
            if self.shell_timer >= self.shell_duration and self.shell_speed == 0:
                self.in_shell = False
                self.image = self.frames_right[0] if self.direction > 0 else self.frames_left[0]
                self.shell_timer = 0

        # Ground collision - reset at the beginning of each frame
        self.on_ground = False
        
        # Ground collision check
        if self.rect.bottom > SCREEN_HEIGHT - 10:
            self.rect.bottom = SCREEN_HEIGHT - 10
            self.velocity_y = 0
            self.on_ground = True
        
    def detect_player(self, player, camera):
        # Only detect player if they're on screen
        if (self.rect.x + self.rect.width + camera.scroll_x > 0 and 
            self.rect.x + camera.scroll_x < camera.width):
            
            # Check if player is within vision range horizontally
            if abs(player.rect.x - self.rect.x) < self.vision_range:
                # Check if player is at roughly the same height or below
                if abs(player.rect.y - self.rect.y) < 100 or player.rect.y > self.rect.y:
                    self.spotted_player = True
                    return True
        
        return False
    
    def check_platform_edge(self, platforms):
        """Check if enemy is near a platform edge"""
        if not self.spotted_player and self.on_ground and not self.in_shell:
            # Create a rect that extends slightly in the direction of movement
            edge_check = self.rect.copy()
            
            if self.direction > 0:  # Moving right
                edge_check.x += self.platform_edge_detection
            else:  # Moving left
                edge_check.x -= self.platform_edge_detection
                
            # Extend the check downward
            edge_check.y += 5
            edge_check.height += 15
            
            # Check if any platform is under this extended rect
            platform_below = False
            for platform in platforms:
                if platform.rect.colliderect(edge_check) and platform.rect.top >= self.rect.bottom - 10:
                    platform_below = True
                    break
            
            if not platform_below:
                # No platform ahead, change direction
                self.direction *= -1
                return True
                
        return False
    
    def enter_shell(self):
        """Make turtle enter its shell"""
        self.in_shell = True
        self.shell_timer = 0
        self.shell_speed = 0
        self.image = self.shell_image
        
    def kick_shell(self, direction):
        """Kick the shell in the given direction"""
        if self.in_shell:
            self.shell_speed = self.shell_max_speed * direction
            return True
        return False
    
    def check_shell_collision(self, other_enemies):
        """Check if moving shell hits other enemies"""
        if self.in_shell and self.shell_speed != 0:
            hit_enemies = []
            for enemy in other_enemies:
                if enemy != self and self.rect.colliderect(enemy.rect):
                    hit_enemies.append(enemy)
            return hit_enemies
        return []

    def check_platform_collision(self, platforms):
        """Check for platform collisions specifically for the shell state"""
        if self.in_shell and self.shell_speed != 0:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    # If hitting side of platform, bounce
                    if ((self.shell_speed > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left) or
                        (self.shell_speed < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right)):
                        if self.rect.bottom > platform.rect.top + 10:  # Not landing on top
                            self.shell_speed = -self.shell_speed  # Reverse direction
                            return True
        return False 