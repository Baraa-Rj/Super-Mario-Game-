import pygame
import random
import sys
import os

# Add the parent directory to path so we can import modules when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.player import Player
from src.enemy import Enemy
from src.turtle import Turtle
from src.coin import Coin
from src.platform import Platform, MovingPlatform
from src.spike import Spike
from src.background import Tree, Bush, Cloud, Background
from src.powerup import PowerUp, LifeIcon
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, MAX_LIVES

def handle_enemy_collision(player, enemy, enemies, all_sprites):
    """Handle collision between player and enemy"""
    # If player has star power, enemies can't hurt them
    if player.has_star:
        enemies.remove(enemy)
        all_sprites.remove(enemy)
        player.score += 10 * player.score_multiplier
        return False  # No damage to player
        
    # Check if player is above the enemy and falling (stomping)
    if player.rect.bottom < enemy.rect.centery and player.velocity_y > 0:
        # For regular enemies
        if not isinstance(enemy, Turtle):
            # Kill enemy
            enemies.remove(enemy)
            all_sprites.remove(enemy)
            player.score += 5 * player.score_multiplier  # Apply score multiplier
            player.velocity_y = -10  # Bounce after killing enemy
            player.jumps_left = player.max_jumps  # Reset jumps after killing enemy
            return False  # Not game over
        else:
            # For turtles, handle shell state
            if not enemy.in_shell:
                # First jump puts turtle in shell
                enemy.enter_shell()
                player.score += 2 * player.score_multiplier  # Apply score multiplier
                player.velocity_y = -10  # Bounce
                player.jumps_left = player.max_jumps  # Reset jumps
                return False  # Not game over
            else:
                # If already in shell and player jumps on it again, kick it
                direction = 1 if player.rect.centerx > enemy.rect.centerx else -1
                enemy.kick_shell(direction)
                player.score += 1 * player.score_multiplier  # Apply score multiplier
                player.velocity_y = -10  # Bounce after kicking
                player.jumps_left = player.max_jumps  # Reset jumps
                return False  # Not game over
    elif isinstance(enemy, Turtle) and enemy.in_shell:
        # For side collisions with shells
        if enemy.shell_speed == 0:
            # Kick stationary shell if approached from the side
            direction = 1 if player.rect.centerx < enemy.rect.centerx else -1
            enemy.kick_shell(direction)
            return False  # Not game over
        else:
            # If shell is already moving fast, it hurts the player
            return True  # Return true to indicate damage
    else:
        # Player is hurt by enemy (not a turtle shell)
        if not isinstance(enemy, Turtle) or not enemy.in_shell:
            return True  # Return true to indicate damage
        return False  # Not game over if it's a turtle in shell state

def reset_boss(boss, all_sprites):
    """Completely reset a boss to initial state"""
    if not boss:
        return
        
    # Position
    boss.rect.x = WORLD_WIDTH - 200
    boss.rect.y = SCREEN_HEIGHT - 130
    
    # Health and state
    boss.health = boss.max_health
    boss.active = False
    boss.defeated = False
    boss.phase = 1
    boss.rage_mode = False
    boss.rage_timer = 0
    
    # Movement
    boss.velocity_x = 0
    boss.velocity_y = 0
    boss.direction = -1
    boss.speed = 3.0  # Reset to base speed
    
    # Attack state
    boss.attacking = False
    boss.attack_timer = 0
    boss.attack_cooldown = 90
    boss.stomped = False
    boss.stomp_timer = 0
    boss.invulnerable = False
    boss.invulnerable_timer = 0
    boss.current_attack = "none"
    boss.current_pattern_index = 0
    
    # Visual effects
    boss.flash_timer = 0
    boss.shake_offset = [0, 0]
    
    # Reset animation
    boss.animation_index = 0
    boss.animation_timer = 0
    boss.image = boss.idle_frames[0]
    
    # Clear projectiles
    for projectile in boss.projectiles:
        if projectile in all_sprites:
            all_sprites.remove(projectile)
    boss.projectiles.empty()

def reset_game(all_sprites, enemies, coins, powerups, ui_elements, life_icons, platforms, moving_platforms,
               player, camera, enemy_positions, turtle_positions, powerup_positions, fireballs, boss=None):
    """Reset the game state"""
    # Remove sound imports
    # Import sound objects inside function to ensure we get current values
    # from src.audio import jump_sound, coin_sound, powerup_sound, damage_sound, game_over_sound, star_sound
    
    # Reset player
    player.rect.x = 100
    player.rect.y = SCREEN_HEIGHT - player.rect.height - 10
    player.velocity_y = 0
    player.velocity_x = 0
    player.score = 0
    player.jumps_left = player.max_jumps
    player.image = player.idle_frame_right
    player.facing_right = True
    player.lives = MAX_LIVES
    player.has_star = False
    player.star_timer = 0
    player.has_flower = False
    player.flower_timer = 0
    player.has_mushroom = False
    player.fireball_cooldown = 0
    player.invincible = False
    player.invincibility_timer = 0
    player.score_multiplier = 1
    player.multiplier_timer = 0
    player.image.set_alpha(255)  # Reset transparency
    
    # Reset player color to normal
    player.update_color(player.normal_color)
    
    # Reset camera
    camera.scroll_x = 0
    
    # Reset moving platforms to original positions
    for platform in moving_platforms:
        platform.rect.x = platform.start_x
        platform.rect.y = platform.start_y
        platform.speed = abs(platform.speed)  # Reset to original direction
    
    # Reset shrinking and falling platforms
    for platform in platforms:
        if hasattr(platform, 'reset'):
            platform.reset()
    
    # Recreate coins if needed
    if len(coins) == 0:
        for _ in range(30):
            coin = Coin(random.randint(0, camera.width - 20), random.randint(100, SCREEN_HEIGHT - 100))
            all_sprites.add(coin)
            coins.add(coin)
    
    # Clear and recreate all enemies
    for enemy in enemies:
        all_sprites.remove(enemy)
    enemies.empty()
    
    # Add regular enemies
    for pos in enemy_positions:
        enemy = Enemy(*pos)
        enemy.spotted_player = False
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    # Add turtles
    for pos in turtle_positions:
        turtle = Turtle(*pos)
        turtle.spotted_player = False
        all_sprites.add(turtle)
        enemies.add(turtle)
        
    # Reset power-ups
    for powerup in powerups:
        all_sprites.remove(powerup)
    powerups.empty()
    
    # Add power-ups back
    for pos in powerup_positions:
        powerup = PowerUp(*pos)
        all_sprites.add(powerup)
        powerups.add(powerup)
    
    # Clear fireballs
    if fireballs:
        for fireball in fireballs:
            all_sprites.remove(fireball)
        fireballs.empty()
        
    # Reset boss if present
    if boss:
        reset_boss(boss, all_sprites)
        
    # Reset UI elements (life icons)
    for icon in ui_elements:
        ui_elements.remove(icon)
    ui_elements.empty()
    life_icons.clear()
    
    # Create life icons again
    for i in range(MAX_LIVES):
        icon = LifeIcon(SCREEN_WIDTH - 30 - i * 25, 10)
        ui_elements.add(icon)
        life_icons.append(icon)
    
    # Reset music to main theme - remove this
    # if main_theme:
    #     play_music(main_theme)
    
    return False, False  # game_over, game_won

# Add a simple test function that runs if this file is executed directly
if __name__ == "__main__":
    print("Game module imported successfully!")
    print("This file contains game utility functions and should not be run directly.")
    print("Run main.py to start the game.") 