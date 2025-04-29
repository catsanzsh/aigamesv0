from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import PerlinNoise
import random

app = Ursina()
window.title = 'Minecraft 1.0 Clone'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False

# Define block types with solid colors (no PNGs)
block_types = {
    'grass': color.green,
    'dirt': color.brown,
    'stone': color.gray,
    'wood': color.rgb(139, 69, 19),  # Brown for wood
    'leaves': color.rgb(0, 100, 0)   # Dark green for leaves
}

# Terrain parameters
terrain_size = 20  # Small size for performance
block_size = 1
pnoise = PerlinNoise()  # For natural terrain height variation

# Inventory system (tracks block counts)
inventory = {block: 0 for block in block_types}
selected_block = 'grass'  # Default selected block for placement

# Function to create a voxel (block)
def create_voxel(position, block_type):
    voxel = Entity(
        model='cube',
        color=block_types[block_type],
        scale=block_size,
        position=position,
        collider='box'  # Enables collision with the player
    )
    voxel.block_type = block_type  # Store block type for interaction
    return voxel

# Generate terrain with height variation and trees
def generate_terrain():
    for x in range(-terrain_size//2, terrain_size//2):
        for z in range(-terrain_size//2, terrain_size//2):
            # Calculate height using Perlin noise
            height = int((pnoise([x * 0.1, z * 0.1]) + 1) * 5)
            for y in range(height + 1):
                if y == height:
                    block_type = 'grass'  # Top layer
                elif y >= height - 3:
                    block_type = 'dirt'   # Middle layers
                else:
                    block_type = 'stone'  # Deep layers
                create_voxel(Vec3(x, y, z), block_type)
            # Add trees with 5% probability
            if random.random() < 0.05:
                tree_height = random.randint(3, 5)
                for ty in range(height + 1, height + 1 + tree_height):
                    create_voxel(Vec3(x, ty, z), 'wood')
                # Add leaves around the top of the tree
                for lx in range(-1, 2):
                    for lz in range(-1, 2):
                        for ly in range(tree_height - 1, tree_height + 1):
                            create_voxel(Vec3(x + lx, height + 1 + ly, z + lz), 'leaves')

# Player setup with first-person controls
player = FirstPersonController()
player.position = Vec3(0, 10, 0)  # Start above terrain
player.gravity = 0.5

# Simple mob class for basic AI behavior
class Mob(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.red,  # Red cube for mobs
            scale=1,
            position=position
        )
        self.speed = 2
        self.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized()

    def update(self):
        # Move towards player if within 10 units, else move randomly
        if distance(self, player) < 10:
            direction = (player.position - self.position).normalized()
            self.position += direction * self.speed * time.dt
        else:
            if random.random() < 0.01:
                self.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized()
            self.position += self.direction * self.speed * time.dt

# Spawn a few mobs at random positions
for _ in range(5):
    mob = Mob(position=Vec3(random.uniform(-10,10), 5, random.uniform(-10,10)))

# Add a sky background
Sky(color=color.cyan)

# Text to display the currently selected block
selected_text = Text(text=f'Selected: {selected_block}', position=(-0.5,0.4), scale=2)

# Input handler for block interaction and selection
def input(key):
    global selected_block
    # Select block type with number keys
    if key == '1':
        selected_block = 'grass'
        selected_text.text = f'Selected: {selected_block}'
    elif key == '2':
        selected_block = 'dirt'
        selected_text.text = f'Selected: {selected_block}'
    elif key == '3':
        selected_block = 'stone'
        selected_text.text = f'Selected: {selected_block}'
    elif key == '4':
        selected_block = 'wood'
        selected_text.text = f'Selected: {selected_block}'
    elif key == '5':
        selected_block = 'leaves'
        selected_text.text = f'Selected: {selected_block}'
    # Break block with left mouse click
    elif key == 'left mouse down':
        hit_info = raycast(camera.position, camera.forward, distance=5)
        if hit_info.hit and hasattr(hit_info.entity, 'block_type'):
            inventory[hit_info.entity.block_type] += 1
            destroy(hit_info.entity)
    # Place block with right mouse click if available in inventory
    elif key == 'right mouse down' and inventory[selected_block] > 0:
        hit_info = raycast(camera.position, camera.forward, distance=5)
        if hit_info.hit:
            new_pos = hit_info.entity.position + hit_info.normal
            create_voxel(new_pos, selected_block)
            inventory[selected_block] -= 1

# Generate the terrain
generate_terrain()

app.run()
