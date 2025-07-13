Hier ein kleiner ausschnitt :D

``` python
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
```
