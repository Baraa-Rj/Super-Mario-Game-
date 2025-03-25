import pygame
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
COIN_SIZE = 20
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
GRAVITY = 0.6  # Reduced for smoother falling
JUMP_FORCE = -13  # Adjusted for smoother jumps
PLAYER_SPEED = 7  # Slightly reduced for more challenge
PLAYER_ACCELERATION = 1.0  # Reduced for more challenge
PLAYER_DECELERATION = 0.9  # Adjusted for more responsiveness but more challenge
ENEMY_SPEED = 2.0  # Increased for more challenge
ENEMY_SIZE = 40
MAX_JUMPS = 1  # Reduced to single jump for more challenge
SPIKE_WIDTH = 30
SPIKE_HEIGHT = 20
MOVING_PLATFORM_SPEED = 1.5  # Increased for more challenge
CAMERA_SMOOTH_FACTOR = 0.1  # New constant for camera smoothing
POWERUP_SIZE = 30
MAX_LIVES = 2  # Reduced lives for more challenge
INVINCIBILITY_DURATION = 90  # Reduced invincibility duration
STAR_DURATION = 300  # Reduced star power duration (5 seconds at 60fps)
SCORE_MULTIPLIER_DURATION = 200  # Reduced score multiplier duration

# Boss constants
BOSS_WIDTH = 80
BOSS_HEIGHT = 100
BOSS_HEALTH = 6   # Reduced from 10 for easier battles
BOSS_ACTIVATION_DISTANCE = 800  # Distance at which boss activates

# Shrinking platform constants
SHRINK_DELAY = 60  # Frames before platform starts shrinking
SHRINK_SPEED = 2   # Pixels to shrink per frame
MIN_PLATFORM_WIDTH = 20  # Minimum width before platform is removed

# World dimensions (larger than screen)
WORLD_WIDTH = 3000  # Extended world width
SCROLL_THRESHOLD = 400  # Start scrolling when player reaches this x position

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

# Create assets directory if it doesn't exist
assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
os.makedirs(assets_dir, exist_ok=True)

# Load images or create placeholders
def load_image(name, width, height, color=None):
    try:
        image_path = os.path.join(assets_dir, name)
        if os.path.exists(image_path):
            img = pygame.image.load(image_path)
            return pygame.transform.scale(img, (width, height))
    except:
        pass

    # Create a placeholder with more detailed character if image doesn't exist
    img = pygame.Surface((width, height), pygame.SRCALPHA)
    
    if name.startswith("boss"):
        # Draw a more savage-looking boss
        # Base body (dark red)
        dark_red = (180, 0, 0)
        pygame.draw.rect(img, dark_red, (width//6, height//6, width*2//3, height*2//3))
        
        # Spiky outline
        for i in range(8):  # Add spikes around the body
            spike_angle = i * 45  # degrees (8 spikes around)
            spike_length = width//3
            center_x, center_y = width//2, height//2
            end_x = center_x + int(spike_length * pygame.math.Vector2(1, 0).rotate(spike_angle)[0])
            end_y = center_y + int(spike_length * pygame.math.Vector2(1, 0).rotate(spike_angle)[1])
            pygame.draw.line(img, (255, 0, 0), (center_x, center_y), (end_x, end_y), width//10)
        
        # Menacing face
        if name.startswith("boss_attack"):
            # Angry attacking eyes (jagged)
            eye_color = (255, 255, 0)  # Yellow
            pygame.draw.polygon(img, eye_color, [(width//3, height//3), 
                                             (width//2, height//4), 
                                             (width*2//3, height//3)])
            pygame.draw.polygon(img, eye_color, [(width//3, height//2), 
                                             (width//2, height*3//5), 
                                             (width*2//3, height//2)])
            
            # Open mouth with teeth
            pygame.draw.rect(img, (0, 0, 0), (width//4, height*2//3, width//2, height//5))
            # Teeth
            for i in range(4):
                tooth_x = width//4 + i * width//8
                pygame.draw.polygon(img, WHITE, [(tooth_x, height*2//3), 
                                              (tooth_x + width//16, height*2//3), 
                                              (tooth_x + width//32, height*2//3 + height//10)])
        else:
            # Default face (less aggressive but still menacing)
            # Eyes
            eye_color = (255, 255, 0)  # Yellow
            pygame.draw.circle(img, eye_color, (width//3, height*2//5), width//10)
            pygame.draw.circle(img, eye_color, (width*2//3, height*2//5), width//10)
            pygame.draw.circle(img, (0, 0, 0), (width//3, height*2//5), width//20)  # Pupil
            pygame.draw.circle(img, (0, 0, 0), (width*2//3, height*2//5), width//20)  # Pupil
            
            # Mouth with teeth
            pygame.draw.rect(img, (0, 0, 0), (width//3, height*3//5, width//3, height//8))
            # Teeth
            for i in range(2):
                tooth_x = width//3 + i * width//6
                pygame.draw.rect(img, WHITE, (tooth_x, height*3//5, width//12, height//16))
        
        # Claws/Hands
        claw_color = (100, 0, 0)  # Darker red
        
        # Left hand with sharp claws
        pygame.draw.rect(img, claw_color, (width//8, height//2, width//6, height//4))
        for i in range(3):
            claw_y = height//2 + i * height//12
            pygame.draw.polygon(img, (50, 0, 0), [(width//8, claw_y), 
                                               (0, claw_y - height//16), 
                                               (0, claw_y + height//16)])
        
        # Right hand with sharp claws
        pygame.draw.rect(img, claw_color, (width*5//6 - width//6, height//2, width//6, height//4))
        for i in range(3):
            claw_y = height//2 + i * height//12
            pygame.draw.polygon(img, (50, 0, 0), [(width*5//6, claw_y), 
                                               (width, claw_y - height//16), 
                                               (width, claw_y + height//16)])
            
        # Horns on head
        pygame.draw.polygon(img, (50, 0, 0), [(width//4, height//6), 
                                           (width//6, 0), 
                                           (width//3, 0)])
        pygame.draw.polygon(img, (50, 0, 0), [(width*3//4, height//6), 
                                           (width*5//6, 0), 
                                           (width*2//3, 0)])
                                           
        # Add text label at bottom
        font = pygame.font.Font(None, 20)
        label = font.render(name.split('.')[0], True, WHITE)
        label_rect = label.get_rect(center=(width//2, height - 10))
        img.blit(label, label_rect)
        
    elif name.startswith("player"):
        # Draw a more detailed Mario-like character
        # Body (red overalls)
        pygame.draw.rect(img, RED, (width//4, height//3, width//2, height//2))
        
        # Head (skin tone)
        skin_color = (255, 200, 150)
        pygame.draw.circle(img, skin_color, (width//2, height//4), width//5)
        
        # Cap (red)
        pygame.draw.rect(img, RED, (width//4, height//6, width//2, height//8))
        
        # Eyes
        eye_color = (0, 0, 150)  # Blue eyes
        pygame.draw.circle(img, eye_color, (width//2 - width//10, height//4 - height//20), width//25)
        
        # Arms (skin tone)
        if name.endswith("walk1.png"):
            # Walking pose 1
            pygame.draw.line(img, skin_color, (width//4, height//2), (width//8, height*2//3), width//10)
            pygame.draw.line(img, skin_color, (width*3//4, height//2), (width*7//8, height*2//3), width//10)
        elif name.endswith("walk2.png"):
            # Walking pose 2
            pygame.draw.line(img, skin_color, (width//4, height//2), (width//6, height*2//3), width//10)
            pygame.draw.line(img, skin_color, (width*3//4, height//2), (width*5//6, height*2//3), width//10)
        else:
            # Default pose
            pygame.draw.line(img, skin_color, (width//4, height//2), (width//6, height*2//3), width//10)
            pygame.draw.line(img, skin_color, (width*3//4, height//2), (width*5//6, height*2//3), width//10)
        
        # Hands (white gloves)
        pygame.draw.circle(img, WHITE, (width//8, height*2//3), width//15)
        pygame.draw.circle(img, WHITE, (width*7//8, height*2//3), width//15)
        
        # Legs (blue)
        leg_color = (0, 0, 200)
        if name.endswith("walk1.png") or name.endswith("jump.png"):
            # Walking pose 1 or jumping
            pygame.draw.rect(img, leg_color, (width//3, height*3//4, width//6, height//4))
            pygame.draw.rect(img, leg_color, (width//2, height*3//4, width//6, height//4))
        elif name.endswith("walk2.png"):
            # Walking pose 2
            pygame.draw.rect(img, leg_color, (width//4, height*3//4, width//6, height//4))
            pygame.draw.rect(img, leg_color, (width*3//5, height*3//4, width//6, height//4))
        else:
            # Default pose
            pygame.draw.rect(img, leg_color, (width//3, height*3//4, width//6, height//4))
            pygame.draw.rect(img, leg_color, (width//2, height*3//4, width//6, height//4))
        
        # Feet (brown shoes)
        shoe_color = (139, 69, 19)
        pygame.draw.rect(img, shoe_color, (width//3 - width//20, height - height//10, width//5, height//10))
        pygame.draw.rect(img, shoe_color, (width//2, height - height//10, width//5, height//10))
        
        # Moustache (if not jumping)
        if not name.endswith("jump.png"):
            pygame.draw.rect(img, (0, 0, 0), (width*2//5, height//3, width//5, height//20))
        
    elif name.startswith("enemy"):
        # Draw a more detailed enemy (Goomba-like)
        
        # Body (brown)
        body_color = (139, 69, 19)
        pygame.draw.ellipse(img, body_color, (width//10, height//3, width*8//10, height*2//3))
        
        # Head
        pygame.draw.ellipse(img, body_color, (width//8, height//10, width*3//4, height//2))
        
        # Eyes
        eye_white = (255, 255, 255)
        eye_black = (0, 0, 0)
        pygame.draw.circle(img, eye_white, (width//3, height//4), width//10)
        pygame.draw.circle(img, eye_white, (width*2//3, height//4), width//10)
        pygame.draw.circle(img, eye_black, (width//3, height//4), width//20)
        pygame.draw.circle(img, eye_black, (width*2//3, height//4), width//20)
        
        # Feet
        if name.endswith("walk1.png"):
            # Walking pose 1
            pygame.draw.rect(img, BLACK, (width//6, height*9//10, width//4, height//10))
            pygame.draw.rect(img, BLACK, (width*3//5, height*9//10, width//4, height//10))
        else:
            # Walking pose 2 or default
            pygame.draw.rect(img, BLACK, (width//4, height*9//10, width//4, height//10))
            pygame.draw.rect(img, BLACK, (width//2, height*9//10, width//4, height//10))
    
    elif name.startswith("coin"):
        # Simple animated coin with shine effect
        pygame.draw.circle(img, YELLOW, (width//2, height//2), width//2.5)
        
        # Add shine effect based on animation frame
        if name.endswith("2.png"):
            pygame.draw.line(img, WHITE, (width//3, height//3), (width*2//3, height*2//3), width//10)
        elif name.endswith("3.png"):
            pygame.draw.circle(img, WHITE, (width//2, height//2), width//5)
        elif name.endswith("4.png"):
            pygame.draw.line(img, WHITE, (width*2//3, height//3), (width//3, height*2//3), width//10)
    
    elif name.startswith("turtle"):
        # Draw a more detailed turtle (Koopa-like)
        shell_color = (150, 100, 50)  # Brown shell
        skin_color = (0, 180, 0)  # Bright green skin
        
        if name.startswith("turtle_shell"):
            # Just draw the shell for shell state
            # Main shell (oval)
            pygame.draw.ellipse(img, shell_color, (width//10, height//6, width*8//10, height*2//3))
            
            # Shell pattern (lines)
            for i in range(3):
                y_pos = height//3 + i * height//9
                pygame.draw.line(img, (100, 60, 20), (width//5, y_pos), (width*4//5, y_pos), width//20)
                
            # Shell shine
            pygame.draw.ellipse(img, (200, 150, 100), (width//4, height//4, width//5, height//5))
        else:
            # Head
            pygame.draw.circle(img, skin_color, (width*3//4 if name.endswith("walk1.png") else width//4, height//4), width//5)
            
            # Eyes
            eye_pos_x = width*4//5 if name.endswith("walk1.png") else width//5
            pygame.draw.circle(img, WHITE, (eye_pos_x, height//4), width//15)
            pygame.draw.circle(img, BLACK, (eye_pos_x, height//4), width//30)
            
            # Shell (main body)
            pygame.draw.ellipse(img, shell_color, (width//4, height//3, width//2, height//2))
            
            # Shell pattern
            for i in range(2):
                y_pos = height//2 + i * height//8
                pygame.draw.line(img, (100, 60, 20), (width//3, y_pos), (width*2//3, y_pos), width//25)
            
            # Arms
            arm_start_x = width*2//3 if name.endswith("walk1.png") else width//3
            pygame.draw.line(img, skin_color, (arm_start_x, height//2), (width*4//5 if name.endswith("walk1.png") else width//5, height*2//3), width//15)
            
            # Legs
            if name.endswith("walk1.png"):
                # Walking pose 1
                pygame.draw.rect(img, skin_color, (width//3, height*3//4, width//6, height//5))
                pygame.draw.rect(img, skin_color, (width//2, height*4//5, width//6, height//5))
            else:
                # Walking pose 2
                pygame.draw.rect(img, skin_color, (width//4, height*4//5, width//6, height//5))
                pygame.draw.rect(img, skin_color, (width*3//5, height*3//4, width//6, height//5))
            
            # Feet
            pygame.draw.ellipse(img, (220, 220, 0), (width//3 - width//20, height - height//10, width//4, height//15))
            pygame.draw.ellipse(img, (220, 220, 0), (width*3//5 - width//20, height - height//10, width//4, height//15))
    
    elif name.startswith("boss_projectile"):
        # Create a spiky fireball projectile
        # Base circle
        pygame.draw.circle(img, (255, 50, 0), (width//2, height//2), width//3)
        # Flame effect
        for i in range(8):
            angle = i * 45
            outer_x = width//2 + int(width//2 * pygame.math.Vector2(1, 0).rotate(angle)[0])
            outer_y = height//2 + int(height//2 * pygame.math.Vector2(1, 0).rotate(angle)[1])
            pygame.draw.polygon(img, (255, 200, 0), [
                (width//2, height//2),
                (width//2 + int(width//4 * pygame.math.Vector2(0.5, 0.5).rotate(angle)[0]), 
                 height//2 + int(height//4 * pygame.math.Vector2(0.5, 0.5).rotate(angle)[1])),
                (outer_x, outer_y),
                (width//2 + int(width//4 * pygame.math.Vector2(0.5, -0.5).rotate(angle)[0]), 
                 height//2 + int(height//4 * pygame.math.Vector2(0.5, -0.5).rotate(angle)[1]))
            ])
        # Core
        pygame.draw.circle(img, (255, 255, 200), (width//2, height//2), width//6)
    
    elif color:
        img.fill(color)
    
    return img 