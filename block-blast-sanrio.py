import pygame
import random

# Initialize Pygame
pygame.init()

# Screen settings
GRID_SIZE = 8  # 8x8 grid
BLOCK_SIZE = 50
SCREEN_WIDTH = GRID_SIZE * BLOCK_SIZE
SCREEN_HEIGHT = GRID_SIZE * BLOCK_SIZE
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

# Grid setup
grid = [[random.choice(BLOCK_TYPES) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Font for text
font = pygame.font.SysFont("Arial", 24)

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color = COLORS[grid[y][x]]
            pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            # Add Sanrio name on block (simplified)
            text = font.render(grid[y][x][0], True, (255, 255, 255))  # First letter of block type
            screen.blit(text, (x * BLOCK_SIZE + 15, y * BLOCK_SIZE + 15))

def find_matches(x, y):
    """Check for 3+ matches horizontally or vertically."""
    block_type = grid[y][x]
    matches = [(x, y)]

    # Check horizontal
    for dx in [-1, 1]:
        nx = x + dx
        while 0 <= nx < GRID_SIZE and grid[y][nx] == block_type:
            matches.append((nx, y))
            nx += dx

    # Check vertical
    for dy in [-1, 1]:
        ny = y + dy
        while 0 <= ny < GRID_SIZE and grid[ny][x] == block_type:
            matches.append((x, ny))
            ny += dy

    return matches if len(matches) >= 3 else []

def remove_matches(matches):
    """Remove matched blocks and shift down."""
    for x, y in matches:
        grid[y][x] = None
    
    # Shift blocks down
    for x in range(GRID_SIZE):
        column = [grid[y][x] for y in range(GRID_SIZE)]
        new_column = [b for b in column if b is not None]
        new_column = [random.choice(BLOCK_TYPES) for _ in range(GRID_SIZE - len(new_column))] + new_column
        for y in range(GRID_SIZE):
            grid[y][x] = new_column[y]

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get clicked position
            mx, my = pygame.mouse.get_pos()
            grid_x, grid_y = mx // BLOCK_SIZE, my // BLOCK_SIZE
            
            # Find and remove matches
            matches = find_matches(grid_x, grid_y)
            if matches:
                remove_matches(matches)

    # Draw everything
    screen.fill((255, 182, 193))  # Pastel pink background
    draw_grid()
    pygame.display.flip()

pygame.quit()