import pygame
import sys
import random
import os

# Init
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP = -10
PIPE_WIDTH = 60
PIPE_GAP = 150
PIPE_SPEED = 3

# Screen Setup (Resizable)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)

# Load assets
bg_img = pygame.image.load("assets/background.jpeg")
bird_img = pygame.transform.scale(pygame.image.load("assets/bird.jpg").convert_alpha(), (40, 30))
jump_sound = pygame.mixer.Sound("assets/jump.wav")
pygame.mixer.music.load("assets/theme.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

# Bird
bird_x = 100
bird_y = HEIGHT // 2
bird_vel = 0
bird_rect = bird_img.get_rect(topleft=(bird_x, bird_y))

# Pipes and Score
pipes = []
pipe_timer = 0
score = 0
game_active = False
game_paused = False
game_over = False

# High Score File
high_score = 0
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0

def save_high_score():
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))

def create_pipe():
    height = random.randint(100, HEIGHT - 200)
    top = pygame.Rect(WIDTH, 0, PIPE_WIDTH, height)
    bottom = pygame.Rect(WIDTH, height + PIPE_GAP, PIPE_WIDTH, HEIGHT)
    return top, bottom

def reset_game():
    global pipes, score, bird_y, bird_vel, bird_rect, pipe_timer
    global game_active, game_paused, game_over

    pipes.clear()
    bird_y = HEIGHT // 2
    bird_vel = 0
    bird_rect.topleft = (bird_x, bird_y)
    score = 0
    pipe_timer = 0
    game_active = False
    game_paused = False
    game_over = False

def draw_text(text, size, y, color=(255,255,255)):
    f = pygame.font.SysFont("Arial", size)
    t = f.render(text, True, color)
    rect = t.get_rect(center=(WIDTH // 2, y))
    screen.blit(t, rect)

def draw_pipes():
    for p in pipes:
        pygame.draw.rect(screen, (0, 255, 0), p)

def move_pipes():
    for p in pipes:
        p.x -= PIPE_SPEED

def check_collision():
    for p in pipes:
        if bird_rect.colliderect(p):
            return True
    return bird_y <= 0 or bird_y >= HEIGHT

# Main Loop
running = True
while running:
    clock.tick(FPS)

    # Resize support
    WIDTH, HEIGHT = screen.get_size()
    bg = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    screen.blit(bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score()
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_active:
                    game_active = True
                elif not game_paused and not game_over:
                    bird_vel = JUMP
                    jump_sound.play()
            elif event.key == pygame.K_p and game_active and not game_over:
                game_paused = not game_paused
            elif event.key == pygame.K_r and game_over:
                reset_game()

    # Game logic
    if game_active and not game_paused and not game_over:
        bird_vel += GRAVITY
        bird_y += bird_vel
        bird_rect.topleft = (bird_x, bird_y)

        # Pipe handling
        pipe_timer += 1
        if pipe_timer >= 90:
            pipes.extend(create_pipe())
            pipe_timer = 0

        move_pipes()
        pipes = [p for p in pipes if p.x + PIPE_WIDTH > 0]

        # Score logic (only top pipes)
        for p in pipes:
            if p.x == bird_x and p.height > 0:
                score += 1

        if check_collision():
            game_over = True
            high_score = max(high_score, score)
            save_high_score()

    # Draw pipes and bird
    draw_pipes()
    screen.blit(bird_img, (bird_x, bird_y))

    # Draw text info
    if game_active:
        draw_text(f"Score: {score}", 28, 30)
    if not game_active:
        draw_text("Flappy Bird", 48, 150)
        draw_text("Press SPACE to Start", 24, 220)
    elif game_paused:
        draw_text("Paused", 40, HEIGHT // 2 - 40)
        draw_text("Press P to Resume", 24, HEIGHT // 2 + 10)
    elif game_over:
        draw_text("Game Over", 48, 200)
        draw_text(f"Score: {score}", 28, 260)
        draw_text(f"High Score: {high_score}", 24, 300)
        draw_text("Press R to Restart", 20, 350)

    pygame.display.flip()

pygame.quit()
sys.exit()
