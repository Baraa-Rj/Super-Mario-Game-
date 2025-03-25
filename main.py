#!/usr/bin/env python3
import pygame
import sys
import random
import os
import math

# Import from modular files
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, 
    BLACK, WHITE, RED, YELLOW, GOLD, ORANGE, GREEN,
    COIN_SIZE, ENEMY_WIDTH, ENEMY_HEIGHT, SPIKE_HEIGHT,
    MAX_JUMPS, MAX_LIVES, BOSS_ACTIVATION_DISTANCE,
    BOSS_WIDTH, BOSS_HEIGHT
)
from src.player import Player
from src.camera import Camera
from src.coin import Coin
from src.enemy import Enemy, PatrollingEnemy
from src.turtle import Turtle
from src.platform import Platform, MovingPlatform, ShrinkingPlatform, FallingPlatform
from src.background import Background, Tree, Bush, Cloud
from src.spike import Spike
from src.powerup import PowerUp, LifeIcon
from src.game import handle_enemy_collision, reset_game, reset_boss
from src.fireball import Fireball
from src.boss import Boss, BossProjectile

# Load high score from file or create if it doesn't exist
def load_high_score():
    try:
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as file:
                return int(file.read())
        return 0
    except:
        return 0
        
# Save high score to file
def save_high_score(score):
    try:
        with open("highscore.txt", "w") as file:
            file.write(str(score))
    except:
        pass

def draw_text(surface, text, size, x, y, color=WHITE, align="topleft"):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "topleft":
        text_rect.topleft = (x, y)
    elif align == "center":
        text_rect.center = (x, y)
    elif align == "midtop":
        text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_menu(screen, high_score=0):
    screen.fill((0, 0, 25))  # Dark blue background
    
    # Title
    title_y = SCREEN_HEIGHT // 4
    draw_text(screen, "SUPER MARIO CLONE", 72, SCREEN_WIDTH // 2, title_y, GOLD, "center")
    
    # Instructions
    instructions_y = title_y + 100
    draw_text(screen, "PRESS ENTER TO START", 42, SCREEN_WIDTH // 2, instructions_y, WHITE, "center")
    draw_text(screen, "ARROW KEYS / WASD TO MOVE", 30, SCREEN_WIDTH // 2, instructions_y + 50, WHITE, "center")
    draw_text(screen, "SPACE TO JUMP", 30, SCREEN_WIDTH // 2, instructions_y + 80, WHITE, "center")
    draw_text(screen, "F TO SHOOT FIREBALLS (with flower power)", 30, SCREEN_WIDTH // 2, instructions_y + 110, GREEN, "center")
    
    # Power-ups
    powerup_y = instructions_y + 160
    draw_text(screen, "POWER-UPS:", 36, SCREEN_WIDTH // 2, powerup_y, WHITE, "center")
    
    # Mushroom
    pygame.draw.circle(screen, RED, (SCREEN_WIDTH // 2 - 150, powerup_y + 50), 15)
    draw_text(screen, "MUSHROOM - EXTRA LIFE", 28, SCREEN_WIDTH // 2 - 120, powerup_y + 42, WHITE, "topleft")
    
    # Star
    pygame.draw.circle(screen, GOLD, (SCREEN_WIDTH // 2 - 150, powerup_y + 80), 15)
    draw_text(screen, "STAR - INVINCIBILITY", 28, SCREEN_WIDTH // 2 - 120, powerup_y + 72, WHITE, "topleft")
    
    # Flower
    pygame.draw.circle(screen, GREEN, (SCREEN_WIDTH // 2 - 150, powerup_y + 110), 15)
    draw_text(screen, "FLOWER - SHOOT FIREBALLS", 28, SCREEN_WIDTH // 2 - 120, powerup_y + 102, WHITE, "topleft")
    
    # High score
    draw_text(screen, f"HIGH SCORE: {high_score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, GOLD, "center")
    
    # Credits
    draw_text(screen, "PRESS ESC TO QUIT", 20, SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10, WHITE, "topright")

def main():
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Game")
    clock = pygame.time.Clock()
    
    # Game states
    MENU = 0
    PLAYING = 1
    game_state = MENU
    
    # Load high score
    high_score = load_high_score()

    # Create camera
    camera = Camera(WORLD_WIDTH, SCREEN_HEIGHT)

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    moving_platforms = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    decorations = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    ui_elements = pygame.sprite.Group()
    fireballs = pygame.sprite.Group()  # New sprite group for fireballs

    # Create player
    player = Player()
    all_sprites.add(player)

    # Create background
    background = Background()

    # Create life icons
    life_icons = []
    for i in range(player.lives):
        icon = LifeIcon(SCREEN_WIDTH - 30 - i * 25, 10)
        ui_elements.add(icon)
        life_icons.append(icon)

    # Create platforms
    platform_positions = [
        (0, SCREEN_HEIGHT - 10, WORLD_WIDTH),  # Ground across entire world
        (300, 400, 200),
        (700, 350, 200),
        (1000, 300, 200),
        (1400, 400, 200),
        (1800, 300, 200),
        (2200, 350, 200),
        (2600, 300, 200),
    ]

    for pos in platform_positions:
        platform = Platform(*pos)
        all_sprites.add(platform)
        platforms.add(platform)

    # Add moving platforms
    moving_platform_data = [
        (550, 250, 100, 100, True),    # (x, y, width, move_distance, horizontal)
        (1200, 250, 100, 80, False),   # Vertical
        (1700, 200, 120, 150, True),   # Horizontal
        (2300, 300, 100, 100, False),  # Vertical
    ]

    for data in moving_platform_data:
        platform = MovingPlatform(*data)
        all_sprites.add(platform)
        platforms.add(platform)
        moving_platforms.add(platform)

    # Add power-ups
    powerup_positions = [
        (350, 200, "mushroom"),  # Extra life
        (1100, 150, "star"),     # Star power
        (1900, 150, "flower"),   # Score multiplier
        (2500, 200, "mushroom"), # Extra life at end
    ]

    for pos in powerup_positions:
        powerup = PowerUp(*pos)
        all_sprites.add(powerup)
        powerups.add(powerup)

    # Add spike obstacles
    spike_positions = [
        (400, 400 - SPIKE_HEIGHT),  # On platform
        (850, 350 - SPIKE_HEIGHT),  # On platform
        (1550, 400 - SPIKE_HEIGHT),  # On platform
        (2400, 350 - SPIKE_HEIGHT),  # On platform
        # Add some spikes on the ground too
        (600, SCREEN_HEIGHT - 10 - SPIKE_HEIGHT),
        (1300, SCREEN_HEIGHT - 10 - SPIKE_HEIGHT),
        (2000, SCREEN_HEIGHT - 10 - SPIKE_HEIGHT),
        (2700, SCREEN_HEIGHT - 10 - SPIKE_HEIGHT),
    ]

    for pos in spike_positions:
        spike = Spike(*pos)
        all_sprites.add(spike)
        obstacles.add(spike)

    # Add decorative trees
    tree_positions = [
        (100, SCREEN_HEIGHT - 10, 'large'),
        (500, SCREEN_HEIGHT - 10, 'medium'),
        (900, SCREEN_HEIGHT - 10, 'small'),
        (1200, SCREEN_HEIGHT - 10, 'large'),
        (1800, SCREEN_HEIGHT - 10, 'medium'),
        (2100, SCREEN_HEIGHT - 10, 'large'),
        (2500, SCREEN_HEIGHT - 10, 'medium'),
        (2900, SCREEN_HEIGHT - 10, 'small'),
        # Trees on platforms
        (320, 400, 'small'),
        (1050, 300, 'small'),
        (1450, 400, 'small'),
        (2250, 350, 'small'),
    ]

    for pos in tree_positions:
        tree = Tree(*pos)
        decorations.add(tree)
        all_sprites.add(tree)

    # Add bushes
    bush_positions = [
        (150, SCREEN_HEIGHT - 10, 'medium'),
        (300, SCREEN_HEIGHT - 10, 'small'),
        (700, SCREEN_HEIGHT - 10, 'large'),
        (1100, SCREEN_HEIGHT - 10, 'medium'),
        (1500, SCREEN_HEIGHT - 10, 'small'),
        (1900, SCREEN_HEIGHT - 10, 'large'),
        (2200, SCREEN_HEIGHT - 10, 'medium'),
        (2700, SCREEN_HEIGHT - 10, 'small'),
        # Bushes on platforms
        (380, 400, 'small'),
        (780, 350, 'small'),
        (1850, 300, 'small'),
        (2650, 300, 'small'),
    ]

    for pos in bush_positions:
        bush = Bush(*pos)
        decorations.add(bush)
        all_sprites.add(bush)

    # Create coins
    for _ in range(30):
        coin = Coin(random.randint(0, WORLD_WIDTH - COIN_SIZE),
                   random.randint(100, SCREEN_HEIGHT - 100))
        all_sprites.add(coin)
        coins.add(coin)

    # Create enemies
    enemy_positions = [
        (400, SCREEN_HEIGHT - ENEMY_HEIGHT - 10),
        (800, SCREEN_HEIGHT - ENEMY_HEIGHT - 10),
        (1200, SCREEN_HEIGHT - ENEMY_HEIGHT - 10),
        (1600, SCREEN_HEIGHT - ENEMY_HEIGHT - 10),
        (2000, SCREEN_HEIGHT - ENEMY_HEIGHT - 10),
        (2400, SCREEN_HEIGHT - ENEMY_HEIGHT - 10),
        (2800, SCREEN_HEIGHT - ENEMY_HEIGHT - 10),
    ]

    turtle_positions = [
        (350, 400 - ENEMY_HEIGHT),  # On a platform
        (750, 350 - ENEMY_HEIGHT),  # On a platform
        (1500, 400 - ENEMY_HEIGHT)  # On a platform
    ]

    # Add regular enemies
    for pos in enemy_positions:
        enemy = Enemy(*pos)
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Add turtles
    for pos in turtle_positions:
        turtle = Turtle(*pos)
        all_sprites.add(turtle)
        enemies.add(turtle)

    # Create boss at the end of the level
    boss = Boss(WORLD_WIDTH - 200, SCREEN_HEIGHT - 130)
    all_sprites.add(boss)
    boss_battle_active = False
    boss_battle_won = False

    # Game state
    game_over = False
    game_won = False
    font = pygame.font.Font(None, 36)

    # Game loop
    running = True
    last_time = pygame.time.get_ticks()
    dt = 1
    frame_count = 0
    fps_update_timer = 0
    current_fps = 60
    
    # Performance optimization
    boss_attack_particles = []  # For visual effects from boss
    last_sprite_update = 0
    low_fps_mode = False
    skip_frame = False

    while running:
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / (1000 / 60)
        dt = min(dt, 2.0)  # Cap delta time to prevent physics issues
        last_time = current_time
        
        # Calculate actual FPS
        frame_count += 1
        fps_update_timer += dt
        if fps_update_timer >= 60:  # Update FPS display once per second
            current_fps = frame_count
            frame_count = 0
            fps_update_timer = 0
            # Detect low FPS and enable optimization
            low_fps_mode = current_fps < 45
        
        # Skip every other frame during boss battles if FPS is low
        if boss_battle_active and low_fps_mode:
            skip_frame = not skip_frame
            if skip_frame and not game_over and not game_won:
                # Just handle minimum events to stay responsive
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if game_state == PLAYING:
                                if player.score > high_score:
                                    high_score = player.score
                                    save_high_score(high_score)
                                game_state = MENU
                            else:
                                running = False
                # Skip the rest of this frame
                clock.tick(60)
                continue

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == PLAYING:
                        # Save high score before going to menu
                        if player.score > high_score:
                            high_score = player.score
                            save_high_score(high_score)
                        game_state = MENU
                    else:
                        running = False
                elif game_state == MENU:
                    if event.key == pygame.K_RETURN:
                        game_state = PLAYING
                        # Reset everything for a fresh start
                        game_over, game_won = reset_game(
                            all_sprites, enemies, coins, powerups, ui_elements, 
                            life_icons, platforms, moving_platforms, player, camera, 
                            enemy_positions, turtle_positions, powerup_positions, fireballs, boss
                        )
                        # Reset boss battle flags
                        boss_battle_active = False
                        boss_battle_won = False
                        
                        # Ensure boss is completely reset
                        reset_boss(boss, all_sprites)
                elif game_state == PLAYING:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                        if game_over or game_won:
                            # Check for new high score
                            if player.score > high_score:
                                high_score = player.score
                                save_high_score(high_score)
                            # Reset game when space is pressed after game end
                            game_over, game_won = reset_game(
                                all_sprites, enemies, coins, powerups, ui_elements, 
                                life_icons, platforms, moving_platforms, player, camera, 
                                enemy_positions, turtle_positions, powerup_positions, fireballs, boss
                            )
                            # Reset boss battle flags
                            boss_battle_active = False
                            boss_battle_won = False
                            
                            # Ensure boss is completely reset
                            reset_boss(boss, all_sprites)
                        else:
                            player.jump()
                    elif event.key == pygame.K_r and (game_over or game_won):
                        # Check for new high score
                        if player.score > high_score:
                            high_score = player.score
                            save_high_score(high_score)
                        # Reset game when R is pressed after game end
                        game_over, game_won = reset_game(
                            all_sprites, enemies, coins, powerups, ui_elements, 
                            life_icons, platforms, moving_platforms, player, camera, 
                            enemy_positions, turtle_positions, powerup_positions, fireballs, boss
                        )
                        # Reset boss battle flags
                        boss_battle_active = False
                        boss_battle_won = False
                        
                        # Ensure boss is completely reset
                        reset_boss(boss, all_sprites)
                    elif event.key == pygame.K_f:
                        # Shoot fireball when F is pressed
                        if player.has_flower and not game_over and not game_won:
                            if player.shoot_fireball(fireballs):
                                # Add fireball to all sprites if successfully shot
                                for fireball in fireballs:
                                    if fireball not in all_sprites:
                                        all_sprites.add(fireball)

        # Menu state
        if game_state == MENU:
            draw_menu(screen, high_score)
            pygame.display.flip()
            clock.tick(60)
            continue

        # Game playing state
        if not game_over and not game_won:
            # Get keyboard state
            keys = pygame.key.get_pressed()
            
            # Player movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.move_right()

            # Update camera and background
            camera.update(player)
            background.update()
            
            # Update player
            player.update(WORLD_WIDTH)
            
            # Update moving platforms
            for platform in moving_platforms:
                platform.update()
            
            # Enemy behavior
            for enemy in enemies:
                enemy.detect_player(player, camera)
                enemy.check_platform_edge(platforms)
                
                # Check for movement range boundaries
                if hasattr(enemy, 'start_x') and hasattr(enemy, 'move_range'):
                    if enemy.rect.x > enemy.start_x + enemy.move_range or enemy.rect.x < enemy.start_x - enemy.move_range:
                        enemy.direction *= -1
            
            # Update other sprites
            for sprite in all_sprites:
                if sprite != player and sprite not in moving_platforms:
                    sprite.update()
                    
            # Check for player-enemy collisions
            enemy_collisions = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in enemy_collisions:
                # Use the handle_enemy_collision function to process the collision
                take_damage = handle_enemy_collision(player, enemy, enemies, all_sprites)
                
                if take_damage and not player.invincible:
                    # Player is hurt by the enemy
                    is_dead = player.take_damage()
                    if is_dead:
                        # Game over if player has no lives left
                        if player.score > high_score:
                            high_score = player.score
                            save_high_score(high_score)
                        game_over = True
                    else:
                        # Update life icons
                        if len(life_icons) > player.lives:
                            icon = life_icons.pop()
                            ui_elements.remove(icon)
                    
                    # Move player away slightly to prevent continuous collisions
                    if player.rect.centerx < enemy.rect.centerx:
                        player.rect.x -= 20
                    else:
                        player.rect.x += 20
                    player.rect.y -= 10
                    
            # Update fireballs and check collisions
            for fireball in fireballs.copy():
                # Check platform collisions for fireballs
                if not fireball.check_platform_collision(platforms):
                    # Remove fireball if it hit a platform and shouldn't continue
                    fireballs.remove(fireball)
                    all_sprites.remove(fireball)
                
                # Check if fireball is off screen
                if fireball.rect.x < -50 or fireball.rect.x > WORLD_WIDTH + 50 or fireball.rect.y > SCREEN_HEIGHT + 50:
                    fireballs.remove(fireball)
                    all_sprites.remove(fireball)
                    
                # Check for enemy collisions
                for enemy in enemies.copy():
                    if fireball.rect.colliderect(enemy.rect):
                        # Hit enemy with fireball
                        enemies.remove(enemy)
                        all_sprites.remove(enemy)
                        player.score += 15 * player.score_multiplier  # More points for fireball kill
                        
                        # Remove the fireball after hitting an enemy
                        fireballs.remove(fireball)
                        all_sprites.remove(fireball)
                        break
                    
            # Update power-ups and check platform collisions
            for powerup in powerups:
                powerup.check_platform_collision(platforms)

            # Moving platform logic - make the player move with platforms
            for platform in moving_platforms:
                if (player.rect.bottom == platform.rect.top or 
                    player.rect.bottom == platform.rect.top + 1) and \
                   player.rect.right > platform.rect.left and \
                   player.rect.left < platform.rect.right:
                    if platform.horizontal:
                        player.rect.x += platform.speed
                    else:
                        player.rect.y += platform.speed
                        player.velocity_y = platform.speed

            # Check for turtle shell collisions with other enemies
            for enemy in enemies:
                if isinstance(enemy, Turtle) and enemy.in_shell and enemy.shell_speed != 0:
                    for other_enemy in enemies:
                        if other_enemy != enemy and enemy.rect.colliderect(other_enemy.rect):
                            enemies.remove(other_enemy)
                            all_sprites.remove(other_enemy)
                            player.score += 10 * player.score_multiplier
                    
                    # Check if shell hits platforms on the sides
                    enemy.check_platform_collision(platforms)

            # Platform collision for player
            player_on_platform = False
            for platform in platforms:
                if player.rect.colliderect(platform.rect):
                    # Landing on top of platform
                    if player.velocity_y > 0 and player.rect.bottom < platform.rect.bottom + 10:
                        player.rect.bottom = platform.rect.top
                        player.velocity_y = 0
                        player.jumping = False
                        player.jumps_left = MAX_JUMPS
                        player.on_ground = True
                        player_on_platform = True
                    # Head collision with bottom of platform
                    elif player.velocity_y < 0 and player.rect.top < platform.rect.bottom and player.rect.top > platform.rect.top:
                        player.rect.top = platform.rect.bottom
                        player.velocity_y = 0
                    # Side collisions
                    elif player.rect.right > platform.rect.left and player.rect.left < platform.rect.left:
                        player.rect.right = platform.rect.left
                        player.velocity_x = 0
                    elif player.rect.left < platform.rect.right and player.rect.right > platform.rect.right:
                        player.rect.left = platform.rect.right
                        player.velocity_x = 0
            
            # If not on any platform and not jumping, ensure falling state is correct
            if not player_on_platform and not player.on_ground and player.velocity_y >= 0:
                player.jumping = True
                        
            # Platform collision for enemies
            for enemy in enemies:
                enemy.on_ground = False
                for platform in platforms:
                    if enemy.rect.colliderect(platform.rect):
                        if enemy.velocity_y > 0 and enemy.rect.bottom < platform.rect.bottom + 10:
                            enemy.rect.bottom = platform.rect.top
                            enemy.velocity_y = 0
                            enemy.on_ground = True
                            break
            
            # Check for spike collisions
            spike_collisions = pygame.sprite.spritecollide(player, obstacles, False)
            if spike_collisions:
                # If player has stars, don't get hurt by spikes
                if not player.has_star:
                    is_dead = player.take_damage()
                    if is_dead:
                        # Check for new high score
                        if player.score > high_score:
                            high_score = player.score
                            save_high_score(high_score)
                        game_over = True
                    else:
                        # Update life icons
                        if len(life_icons) > player.lives:
                            icon = life_icons.pop()
                            ui_elements.remove(icon)
                            
                    # Move player up to avoid being stuck in spikes
                    player.rect.y -= 50
            
            # Check for power-up collisions
            powerup_collisions = pygame.sprite.spritecollide(player, powerups, True)
            for powerup in powerup_collisions:
                player.collect_powerup(powerup.type)
                all_sprites.remove(powerup)
                
                # Update UI for lives if needed
                if powerup.type == "mushroom" and player.lives > len(life_icons):
                    icon = LifeIcon(SCREEN_WIDTH - 30 - (len(life_icons)) * 25, 10)
                    ui_elements.add(icon)
                    life_icons.append(icon)

            # Coin collection
            visible_coins = [coin for coin in coins if abs(coin.rect.x - player.rect.x) < SCREEN_WIDTH // 2]
            visible_coins_group = pygame.sprite.Group()
            visible_coins_group.add(visible_coins)
            coin_collisions = pygame.sprite.spritecollide(player, visible_coins_group, True)
            for coin in coin_collisions:
                coins.remove(coin)
                player.score += 1 * player.score_multiplier

            # Check if all coins are collected
            if len(coins) == 0:
                # Check for new high score
                if player.score > high_score:
                    high_score = player.score
                    save_high_score(high_score)
                    
                # Don't end game immediately if boss battle is available or active
                if boss_battle_won or (not boss_battle_active and player.rect.x < WORLD_WIDTH - 1000):
                    game_won = True
                
            # Check if player is near boss arena to activate boss
            if not boss_battle_active and not boss.active and player.rect.x > WORLD_WIDTH - BOSS_ACTIVATION_DISTANCE:
                boss.active = True
                boss_battle_active = True
                
                # Boss battle transition animation
                boss_transition_time = 3.0  # seconds
                frames = int(boss_transition_time * 60)  # at 60 fps
                
                # Create background for boss arena (darker and more dramatic)
                sky_color = (20, 20, 40)  # Darker blue
                ground_color = (60, 30, 30)  # Darker red/brown
                boss_arena_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # Lightning effect parameters
                lightning_flash = False
                lightning_alpha = 0
                lightning_timer = 0
                lightning_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                lightning_surf.fill((255, 255, 255))
                
                # Warning text flashing
                warning_text = "BOSS BATTLE"
                warning_font = pygame.font.Font(None, 72)
                warning_alpha = 0
                warning_direction = 1  # 1 = fade in, -1 = fade out
                
                # Boss silhouette
                boss_silhouette = pygame.Surface((BOSS_WIDTH * 2, BOSS_HEIGHT * 2), pygame.SRCALPHA)
                pygame.draw.rect(boss_silhouette, (200, 0, 0), boss_silhouette.get_rect(), 0)
                boss_silhouette.set_alpha(0)
                boss_silhouette_alpha = 0
                boss_silhouette_pos = [SCREEN_WIDTH // 2 - boss_silhouette.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 - boss_silhouette.get_height() // 2]
                
                # Transition animation loop
                for frame in range(frames):
                    # Calculate progress (0.0 to 1.0)
                    progress = frame / frames
                    
                    # Handle events during animation
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            # Skip animation on keypress
                            frame = frames - 1
                            progress = 1.0
                    
                    # Fill with background color that gradually changes
                    current_sky_color = [
                        int(BLACK[0] + (sky_color[0] - BLACK[0]) * progress),
                        int(BLACK[1] + (sky_color[1] - BLACK[1]) * progress),
                        int(BLACK[2] + (sky_color[2] - BLACK[2]) * progress),
                    ]
                    boss_arena_bg.fill(current_sky_color)
                    
                    # Draw ground
                    ground_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
                    pygame.draw.rect(boss_arena_bg, ground_color, ground_rect)
                    
                    # Draw decorative elements
                    for i in range(5):
                        # Jagged mountains in background
                        points = [
                            (SCREEN_WIDTH * i // 5, SCREEN_HEIGHT - 60),
                            (SCREEN_WIDTH * i // 5 + SCREEN_WIDTH // 10, SCREEN_HEIGHT - 120 - random.randint(0, 50)),
                            (SCREEN_WIDTH * (i+1) // 5, SCREEN_HEIGHT - 60)
                        ]
                        pygame.draw.polygon(boss_arena_bg, (40, 20, 20), points)
                        
                    # Draw lightning effect (randomly)
                    if progress > 0.3:
                        lightning_timer += 1
                        if lightning_timer % 20 == 0 or (progress > 0.8 and lightning_timer % 10 == 0):
                            lightning_flash = True
                            lightning_alpha = random.randint(100, 200)
                            
                        if lightning_flash:
                            lightning_alpha -= 10
                            if lightning_alpha <= 0:
                                lightning_flash = False
                                lightning_alpha = 0
                            else:
                                lightning_surf.set_alpha(lightning_alpha)
                                boss_arena_bg.blit(lightning_surf, (0, 0), special_flags=pygame.BLEND_ADD)
                    
                    # Update warning text
                    if progress > 0.4:
                        warning_alpha += warning_direction * 8
                        if warning_alpha >= 255:
                            warning_alpha = 255
                            warning_direction = -1
                        elif warning_alpha <= 0:
                            warning_alpha = 0
                            warning_direction = 1
                            
                        warning_text_surf = warning_font.render(warning_text, True, RED)
                        warning_text_surf.set_alpha(warning_alpha)
                        warning_rect = warning_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
                        boss_arena_bg.blit(warning_text_surf, warning_rect)
                        
                        # Draw subtitle
                        if frame % 30 < 15:  # Blinking
                            subtitle_text = "PREPARE FOR BATTLE!"
                            subtitle_font = pygame.font.Font(None, 36)
                            subtitle_surf = subtitle_font.render(subtitle_text, True, YELLOW)
                            subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50))
                            boss_arena_bg.blit(subtitle_surf, subtitle_rect)
                    
                    # Update boss silhouette
                    if progress > 0.6:
                        # Make silhouette appear
                        boss_silhouette_alpha = min(boss_silhouette_alpha + 5, 200)
                        boss_silhouette.set_alpha(boss_silhouette_alpha)
                        
                        # Add eye glow
                        if progress > 0.8:
                            eye_radius = int(5 + 5 * math.sin(frame / 10))
                            eye_color = (255, 0, 0)
                            pygame.draw.circle(boss_silhouette, eye_color, 
                                               (boss_silhouette.get_width() // 3, boss_silhouette.get_height() // 3), 
                                               eye_radius)
                            pygame.draw.circle(boss_silhouette, eye_color, 
                                               (boss_silhouette.get_width() * 2 // 3, boss_silhouette.get_height() // 3), 
                                               eye_radius)
                        
                        # Draw silhouette with slight movement
                        shake_x = random.randint(-2, 2) if progress > 0.8 else 0
                        shake_y = random.randint(-2, 2) if progress > 0.8 else 0
                        boss_arena_bg.blit(boss_silhouette, 
                                           (boss_silhouette_pos[0] + shake_x, 
                                            boss_silhouette_pos[1] + shake_y))
                    
                    # Draw screen shake in later part of animation
                    screen_shake = 0
                    if progress > 0.85:
                        screen_shake = random.randint(-4, 4)
                    
                    # Draw to screen
                    screen.blit(boss_arena_bg, (screen_shake, screen_shake))
                    
                    # Update display and control framerate
                    pygame.display.flip()
                    clock.tick(60)
                
                # Final dramatic flash
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255))
                
                for alpha in range(255, 0, -15):
                    # Draw normal game screen
                    screen.fill(BLACK)
                    background.draw(screen, camera)
                    
                    for sprite in all_sprites:
                        screen.blit(sprite.image, camera.apply(sprite))
                        
                    # Flash overlay
                    flash_surf.set_alpha(alpha)
                    screen.blit(flash_surf, (0, 0))
                    
                    # Update display
                    pygame.display.flip()
                    clock.tick(60)
                
                # Show boss health bar
                boss.draw_health_bar(screen)
                pygame.display.flip()
                
                # Brief moment to prepare
                pygame.time.delay(500)

            # Handle boss battle
            if boss_battle_active:
                # Update boss with player position for targeting
                boss.update(player, platforms)
                
                # Only draw health bar if boss is active
                if boss.active:
                    boss.draw_health_bar(screen)
                
                # Don't update all projectiles every frame in low FPS mode
                if low_fps_mode:
                    # Only process projectiles close to the player for collisions
                    collision_distance = 100
                    nearby_projectiles = pygame.sprite.Group()
                    
                    for projectile in boss.projectiles:
                        if (abs(projectile.rect.centerx - player.rect.centerx) < collision_distance and 
                            abs(projectile.rect.centery - player.rect.centery) < collision_distance):
                            nearby_projectiles.add(projectile)
                    
                    # Check for player collision only with nearby projectiles
                    projectile_hits = pygame.sprite.spritecollide(player, nearby_projectiles, True)
                else:
                    # Normal processing at good frame rates
                    # Add new projectiles to all_sprites when needed
                    for projectile in boss.projectiles:
                        if projectile not in all_sprites:
                            all_sprites.add(projectile)
                    
                    # Check for player collision with boss projectiles
                    projectile_hits = pygame.sprite.spritecollide(player, boss.projectiles, True)
                
                # Handle projectile hits
                if projectile_hits and not player.invincible:
                    # Player takes damage from projectiles
                    is_dead = player.take_damage()
                    if is_dead:
                        if player.score > high_score:
                            high_score = player.score
                            save_high_score(high_score)
                        game_over = True
                    else:
                        # Update life icons
                        if len(life_icons) > player.lives:
                            icon = life_icons.pop()
                            ui_elements.remove(icon)
                
                # Check for fireball hits on boss at reduced frequency in low FPS mode
                if player.has_flower:
                    perform_check = True
                    if low_fps_mode:
                        # Only check every other frame in low FPS mode
                        perform_check = (frame_count % 2 == 0)
                        
                    if perform_check:
                        fireball_hits = pygame.sprite.spritecollide(boss, fireballs, True)
                        for fireball in fireball_hits:
                            all_sprites.remove(fireball)
                            boss.take_damage()
                            # Add points for hitting boss
                            player.score += 25 * player.score_multiplier
                
                # Check for player jump on boss's head (classic stomp)
                if (player.rect.bottom <= boss.rect.top + 20 and 
                    player.rect.bottom >= boss.rect.top - 10 and 
                    player.velocity_y > 0 and 
                    player.rect.right > boss.rect.left + 20 and 
                    player.rect.left < boss.rect.right - 20):
                    
                    boss.take_damage()
                    player.velocity_y = -10  # Bounce up
                    player.score += 50 * player.score_multiplier
                
                # Check for boss charge attack hit on player
                if (boss.current_attack == "charge" and 
                    pygame.sprite.collide_rect(player, boss) and 
                    not player.invincible):
                    
                    is_dead = player.take_damage()
                    if is_dead:
                        if player.score > high_score:
                            high_score = player.score
                            save_high_score(high_score)
                        game_over = True
                    else:
                        # Update life icons
                        if len(life_icons) > player.lives:
                            icon = life_icons.pop()
                            ui_elements.remove(icon)
                
                # Check if boss is defeated
                if boss.defeated and not boss_battle_won:
                    # Victory animation
                    boss_battle_won = True
                    
                    # Play victory fanfare sound if available
                    try:
                        victory_sound = pygame.mixer.Sound("assets/victory.wav")
                        victory_sound.set_volume(0.7)
                        victory_sound.play()
                    except:
                        # If sound file doesn't exist, create a simple victory beep sequence
                        try:
                            # Simple victory jingle using pygame's builtin sounds
                            beep_1 = pygame.mixer.Sound(pygame.sndarray.make_sound(
                                pygame.sndarray.array(pygame.Surface((4, 4)))))
                            beep_1.set_volume(0.2)
                            beep_2 = pygame.mixer.Sound(pygame.sndarray.make_sound(
                                pygame.sndarray.array(pygame.Surface((8, 8)))))
                            beep_2.set_volume(0.2)
                            beep_3 = pygame.mixer.Sound(pygame.sndarray.make_sound(
                                pygame.sndarray.array(pygame.Surface((16, 16)))))
                            beep_3.set_volume(0.2)
                            
                            # Play a sequence of beeps
                            beep_1.play()
                            pygame.time.delay(200)
                            beep_2.play()
                            pygame.time.delay(200)
                            beep_3.play()
                        except:
                            # If all fails, silently continue
                            pass
                    
                    # Create victory particles
                    victory_particles = []
                    for _ in range(100):
                        # Particles explode from boss position
                        particle = {
                            'x': boss.rect.centerx + random.randint(-50, 50),
                            'y': boss.rect.centery + random.randint(-50, 50),
                            'dx': random.uniform(-3, 3),
                            'dy': random.uniform(-5, -1),  # Mostly upward
                            'color': random.choice([GOLD, YELLOW, WHITE, ORANGE]),
                            'size': random.randint(3, 8),
                            'life': random.randint(30, 120)
                        }
                        victory_particles.append(particle)
                    
                    # Create flash effect
                    flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    flash_surf.fill((255, 255, 255, 180))  # White with some transparency
                    
                    # Animation loop
                    animation_frames = 120  # 2 seconds at 60fps
                    victory_text = "BOSS DEFEATED!"
                    for frame in range(animation_frames):
                        # Handle events during animation to keep game responsive
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                break
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    running = False
                                    break
                                # Skip animation with any key
                                animation_frames = frame + 1
                                
                        # Draw the background scene
                        screen.fill(BLACK)
                        background.draw(screen, camera)
                        
                        # Draw core game elements
                        for sprite in decorations:
                            screen.blit(sprite.image, camera.apply(sprite))
                        for sprite in platforms:
                            screen.blit(sprite.image, camera.apply(sprite))
                        for sprite in all_sprites:
                            if sprite != boss and sprite not in boss.projectiles:
                                screen.blit(sprite.image, camera.apply(sprite))
                        
                        # Draw boss (defeated pose)
                        boss.image = boss.hurt_frame
                        screen.blit(boss.image, camera.apply(boss))
                        
                        # Flash effect fades out
                        if frame < 20:
                            flash_alpha = max(0, 180 - (frame * 9))
                            flash_surf.set_alpha(flash_alpha)
                            screen.blit(flash_surf, (0, 0))
                        
                        # Update and draw particles
                        for particle in victory_particles[:]:
                            # Move particle
                            particle['x'] += particle['dx']
                            particle['y'] += particle['dy']
                            particle['dy'] += 0.1  # Gravity
                            
                            # Fade out particle
                            particle['life'] -= 1
                            if particle['life'] <= 0:
                                victory_particles.remove(particle)
                                continue
                            
                            # Draw particle
                            alpha = min(255, particle['life'] * 3)
                            pygame.draw.circle(
                                screen, 
                                particle['color'], 
                                (int(particle['x'] - camera.scroll_x), int(particle['y'])), 
                                particle['size']
                            )
                        
                        # Draw victory text with animation
                        if frame > 30:
                            text_size = min(72, (frame - 30) * 2)  # Grows to full size
                            if text_size > 0:
                                text_alpha = min(255, (frame - 30) * 8)
                                font = pygame.font.Font(None, text_size)
                                text_surf = font.render(victory_text, True, GOLD)
                                text_surf.set_alpha(text_alpha)
                                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
                                
                                # Add pulsing effect
                                if frame > 60:
                                    scale = 1.0 + 0.05 * abs(math.sin((frame - 60) / 10))
                                    scaled_size = (int(text_surf.get_width() * scale), int(text_surf.get_height() * scale))
                                    text_surf = pygame.transform.scale(text_surf, scaled_size)
                                    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
                                
                                screen.blit(text_surf, text_rect)
                        
                        # Draw "big bonus" text
                        if frame > 60:
                            bonus_text = f"+1000 POINTS!"
                            bonus_alpha = min(255, (frame - 60) * 12)
                            bonus_font = pygame.font.Font(None, 48)
                            bonus_surf = bonus_font.render(bonus_text, True, WHITE)
                            bonus_surf.set_alpha(bonus_alpha)
                            bonus_rect = bonus_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                            screen.blit(bonus_surf, bonus_rect)
                            
                            # Draw continue prompt
                            if frame > 90:
                                continue_alpha = min(255, (frame - 90) * 15)
                                continue_font = pygame.font.Font(None, 30)
                                continue_surf = continue_font.render("Press any key to continue", True, WHITE)
                                continue_surf.set_alpha(continue_alpha)
                                continue_rect = continue_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
                                screen.blit(continue_surf, continue_rect)
                        
                        # Update display
                        pygame.display.flip()
                        clock.tick(60)
                    
                    # After animation, add score bonus
                    player.score += 1000

        # Draw
        screen.fill(BLACK)
        
        # Draw background with camera offset
        background.draw(screen, camera)
        
        # Draw decorations
        for sprite in decorations:
            # Skip rendering decorations far from the camera view in low FPS mode during boss battles
            if low_fps_mode and boss_battle_active:
                if not (-100 < camera.apply(sprite).x < SCREEN_WIDTH + 100):
                    continue
            screen.blit(sprite.image, camera.apply(sprite))
        
        # For performance, collect sprites to render to avoid multiple render passes
        sprites_to_render = []
        
        # Only render sprites that are in or near the viewport
        viewport_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Draw platforms and other sprites
        for sprite in all_sprites:
            if sprite in decorations:
                continue  # Already rendered
                
            # Get screen position
            screen_pos = camera.apply(sprite)
            
            # In low FPS mode during boss battle, skip sprites far from the viewport
            if low_fps_mode and boss_battle_active:
                # Expand viewport for checking
                expanded_viewport = viewport_rect.inflate(200, 200)
                if not expanded_viewport.collidepoint(screen_pos.x + sprite.rect.width/2, screen_pos.y + sprite.rect.height/2):
                    # Skip rendering this sprite
                    continue
            
            # Prioritize player, boss, and important elements
            if sprite == player or sprite == boss or (boss_battle_active and sprite in boss.projectiles):
                # These are always rendered
                sprites_to_render.append((sprite, screen_pos))
            elif isinstance(sprite, Platform):
                # Platforms are important for gameplay
                sprites_to_render.append((sprite, screen_pos))
            else:
                # Other sprites
                sprites_to_render.append((sprite, screen_pos))
                
        # Render the collected sprites
        for sprite, pos in sprites_to_render:
            screen.blit(sprite.image, pos)

        # Draw UI elements - always render these as they're critical
        for ui_element in ui_elements:
            screen.blit(ui_element.image, ui_element.rect)

        # Draw score, jumps, and other UI elements
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        high_score_text = font.render(f'High: {high_score}', True, GOLD)
        jumps_text = font.render(f'Jumps: {player.jumps_left}', True, WHITE)
        fps_text = font.render(f'FPS: {current_fps}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))
        screen.blit(jumps_text, (10, 70))
        screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
        
        # Draw active power-ups
        if player.score_multiplier > 1:
            multiplier_text = font.render(f'x{player.score_multiplier}', True, ORANGE)
            screen.blit(multiplier_text, (170, 10))
        
        if player.has_star:
            star_text = font.render('★', True, GOLD)
            screen.blit(star_text, (210, 10))
            
        if player.has_flower:
            flower_text = font.render('❀', True, GREEN)
            screen.blit(flower_text, (240, 10))
            
            # Show fireball instruction
            if not game_over and not game_won and not low_fps_mode:  # Skip in low FPS mode
                fire_text = font.render('Press F to shoot fireballs', True, GREEN)
                screen.blit(fire_text, (10, SCREEN_HEIGHT - 30))

        # Game over or win message
        if game_over:
            message = font.render('Game Over! Press R to restart', True, RED)
            screen.blit(message, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            
            # Show high score info
            if player.score >= high_score:
                high_score_msg = font.render('NEW HIGH SCORE!', True, GOLD)
                screen.blit(high_score_msg, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40))
                
            esc_text = font.render('Press ESC for main menu', True, WHITE)
            screen.blit(esc_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 40))
            
        elif game_won:
            # Special winning animation
            win_text_pulse = math.sin(pygame.time.get_ticks() / 200) * 0.1 + 1.0
            win_text_size = int(48 * win_text_pulse)
            
            # Calculate color based on time
            hue = (pygame.time.get_ticks() / 50) % 360  # Rotating hue
            # Convert HSV to RGB
            h = hue / 60
            i = int(h)
            f = h - i
            p = 0
            q = 255 * (1 - f)
            t = 255 * f
            
            # Cycling rainbow colors
            if i == 0:
                win_color = (255, t, p)
            elif i == 1:
                win_color = (q, 255, p)
            elif i == 2:
                win_color = (p, 255, t)
            elif i == 3:
                win_color = (p, q, 255)
            elif i == 4:
                win_color = (t, p, 255)
            else:
                win_color = (255, p, q)
            
            # Draw win message with rainbow effect
            win_font = pygame.font.Font(None, win_text_size)
            win_message = win_font.render('YOU WIN!', True, win_color)
            win_rect = win_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(win_message, win_rect)
            
            # Show info about how to restart
            restart_font = pygame.font.Font(None, 36)
            restart_message = restart_font.render('Press R to play again', True, WHITE)
            restart_rect = restart_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_message, restart_rect)
            
            # Draw stats summary
            stats_font = pygame.font.Font(None, 28)
            stats_y = SCREEN_HEIGHT // 2 + 50
            
            score_text = stats_font.render(f'Final Score: {player.score}', True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
            screen.blit(score_text, score_rect)
            
            # Show high score info with animation
            if player.score >= high_score:
                high_pulse = abs(math.sin(pygame.time.get_ticks() / 300))
                high_score_color = (
                    int(255 * high_pulse + 100),
                    int(215 * high_pulse + 40),
                    0
                )
                high_score_msg = stats_font.render('NEW HIGH SCORE!', True, high_score_color)
                high_score_rect = high_score_msg.get_rect(center=(SCREEN_WIDTH // 2, stats_y + 30))
                screen.blit(high_score_msg, high_score_rect)
            else:
                high_score_msg = stats_font.render(f'High Score: {high_score}', True, GOLD)
                high_score_rect = high_score_msg.get_rect(center=(SCREEN_WIDTH // 2, stats_y + 30))
                screen.blit(high_score_msg, high_score_rect)
                
            # Show boss defeated message if applicable
            if boss_battle_won:
                boss_text = stats_font.render('★ BOSS DEFEATED ★', True, GOLD)
                boss_rect = boss_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y + 60))
                screen.blit(boss_text, boss_rect)
                
            # Instruction to return to menu
            esc_text = stats_font.render('Press ESC for main menu', True, WHITE)
            esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(esc_text, esc_rect)
            
            # Draw animated stars around the screen
            if 'win_stars' not in globals():
                # Create star positions first time
                global win_stars
                win_stars = []
                for _ in range(20):
                    star = {
                        'x': random.randint(0, SCREEN_WIDTH),
                        'y': random.randint(0, SCREEN_HEIGHT),
                        'size': random.randint(2, 6),
                        'speed': random.uniform(0.5, 2.0)
                    }
                    win_stars.append(star)
                    
            # Update and draw stars
            for star in win_stars:
                # Move star
                star['y'] += star['speed']
                if star['y'] > SCREEN_HEIGHT:
                    star['y'] = 0
                    star['x'] = random.randint(0, SCREEN_WIDTH)
                
                # Draw star
                pygame.draw.circle(screen, GOLD, (int(star['x']), int(star['y'])), star['size'])
                
                # Draw tail
                pygame.draw.line(
                    screen, 
                    GOLD, 
                    (int(star['x']), int(star['y'])), 
                    (int(star['x']), int(star['y'] - star['size'] * 3)),
                    1
                )

        pygame.display.flip()
        clock.tick(60)

    # Quit game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 