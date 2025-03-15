import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen settings
GRID_SIZE = 8
BLOCK_SIZE = 50
SCREEN_WIDTH = GRID_SIZE * BLOCK_SIZE
SCREEN_HEIGHT = GRID_SIZE * BLOCK_SIZE + 50  # Extra space for score at bottom
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

# Grid and game state
grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
score = 0
current_shape = None
shape_x, shape_y = 0, 0  # Shape position
drop_timer = time.time()
DROP_INTERVAL = 0.5  # Seconds between drops
animated_blocks = []  # (x, y, target_y, block_type, progress)

# Fonts
font = pygame.font.SysFont("Arial", 24)
score_font = pygame.font.SysFont("Arial", 30, bold=True)

def new_shape():
    """Generate a new falling shape (single block for simplicity)."""
    global current_shape, shape_x, shape_y
    current_shape = random.choice(BLOCK_TYPES)
    shape_x = GRID_SIZE // 2  # Start in middle
    shape_y = -1  # Start above grid

def adjust_color(color, factor):
    return tuple(min(255, max(0, int(c * factor))) for c in color)

def draw_grid(hover_pos=None):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] is not None:
                color = COLORS[grid[y][x]]
                if (x, y) == hover_pos:
                    color = adjust_color(color, 1.2)
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                text = font.render(grid[y][x][0], True, (255, 255, 255))
                screen.blit(text, (x * BLOCK_SIZE + 15, y * BLOCK_SIZE + 15))

def draw_current_shape():
    if current_shape:
        color = COLORS[current_shape]
        pygame.draw.rect(screen, color, (shape_x * BLOCK_SIZE, shape_y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        text = font.render(current_shape[0], True, (255, 255, 255))
        screen.blit(text, (shape_x * BLOCK_SIZE + 15, shape_y * BLOCK_SIZE + 15))

def draw_animated_blocks():
    for x, y, target_y, block_type, progress in animated_blocks:
        color = COLORS[block_type]
        current_y = y + (target_y - y) * progress
        pygame.draw.rect(screen, color, (x * BLOCK_SIZE, current_y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        text = font.render(block_type[0], True, (255, 255, 255))
        screen.blit(text, (x * BLOCK_SIZE + 15, current_y * BLOCK_SIZE + 15))

def draw_score():
    score_box = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40, 140, 40)
    pygame.draw.rect(screen, (221, 160, 221), score_box)
    pygame.draw.rect(screen, (255, 255, 255), score_box, 2)
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 140, SCREEN_HEIGHT - 35))

def find_matches():
    matches = set()
    # Check horizontal
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE - 2):
            if (grid[y][x] is not None and
                grid[y][x] == grid[y][x + 1] == grid[y][x + 2]):
                matches.update([(x, y), (x + 1, y), (x + 2, y)])
    # Check vertical
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 2):
            if (grid[y][x] is not None and
                grid[y][x] == grid[y + 1][x] == grid[y + 2][x]):
                matches.update([(x, y), (x, y + 1), (x, y + 2)])
    return list(matches)

def animate_matches(matches):
    global animated_blocks, score
    score += len(matches) * 10
    for x, y in matches:
        grid[y][x] = None
    # Animate falling blocks
    for x in range(GRID_SIZE):
        column = [grid[y][x] for y in range(GRID_SIZE)]
        new_column = [b for b in column if b is not None]
        gaps = GRID_SIZE - len(new_column)
        for y in range(len(new_column)):
            target_y = GRID_SIZE - 1 - (len(new_column) - 1 - y)
            if column[y] is not None and y != target_y:
                animated_blocks.append((x, y, target_y, new_column[y], 0))
        for y in range(GRID_SIZE):
            grid[y][x] = new_column[y - gaps] if y >= gaps else None

def update_animations():
    global animated_blocks
    for i in range(len(animated_blocks)):
        x, y, target_y, block_type, progress = animated_blocks[i]
        progress += 0.05
        if progress >= 1:
            grid[target_y][x] = block_type
            animated_blocks[i] = (x, y, target_y, block_type, 1)
        else:
            animated_blocks[i] = (x, y, target_y, block_type, progress)
    animated_blocks = [ab for ab in animated_blocks if ab[4] < 1]

def drop_shape():
    global shape_y, current_shape
    if shape_y + 1 < GRID_SIZE and grid[shape_y + 1][shape_x] is None:
        shape_y += 1
    else:
        grid[shape_y][shape_x] = current_shape
        current_shape = None
        matches = find_matches()
        if matches:
            animate_matches(matches)

# Main game loop
running = True
clock = pygame.time.Clock()
new_shape()  # Start with a shape
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if current_shape:
                if event.key == pygame.K_LEFT and shape_x > 0 and grid[shape_y][shape_x - 1] is None:
                    shape_x -= 1
                elif event.key == pygame.K_RIGHT and shape_x < GRID_SIZE - 1 and grid[shape_y][shape_x + 1] is None:
                    shape_x += 1
                elif event.key == pygame.K_DOWN:
                    drop_shape()

    # Auto-drop shape
    if current_shape and time.time() - drop_timer > DROP_INTERVAL:
        drop_shape()
        drop_timer = time.time()

    # Spawn new shape if none exists
    if not current_shape and not animated_blocks:
        new_shape()

    # Update animations
    update_animations()

    # Draw everything
    screen.fill((255, 182, 193))
    draw_grid()
    draw_current_shape()
    draw_animated_blocks()
    draw_score()
    pygame.display.flip()

    clock.tick(60)

pygame.quit()