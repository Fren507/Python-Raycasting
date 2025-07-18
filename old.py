import pygame
import math
import sys
    
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]         
            
# === CONSTANTS ===
FPS = 60
TILE_SIZE = 64

map_width = len(game_map[0])
map_height = len(game_map)

# WIDTH = map_width * TILE_SIZE
# HEIGHT = map_height * TILE_SIZE

# === VARIABLES ===
tile_depth = TILE_SIZE / 1.2
if map_height < 10:
    max_depth = tile_depth * map_height / 1.5
else:
    max_depth = tile_depth * 10

# # === IMPORTANT CHECK ===
# if map_width != map_height:
#     print("Game map must be square.")
#     sys.exit(1)
    
# === INPUT: Resolution & Rays ===
print("Enter resolution (1-100) or -1 for minimap:")
def Initialization():
    while True:
        try:
            res = int(input("> "))
            if res == -1:
                for ry, row in enumerate(game_map):
                    for cx, cell in enumerate(row):
                        char = "██" if cell == 1 else "  "
                        print(char, end="")
                    print()
            elif 1 <= res <= 100:
                return res
            else:
                print("Please enter a number between 1 and 100, or -1.")
        except ValueError:
            print("Invalid input.")

# === INITIALIZATION ===

res = Initialization()

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
info = pygame.display.Info()
clock = pygame.time.Clock()

WIDTH, HEIGHT = info.current_w, info.current_h

NUM_RAYS = int(WIDTH * res / 100)

if WIDTH == HEIGHT:
    MIN_SIZE = WIDTH
elif WIDTH < HEIGHT:
    MIN_SIZE = WIDTH
else:
    MIN_SIZE = HEIGHT
    
minimap_size = MIN_SIZE // 4
minimap_tile_size = minimap_size // max(map_width, map_height)
if map_width > 30 or map_height > 30: 
    minimap_size *= 2
MINImap_width = minimap_tile_size * len(game_map[0])
MINImap_height = minimap_tile_size * len(game_map)

def find_spawn_point(game_map):
    """Setzt den Spieler in die Mitte eines freien Tiles."""
    for y in range(1, len(game_map) - 1):  # Keine Randbereiche
        for x in range(1, len(game_map[y]) - 1):
            if game_map[y][x] == 0:  # Freie Zelle gefunden
                return (x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE  # Mitte des Tiles

    return WIDTH // 2, HEIGHT // 2  # Falls nichts gefunden wird, zentral spawnen

# === PLAYER SETUP ===
player_x, player_y = find_spawn_point(game_map)
player_angle = 0
move_speed = 3
rot_speed = 0.05
PLAYER_RADIUS = 10  # collision radius

# Helper function for collision detection
def can_move(x: float, y: float) -> bool:
    """
    Checks if position (x, y) is within an empty cell.
    Treats the player as a circle with radius.
    """
    for dx in (-PLAYER_RADIUS, PLAYER_RADIUS):
        for dy in (-PLAYER_RADIUS, PLAYER_RADIUS):
            gx = int((x + dx) // TILE_SIZE)
            gy = int((y + dy) // TILE_SIZE)
            # print(f"Checking cell gx={gx}, gy={gy}...")
            if gx < 0 or gx >= map_width or gy < 0 or gy >= map_height:
                # print("-> Movement blocked: outside map")
                return False
            if game_map[gy][gx] != 0:
                # print("-> Movement blocked: wall detected")
                return False
    # print("-> Movement allowed")
    return True

# === FUNCTIONS: Raycasting & Scene Drawing ===
def cast_rays(screen, px, py, angle):
    fov = math.pi / 2.8
    start_angle = angle - fov / 2
    distances = []

    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * (fov / NUM_RAYS)
        for depth in range(1, int(max_depth)):
            tx = px + math.cos(ray_angle) * depth
            ty = py + math.sin(ray_angle) * depth
            gx = int(tx // TILE_SIZE)
            gy = int(ty // TILE_SIZE)
            if gx < 0 or gx >= map_width or gy < 0 or gy >= map_height:
                distances.append(max_depth)
                break
            if game_map[gy][gx] == 1:
                dist = depth * math.cos(angle - ray_angle)
                distances.append(dist)
                pygame.draw.line(screen, (255, 255, 0), (px, py), (tx, ty), 1)
                break
        else:
            distances.append(max_depth)
    return distances

def draw_floor():
    for i in range(HEIGHT // 2, HEIGHT):  # Nur unteren Bereich färben
        shade = min(255, int((i - HEIGHT // 2) / (HEIGHT // 2) * 85) + 85)
        pygame.draw.line(screen, (shade, shade, shade), (0, i), (WIDTH, i))

def draw_walls(distances: list[float]):
    screen.fill((0, 0, 0))
    ray_width = WIDTH // len(distances)
    pygame.draw.rect(screen, (75, 75, 75), (0, 0, WIDTH, HEIGHT))
    draw_floor()
    for i, dist in enumerate(distances):
        wall_h = TILE_SIZE * HEIGHT / (dist + 0.0001)
        shade = max(0, 255 - int(dist / max_depth * 255))
        color = (shade, shade, shade)
        x = i * ray_width
        y = HEIGHT // 2 - wall_h // 2
        if dist >= max_depth:
            pygame.draw.rect(screen, (0, 0, 0), (x, y, ray_width, wall_h))
        pygame.draw.rect(screen, color, (x, y, ray_width, wall_h))
    
def draw_player():
    px = WIDTH - MINImap_width + (player_x / TILE_SIZE * minimap_tile_size)
    py = player_y / TILE_SIZE * minimap_tile_size
    pygame.draw.circle(screen, (0, 255, 0), (px, py), minimap_tile_size * 1.2)
    
# def draw_minimap():
#     pygame.draw.rect(screen, (0, 0, 0), (WIDTH - MINImap_width, 0, MINImap_width, MINImap_height))
#     for i, row in enumerate(game_map):
#         for j, col in enumerate(game_map[i]):
#             if col == 1:
#                 continue;
#             color = (255, 255, 255)
#             x = WIDTH - MINImap_width + j * minimap_tile_size
#             y = i * minimap_tile_size  # Von unten zeichnen
#             pygame.draw.rect(screen, color, (x, y, minimap_tile_size, minimap_tile_size))

def create_minimap_surface():
    minimap_surface = pygame.Surface((MINImap_width, MINImap_height))
    minimap_surface.fill((0, 0, 0))  # Hintergrund

    for i, row in enumerate(game_map):
        for j, col in enumerate(row):
            if col == 1:
                continue  # Wände weglassen
            color = (255, 255, 255)  # Nur begehbare Felder
            x = j * minimap_tile_size
            y = i * minimap_tile_size
            pygame.draw.rect(minimap_surface, color, (x, y, minimap_tile_size, minimap_tile_size))
    
    return minimap_surface

def draw_minimap():
    screen.blit(minimap_static, (WIDTH - MINImap_width, 0))

def numeral_input(prompt: str, legal_range_start: int, legal_range_end: int, error_msg: str = "Bitte eine Zahl eingeben.") -> int: # type: ignore
    pygame.init()
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    
    input_text = ""  # Speichert die Eingabe
    running = True

    while running:
        screen.fill((0, 0, 0))
        
        # Anzeige der Texte
        prompt_text = small_font.render(prompt, True, (200, 200, 255))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 4))

        text_surface = font.render(input_text, True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 3))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter-Taste gedrückt
                    try:
                        user_number = int(input_text)  # Konvertiere in eine Zahl
                        if user_number <= legal_range_end and user_number >= legal_range_start:
                            return user_number
                        else:
                            input_text = f"Number must be between {legal_range_start} and {legal_range_end}."
                    except ValueError:
                        input_text = error_msg  # Fehlermeldung anzeigen
                elif event.key == pygame.K_BACKSPACE:  # Rücktaste gedrückt
                    input_text = input_text[:-1]
                else:
                    if event.unicode.isdigit():  # Nur Zahlen zulassen
                        input_text += event.unicode

def start_menu():
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    running = True
    
    def map_menu() -> bool:
        def generated_map() -> bool:
            try:
                import mazegenerator as mg
                global game_map, map_width, map_height
                maze_size = numeral_input("Please enter the maze size (1-100):", legal_range_start = 1, legal_range_end = 100)
                
                game_map = mg.getMaze(maze_size)
                return True
            
            except ImportError:
                running = False
                while running:
                    screen.fill((0, 0, 0))
                    error_text = small_font.render("The file 'mazegenerator.py' was not found. To return to previous menu press any key.", True, (255, 255, 255))
                    screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 3))
                    pygame.display.flip()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            running = False

            return False

        def own_map():
            try:
                import maze # type: ignore
                global game_map, map_width, map_height
                
                game_map = maze.game_map
                map_width = len(game_map[0])
                map_height = len(game_map)
                return True
            except ImportError:
                running = False
                while running:
                    screen.fill((0, 0, 0))
                    error_text = small_font.render("The file 'maze.py' was not found. To return to previous menu press any key.", True, (255, 255, 255))
                    screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 3))
                    pygame.display.flip()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            running = False
        
        running = True
        while running:
            screen.fill((0, 0, 0))   
            title_text = font.render("Maze Switcher", True, (255, 255, 255))
            
            own_map_text = small_font.render("Press [O] for own map", True, (255, 255, 255))
            generated_map_text = small_font.render("Press [G] for generated maze", True, (255, 255, 255))
            return_to_last_menu_text = small_font.render("Press [R] or [ESC] to return", True, (255, 255, 255))
            
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
            screen.blit(own_map_text, (WIDTH // 2 - own_map_text.get_width() // 2, HEIGHT // 2))
            screen.blit(generated_map_text, (WIDTH // 2 - generated_map_text.get_width() // 2, HEIGHT // 2 + 50))
            screen.blit(return_to_last_menu_text, (WIDTH // 2 - return_to_last_menu_text.get_width() // 2, HEIGHT // 2 + 100))
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o or event.key == pygame.K_0:
                        if own_map():
                            return True
                    elif event.key == pygame.K_g:
                        if generated_map():
                            return True
                    elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                        running = False
                
        return False

    while running:
        screen.fill((0, 0, 0))
        title_text = font.render("Enti 3D", True, (200, 200, 255))
        
        start_text = small_font.render("Press [S] to enter Map Menu", True, (255, 255, 255))
        quit_text = small_font.render("Press [Q] to quit", True, (255, 255, 255))

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if map_menu():
                        running = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def menu():
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    running = True

    while running:
        screen.fill((0, 0, 0))
        title_text = font.render("Enti 3D", True, (200, 200, 255))
        
        start_text = small_font.render("Press [S] to return", True, (255, 255, 255))
        quit_text = small_font.render("Press [Q] to quit", True, (255, 255, 255))

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    running = False  # Spiel startet
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# === MAIN LOOP ===
start_menu()

minimap_static = create_minimap_surface()
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = math.cos(player_angle) * move_speed
    dy = math.sin(player_angle) * move_speed

    new_x, new_y = player_x, player_y
    if keys[pygame.K_w]:
        new_x += dx
        new_y += dy
    if keys[pygame.K_s]:
        new_x -= dx
        new_y -= dy
    if keys[pygame.K_ESCAPE]:
        menu()

    # print(f"Attempting move to ({new_x:.2f}, {player_y:.2f})")
    if can_move(new_x, player_y):
        player_x = new_x
    # print(f"Attempting move to ({player_x:.2f}, {new_y:.2f})")
    if can_move(player_x, new_y):
        player_y = new_y

    if keys[pygame.K_a]: player_angle -= rot_speed
    if keys[pygame.K_d]: player_angle += rot_speed

    distances = cast_rays(screen, player_x, player_y, player_angle)
    draw_walls(distances)
    draw_minimap()
    draw_player()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
