import pygame
import random
import time
import math

# Initialize Pygame
pygame.init()

# Screen settings
GRID_SIZE = 8
BLOCK_SIZE = 50
SCREEN_WIDTH = GRID_SIZE * BLOCK_SIZE + 150  # Extra space for preview
SCREEN_HEIGHT = GRID_SIZE * BLOCK_SIZE + 50  # Space for score
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

# Shape definitions (relative coordinates from anchor point)
SHAPES = {
    "L": [(0, 0), (0, 1), (0, 2), (1, 2)],  # L shape
    "T": [(0, 0), (0, 1), (1, 1), (-1, 1)], # T shape
    "Square": [(0, 0), (0, 1), (1, 0), (1, 1)], # Square
    "Line": [(0, 0), (0, 1), (0, 2), (0, 3)] # Straight line
}

# Grid and game state
grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
score = 0
current_shape = None
next_shape = None
shape_x, shape_y = 0, 0
rotation = 0
drop_timer = time.time()
DROP_INTERVAL = 0.5
animated_blocks = []  # (x, y, target_y, block_type, progress)
game_over = False
cheer_timer = 0

# Fonts
font = pygame.font.SysFont("Arial", 24)
score_font = pygame.font.SysFont("Arial", 30, bold=True)
game_over_font = pygame.font.SysFont("Arial", 40, bold=True)

def new_shape():
    global current_shape, next_shape, shape_x, shape_y, rotation
    if not next_shape:
        shape_key = random.choice(list(SHAPES.keys()))
        # Randomize block types for each coordinate
        next_shape = [(dx, dy, random.choice(BLOCK_TYPES)) for dx, dy in SHAPES[shape_key]]
    current_shape = next_shape
    shape_key = random.choice(list(SHAPES.keys()))
    next_shape = [(dx, dy, random.choice(BLOCK_TYPES)) for dx, dy in SHAPES[shape_key]]
    shape_x = GRID_SIZE // 2 - 1  # Center horizontally
    shape_y = -3  # Start above grid
    rotation = 0
    if not can_place_shape():
        return False
    return True

def rotate_shape():
    global rotation
    old_rotation = rotation
    rotation = (rotation + 1) % 4
    if not can_place_shape():
        rotation = old_rotation

def can_place_shape():
    for dx, dy, _ in get_shape_coords():
        x, y = shape_x + dx, shape_y + dy
        if not (0 <= x < GRID_SIZE and y < GRID_SIZE) or (0 <= y < GRID_SIZE and grid[y][x] is not None):
            return False
    return True

def get_shape_coords():
    coords = [(dx, dy, block_type) for dx, dy, block_type in current_shape]
    if rotation == 0:
        return coords
    elif rotation == 1:  # 90 degrees
        return [(-dy, dx, block_type) for dx, dy, block_type in coords]
    elif rotation == 2:  # 180 degrees
        return [(-dx, -dy, block_type) for dx, dy, block_type in coords]
    elif rotation == 3:  # 270 degrees
        return [(dy, -dx, block_type) for dx, dy, block_type in coords]

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] is not None:
                color = COLORS[grid[y][x]]
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                text = font.render(grid[y][x][0], True, (255, 255, 255))
                screen.blit(text, (x * BLOCK_SIZE + 15, y * BLOCK_SIZE + 15))

def draw_current_shape():
    if current_shape:
        for dx, dy, block_type in get_shape_coords():
            x, y = shape_x + dx, shape_y + dy
            color = COLORS[block_type]
            wobble = math.sin(time.time() * 10) * 2
            pygame.draw.rect(screen, color, (x * BLOCK_SIZE + wobble, y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            text = font.render(block_type[0], True, (255, 255, 255))
            screen.blit(text, (x * BLOCK_SIZE + 15 + wobble, y * BLOCK_SIZE + 15))

def draw_next_shape():
    pygame.draw.rect(screen, (255, 218, 185), (GRID_SIZE * BLOCK_SIZE + 10, 10, 130, 130))
    for dx, dy, block_type in next_shape:
        x, y = GRID_SIZE * BLOCK_SIZE + 50 + dx * BLOCK_SIZE // 2, 50 + dy * BLOCK_SIZE // 2
        color = COLORS[block_type]
        pygame.draw.rect(screen, color, (x, y, BLOCK_SIZE // 2 - 2, BLOCK_SIZE // 2 - 2))
        text = font.render(block_type[0], True, (255, 255, 255))
        screen.blit(text, (x + 5, y + 5))

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

def draw_game_over():
    if game_over:
        game_over_text = game_over_font.render("Game Over!", True, (255, 105, 180))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))

def draw_cheer():
    global cheer_timer
    if cheer_timer > time.time():
        cheer_text = font.render("Yay, Kitty!", True, (255, 255, 255))
        pygame.draw.rect(screen, (255, 182, 193), (SCREEN_WIDTH // 2 - 50, 10, 100, 40))
        screen.blit(cheer_text, (SCREEN_WIDTH // 2 - 40, 15))

def find_matches():
    matches = set()
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE - 2):
            if (grid[y][x] is not None and
                grid[y][x] == grid[y][x + 1] == grid[y][x + 2]):
                matches.update([(x, y), (x + 1, y), (x + 2, y)])
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 2):
            if (grid[y][x] is not None and
                grid[y][x] == grid[y + 1][x] == grid[y + 2][x]):
                matches.update([(x, y), (x, y + 1), (x, y + 2)])
    return list(matches)

def animate_matches(matches):
    global animated_blocks, score, cheer_timer
    score += len(matches) * 10
    cheer_timer = time.time() + 1
    for x, y in matches:
        grid[y][x] = None
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
    global shape_y, current_shape, game_over
    if current_shape:
        new_y = shape_y + 1
        shape_y = new_y
        if not can_place_shape():
            shape_y -= 1  # Revert to last valid position
            if max([shape_y + dy for _, dy, _ in get_shape_coords()]) < 0:
                game_over = True
            else:
                for dx, dy, block_type in get_shape_coords():
                    x, y = shape_x + dx, shape_y + dy
                    if 0 <= y < GRID_SIZE and 0 <= x < GRID_SIZE:
                        grid[y][x] = block_type
                current_shape = None
                matches = find_matches()
                if matches:
                    animate_matches(matches)

# Main game loop
running = True
clock = pygame.time.Clock()
if not new_shape():
    game_over = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            if current_shape:
                if event.key == pygame.K_LEFT:
                    shape_x -= 1
                    if not can_place_shape():
                        shape_x += 1
                elif event.key == pygame.K_RIGHT:
                    shape_x += 1
                    if not can_place_shape():
                        shape_x += 1
                elif event.key == pygame.K_DOWN:
                    drop_shape()
                elif event.key == pygame.K_UP:
                    rotate_shape()

    if not game_over and current_shape and time.time() - drop_timer > DROP_INTERVAL:
        drop_shape()
        drop_timer = time.time()

    if not game_over and not current_shape and not animated_blocks:
        if not new_shape():
            game_over = True

    update_animations()

    screen.fill((255, 182, 193))
    draw_grid()
    draw_current_shape()
    draw_animated_blocks()
    draw_next_shape()
    draw_score()
    draw_cheer()
    draw_game_over()
    pygame.display.flip()

    clock.tick(60)

pygame.quit()