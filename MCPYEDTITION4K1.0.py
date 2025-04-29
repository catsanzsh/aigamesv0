from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import PerlinNoise
import random

# Initialize Ursina application
app = Ursina()
window.title = 'Minecraft 1.0 Clone'
window.borderless = False
window.fullscreen = False
# window.exit_button.visible = False  # Commented for debugging

# Debug message
print_on_screen("Game is running", position=(0, 0), scale=2, duration=5)

# Block types
block_types = {
    'grass': color.green,
    'dirt': color.brown,
    'stone': color.gray,
    'wood': color.rgb(139, 69, 19),
    'leaves': color.rgb(0, 100, 0),
    'water': color.blue
}

# Simplified terrain generation
terrain_size = 20
block_size = 1
pnoise = PerlinNoise()

def create_voxel(position, block_type):
    voxel = Entity(
        model='cube',
        color=block_types[block_type],
        scale=block_size,
        position=position,
        collider='box'
    )
    voxel.block_type = block_type
    return voxel

def generate_terrain():
    for x in range(-terrain_size // 2, terrain_size // 2):
        for z in range(-terrain_size // 2, terrain_size // 2):
            height = int((pnoise([x * 0.1, z * 0.1]) + 1) * 10)
            for y in range(0, height + 1):
                if y == height:
                    block_type = 'grass'
                elif y >= height - 3:
                    block_type = 'dirt'
                else:
                    block_type = 'stone'
                create_voxel(Vec3(x, y, z), block_type)

# Player setup
player = FirstPersonController()
player.position = Vec3(0, 25, 0)  # Raised to ensure visibility
print(f"Player position: {player.position}")

# Sky
sky = Sky(color=color.cyan)

# Generate terrain and run
generate_terrain()
app.run()
