import pygame
import os
from src.constants import assets_dir

# Initialize sound variables
jump_sound = None
coin_sound = None
powerup_sound = None
damage_sound = None
game_over_sound = None
star_sound = None
current_music = None
music_volume = 0.5

def initialize_sounds():
    """Initialize all game sounds"""
    global jump_sound, coin_sound, powerup_sound, damage_sound, game_over_sound, star_sound
    
    try:
        # Create dummy sound as fallback
        dummy_sound = pygame.mixer.Sound(buffer=bytes([0] * 44100))
        
        # Try to load each sound, fall back to dummy if not found
        jump_sound_path = os.path.join(assets_dir, "jump.wav")
        if os.path.exists(jump_sound_path):
            jump_sound = pygame.mixer.Sound(jump_sound_path)
        else:
            jump_sound = dummy_sound
            
        coin_sound_path = os.path.join(assets_dir, "coin.wav")
        if os.path.exists(coin_sound_path):
            coin_sound = pygame.mixer.Sound(coin_sound_path)
        else:
            coin_sound = dummy_sound
            
        powerup_sound_path = os.path.join(assets_dir, "powerup.wav")
        if os.path.exists(powerup_sound_path):
            powerup_sound = pygame.mixer.Sound(powerup_sound_path)
        else:
            powerup_sound = dummy_sound
            
        damage_sound_path = os.path.join(assets_dir, "damage.wav")
        if os.path.exists(damage_sound_path):
            damage_sound = pygame.mixer.Sound(damage_sound_path)
        else:
            damage_sound = dummy_sound
            
        game_over_sound_path = os.path.join(assets_dir, "game_over.wav")
        if os.path.exists(game_over_sound_path):
            game_over_sound = pygame.mixer.Sound(game_over_sound_path)
        else:
            game_over_sound = dummy_sound
            
        star_sound_path = os.path.join(assets_dir, "star.wav")
        if os.path.exists(star_sound_path):
            star_sound = pygame.mixer.Sound(star_sound_path)
        else:
            star_sound = dummy_sound
            
        print("Sound files not found. Using silent sounds.")
    except Exception as e:
        print(f"Error initializing sounds: {e}")
        # Create a dummy sound
        dummy_sound = pygame.mixer.Sound(buffer=bytes([0] * 44100))
        jump_sound = dummy_sound
        coin_sound = dummy_sound
        powerup_sound = dummy_sound
        damage_sound = dummy_sound
        game_over_sound = dummy_sound
        star_sound = dummy_sound
        print("Sound files not found. Using silent sounds.")

    # Set sound volumes
    if jump_sound:
        jump_sound.set_volume(0.4)
    if coin_sound:
        coin_sound.set_volume(0.5)
    if powerup_sound:
        powerup_sound.set_volume(0.6)
    if damage_sound:
        damage_sound.set_volume(0.5)
    if game_over_sound:
        game_over_sound.set_volume(0.7)
    if star_sound:
        star_sound.set_volume(0.6)

def load_music(filename):
    """Try to load a music file and return its path if successful"""
    try:
        # Check if the file exists
        music_path = os.path.join(assets_dir, filename)
        if os.path.exists(music_path):
            return music_path
    except:
        pass
    return None

def initialize_music():
    """Initialize and return music tracks"""
    main_theme = load_music("main_theme.mp3")
    star_theme = load_music("star_theme.mp3")
    gameover_theme = load_music("gameover_theme.mp3")
    victory_theme = load_music("victory_theme.mp3")
    
    if main_theme:
        play_music(main_theme)
    else:
        print("Main theme music file not found.")
        
    return main_theme, star_theme, gameover_theme, victory_theme

def play_music(track, loop=True):
    """Play a music track with optional looping"""
    global current_music
    # Only change if it's a different track
    if track != current_music:
        current_music = track
        if track is None:
            pygame.mixer.music.stop()
            return
            
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except:
            print(f"Could not play music track: {track}") 