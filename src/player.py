import pygame
import random
from src.constants import (
    PLAYER_WIDTH, PLAYER_HEIGHT, GRAVITY, JUMP_FORCE, PLAYER_SPEED, 
    PLAYER_ACCELERATION, PLAYER_DECELERATION, MAX_JUMPS, 
    WORLD_WIDTH, SCREEN_HEIGHT, MAX_LIVES, STAR_DURATION,
    INVINCIBILITY_DURATION, SCORE_MULTIPLIER_DURATION,
    GOLD, WHITE, RED, GREEN, BLUE, ORANGE, PURPLE, YELLOW
)
from src.constants import load_image

class Player(pygame.sprite.Sprite):
    # Add max_jumps class variable
    max_jumps = MAX_JUMPS
    
    def __init__(self):
        super().__init__()
        
        # Define base colors for different power states
        self.normal_color = RED
        self.mushroom_color = BLUE
        self.star_color = GOLD
        self.flower_color = GREEN
        
        # Store the current color
        self.current_color = self.normal_color
        
        # Create animation frames for normal state
        self.frames_right = [
            load_image("player_walk1.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color),
            load_image("player_walk2.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color)
        ]
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]
        self.jump_frame_right = load_image("player_jump.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color)
        self.jump_frame_left = pygame.transform.flip(self.jump_frame_right, True, False)
        self.idle_frame_right = load_image("player_idle.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color)
        self.idle_frame_left = pygame.transform.flip(self.idle_frame_right, True, False)

        # Create powered-up versions (with star sparkle effects)
        self.star_frames_right = []
        self.star_frames_left = []
        for frame in self.frames_right:
            star_frame = frame.copy()
            # Add star sparkle effect
            self.add_sparkle_effect(star_frame)
            self.star_frames_right.append(star_frame)
            self.star_frames_left.append(pygame.transform.flip(star_frame, True, False))
        
        # Create flower power-up versions (with fire effects)
        self.flower_frames_right = []
        self.flower_frames_left = []
        for frame in self.frames_right:
            flower_frame = frame.copy()
            # Add flower effect (fire highlights)
            self.add_flower_effect(flower_frame)
            self.flower_frames_right.append(flower_frame)
            self.flower_frames_left.append(pygame.transform.flip(flower_frame, True, False))
        
        self.star_jump_frame_right = self.jump_frame_right.copy()
        self.add_sparkle_effect(self.star_jump_frame_right)
        self.star_jump_frame_left = pygame.transform.flip(self.star_jump_frame_right, True, False)
        
        self.flower_jump_frame_right = self.jump_frame_right.copy()
        self.add_flower_effect(self.flower_jump_frame_right)
        self.flower_jump_frame_left = pygame.transform.flip(self.flower_jump_frame_right, True, False)
        
        self.star_idle_frame_right = self.idle_frame_right.copy()
        self.add_sparkle_effect(self.star_idle_frame_right)
        self.star_idle_frame_left = pygame.transform.flip(self.star_idle_frame_right, True, False)
        
        self.flower_idle_frame_right = self.idle_frame_right.copy()
        self.add_flower_effect(self.flower_idle_frame_right)
        self.flower_idle_frame_left = pygame.transform.flip(self.flower_idle_frame_right, True, False)
        
        self.image = self.idle_frame_right
        self.rect = self.image.get_rect()
        self.rect.x = 100  # Start a bit more to the right
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
        self.velocity_y = 0
        self.velocity_x = 0
        self.jumping = False
        self.jumps_left = MAX_JUMPS
        self.score = 0
        self.facing_right = True
        self.animation_index = 0
        self.animation_timer = 0
        self.on_ground = False
        self.coyote_time = 0  # Time after leaving a platform when you can still jump
        self.max_coyote_time = 7  # Frames of coyote time
        
        # New attributes for power-ups and lives
        self.lives = MAX_LIVES
        self.has_star = False
        self.star_timer = 0
        self.has_flower = False  # Flower power-up state
        self.flower_timer = 0    # Duration of flower power
        self.has_mushroom = False # Mushroom power-up state (for blue color)
        self.fireball_cooldown = 0  # Cooldown between firing fireballs
        self.invincible = False
        self.invincibility_timer = 0
        self.score_multiplier = 1
        self.multiplier_timer = 0
        self.flash_timer = 0  # For invincibility flashing effect
    
    def update_color(self, new_color):
        """Update player's base color and recreate animation frames"""
        self.current_color = new_color
        
        # Store current state
        was_facing_right = self.facing_right
        was_jumping = self.jumping
        
        # Recreate normal animation frames with new color
        self.frames_right = [
            load_image("player_walk1.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color),
            load_image("player_walk2.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color)
        ]
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]
        self.jump_frame_right = load_image("player_jump.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color)
        self.jump_frame_left = pygame.transform.flip(self.jump_frame_right, True, False)
        self.idle_frame_right = load_image("player_idle.png", PLAYER_WIDTH, PLAYER_HEIGHT, self.current_color)
        self.idle_frame_left = pygame.transform.flip(self.idle_frame_right, True, False)
        
        # Recreate star frames
        self.star_frames_right = []
        self.star_frames_left = []
        for frame in self.frames_right:
            star_frame = frame.copy()
            self.add_sparkle_effect(star_frame)
            self.star_frames_right.append(star_frame)
            self.star_frames_left.append(pygame.transform.flip(star_frame, True, False))
        
        self.star_jump_frame_right = self.jump_frame_right.copy()
        self.add_sparkle_effect(self.star_jump_frame_right)
        self.star_jump_frame_left = pygame.transform.flip(self.star_jump_frame_right, True, False)
        
        self.star_idle_frame_right = self.idle_frame_right.copy()
        self.add_sparkle_effect(self.star_idle_frame_right)
        self.star_idle_frame_left = pygame.transform.flip(self.star_idle_frame_right, True, False)
        
        # Recreate flower frames
        self.flower_frames_right = []
        self.flower_frames_left = []
        for frame in self.frames_right:
            flower_frame = frame.copy()
            self.add_flower_effect(flower_frame)
            self.flower_frames_right.append(flower_frame)
            self.flower_frames_left.append(pygame.transform.flip(flower_frame, True, False))
        
        self.flower_jump_frame_right = self.jump_frame_right.copy()
        self.add_flower_effect(self.flower_jump_frame_right)
        self.flower_jump_frame_left = pygame.transform.flip(self.flower_jump_frame_right, True, False)
        
        self.flower_idle_frame_right = self.idle_frame_right.copy()
        self.add_flower_effect(self.flower_idle_frame_right)
        self.flower_idle_frame_left = pygame.transform.flip(self.flower_idle_frame_right, True, False)
        
        # Set correct frame based on current state
        if self.has_star:
            if was_jumping:
                self.image = self.star_jump_frame_right if was_facing_right else self.star_jump_frame_left
            else:
                self.image = self.star_idle_frame_right if was_facing_right else self.star_idle_frame_left
        elif self.has_flower:
            if was_jumping:
                self.image = self.flower_jump_frame_right if was_facing_right else self.flower_jump_frame_left
            else:
                self.image = self.flower_idle_frame_right if was_facing_right else self.flower_idle_frame_left
        else:
            if was_jumping:
                self.image = self.jump_frame_right if was_facing_right else self.jump_frame_left
            else:
                self.image = self.idle_frame_right if was_facing_right else self.idle_frame_left
                
    def add_sparkle_effect(self, surface):
        """Add sparkle effect to a surface for star power"""
        width, height = surface.get_size()
        # Add yellow sparkles
        for _ in range(5):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            pygame.draw.circle(surface, GOLD, (x, y), 2)
            # Add white center to sparkle
            pygame.draw.circle(surface, WHITE, (x, y), 1)
            
    def add_flower_effect(self, surface):
        """Add flower power effect to a surface (fire highlights)"""
        width, height = surface.get_size()
        # Add fire-like highlights (orange and yellow)
        for _ in range(4):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            # Create a small 'flame' shaped highlight
            pygame.draw.circle(surface, ORANGE, (x, y), 3)
            # Add yellow center
            pygame.draw.circle(surface, YELLOW, (x, y), 1)

    def update(self, world_bounds):
        # Track if player was on ground in previous frame
        was_on_ground = self.on_ground
        
        # Animation timing - dynamically adjust animation speed based on movement speed
        animation_speed = max(3, 8 - abs(self.velocity_x) // 2)  # Faster animation when moving faster
        self.animation_timer += 1
        if self.animation_timer > animation_speed:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames_right)

        # Apply gravity with terminal velocity
        max_fall_speed = 15
        self.velocity_y = min(self.velocity_y + GRAVITY, max_fall_speed)
        self.rect.y += self.velocity_y
        
        # Apply horizontal movement with sub-pixel precision
        self.rect.x += round(self.velocity_x)  # Round to avoid pixel jittering

        # Update animation based on state
        if self.has_star:
            if self.jumping:
                self.image = self.star_jump_frame_right if self.facing_right else self.star_jump_frame_left
            elif abs(self.velocity_x) > 0.5:  # Only show walking animation if actually moving
                if self.velocity_x > 0:
                    self.facing_right = True
                    self.image = self.star_frames_right[self.animation_index]
                else:
                    self.facing_right = False
                    self.image = self.star_frames_left[self.animation_index]
            else:
                self.image = self.star_idle_frame_right if self.facing_right else self.star_idle_frame_left
        elif self.has_flower:
            if self.jumping:
                self.image = self.flower_jump_frame_right if self.facing_right else self.flower_jump_frame_left
            elif abs(self.velocity_x) > 0.5:  # Only show walking animation if actually moving
                if self.velocity_x > 0:
                    self.facing_right = True
                    self.image = self.flower_frames_right[self.animation_index]
                else:
                    self.facing_right = False
                    self.image = self.flower_frames_left[self.animation_index]
            else:
                self.image = self.flower_idle_frame_right if self.facing_right else self.flower_idle_frame_left
        else:
            # Normal animation (non-power-up)
            if self.jumping:
                self.image = self.jump_frame_right if self.facing_right else self.jump_frame_left
            elif abs(self.velocity_x) > 0.5:  # Only show walking animation if actually moving
                if self.velocity_x > 0:
                    self.facing_right = True
                    self.image = self.frames_right[self.animation_index]
                else:
                    self.facing_right = False
                    self.image = self.frames_left[self.animation_index]
            else:
                self.image = self.idle_frame_right if self.facing_right else self.idle_frame_left

        # Apply friction
        self.velocity_x *= PLAYER_DECELERATION
        if abs(self.velocity_x) < 0.5:
            self.velocity_x = 0

        # Ground collision
        if self.rect.bottom > SCREEN_HEIGHT - 10:
            self.rect.bottom = SCREEN_HEIGHT - 10
            self.velocity_y = 0
            self.jumping = False
            self.jumps_left = MAX_JUMPS
            self.on_ground = True
        else:
            self.on_ground = False
            
        # Coyote time logic - allow jumping briefly after leaving a platform
        if was_on_ground and not self.on_ground:
            self.coyote_time = self.max_coyote_time
        elif self.coyote_time > 0:
            self.coyote_time -= 1

        # World boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
        if self.rect.right > world_bounds:
            self.rect.right = world_bounds
            self.velocity_x = 0
            
        # Update power-up timers
        self.update_powerup_timers()
        
        # Update fireball cooldown
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        
    def update_powerup_timers(self):
        # Update star power timer
        if self.has_star:
            self.star_timer -= 1
            # Remove music code
            # Star music handled in the main game loop
                
            if self.star_timer <= 0:
                self.has_star = False
                self.invincible = False  # Star power also gives invincibility
                
                # Reset color based on other powerups
                if self.has_flower:
                    self.update_color(self.flower_color)
                elif self.has_mushroom:
                    self.update_color(self.mushroom_color)
                else:
                    self.update_color(self.normal_color)
                
                # Remove music code
                # Music change handled in the main game loop
        
        # Update flower power timer
        if self.has_flower:
            self.flower_timer -= 1
            if self.flower_timer <= 0:
                self.has_flower = False
                
                # Reset color based on other powerups
                if self.has_star:
                    self.update_color(self.star_color)
                elif self.has_mushroom:
                    self.update_color(self.mushroom_color)
                else:
                    self.update_color(self.normal_color)
        
        # Update temporary invincibility timer (after taking damage)
        if self.invincible and not self.has_star:
            self.invincibility_timer -= 1
            # Flash effect
            self.flash_timer += 1
            if self.flash_timer > 5:  # Flash every 5 frames
                self.flash_timer = 0
                # Toggle visibility for flash effect
                if self.image.get_alpha() == 255:
                    self.image.set_alpha(150)
                else:
                    self.image.set_alpha(255)
                    
            if self.invincibility_timer <= 0:
                self.invincible = False
                self.image.set_alpha(255)  # Restore full opacity
        
        # Update score multiplier timer
        if self.score_multiplier > 1:
            self.multiplier_timer -= 1
            if self.multiplier_timer <= 0:
                self.score_multiplier = 1
    
    def jump(self):
        if self.on_ground or self.coyote_time > 0 or (self.jumps_left > 0 and not self.on_ground):
            self.velocity_y = JUMP_FORCE
            self.jumping = True
            
            # Only decrement jumps if not on ground and not in coyote time
            if not self.on_ground and self.coyote_time <= 0:
                self.jumps_left -= 1
            
            # Reset coyote time
            self.coyote_time = 0
            self.on_ground = False

    def move_left(self):
        self.velocity_x = max(self.velocity_x - PLAYER_ACCELERATION, -PLAYER_SPEED)
        self.facing_right = False

    def move_right(self):
        self.velocity_x = min(self.velocity_x + PLAYER_ACCELERATION, PLAYER_SPEED)
        self.facing_right = True
    
    def shoot_fireball(self, fireballs_group):
        """Shoot a fireball if player has flower power"""
        if self.has_flower and self.fireball_cooldown <= 0:
            from src.fireball import Fireball  # Import here to avoid circular imports
            
            # Create fireball at appropriate position
            if self.facing_right:
                fireball_x = self.rect.right
            else:
                fireball_x = self.rect.left
                
            fireball_y = self.rect.centery - 5
            
            # Create fireball with direction based on player facing
            direction = 1 if self.facing_right else -1
            fireball = Fireball(fireball_x, fireball_y, direction)
            
            # Add to fireballs group
            fireballs_group.add(fireball)
            
            # Set cooldown to prevent rapid fire
            self.fireball_cooldown = 20  # 20 frames (about 1/3 second at 60fps)
            
            # Optional: Small recoil for visual effect
            self.velocity_x -= direction * 0.5
            
            return True
        return False
        
    def collect_powerup(self, powerup_type):
        """Apply effect of a collected power-up"""
        if powerup_type == "mushroom":
            if self.lives < MAX_LIVES:
                self.lives += 1
                # Apply blue color for mushroom power-up
                self.has_mushroom = True
                
                # Star power overrides mushroom color
                if not self.has_star and not self.has_flower:
                    self.update_color(self.mushroom_color)
            else:
                # If already at max lives, give points instead
                self.score += 50
        elif powerup_type == "star":
            self.has_star = True
            self.invincible = True
            self.star_timer = STAR_DURATION
            # Update color to yellow/gold
            self.update_color(self.star_color)
            # Add star sound effect here
        elif powerup_type == "flower":
            self.has_flower = True
            self.flower_timer = STAR_DURATION  # Use same duration as star
            self.score_multiplier = 2
            self.multiplier_timer = SCORE_MULTIPLIER_DURATION
            
            # Star power overrides flower color
            if not self.has_star:
                self.update_color(self.flower_color)
            
    def take_damage(self):
        """Handle player taking damage"""
        # Don't take damage if invincible
        if self.invincible:
            return False
            
        # Lose a life
        self.lives -= 1
        
        # Reset power-up states when damaged
        self.has_flower = False
        self.has_mushroom = False
        # Star power is not lost on damage due to invincibility
        
        # Reset color if not star powered
        if not self.has_star:
            self.update_color(self.normal_color)
        
        # Temporary invincibility
        self.invincible = True
        self.invincibility_timer = INVINCIBILITY_DURATION
        
        # Knocked back slightly and bounce up
        direction = -1 if self.facing_right else 1
        self.velocity_x = 5 * direction
        self.velocity_y = -8
        
        return self.lives <= 0  # Return whether player is dead 