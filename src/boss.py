import pygame
import random
import math
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRAVITY, PURPLE, RED, YELLOW, 
    BOSS_WIDTH, BOSS_HEIGHT, BOSS_HEALTH
)
from src.constants import load_image

# Cache for projectile images to avoid recreation on every frame
projectile_image_cache = {}

class Boss(pygame.sprite.Sprite):
    """Boss enemy with multiple attack patterns and health bar"""
    def __init__(self, x, y):
        super().__init__()
        
        # Create boss animation frames
        self.idle_frames = [
            load_image("boss_idle1.png", BOSS_WIDTH, BOSS_HEIGHT, RED),
            load_image("boss_idle2.png", BOSS_WIDTH, BOSS_HEIGHT, RED)
        ]
        self.attack_frames = [
            load_image("boss_attack1.png", BOSS_WIDTH, BOSS_HEIGHT, RED),
            load_image("boss_attack2.png", BOSS_WIDTH, BOSS_HEIGHT, RED),
            load_image("boss_attack3.png", BOSS_WIDTH, BOSS_HEIGHT, RED)
        ]
        self.hurt_frame = load_image("boss_hurt.png", BOSS_WIDTH, BOSS_HEIGHT, PURPLE)
        
        # Pre-flip all animation frames to avoid doing it during gameplay
        self.idle_frames_flipped = [pygame.transform.flip(frame, True, False) for frame in self.idle_frames]
        self.attack_frames_flipped = [pygame.transform.flip(frame, True, False) for frame in self.attack_frames]
        self.hurt_frame_flipped = pygame.transform.flip(self.hurt_frame, True, False)
        
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement and physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = -1  # -1 left, 1 right
        self.speed = 2.0      # Reduced base speed for easier dodging
        self.jump_force = -12  # Less aggressive jump
        
        # Animation variables
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 8  # Faster animation
        self.current_animation = "idle"
        
        # Attack variables
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 120  # Longer cooldown between attacks (easier)
        self.attack_duration = 60   # How long an attack lasts
        self.current_attack = "none"
        self.stomped = False
        self.stomp_timer = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.vulnerability_time = 90  # Longer vulnerability time after being hit
        
        # Health and state
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.phase = 1  # Boss gets more aggressive in higher phases
        self.damage_per_hit = 2  # Boss takes more damage per hit (easier)
        self.defeated = False
        self.active = False  # Boss only activates when player is near
        self.rage_mode = False  # New rage mode when health is low
        self.rage_timer = 0     # Timer for rage mode effects
        
        # Projectiles and special attacks
        self.projectiles = pygame.sprite.Group()
        self.attack_pattern = ["jump", "throw", "charge", "stomp", "spin"]  # Added spin attack
        self.current_pattern_index = 0
        
        # Visual effects
        self.flash_timer = 0
        self.shake_offset = [0, 0]
        
        # Performance optimizations
        self.max_projectiles = 30  # Fewer projectiles for easier gameplay
        self.last_update_time = 0  # For tracking time between updates
        
        # Weak spot indicator
        self.weak_spot_visible = True
        self.weak_spot_rect = pygame.Rect(0, 0, 30, 30)
        self.weak_spot_timer = 0
    
    def update(self, player=None, platforms=None):
        if self.defeated:
            # Death animation would go here
            return
            
        if not self.active:
            # Only animate when inactive
            self.animate("idle")
            return
        
        # Update weak spot location
        if self.direction > 0:
            self.weak_spot_rect.center = (self.rect.centerx + 20, self.rect.top + 30)
        else:
            self.weak_spot_rect.center = (self.rect.centerx - 20, self.rect.top + 30)
            
        # Make weak spot flash
        self.weak_spot_timer += 1
        self.weak_spot_visible = self.weak_spot_timer % 30 < 20
            
        # Check if boss should enter rage mode
        if not self.rage_mode and self.health <= self.max_health // 3:
            self.rage_mode = True
            self.speed *= 1.2  # Reduced rage speed increase (easier)
            self.attack_cooldown = 100  # Less cooldown reduction in rage mode
            # Visual indication of rage mode
            self.flash_timer = 30
            
        # Handle rage mode effects - reduce frequency of updates
        if self.rage_mode:
            self.rage_timer += 1
            if self.rage_timer % 120 < 60 and self.rage_timer % 4 == 0:  # Reduced frequency
                # Randomly shake during rage mode
                self.shake_offset = [random.randint(-2, 2), random.randint(-2, 2)]
            else:
                self.shake_offset = [0, 0]
                
        # Handle flash effect timer
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        # Apply gravity
        self.velocity_y += GRAVITY * 0.7  # Reduced gravity for easier jumps to avoid
        self.rect.y += self.velocity_y
        
        # Check ground collision
        if self.rect.bottom > SCREEN_HEIGHT - 10:
            self.rect.bottom = SCREEN_HEIGHT - 10
            self.velocity_y = 0
            self.stomped = False
            
            # Create shockwave when landing from a high jump
            if self.current_attack == "jump" and self.attack_timer > 30 and len(self.projectiles) < self.max_projectiles:
                self.create_shockwave()
        
        # Check platform collisions
        if platforms:
            self.check_platform_collision(platforms)
            
        # Handle attack cooldown
        if self.attacking:
            self.attack_timer += 1
            if self.attack_timer >= self.attack_duration:
                self.attacking = False
                self.attack_timer = 0
                self.current_attack = "none"
                # Reset velocity after attack
                self.velocity_x = 0
                # Add recovery period after attack (easier)
                self.attack_cooldown += 30
        elif self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Handle invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer += 1
            if self.invulnerable_timer >= self.vulnerability_time:  # Longer invulnerability
                self.invulnerable = False
                self.invulnerable_timer = 0
        
        # Handle stomp status
        if self.stomped:
            self.stomp_timer += 1
            if self.stomp_timer >= 45:  # Longer stun time (easier)
                self.stomped = False
                self.stomp_timer = 0
                # Jump after being stomped
                self.velocity_y = self.jump_force * 0.8  # Reduced post-stomp jump
        
        # Movement during non-attack
        if not self.attacking and not self.stomped:
            if player:
                # Track player
                if player.rect.x < self.rect.x:
                    self.direction = -1
                    self.velocity_x = -self.speed
                else:
                    self.direction = 1
                    self.velocity_x = self.speed
                    
                # Choose attack if cooldown is done
                if self.attack_cooldown <= 0 and self.health > 0:
                    # Less aggressive in phases and rage mode (easier)
                    attack_chance = 0.005 * self.phase * (1.5 if self.rage_mode else 1)
                    if random.random() < attack_chance:
                        self.choose_attack(player)
        
        # Apply horizontal movement
        if not self.stomped:
            self.rect.x += self.velocity_x
        
        # Handle animation
        if self.stomped:
            self.animate("hurt")
        elif self.attacking:
            self.animate("attack")
        else:
            self.animate("idle")
            
        # Update projectiles - only update a subset per frame if there are many
        projectile_count = len(self.projectiles)
        if projectile_count > 0:
            # Dynamically adjust update frequency based on projectile count
            for i, projectile in enumerate(list(self.projectiles)):
                # Always update projectiles that are close to the screen edges
                off_screen = (projectile.rect.right < 50 or
                            projectile.rect.left > SCREEN_WIDTH - 50 or
                            projectile.rect.bottom < 50 or
                            projectile.rect.top > SCREEN_HEIGHT - 50)
                
                # For many projectiles, stagger updates to improve performance
                if off_screen or i % max(1, projectile_count // 10) == 0:
                    if not projectile.update():
                        self.projectiles.remove(projectile)
                
            # Limit total projectiles for performance
            if projectile_count > self.max_projectiles:
                # Remove the oldest projectiles
                for _ in range(projectile_count - self.max_projectiles):
                    if self.projectiles:
                        oldest = next(iter(self.projectiles))
                        self.projectiles.remove(oldest)
                
        # Keep boss within screen bounds
        if self.rect.left < 50:
            self.rect.left = 50
            if self.velocity_x < 0:
                self.velocity_x = 0
        elif self.rect.right > SCREEN_WIDTH - 50:
            self.rect.right = SCREEN_WIDTH - 50
            if self.velocity_x > 0:
                self.velocity_x = 0
                
    def animate(self, animation_type):
        """Handle boss animations"""
        self.animation_timer += 1
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            
            if animation_type == "idle":
                self.animation_index = (self.animation_index + 1) % len(self.idle_frames)
                if self.direction > 0:
                    self.image = self.idle_frames_flipped[self.animation_index]
                else:
                    self.image = self.idle_frames[self.animation_index]
            
            elif animation_type == "attack":
                self.animation_index = (self.animation_index + 1) % len(self.attack_frames)
                if self.direction > 0:
                    self.image = self.attack_frames_flipped[self.animation_index]
                else:
                    self.image = self.attack_frames[self.animation_index]
            
            elif animation_type == "hurt":
                if self.direction > 0:
                    self.image = self.hurt_frame_flipped
                else:
                    self.image = self.hurt_frame
                    
        # Flash when invulnerable - reduce frequency for performance
        if self.invulnerable and self.animation_timer % 4 < 2:
            self.image.set_alpha(150)
        else:
            self.image.set_alpha(255)
            
        # Flash red when in rage mode - reduce frequency for performance
        if self.rage_mode and self.flash_timer > 0 and self.flash_timer % 6 < 3:
            # Use a more efficient method than creating a new surface every frame
            if not hasattr(self, 'rage_image') or self.animation_timer == 0:
                # Only create the rage image when needed
                self.rage_image = self.image.copy()
                self.rage_image.fill((255, 0, 0, 100), None, pygame.BLEND_RGBA_ADD)
            self.image = self.rage_image
                
    def choose_attack(self, player):
        """Choose and initiate an attack pattern"""
        self.attacking = True
        self.attack_timer = 0
        
        if self.rage_mode and random.random() < 0.3:
            # In rage mode, sometimes use random attack for unpredictability
            attack_type = random.choice(self.attack_pattern)
        else:
            # Get next attack in pattern - more predictable for easier gameplay
            attack_type = self.attack_pattern[self.current_pattern_index]
            self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_pattern)
        
        # Execute the chosen attack
        if attack_type == "jump":
            self.jump_attack()
        elif attack_type == "throw":
            self.throw_attack(player)
        elif attack_type == "charge":
            self.charge_attack(player)
        elif attack_type == "stomp":
            self.stomp_attack(player)
        elif attack_type == "spin":
            self.spin_attack()
            
        # Set cooldown - longer in all phases (easier)
        self.attack_cooldown = max(90, 150 - (self.phase * 15))
        if self.rage_mode:
            self.attack_cooldown = max(60, self.attack_cooldown // 1.5)  # Less cooldown reduction
            
        self.current_attack = attack_type
        
    def jump_attack(self):
        """Jump high and land heavily"""
        self.velocity_y = self.jump_force * 1.3  # Less high jump
    
    def throw_attack(self, player):
        """Throw projectiles at the player"""
        # Only throw if we're under the projectile limit
        if len(self.projectiles) >= self.max_projectiles:
            return
            
        # Create fewer projectiles (easier)
        num_projectiles = min(1 + self.phase // 2, 3)
        if self.rage_mode:
            num_projectiles += 1
            
        # Limit based on current count
        num_projectiles = min(num_projectiles, self.max_projectiles - len(self.projectiles))
        
        if num_projectiles <= 0:
            return
        
        if self.rage_mode:
            # In rage mode, throw in a spread pattern
            angle_step = math.pi / (num_projectiles + 1)
            base_angle = math.atan2(player.rect.centery - self.rect.centery,
                                  player.rect.centerx - self.rect.centerx)
            
            for i in range(num_projectiles):
                angle = base_angle + (i - num_projectiles // 2) * angle_step
                speed = 4 + self.phase  # Slower projectiles (easier)
                
                # Create projectile
                projectile = BossProjectile(
                    self.rect.centerx, 
                    self.rect.centery,
                    speed * math.cos(angle),
                    speed * math.sin(angle)
                )
                self.projectiles.add(projectile)
        else:
            # Normal throw attack - more spread (easier to dodge)
            for i in range(num_projectiles):
                # Calculate angle to player with more variance
                angle = math.atan2(player.rect.centery - self.rect.centery,
                                  player.rect.centerx - self.rect.centerx)
                angle += random.uniform(-0.5, 0.5)  # More spread (easier)
                
                speed = 4 + self.phase  # Slower projectiles (easier)
                
                # Create projectile
                projectile = BossProjectile(
                    self.rect.centerx, 
                    self.rect.centery,
                    speed * math.cos(angle),
                    speed * math.sin(angle)
                )
                self.projectiles.add(projectile)
    
    def charge_attack(self, player):
        """Rush toward the player"""
        # Calculate direction to player
        if player.rect.centerx > self.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1
            
        # Set velocity for charge - slower in rage mode (easier)
        charge_speed = 8 + (self.phase * 1.5)  # Slower charge (easier)
        if self.rage_mode:
            charge_speed *= 1.2  # Less rage boost (easier)
            
        self.velocity_x = charge_speed * self.direction
    
    def stomp_attack(self, player):
        """Jump high and try to land on player's position"""
        self.velocity_y = self.jump_force * 1.4  # Less high jump
        
        # Try to predict where player will be - less accurate (easier)
        if player:
            # Add randomness to target position (easier)
            target_x = player.rect.x + random.randint(-100, 100)
            distance = abs(target_x - self.rect.x)
            
            # Calculate how much to move horizontally - less precise (easier)
            jump_time = abs(self.velocity_y / GRAVITY) * 2  # Rough estimate of time in air
            needed_vel_x = distance / jump_time
            
            # Cap the horizontal velocity - slower (easier)
            max_vel = 6 + (self.phase * 1.0)
            if self.rage_mode:
                max_vel *= 1.1
                
            if needed_vel_x > max_vel:
                needed_vel_x = max_vel
                
            # Set velocity
            if target_x > self.rect.x:
                self.velocity_x = needed_vel_x
                self.direction = 1
            else:
                self.velocity_x = -needed_vel_x
                self.direction = -1
                
    def spin_attack(self):
        """New attack: Spin rapidly and release projectiles in all directions"""
        # Only create projectiles if we're under the limit
        if len(self.projectiles) >= self.max_projectiles:
            return
            
        # Spin motion effect
        self.velocity_x = 0
        self.velocity_y = -4  # Smaller hop during spin
        
        # Create projectiles in all directions - fewer (easier)
        num_projectiles = min(6 + (self.phase * 1), 12)
        if self.rage_mode:
            num_projectiles = min(12, self.max_projectiles // 2)
            
        # Limit based on current count
        num_projectiles = min(num_projectiles, self.max_projectiles - len(self.projectiles))
        
        if num_projectiles <= 0:
            return
            
        angle_step = 2 * math.pi / num_projectiles
        
        for i in range(num_projectiles):
            angle = i * angle_step
            speed = 4 + (self.phase * 0.5)  # Slower projectiles (easier)
            
            projectile = BossProjectile(
                self.rect.centerx,
                self.rect.centery,
                speed * math.cos(angle),
                speed * math.sin(angle)
            )
            self.projectiles.add(projectile)
            
    def create_shockwave(self):
        """Create a shockwave of projectiles when landing from a high jump"""
        # Only create shockwave if we're under the projectile limit
        if len(self.projectiles) >= self.max_projectiles:
            return
            
        # Adjust number of projectiles - fewer (easier)
        num_projectiles = min(4 + self.phase, 8)
        
        # Limit based on current count
        num_projectiles = min(num_projectiles, self.max_projectiles - len(self.projectiles))
        
        if num_projectiles <= 0:
            return
            
        speed = 4 + (self.phase * 0.5)  # Slower projectiles (easier)
        
        for i in range(num_projectiles):
            angle = 2 * math.pi * i / num_projectiles
            # Ground level projectiles (horizontal path)
            projectile = BossProjectile(
                self.rect.centerx, 
                self.rect.bottom - 5,
                speed * math.cos(angle),
                min(-1.5, speed * math.sin(angle))  # Bias upward slightly
            )
            self.projectiles.add(projectile)
            
    def take_damage(self):
        """Boss takes damage"""
        if not self.invulnerable:
            self.health -= self.damage_per_hit  # Take more damage per hit
            self.invulnerable = True
            self.invulnerable_timer = 0
            self.stomped = True
            self.stomp_timer = 0
            
            # Phase increase after taking damage
            self.phase = max(1, (self.max_health - self.health) // 4 + 1)  # Slower phase progression
            
            # Rage mode check
            if not self.rage_mode and self.health <= self.max_health // 3:
                self.rage_mode = True
                self.speed *= 1.2  # Less speed boost in rage mode (easier)
                self.attack_cooldown = 80  # Less reduction in cooldown (easier)
                self.flash_timer = 30
            
            # Check if defeated
            if self.health <= 0:
                self.defeated = True
                # Clear all projectiles when defeated
                self.projectiles.empty()
                
            # Visual effects when damaged
            self.flash_timer = 15
                
            return True
        return False
            
    def check_platform_collision(self, platforms):
        """Check for collisions with platforms"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Bottom collision (landing)
                if self.velocity_y > 0 and self.rect.bottom < platform.rect.bottom + 10:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    
                    # Create shockwave when landing from a high jump
                    if self.current_attack == "jump" and self.attack_timer > 30 and len(self.projectiles) < self.max_projectiles:
                        self.create_shockwave()
                # Top collision
                elif self.velocity_y < 0 and self.rect.top < platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                # Side collision
                elif self.velocity_x > 0 and self.rect.right > platform.rect.left:
                    self.rect.right = platform.rect.left
                    self.velocity_x *= -1
                    self.direction *= -1
                elif self.velocity_x < 0 and self.rect.left < platform.rect.right:
                    self.rect.left = platform.rect.right
                    self.velocity_x *= -1
                    self.direction *= -1
            
    def draw_health_bar(self, surface):
        """Draw health bar above boss"""
        if not self.active or self.defeated:
            return
            
        # Bar background
        bar_width = BOSS_WIDTH * 1.5
        bar_height = 10
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 20
        
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Calculate health percentage
        health_percent = self.health / self.max_health
        
        # Health bar color based on health
        if health_percent > 0.6:
            color = (0, 255, 0)  # Green
        elif health_percent > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
            
        # Health bar
        health_width = int(bar_width * health_percent)
        pygame.draw.rect(surface, color, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Add phase indicator
        phase_text = f"Phase {self.phase}"
        font = pygame.font.Font(None, 20)
        text_surface = font.render(phase_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midtop=(bar_x + bar_width // 2, bar_y - 15))
        surface.blit(text_surface, text_rect)
        
        # Draw weak spot indicator
        if self.weak_spot_visible:
            pygame.draw.circle(surface, (255, 255, 0), self.weak_spot_rect.center, 10)
            pygame.draw.circle(surface, (255, 0, 0), self.weak_spot_rect.center, 5)

class BossProjectile(pygame.sprite.Sprite):
    """Projectile fired by the boss"""
    def __init__(self, x, y, vel_x, vel_y):
        super().__init__()
        
        # Use cached images for better performance
        rotation_key = 0  # Start with no rotation
        if rotation_key not in projectile_image_cache:
            projectile_image_cache[rotation_key] = load_image("boss_projectile.png", 20, 20, (255, 100, 0))
        
        self.image = projectile_image_cache[rotation_key]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_x = vel_x
        self.velocity_y = vel_y
        self.rotation = 0
        self.rotation_speed = random.randint(5, 15)
        self.age = 0
        self.max_age = 120  # 2 seconds at 60fps - shorter lifespan (easier)
        
    def update(self):
        """Update projectile position"""
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Add gravity to projectiles for more realistic arcs
        self.velocity_y += 0.15  # More gravity (easier)
        
        # Rotate the projectile for visual effect - but less frequently
        self.age += 1
        if self.age % 3 == 0:  # Only update rotation every 3 frames
            self.rotation = (self.rotation + self.rotation_speed) % 360
            
            # Use image cache for rotated images
            rotation_key = self.rotation // 15 * 15  # Round to nearest 15 degrees for caching
            if rotation_key not in projectile_image_cache:
                projectile_image_cache[rotation_key] = pygame.transform.rotate(
                    projectile_image_cache[0], rotation_key
                )
            
            self.image = projectile_image_cache[rotation_key]
            
        # Check for off-screen or max age to remove projectile
        if (self.rect.right < 0 or 
            self.rect.left > SCREEN_WIDTH or 
            self.rect.bottom < 0 or 
            self.rect.top > SCREEN_HEIGHT + 50 or
            self.age > self.max_age):
            return False
            
        return True 