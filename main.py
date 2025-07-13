from dataclasses import dataclass
import pygame
import math
import sys

# Initial default game map
# This will be replaced if the user chooses a generated or custom map
initial_game_map = [
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

# === CLASSES ===

@dataclass
class Colors:
    """A dataclass to hold common color tuples for easy access."""
    black: tuple[int, int, int] = (0, 0, 0)
    white: tuple[int, int, int] = (255, 255, 255)
    gray: tuple[int, int, int] = (75, 75, 75)
    light_gray: tuple[int, int, int] = (200, 200, 200)
    dark_gray: tuple[int, int, int] = (50, 50, 50)
    yellow: tuple[int, int, int] = (255, 255, 0)
    green: tuple[int, int, int] = (0, 255, 0)

class Size:
    """A simple class to hold width, height, and minimum dimension."""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.min = min(width, height)
        
class World:
    """Manages the game map and provides map-related utilities."""
    def __init__(self, game_map: list[list[int]], tile_size: int):
        self.game_map = game_map
        self.size = Size(len(game_map[0]), len(game_map)) # Dimensions of the map in tiles
        self.tile_size = tile_size # Size of a single tile in pixels
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Checks if a given tile coordinate (x, y) is within bounds and is a walkable (non-wall) tile."""
        if 0 <= y < self.size.height and 0 <= x < self.size.width:
            return self.game_map[y][x] == 0
        return False

@dataclass
class Information:
    """Holds general Pygame display and time information."""
    screen: pygame.Surface   # The main display surface
    info: pygame.display.Info # Display resolution info # type: ignore
    clock: pygame.time.Clock  # Pygame clock for FPS control
    size: Size                # Current screen width and height
    fps: int = 60             # Frames per second target
    
@dataclass
class Player:
    """Represents the player's state and handles movement."""
    x: float
    y: float
    angle: float      # Player's current viewing angle in radians
    move_speed: float # Speed of linear movement
    rot_speed: float  # Speed of angular rotation
    radius: float     # Collision radius for the player
    
    def find_spawn_point(self, world: World):
        """
        Sets the player in the center of the first available free tile found.
        Searches from the inside of the map to avoid edges.
        """
        for wy in range(1, world.size.height - 1):  # Avoid map edges (1 tile in from border)
            for wx in range(1, world.size.width - 1):
                if world.game_map[wy][wx] == 0:  # Found a free cell (value 0)
                    # Correct calculation: (tile_index + 0.5) * tile_size to get center of tile
                    self.x = (wx + 0.5) * world.tile_size
                    self.y = (wy + 0.5) * world.tile_size
                    return # Spawn point found and set
        
        # Fallback if no suitable free spawn point is found (should ideally not be reached with valid maps)
        self.x = (world.size.width // 2 + 0.5) * world.tile_size
        self.y = (world.size.height // 2 + 0.5) * world.tile_size
        print("Warning: No free spawn point found, defaulting to map center.")
    
    def can_move(self, x: float, y: float, world: World) -> bool:
        """
        Checks if a proposed position (x, y) is valid for player movement.
        Considers player's radius for collision detection with walls.
        """
        # Check all four corners of the player's bounding box (defined by radius)
        # to ensure no part of the player overlaps with a wall.
        for dx_offset in (-self.radius, self.radius):
            for dy_offset in (-self.radius, self.radius):
                # Calculate the grid coordinates for the offset point
                gx = int((x + dx_offset) // world.tile_size)
                gy = int((y + dy_offset) // world.tile_size)
                
                # Check map bounds first: if any part of player is outside, movement is blocked
                if not (0 <= gx < world.size.width and 0 <= gy < world.size.height):
                    return False
                
                # Check if the tile at these grid coordinates is a wall
                if world.game_map[gy][gx] != 0:
                    return False # Movement blocked by a wall
        return True # Movement is allowed

    def move(self, info: Information, world: World):
        """
        Handles player movement based on keyboard input (W, S for forward/backward)
        and rotation (A, D for left/right). Includes collision detection.
        """
        keys = pygame.key.get_pressed() # Get current state of all keyboard keys
        
        # Calculate base movement vector based on player's angle
        dx = math.cos(self.angle) * self.move_speed
        dy = math.sin(self.angle) * self.move_speed

        new_x, new_y = self.x, self.y # Tentative new position
        
        # Apply linear movement
        if keys[pygame.K_w]: # Move forward
            new_x += dx
            new_y += dy
        if keys[pygame.K_s]: # Move backward
            new_x -= dx
            new_y -= dy
        
        # Check horizontal movement (X-axis) for collision independently
        if self.can_move(new_x, self.y, world):
            self.x = new_x # If no collision, update X position
        
        # Check vertical movement (Y-axis) for collision independently
        if self.can_move(self.x, new_y, world):
            self.y = new_y # If no collision, update Y position

        # Apply rotation
        if keys[pygame.K_a]: self.angle -= self.rot_speed # Rotate left
        if keys[pygame.K_d]: self.angle += self.rot_speed # Rotate right

@dataclass
class RaycastingConfig:
    """Configures the parameters for the raycasting engine."""
    fov: float          # Field of View in radians
    num_rays: int       # Number of rays to cast (determines horizontal resolution)
    max_depth: float    # Maximum distance a ray can travel before stopping
    
    def cast_rays(self, info: Information, player: Player, world: World) -> list[float]:
        """
        Casts rays from the player's position into the world to determine
        the distance to the nearest wall for each ray.
        """
        distances = []
        # Calculate the starting angle for raycasting based on player's current angle and FOV
        start_angle = player.angle - self.fov / 2

        for ray_idx in range(self.num_rays):
            # Calculate the angle for the current ray
            ray_angle = start_angle + ray_idx * (self.fov / self.num_rays)
            
            # Iterate through depth steps to find wall intersection
            for depth_step in range(1, int(self.max_depth) + 1): # +1 to include max_depth in checks
                # Calculate the world coordinates of the point along the ray
                tx = player.x + math.cos(ray_angle) * depth_step
                ty = player.y + math.sin(ray_angle) * depth_step
                
                # Convert world coordinates to grid (tile) coordinates
                gx = int(tx // world.tile_size)
                gy = int(ty // world.tile_size)
                
                # Check if the ray has gone outside the map boundaries
                if not (0 <= gx < world.size.width and 0 <= gy < world.size.height):
                    distances.append(self.max_depth) # Treat as hitting max depth
                    break # Stop casting this ray
                
                # Check if the current grid cell is a wall (value 1)
                if world.game_map[gy][gx] == 1:
                    # Calculate the true distance, correcting for fish-eye effect
                    # This projects the distance onto the player's view plane,
                    # preventing distortion at the edges of the FOV.
                    dist = depth_step * math.cos(player.angle - ray_angle)
                    distances.append(dist)
                    
                    # Optional: Draw ray on minimap for debugging/visualization (commented out by default)
                    # pygame.draw.line(info.screen, Colors.yellow, (player.x, player.y), (tx, ty), 1)
                    break # Ray hit a wall, stop casting this ray
            else:
                # If the ray reached max_depth without hitting any wall
                distances.append(self.max_depth)
        return distances

@dataclass
class Minimap:
    """Manages the drawing and state of the in-game minimap."""
    size: Size                      # Dimensions of the minimap surface in pixels
    tile_size: int                  # Size of a single tile on the minimap in pixels
    minimap_static: pygame.Surface = pygame.Surface((0, 0)) # Pre-rendered static minimap background
    
    def create_minimap_surface(self, world: World):
        """
        Creates and stores a static Pygame Surface representing the minimap background.
        This includes drawing walls and walkable paths.
        """
        # Create a new surface for the minimap
        minimap_surface = pygame.Surface((self.size.width, self.size.height))
        minimap_surface.fill(Colors.black)  # Fill background of minimap area

        # Iterate through the game map to draw each tile
        for i, row in enumerate(world.game_map):
            for j, col in enumerate(row):
                if col == 1:
                    # If it's a wall, draw it as a dark gray rectangle
                    color = Colors.dark_gray
                else:
                    # If it's a walkable path, draw it as a white rectangle
                    color = Colors.white
                
                # Calculate position for the current tile on the minimap surface
                x = j * self.tile_size
                y = i * self.tile_size
                
                pygame.draw.rect(minimap_surface, color, (x, y, self.tile_size, self.tile_size))
        
        self.minimap_static = minimap_surface # Store the created surface

    def draw_minimap(self, info: Information):
        """Draws the static minimap background onto the main game screen."""
        # Blit (copy) the pre-rendered static minimap surface to the main screen.
        # It's positioned in the top-right corner of the screen.
        info.screen.blit(self.minimap_static, (info.size.width - self.size.width, 0))

    def draw_player_on_minimap(self, info: Information, player: Player, world: World):
        """
        Draws the player's position and direction on top of the minimap.
        """
        # Calculate player's position relative to the minimap's coordinate system
        px_on_minimap = (player.x / world.tile_size) * self.tile_size
        py_on_minimap = (player.y / world.tile_size) * self.tile_size
        
        # Calculate the absolute screen coordinates where the minimap is drawn
        minimap_screen_x = info.size.width - self.size.width
        minimap_screen_y = 0
        
        # Draw the player as a green circle on the minimap
        pygame.draw.circle(info.screen, Colors.green, 
                           (int(minimap_screen_x + px_on_minimap), int(minimap_screen_y + py_on_minimap)), 
                           int(self.tile_size * 0.5)) # Player icon size on minimap
        
        # Draw a yellow line to indicate player's viewing direction
        line_length = self.tile_size * 1.5 # Length of the direction line
        line_end_x = px_on_minimap + math.cos(player.angle) * line_length
        line_end_y = py_on_minimap + math.sin(player.angle) * line_length
        
        pygame.draw.line(info.screen, Colors.yellow,
                         (int(minimap_screen_x + px_on_minimap), int(minimap_screen_y + py_on_minimap)),
                         (int(minimap_screen_x + line_end_x), int(minimap_screen_y + line_end_y)),
                         2) # Line thickness

@dataclass
class DrawConfig:
    """Configuration for drawing 3D scene elements like walls and floor."""
    wall_start_shade: int = 85  # Minimum shade for walls (darkest)
    wall_end_shade: int = 255   # Maximum shade for walls (brightest)
    
    floor_start_shade: int = 85 # Minimum shade for floor
    floor_end_shade: int = 170  # Maximum shade for floor
    
    def draw_floor(self, info: Information):
        """Draws the floor with a gradient effect, simulating depth."""
        for i in range(info.size.height // 2, info.size.height):  # Iterate from horizon to bottom of screen
            # Calculate shade: closer to horizon (info.size.height // 2) is darker, closer to bottom is brighter
            shade = min(255, int((i - info.size.height // 2) / (info.size.height // 2) * self.floor_end_shade) + self.floor_start_shade)
            # Draw a horizontal line for each row of pixels
            pygame.draw.line(info.screen, (shade, shade, shade), (0, i), (info.size.width, i)) # FIX: use info.size.width

    def draw_walls(self, info: Information, raycasting_config: RaycastingConfig, world: World, distances: list[float]):
        """
        Draws the 3D walls based on the distances calculated by raycasting.
        Applies shading for depth perception.
        """
        info.screen.fill(Colors.dark_gray) # Fill the top half (sky/ceiling) with a base color
        
        # Draw a distinct ceiling area (optional, can be same as background)
        pygame.draw.rect(info.screen, Colors.gray, (0, 0, info.size.width, info.size.height // 2))
        
        self.draw_floor(info) # Draw the floor beneath the walls

        ray_width = info.size.width // len(distances) # Width of each vertical wall strip
        
        for i, dist in enumerate(distances):
            # Calculate the apparent height of the wall strip on screen
            wall_h = world.tile_size * info.size.height / (dist + 0.0001) # Add small value to prevent division by zero
            
            # Calculate the shade of the wall strip based on its distance
            # Closer walls are brighter (higher shade value), farther walls are darker
            shade = max(0, min(255, self.wall_end_shade - int(dist / raycasting_config.max_depth * self.wall_end_shade)))
            color = (shade, shade, shade) # Grayscale color based on shade
            
            x = i * ray_width # X-coordinate of the current wall strip
            y = info.size.height // 2 - wall_h // 2 # Y-coordinate (centered vertically)

            # If the ray hit the max depth (meaning no wall was found within max_depth),
            # draw a black strip to represent empty space in the distance.
            if dist >= raycasting_config.max_depth:
                pygame.draw.rect(info.screen, Colors.black, (x, y, ray_width, wall_h))
            else:
                # Otherwise, draw the shaded wall strip
                pygame.draw.rect(info.screen, color, (x, y, ray_width, wall_h))


# === CORE PYGAME INITIALIZATION ===

def init_pygame() -> Information:
    """Initializes Pygame modules and sets up the display. Returns core info."""
    pygame.init()
    # Set display mode to fullscreen. (0,0) tells Pygame to use current desktop resolution.
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    info = pygame.display.Info() # Get information about the current display mode
    clock = pygame.time.Clock() # Create a clock object to control frame rate

    WIDTH, HEIGHT = info.current_w, info.current_h # Get actual screen dimensions
    
    # Return an Information dataclass instance with all relevant setup data
    return Information(screen, info, clock, Size(WIDTH, HEIGHT))

# === GENERAL UI / MENU FUNCTIONS ===

def numeral_input(info: Information, prompt: str, legal_range_start: int, legal_range_end: int, error_msg: str = "Please enter a number.") -> int:
    """
    Handles numerical input from the user via the Pygame UI.
    Displays a prompt and accepts digit input until Enter is pressed.
    Ensures the input is within a specified range.
    """
    font = pygame.font.SysFont(None, 72) # Font for input text
    small_font = pygame.font.SysFont(None, 36) # Font for prompt text
    
    input_text = ""  # String to build the user's numerical input
    
    while True: # Loop indefinitely until valid input or quit
        info.screen.fill(Colors.black) # Clear the screen for redrawing
        
        # Render and blit the prompt text
        prompt_text_surface = small_font.render(prompt, True, Colors.light_gray)
        info.screen.blit(prompt_text_surface, (info.size.width // 2 - prompt_text_surface.get_width() // 2, info.size.height // 4))

        # Render and blit the current user input text
        input_text_surface = font.render(input_text, True, Colors.white)
        info.screen.blit(input_text_surface, (info.size.width // 2 - input_text_surface.get_width() // 2, info.size.height // 3))

        pygame.display.flip() # Update the entire display to show changes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Exit if user closes the window
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # User pressed Enter
                    try:
                        user_number = int(input_text)  # Attempt to convert input to integer
                        if legal_range_start <= user_number <= legal_range_end:
                            return user_number # Valid input, return it
                        else:
                            # Input out of range, update input_text to show error
                            input_text = f"Number must be between {legal_range_start} and {legal_range_end}."
                    except ValueError:
                        # Input is not a valid number, show error message
                        input_text = error_msg
                elif event.key == pygame.K_BACKSPACE:  # User pressed Backspace
                    input_text = input_text[:-1] # Remove the last character
                else:
                    if event.unicode.isdigit():  # Only append digits to the input string
                        input_text += event.unicode

def menu(info: Information):
    """
    Displays the in-game pause menu with options to return to game or quit.
    Called when ESC is pressed during gameplay.
    """
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    running = True

    while running:
        info.screen.fill(Colors.black) # Clear screen for menu drawing
        title_text = font.render("Enti 3D", True, Colors.light_gray)
        
        # Options text
        return_text = small_font.render("Press [S] to return", True, Colors.white)
        quit_text = small_font.render("Press [Q] to quit", True, Colors.white)

        # Blit all text surfaces to the screen
        info.screen.blit(title_text, (info.size.width // 2 - title_text.get_width() // 2, info.size.height // 3))
        info.screen.blit(return_text, (info.size.width // 2 - return_text.get_width() // 2, info.size.height // 2))
        info.screen.blit(quit_text, (info.size.width // 2 - quit_text.get_width() // 2, info.size.height // 2 + 50))

        pygame.display.flip() # Update display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Quit game if window is closed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    running = False  # Exit menu loop, return to game
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit() # Quit game immediately

def display_error_message(info: Information, message: str):
    """
    Displays a temporary error message on the screen and waits for any key press to dismiss it.
    Used for feedback when map files are not found.
    """
    small_font = pygame.font.SysFont(None, 36)
    while True:
        info.screen.fill(Colors.black) # Clear screen
        error_text_surface = small_font.render(message, True, Colors.white)
        info.screen.blit(error_text_surface, (info.size.width // 2 - error_text_surface.get_width() // 2, info.size.height // 3))
        pygame.display.flip() # Update display
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return # Exit error message on any key press

def map_selection_menu(info: Information) -> list[list[int]] | None:
    """
    Presents a menu for selecting between a custom 'maze.py' map or a generated map.
    Returns the selected game map (list of lists) or None if the user cancels.
    """
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    
    while True: # Loop until a map is chosen or user returns
        info.screen.fill(Colors.black) # Clear screen for menu
        title_text = font.render("Maze Switcher", True, Colors.white)
        
        # Options text
        own_map_text = small_font.render("Press [O] for own map", True, Colors.white)
        generated_map_text = small_font.render("Press [G] for generated maze", True, Colors.white)
        return_to_last_menu_text = small_font.render("Press [R] or [ESC] to return", True, Colors.white)
        
        # Blit options to screen
        info.screen.blit(title_text, (info.size.width // 2 - title_text.get_width() // 2, info.size.height // 3))
        info.screen.blit(own_map_text, (info.size.width // 2 - own_map_text.get_width() // 2, info.size.height // 2))
        info.screen.blit(generated_map_text, (info.size.width // 2 - generated_map_text.get_width() // 2, info.size.height // 2 + 50))
        info.screen.blit(return_to_last_menu_text, (info.size.width // 2 - return_to_last_menu_text.get_width() // 2, info.size.height // 2 + 100))
        
        pygame.display.flip() # Update display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o or event.key == pygame.K_0:
                    try:
                        import maze # type: ignore # Attempt to import custom maze file
                        return maze.game_map # Return the loaded map
                    except ImportError:
                        display_error_message(info, "The file 'maze.py' was not found. Press any key to return.")
                elif event.key == pygame.K_g:
                    try:
                        import mazegenerator as mg # Attempt to import maze generator
                        # Get maze size from user via input UI
                        maze_size = numeral_input(info, "Please enter the maze size (1-100):", legal_range_start = 1, legal_range_end = 100)
                        return mg.getMaze(maze_size) # Return the generated map
                    except ImportError:
                        display_error_message(info, "The file 'mazegenerator.py' was not found. Press any key to return.")
                elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                    return None # User chose to return without selecting a map

def start_game_menu(info: Information) -> list[list[int]]:
    """
    Displays the initial game start menu. Allows the user to enter the map selection
    menu or quit the game. Returns the final chosen game map.
    """
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    
    while True: # Loop until game starts or quits
        info.screen.fill(Colors.black) # Clear screen for menu
        title_text = font.render("Enti 3D", True, Colors.light_gray)
        
        # Options text
        start_text = small_font.render("Press [S] to enter Map Menu", True, Colors.white)
        quit_text = small_font.render("Press [Q] to quit", True, Colors.white)

        # Blit options to screen
        info.screen.blit(title_text, (info.size.width // 2 - title_text.get_width() // 2, info.size.height // 3))
        info.screen.blit(start_text, (info.size.width // 2 - start_text.get_width() // 2, info.size.height // 2))
        info.screen.blit(quit_text, (info.size.width // 2 - quit_text.get_width() // 2, info.size.height // 2 + 50))

        pygame.display.flip() # Update display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    chosen_map = map_selection_menu(info) # Go to map selection
                    if chosen_map is not None:
                        return chosen_map # A map was successfully chosen, return it to start the game
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit() # User chose to quit

# === GAME COMPONENT SETUP FUNCTIONS ===

def setup_player(world: World) -> Player:
    """Creates and initializes the player object with a spawn point on the map."""
    new_player = Player(0, 0, 0, 3, 0.05, 10) # Initial dummy values for x, y, angle
    new_player.find_spawn_point(world) # Find actual spawn point on the map
    return new_player

def setup_minimap(info: Information, world: World) -> Minimap:
    """
    Configures and creates the minimap object.
    Calculates minimap dimensions and pre-renders its static background.
    """
    minimap_size_base = info.size.min // 4 # Base size relative to smallest screen dimension
    
    # Calculate tile size for the minimap, ensuring it fits the largest map dimension
    minimap_tile_size = minimap_size_base // max(world.size.width, world.size.height)
    
    # Adjust minimap size if the map is very large
    # This logic aims to make the minimap larger for big maps (original code used world.size.min > 30)
    if world.size.min > 30: 
        minimap_size_base *= 2 # Scale up the base size
        
    # Final dimensions of the minimap surface
    minimap_width = minimap_tile_size * world.size.width
    minimap_height = minimap_tile_size * world.size.height

    # Create the Minimap instance
    minimap = Minimap(Size(minimap_width, minimap_height), minimap_tile_size)
    minimap.create_minimap_surface(world) # Pre-render the static map background
    return minimap

def setup_resolution_menu(info: Information) -> int:
    """
    Sets up the rendering resolution, which affects the number of rays cast.
    """
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    
    res = 100
    
    while True: # Loop until a map is chosen or user returns
        info.screen.fill(Colors.black) # Clear screen for menu
        title_text = font.render("Display Resolution", True, Colors.white)
        
        # Options text
        ten_text = small_font.render("Press [1] for 10%", True, Colors.white)
        fifty_text = small_font.render("Press [5] for 50%", True, Colors.white)
        full_text = small_font.render("Press [0] for 100%", True, Colors.white)
        custom_text = small_font.render("Or press [C] for custom", True, Colors.white)
        return_to_last_menu_text = small_font.render("Press [R] or [ESC] to return", True, Colors.white)
        
        # Blit options to screen
        info.screen.blit(title_text, (info.size.width // 2 - title_text.get_width() // 2, info.size.height // 3))
        info.screen.blit(ten_text, (info.size.width // 2 - ten_text.get_width() // 2, info.size.height // 2))
        info.screen.blit(fifty_text, (info.size.width // 2 - fifty_text.get_width() // 2, info.size.height // 2 + 50))
        info.screen.blit(full_text, (info.size.width // 2 - full_text.get_width() // 2, info.size.height // 2 + 100))
        info.screen.blit(custom_text, (info.size.width // 2 - custom_text.get_width() // 2 + 150, info.size.height // 2 + 200))
        info.screen.blit(return_to_last_menu_text, (info.size.width // 2 - return_to_last_menu_text.get_width() // 2, info.size.height // 2 + 250))
        
        pygame.display.flip() # Update display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o or event.key == pygame.K_1:
                    return 10
                elif event.key == pygame.K_5:
                    return 50
                elif event.key == pygame.K_5:
                    return 50
                elif event.key == pygame.K_c:
                    return numeral_input(info, "Enter a custom resolution percentage (1-100):", legal_range_start=1, legal_range_end=100)
                elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                    break;
    # This value determines the detail of the 3D scene (higher = more rays = more detail)

def setup_raycasting(info: Information, world: World, res: int) -> RaycastingConfig:
    """Creates and configures the raycasting parameters based on world and resolution."""
    fov = math.pi / 2.8 # Field of View (e.g., ~64 degrees)
    num_rays = int(info.size.width * res / 100) # Number of rays directly scales with screen width and resolution
    tile_depth = world.tile_size / 1.2 # Base depth derived from tile size
    
    # Calculate the maximum ray casting depth:
    # If map height is small, depth is relative to map size, otherwise a fixed multiple of tile_depth.
    if world.size.height < 10:
        max_depth = tile_depth * world.size.height / 1.5
    else:
        max_depth = tile_depth * 10
    
    # Return the configured RaycastingConfig object
    return RaycastingConfig(fov, num_rays, max_depth)

# === MAIN GAME LOOP ===

def main_loop(info: Information, world: World, player: Player, raycasting_config: RaycastingConfig, minimap: Minimap, draw_config: DrawConfig):
    """
    The main game loop, responsible for handling events, updating game state,
    and rendering the scene each frame.
    """
    running = True # Flag to control the game loop
    clock = info.clock # Pygame clock for frame rate control

    while running:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # Set flag to exit game loop if window is closed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu(info) # Call the pause menu when ESC is pressed

        player.move(info, world)  # Update player's position and angle based on input

        # Perform raycasting to get distances to walls from the player's perspective
        distances = raycasting_config.cast_rays(info, player, world)

        # === RENDERING ===
        info.screen.fill(Colors.black)  # Clear the entire screen (can be optimized if draw_walls fills it completely)
        draw_config.draw_walls(info, raycasting_config, world, distances) # Draw the 3D first-person view of walls and floor
        minimap.draw_minimap(info) # Draw the static minimap background
        minimap.draw_player_on_minimap(info, player, world) # Draw the dynamic player icon on the minimap

        pygame.display.flip() # Update the entire screen to show the rendered frame
        clock.tick(info.fps)  # Control the frame rate to target FPS

    pygame.quit() # Uninitialize Pygame modules
    sys.exit() # Exit the application

# === APPLICATION ENTRY POINT ===
if __name__ == "__main__":
    # 1. Initialize Pygame and gather essential display information
    information = init_pygame()
    
    # 2. Display the initial start menu and get the chosen game map from the user.
    # This function handles quitting the application if the user chooses to.
    chosen_game_map = start_game_menu(information) 
    
    # 3. Define the constant tile size (in pixels)
    TILE_SIZE = 64 
    
    # 4. Create the World object, encapsulating the game map and tile size
    world = World(chosen_game_map, TILE_SIZE)

    # 5. Set up other core game components based on the chosen map and display info
    resolution = setup_resolution_menu(information)          # Get rendering quality setting
    player = setup_player(world)                        # Initialize player, finding a spawn point on the map
    minimap = setup_minimap(information, world)         # Configure and create the minimap
    raycasting_config = setup_raycasting(information, world, resolution) # Set up raycasting parameters
    draw_config = DrawConfig()                          # Initialize drawing configurations (colors, shading)

    # 6. Start the main game loop, passing all configured game objects
    main_loop(information, world, player, raycasting_config, minimap, draw_config)

