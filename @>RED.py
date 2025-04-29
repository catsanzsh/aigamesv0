from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import PerlinNoise
import random

app = Ursina()
window.title = 'Minecraft 1.0 Clone'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False

# Define block types with solid colors
block_types = {
    'grass': color.green,
    'dirt': color.brown,
    'stone': color.gray,
    'wood': color.rgb(139, 69, 19),
    'leaves': color.rgb(0, 100, 0)
}

# Define tools
tools = {
    'wooden_pickaxe': {'speed': 2, 'suitable_for': ['stone']}
}

# Terrain parameters
terrain_size = 20
block_size = 1
pnoise = PerlinNoise()

# Inventory system
inventory = {block: 0 for block in block_types}
inventory.update({tool: 0 for tool in tools})
selected_item = 'grass'

# Variables for block breaking
targeted_block = None
previous_target = None

# Time for day-night cycle
time_of_day = 0

# Function to create a voxel
def create_voxel(position, block_type):
    hardness_values = {
        'grass': 1,
        'dirt': 1,
        'stone': 3,
        'wood': 2,
        'leaves': 1
    }
    voxel = Entity(
        model='cube',
        color=block_types[block_type],
        scale=block_size,
        position=position,
        collider='box'
    )
    voxel.block_type = block_type
    voxel.hardness = hardness_values[block_type]
    voxel.breaking_progress = 0
    return voxel

# Generate terrain
def generate_terrain():
    for x in range(-terrain_size//2, terrain_size//2):
        for z in range(-terrain_size//2, terrain_size//2):
            height = int((pnoise([x * 0.1, z * 0.1]) + 1) * 5)
            for y in range(height + 1):
                if y == height:
                    block_type = 'grass'
                elif y >= height - 3:
                    block_type = 'dirt'
                else:
                    block_type = 'stone'
                create_voxel(Vec3(x, y, z), block_type)
            if random.random() < 0.05:
                tree_height = random.randint(3, 5)
                for ty in range(height + 1, height + 1 + tree_height):
                    create_voxel(Vec3(x, ty, z), 'wood')
                for lx in range(-1, 2):
                    for lz in range(-1, 2):
                        for ly in range(tree_height - 1, tree_height + 1):
                            create_voxel(Vec3(x + lx, height + 1 + ly, z + lz), 'leaves')

# Player setup
player = FirstPersonController()
player.position = Vec3(0, 10, 0)
player.gravity = 0.5
player.health = 20  # Minecraft-like health (20 half-hearts)

# Mob class with enhanced AI
class Mob(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.red,
            scale=1,
            position=position
        )
        self.speed = 2
        self.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized()
        self.wander_timer = random.uniform(1, 3)
        self.attack_cooldown = 1
        self.attack_timer = 0

    def update(self):
        if distance(self, player) < 10:
            direction = (player.position - self.position).normalized()
            self.position += direction * self.speed * time.dt
            if distance(self, player) < 1:
                if self.attack_timer <= 0:
                    player.health -= 1
                    self.attack_timer = self.attack_cooldown
                else:
                    self.attack_timer -= time.dt
        else:
            self.wander_timer -= time.dt
            if self.wander_timer <= 0:
                self.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized()
                self.wander_timer = random.uniform(1, 3)
            self.position += self.direction * self.speed * time.dt
            self.attack_timer = 0

# Spawn mobs
for _ in range(5):
    Mob(position=Vec3(random.uniform(-10,10), 5, random.uniform(-10,10)))

# Sky for day-night cycle
sky = Sky(color=color.cyan)

# UI elements
selected_text = Text(text=f'Selected: {selected_item} ({inventory[selected_item]})', position=(-0.5,0.4), scale=2)
health_text = Text(text=f'Health: {player.health}', position=(-0.5,0.45), scale=2)

# Input handler
def input(key):
    global selected_item
    if key == '1':
        selected_item = 'grass'
    elif key == '2':
        selected_item = 'dirt'
    elif key == '3':
        selected_item = 'stone'
    elif key == '4':
        selected_item = 'wood'
    elif key == '5':
        selected_item = 'leaves'
    elif key == '6':
        selected_item = 'wooden_pickaxe'
    elif key == 'c' and inventory['wood'] >= 3:
        inventory['wood'] -= 3
        inventory['wooden_pickaxe'] += 1
    elif key == 'right mouse down' and selected_item in block_types and inventory[selected_item] > 0:
        hit_info = raycast(camera.position, camera.forward, distance=5)
        if hit_info.hit:
            new_pos = hit_info.entity.position + hit_info.normal
            create_voxel(new_pos, selected_item)
            inventory[selected_item] -= 1

# Update function
def update():
    global targeted_block, previous_target, time_of_day
    # Raycast for block breaking
    hit_info = raycast(camera.position, camera.forward, distance=5)
    if hit_info.hit and hasattr(hit_info.entity, 'block_type'):
        targeted_block = hit_info.entity
    else:
        targeted_block = None
    if targeted_block != previous_target:
        if previous_target:
            previous_target.breaking_progress = 0
        previous_target = targeted_block
    if held_keys['left mouse'] and targeted_block:
        speed = 1
        if selected_item in tools and targeted_block.block_type in tools[selected_item]['suitable_for']:
            speed = tools[selected_item]['speed']
        targeted_block.breaking_progress += speed * time.dt
        if targeted_block.breaking_progress >= targeted_block.hardness:
            inventory[targeted_block.block_type] += 1
            destroy(targeted_block)
            targeted_block = None
            previous_target = None
    # Player death
    if player.health <= 0:
        player.health = 20
        player.position = Vec3(0, 10, 0)
    # Day-night cycle
    time_of_day += time.dt / 100
    if time_of_day > 1:
        time_of_day = 0
    if time_of_day < 0.25:
        sky.color = color.cyan
    elif time_of_day < 0.5:
        sky.color = color.orange
    elif time_of_day < 0.75:
        sky.color = color.black
    else:
        sky.color = color.orange
    # Update UI
    health_text.text = f'Health: {player.health}'
    if selected_item in block_types:
        selected_text.text = f'Selected: {selected_item} ({inventory[selected_item]})'
    else:
        selected_text.text = f'Selected: {selected_item}'

# Generate terrain and run
generate_terrain()
app.run()
