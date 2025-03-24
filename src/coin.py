import pygame
from src.constants import COIN_SIZE, YELLOW
from src.constants import load_image

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create animation frames
        self.frames = [
            load_image("coin1.png", COIN_SIZE, COIN_SIZE, YELLOW),
            load_image("coin2.png", COIN_SIZE, COIN_SIZE, YELLOW),
            load_image("coin3.png", COIN_SIZE, COIN_SIZE, YELLOW),
            load_image("coin4.png", COIN_SIZE, COIN_SIZE, YELLOW)
        ]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_index = 0
        self.animation_timer = 0

    def update(self):
        # Animate coin
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.frames)
            self.image = self.frames[self.animation_index] 