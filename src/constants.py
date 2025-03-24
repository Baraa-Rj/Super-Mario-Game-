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
    
    if name.startswith("player"):
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
            # De fault pose
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
    
    elif color:
        img.fill(color)
    
    return img 