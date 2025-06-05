import pygame
import math
import sys

# === KONSTANTEN ===
FPS = 60
TILE_SIZE = 64

# Spielfeld (1 = Wand, 0 = leer)
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

MAP_WIDTH = len(game_map[0])
MAP_HEIGHT = len(game_map)

WIDTH = MAP_WIDTH * TILE_SIZE
HEIGHT = MAP_HEIGHT * TILE_SIZE 

# == VARIABLEN ===
tile_depth = TILE_SIZE / 1.2
max_depth = tile_depth * MAP_HEIGHT / 1.5

# === WICHTIG ===

if MAP_WIDTH != MAP_HEIGHT:
    print("SPIELFELD MUSS QUADRATISCH SEIN.")
    sys.exit(1)
    
# Hellgrau mit schwarzem Hintergrund
print("\033[37;40m██\033[0m")

# Dunkelgrau mit schwarzem Hintergrund
print("\033[90;40m██\033[0m")
     

print(f"Resolution in percentage\n\n100 = 100%, but the higher the value, the more performance is required.\nYour'e map is {MAP_WIDTH}x{MAP_HEIGHT} big.\n\n\nMy suggestion:\n100%, if your map has small tunnels and no big rooms. \n75%, if it has some, but not too many rooms. \n50% if it has large areas. \n25%, if it is only an Area with like 20 or more tiles.\n\nThe size of the map is not that important, like the size of rooms or tunnels.\n\nEnter -1 to get a minimap printed in terminal.")
while True:
    try:
        resolution = int(input(f"\n\nResolution: "))
        if resolution == -1:
            print("\n\nMinimap:\n")
            for row in range(len(game_map)):
                for col in range(len(game_map[row])):
                    if row%2 == 0: 
                        if col%2 == 0: 
                            print("\033[38;5;252;40m██\033[0m" if game_map[row][col] == 1 else "\033[38;5;232;40m██\033[0m", end="") 
                        else: 
                            print("\033[38;5;255;40m██\033[0m" if game_map[row][col] == 1 else "\033[38;5;234;40m██\033[0m", end="") 
                    else: 
                        if col%2 == 0: 
                            print("\033[38;5;254;40m██\033[0m" if game_map[row][col] == 1 else "\033[38;5;234;40m██\033[0m", end="") 
                        else: 
                            print("\033[38;5;252;40m██\033[0m" if game_map[row][col] == 1 else "\033[38;5;232;40m██\033[0m", end="") 
                    
                print() # Zeilenumbruch nach jeder Reihe
        elif resolution <= 0 or resolution > 100:
            print("Please enter a number between 1 and 100, or type -1 for a minimap.")
        else:
            NUM_RAYS = int((WIDTH * resolution) / 100)
            break;


    except ValueError:
        print("I said \"Enter a number :)\n\"")

# === SPIELER ===
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_angle = 0  
move_speed = 3
rot_speed = 0.05 

# === INITIALISIERUNG ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# === FUNKTION: STRAHLENWERFUNG ===
def cast_rays(screen, px, py, angle):
    fov = math.pi / 2.8
    start_angle = angle - fov / 2

    distances = []

    for ray in range(NUM_RAYS):
        ray_angle = start_angle + (ray * fov / NUM_RAYS)
        ray_x, ray_y = px, py

        for depth in range(1, int(max_depth)):
            target_x = ray_x + math.cos(ray_angle) * depth
            target_y = ray_y + math.sin(ray_angle) * depth

            grid_x = int(target_x // TILE_SIZE)
            grid_y = int(target_y // TILE_SIZE)

            if grid_x < 0 or grid_x >= MAP_WIDTH or grid_y < 0 or grid_y >= MAP_HEIGHT:
                distances.append(max_depth)
                break

            if game_map[grid_y][grid_x] == 1:
                dist = depth * math.cos(angle - ray_angle)
                distances.append(dist)
                pygame.draw.line(screen, (255, 255, 0), (px, py), (target_x, target_y), 1)
                break
        else:
            distances.append(max_depth)  # Fallback, wenn nichts getroffen wurde

    return distances

# === FUNKTION: RENDERING ===
def draw_scene(distances: list[float]):
    screen.fill((0, 0, 0))  
    
    distance_amount = len(distances)
    ray_width = WIDTH // distance_amount

    for i, distance in enumerate(distances):
        if distance >= max_depth:
            continue  # Nichts getroffen, keine Wand zeichnen

        # Perspektivkorrektur
        wall_height = TILE_SIZE * HEIGHT / (distance + 0.0001)

        # Einfache Shading-Farbe
        shade = max(0, 255 - int(distance / max_depth * 255))
        color = (shade, shade, shade)

        # Wand als vertikaler Streifen
        x = i * ray_width
        y = HEIGHT // 2 - wall_height // 2
        pygame.draw.rect(screen, color, (x, y, ray_width, wall_height))

    # Spieler (Top-Down-View, optional)
    pygame.draw.circle(screen, (0, 255, 0), (int(player_x), int(player_y)), 5)
    line_end_x = player_x + math.cos(player_angle) * 30
    line_end_y = player_y + math.sin(player_angle) * 30
    pygame.draw.line(screen, (255, 0, 0), (player_x, player_y), (line_end_x, line_end_y), 2)

    
# def draw_scene():
#     screen.fill((0, 0, 0))  

#     # Zeichne das Spielfeld
#     for row_idx, row in enumerate(game_map):
#         for col_idx, cell in enumerate(row):
#             color = (200, 200, 200) if cell == 0 else (50, 50, 50)
#             pygame.draw.rect(screen, color, (col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))

#     # Zeichne den Spieler
#     pygame.draw.circle(screen, (0, 255, 0), (int(player_x), int(player_y)), 5)

#     # Zeichne Blickrichtung
#     line_end_x = player_x + math.cos(player_angle) * 30
#     line_end_y = player_y + math.sin(player_angle) * 30
#     pygame.draw.line(screen, (255, 0, 0), (player_x, player_y), (line_end_x, line_end_y), 2)

# === HAUPTSCHLEIFE ===

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Tasteneingaben
    keys = pygame.key.get_pressed()
    dx = math.cos(player_angle) * move_speed
    dy = math.sin(player_angle) * move_speed

    # Neue Position berechnen
    new_x, new_y = player_x, player_y
    if keys[pygame.K_w]:
        new_x += dx
        new_y += dy
    if keys[pygame.K_s]:
        new_x -= dx
        new_y -= dy

    # Kollisionsprüfung für neue Position
    grid_x = int(new_x // TILE_SIZE)
    grid_y = int(new_y // TILE_SIZE)
    if game_map[grid_y][grid_x] == 0:
        player_x, player_y = new_x, new_y

    if keys[pygame.K_a]:
        player_angle -= rot_speed
    if keys[pygame.K_d]:
        player_angle += rot_speed

    # Szene zeichnen & Strahlen berechnen
    distances = cast_rays(screen, player_x, player_y, player_angle)
    draw_scene(distances)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
