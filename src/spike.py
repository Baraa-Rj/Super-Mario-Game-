import pygame
from src.constants import SPIKE_WIDTH, SPIKE_HEIGHT

class Spike(pygame.sprite.Sprite):
    # Add class variable for height
    height = SPIKE_HEIGHT
    
    def __init__(self, x, y, width=SPIKE_WIDTH):
        super().__init__()
        self.image = self.create_spike_image(width, SPIKE_HEIGHT)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.deadly = True  # Causes instant game over on collision
    
    def create_spike_image(self, width, height):
        img = pygame.Surface((width, height), pygame.SRCALPHA)
        # Draw triangular spikes
        spike_color = (150, 150, 150)  # Metal gray
        
        # Calculate number of spikes based on width
        num_spikes = max(1, width // 10)
        spike_width = width / num_spikes
        
        for i in range(num_spikes):
            x_pos = i * spike_width
            # Draw a triangle for each spike
            pygame.draw.polygon(img, spike_color, [
                (x_pos, height),  # Bottom left
                (x_pos + spike_width / 2, 0),  # Top middle
                (x_pos + spike_width, height)  # Bottom right
            ])
            
            # Add some shading for 3D effect
            pygame.draw.polygon(img, (200, 200, 200), [
                (x_pos + spike_width / 2, 0),  # Top middle
                (x_pos + spike_width, height),  # Bottom right
                (x_pos + spike_width - 2, height - 2)  # Slightly in from bottom right
            ])
        
        return img 