#!/usr/bin/env python3
import pygame
import sys
import random
import os

# Import from modular files
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, 
    BLACK, WHITE, RED, YELLOW, GOLD, ORANGE, GREEN,
    COIN_SIZE, ENEMY_WIDTH, ENEMY_HEIGHT, SPIKE_HEIGHT,
    MAX_JUMPS, MAX_LIVES
)
from src.player import Player
from src.camera import Camera
from src.coin import Coin
from src.enemy import Enemy
from src.turtle import Turtle
from src.platform import Platform, MovingPlatform
from src.background import Background, Tree, Bush, Cloud
from src.spike import Spike
from src.powerup import PowerUp, LifeIcon
from src.game import handle_enemy_collision, reset_game
from src.fireball import Fireball

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

    # Game state
    game_over = False
    game_won = False
    font = pygame.font.Font(None, 36)

    # Game loop
    running = True
    last_time = pygame.time.get_ticks()
    dt = 1

    while running:
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / (1000 / 60)
        dt = min(dt, 2.0)
        last_time = current_time

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
                            enemy_positions, turtle_positions, powerup_positions, fireballs
                        )
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
                                enemy_positions, turtle_positions, powerup_positions, fireballs
                            )
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
                            enemy_positions, turtle_positions, powerup_positions, fireballs
                        )
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
                game_won = True

            # Enemy collision
            if not player.invincible:
                visible_enemies = [enemy for enemy in enemies if abs(enemy.rect.x - player.rect.x) < SCREEN_WIDTH // 2]
                visible_enemies_group = pygame.sprite.Group()
                visible_enemies_group.add(visible_enemies)
                enemy_collisions = pygame.sprite.spritecollide(player, visible_enemies_group, False)
                
                for enemy in enemy_collisions:
                    collision_result = handle_enemy_collision(player, enemy, enemies, all_sprites)
                    if collision_result:
                        # Player was hurt
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
                        # Move player up slightly to avoid being stuck in enemy
                        player.rect.y -= 50
                        break
            elif player.has_star:
                # If player has star power, defeat any enemies on contact
                visible_enemies = [enemy for enemy in enemies if abs(enemy.rect.x - player.rect.x) < SCREEN_WIDTH // 2]
                enemy_collisions = pygame.sprite.spritecollide(player, visible_enemies, False)
                for enemy in enemy_collisions:
                    enemies.remove(enemy)
                    all_sprites.remove(enemy)
                    player.score += 10 * player.score_multiplier

        # Draw
        screen.fill(BLACK)
        
        # Draw background with camera offset
        background.draw(screen, camera)
        
        # Draw decorations
        for sprite in decorations:
            screen.blit(sprite.image, camera.apply(sprite))
        
        # Draw platforms and other sprites
        for sprite in all_sprites:
            if sprite not in decorations:
                screen.blit(sprite.image, camera.apply(sprite))

        # Draw UI elements
        for ui_element in ui_elements:
            screen.blit(ui_element.image, ui_element.rect)

        # Draw score, jumps, and other UI elements
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        high_score_text = font.render(f'High: {high_score}', True, GOLD)
        jumps_text = font.render(f'Jumps: {player.jumps_left}', True, WHITE)
        fps_text = font.render(f'FPS: {int(clock.get_fps())}', True, WHITE)
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
            if not game_over and not game_won:
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
            message = font.render('You Win! Press R to play again', True, YELLOW)
            screen.blit(message, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            
            # Show high score info
            if player.score >= high_score:
                high_score_msg = font.render('NEW HIGH SCORE!', True, GOLD)
                screen.blit(high_score_msg, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40))
                
            esc_text = font.render('Press ESC for main menu', True, WHITE)
            screen.blit(esc_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(60)

    # Quit game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 