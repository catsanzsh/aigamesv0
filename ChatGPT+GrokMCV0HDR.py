from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()
window.title = 'Minecraft 1.0 Test'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False

# Simple terrain generation
terrain_size = 20
block_size = 1

def create_voxel(position):
    voxel = Button(
        position=position,
        model='cube',
        color=color.rgb(50 + random.randint(-5,5), 200 + random.randint(-5,5), 50 + random.randint(-5,5)),
        scale=block_size,
        origin_y=0.5,
        highlight_color=color.lime
    )

    def input(key):
        if voxel.hovered:
            if key == 'right mouse down':
                create_voxel(voxel.position + mouse.normal)
            if key == 'left mouse down':
                destroy(voxel)

    voxel.input = input

# Generate initial flat terrain
for x in range(-terrain_size//2, terrain_size//2):
    for z in range(-terrain_size//2, terrain_size//2):
        create_voxel(Vec3(x, 0, z))

# Basic player controller
player = FirstPersonController()
player.gravity = 0.5

app.run()
