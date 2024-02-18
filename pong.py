import pygame
import random
import numpy as np
import pygame.sndarray

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions and colors
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
black = (0, 0, 0)
white = (255, 255, 255)

# Paddle settings
paddle_width = 15
paddle_height = 80
paddle_speed = 5
paddle1_x = 10
paddle1_y = screen_height // 2 - paddle_height // 2
paddle2_x = screen_width - paddle_width - 10
paddle2_y = screen_height // 2 - paddle_height // 2

# Ball settings
ball_size = 10
ball_x = screen_width // 2 - ball_size // 2
ball_y = screen_height // 2 - ball_size // 2
ball_x_speed = 3
ball_y_speed = 3

# Scores
player1_score = 0
player2_score = 0

# Font for scores
font = pygame.font.SysFont(None, 30)

# Function to generate beep sounds
def generate_beep(duration_ms, frequency):
    sample_rate = 44100
    samples = np.arange(duration_ms * (sample_rate / 1000.0))
    waveform = np.sin(2 * np.pi * frequency * samples / sample_rate)
    waveform = np.int16(waveform * 32767)  # Convert to 16-bit signed integers
    stereo_waveform = np.column_stack((waveform, waveform))
    sound = pygame.sndarray.make_sound(stereo_waveform)
    return sound

# Reset ball position and speed
def reset_ball():
    return screen_width // 2 - ball_size // 2, screen_height // 2 - ball_size // 2, 3 * random.choice((-1, 1)), 3 * random.choice((-1, 1))

# Draw paddles and ball
def draw_paddles_and_ball():
    pygame.draw.rect(screen, white, [paddle1_x, paddle1_y, paddle_width, paddle_height])
    pygame.draw.rect(screen, white, [paddle2_x, paddle2_y, paddle_width, paddle_height])
    pygame.draw.ellipse(screen, white, [ball_x, ball_y, ball_size, ball_size])

# Draw scores
def draw_scores():
    score_text = font.render(f"{player1_score} : {player2_score}", True, white)
    screen.blit(score_text, [screen_width // 2 - 20, 10])

# Display win/lose message
def display_win_lose_message(winner):
    if winner == "player":
        message = "YOU WIN! Press Y to Restart or N to Quit."
    else:
        message = "YOU LOSE! Press Y to Restart or N to Quit."
    
    message_text = font.render(message, True, white)
    screen.blit(message_text, [screen_width // 2 - message_text.get_width() // 2, screen_height // 2 - 20])
    pygame.display.flip()

# Main game function
def game_loop():
    global paddle1_y, paddle2_y, ball_x, ball_y, ball_x_speed, ball_y_speed, player1_score, player2_score
    running = True
    game_over = False

    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and paddle1_y > 0:
                paddle1_y -= paddle_speed
            if keys[pygame.K_s] and paddle1_y < screen_height - paddle_height:
                paddle1_y += paddle_speed
            if keys[pygame.K_UP] and paddle2_y > 0:
                paddle2_y -= paddle_speed
            if keys[pygame.K_DOWN] and paddle2_y < screen_height - paddle_height:
                paddle2_y += paddle_speed

            ball_x += ball_x_speed
            ball_y += ball_y_speed

            if ball_y <= 0 or ball_y >= screen_height - ball_size:
                ball_y_speed *= -1
                generate_beep(100, 520).play()

            if (ball_x <= paddle1_x + paddle_width and paddle1_y <= ball_y <= paddle1_y + paddle_height) or \
            (ball_x + ball_size >= paddle2_x and paddle2_y <= ball_y <= paddle2_y + paddle_height):
                ball_x_speed *= -1
                generate_beep(100, 440).play()

            if ball_x < 0:
                player2_score += 1
                ball_x, ball_y, ball_x_speed, ball_y_speed = reset_ball()
                generate_beep(200, 330).play()
            elif ball_x > screen_width:
                player1_score += 1
                ball_x, ball_y, ball_x_speed, ball_y_speed = reset_ball()
                generate_beep(200, 330).play()

            screen.fill(black)
            draw_paddles_and_ball()
            draw_scores()

            if player1_score >= 5 or player2_score >= 5:
                game_over = True
                display_win_lose_message("player" if player1_score >= 5 else "opponent")
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_y]:
                player1_score = 0
                player2_score = 0
                ball_x, ball_y, ball_x_speed, ball_y_speed = reset_ball()
                game_over = False
            elif keys[pygame.K_n]:
                running = False

        pygame.display.flip()
        clock.tick(60)

game_loop()
pygame.quit()
