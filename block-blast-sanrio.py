import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen settings
GRID_SIZE = 8
BLOCK_SIZE = 50
SCREEN_WIDTH = GRID_SIZE * BLOCK_SIZE
SCREEN_HEIGHT = GRID_SIZE * BLOCK_SIZE + 50  # Extra space for score
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sanrio Block Party")

# Colors for Sanrio-themed blocks
COLORS = {
    "Hello Kitty Bow": (255, 105, 180),  # Pink
    "My Melody Flower": (186, 85, 211),  # Purple
    "Keroppi Lily Pad": (50, 205, 50),   # Green
    "Cinnamoroll Cloud": (173, 216, 230),# Light Blue
    "Pompompurin Pudding": (255, 215, 0) # Yellow
}
BLOCK_TYPES = list(COLORS.keys())

# Grid and animation state
grid = [[random.choice(BLOCK_TYPES) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
animated_blocks = []  # (x, y, target_y, block_type, progress)
CLICK_DURATION = 0.1
click_timer = None
click_pos = None
score = 0  # New score variable

# Fonts
font = pygame.font.SysFont("Arial", 24)
score_font = pygame.font.SysFont("Arial", 30, bold=True)

def adjust_color(color, factor):
    return tuple(min(255, max(0, int(c * factor))) for c in color)

def draw_grid(hover_pos=None, click_pos=None):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] is None:
                continue
            base_color = COLORS[grid[y][x]]
            color = base_color
            if (x, y) == hover_pos:
                color = adjust_color(base_color, 1.2)
            elif (x, y) == click_pos and click_timer and time.time() < click_timer:
                color = adjust_color(base_color, 0.8)
            pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            text = font.render(grid[y][x][0], True, (255, 255, 255))
            screen.blit(text, (x * BLOCK_SIZE + 15, y * BLOCK_SIZE + 15))

def draw_animated_blocks():
    for x, y, target_y, block_type, progress in animated_blocks:
        color = COLORS[block_type]
        current_y = y + (target_y - y) * progress
        pygame.draw.rect(screen, color, (x * BLOCK_SIZE, current_y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        text = font.render(block_type[0], True, (255, 255, 255))
        screen.blit(text, (x * BLOCK_SIZE + 15, current_y * BLOCK_SIZE + 15))

def draw_score():
    # Draw a pastel purple score box
    score_box = pygame.Rect(SCREEN_WIDTH - 150, 10, 140, 40)
    pygame.draw.rect(screen, (221, 160, 221), score_box)  # Plum color
    pygame.draw.rect(screen, (255, 255, 255), score_box, 2)  # White border
    
    # Render score text
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 140, 15))

def find_matches(x, y):
    block_type = grid[y][x]
    matches = [(x, y)]
    for dx in [-1, 1]:
        nx = x + dx
        while 0 <= nx < GRID_SIZE and grid[y][nx] == block_type:
            matches.append((nx, y))
            nx += dx
    for dy in [-1, 1]:
        ny = y + dy
        while 0 <= ny < GRID_SIZE and grid[ny][x] == block_type:
            matches.append((x, ny))
            ny += dy
    return matches if len(matches) >= 3 else []

def animate_matches(matches):
    global animated_blocks, score
    # Add score based on number of blocks cleared
    score += len(matches) * 10  # 10 points per block
    
    # Remove matched blocks and animate falling
    for x, y in matches:
        grid[y][x] = None
    
    for x in range(GRID_SIZE):
        column = [grid[y][x] for y in range(GRID_SIZE)]
        new_column = [b for b in column if b is not None]
        new_blocks = [random.choice(BLOCK_TYPES) for _ in range(GRID_SIZE - len(new_column))]
        full_column = new_blocks + new_column
        
        for y in range(GRID_SIZE):
            grid[y][x] = full_column[y]
        
        for y in range(GRID_SIZE):
            if column[y] is None and full_column[y] is not None:
                start_y = -len(new_blocks) + y - len(new_column)
                animated_blocks.append((x, start_y, y, full_column[y], 0))

def update_animations():
    global animated_blocks
    for i in range(len(animated_blocks)):
        x, y, target_y, block_type, progress = animated_blocks[i]
        progress += 0.05
        if progress >= 1:
            animated_blocks[i] = (x, y, target_y, block_type, 1)
        else:
            animated_blocks[i] = (x, y, target_y, block_type, progress)
    animated_blocks = [ab for ab in animated_blocks if ab[4] < 1]

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            grid_x, grid_y = mx // BLOCK_SIZE, my // BLOCK_SIZE
            if 0 <= grid_y < GRID_SIZE:  # Ensure click is within grid
                matches = find_matches(grid_x, grid_y)
                if matches:
                    animate_matches(matches)
                    click_pos = (grid_x, grid_y)
                    click_timer = time.time() + CLICK_DURATION

    mx, my = pygame.mouse.get_pos()
    hover_x, hover_y = mx // BLOCK_SIZE, my // BLOCK_SIZE
    hover_pos = (hover_x, hover_y) if (0 <= hover_x < GRID_SIZE and 0 <= hover_y < GRID_SIZE) else None

    update_animations()

    screen.fill((255, 182, 193))  # Pastel pink background
    draw_grid(hover_pos, click_pos)
    draw_animated_blocks()
    draw_score()  # Draw the score
    pygame.display.flip()

    clock.tick(60)

pygame.quit()