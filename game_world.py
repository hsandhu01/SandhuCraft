import pyglet
from pyglet.gl import *
import random
import noise

class Block:
    def __init__(self, position, block_type):
        self.position = position
        self.block_type = block_type

class Chunk:
    def __init__(self, position):
        self.position = position
        self.blocks = {}
        self.batch = pyglet.graphics.Batch()
        self.vertex_lists = []

    def add_block(self, position, block_type):
        local_pos = (position[0] % 16, position[1], position[2] % 16)
        self.blocks[local_pos] = Block(position, block_type)
        self.rebuild_mesh()

    def remove_block(self, position):
        local_pos = (position[0] % 16, position[1], position[2] % 16)
        if local_pos in self.blocks:
            removed_block = self.blocks.pop(local_pos)
            self.rebuild_mesh()
            return removed_block
        return None

    def rebuild_mesh(self):
        for vlist in self.vertex_lists:
            vlist.delete()
        self.vertex_lists.clear()

        for pos, block in self.blocks.items():
            x, y, z = pos
            X, Y, Z = x+1, y+1, z+1

            if not self.blocks.get((x, y, z-1)):
                self._add_face(x, y, z, X, Y, z)
            if not self.blocks.get((x, y, z+1)):
                self._add_face(x, y, Z, X, Y, Z)
            if not self.blocks.get((x-1, y, z)):
                self._add_face(x, y, z, x, Y, Z)
            if not self.blocks.get((x+1, y, z)):
                self._add_face(X, y, z, X, Y, Z)
            if not self.blocks.get((x, y-1, z)):
                self._add_face(x, y, z, X, y, Z)
            if not self.blocks.get((x, y+1, z)):
                self._add_face(x, Y, z, X, Y, Z)

    def _add_face(self, x1, y1, z1, x2, y2, z2):
        vertices = [x1, y1, z1, x2, y1, z1, x2, y2, z1, x1, y2, z1]
        tex_coords = [0, 0, 1, 0, 1, 1, 0, 1]
        self.vertex_lists.append(self.batch.add_indexed(4, GL_TRIANGLES, None,
            [0, 1, 2, 0, 2, 3],
            ('v3f/static', vertices),
            ('t2f/static', tex_coords)
        ))

    def draw(self):
        self.batch.draw()

class GameWorld:
    def __init__(self):
        self.chunks = {}
        self.block_types = ['grass', 'dirt', 'stone', 'wood', 'leaves', 'sand', 'water', 'coal_ore', 'iron_ore', 'gold_ore', 'diamond_ore']
        self.seed = random.randint(0, 9999999)
        self.fluid_queue = []
        self.generate_world()

    def generate_world(self):
        for cx in range(-4, 4):
            for cz in range(-4, 4):
                chunk_pos = (cx, cz)
                self.chunks[chunk_pos] = Chunk(chunk_pos)
                for x in range(16):
                    for z in range(16):
                        world_x = cx * 16 + x
                        world_z = cz * 16 + z
                        self.generate_terrain(world_x, world_z)
                        self.generate_caves(world_x, world_z)
                        self.generate_ores(world_x, world_z)
        self.generate_trees()
        self.generate_water_bodies()

    def generate_terrain(self, world_x, world_z):
        height = int(noise.pnoise2(world_x / 50, world_z / 50, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed) * 15 + 20)
        for y in range(height):
            if y == height - 1:
                if noise.pnoise2(world_x / 100, world_z / 100, octaves=3, base=self.seed) > 0:
                    block_type = 'grass'
                else:
                    block_type = 'sand'
            elif y > height - 4:
                block_type = 'dirt'
            else:
                block_type = 'stone'
            self.add_block((world_x, y, world_z), block_type)

    def generate_caves(self, world_x, world_z):
        for y in range(1, 64):
            if noise.snoise3(world_x / 50, y / 25, world_z / 50, octaves=3) > 0.7:
                self.remove_block((world_x, y, world_z))

    def generate_ores(self, world_x, world_z):
        for y in range(1, 64):
            if self.get_block((world_x, y, world_z)) and self.get_block((world_x, y, world_z)).block_type == 'stone':
                ore_noise = noise.snoise3(world_x / 10, y / 10, world_z / 10, octaves=3)
                if ore_noise > 0.9:
                    self.add_block((world_x, y, world_z), 'diamond_ore')
                elif ore_noise > 0.8:
                    self.add_block((world_x, y, world_z), 'gold_ore')
                elif ore_noise > 0.7:
                    self.add_block((world_x, y, world_z), 'iron_ore')
                elif ore_noise > 0.6:
                    self.add_block((world_x, y, world_z), 'coal_ore')

    def generate_trees(self):
        for cx in range(-4, 4):
            for cz in range(-4, 4):
                for _ in range(5):  # Try to generate 5 trees per chunk
                    x = cx * 16 + random.randint(0, 15)
                    z = cz * 16 + random.randint(0, 15)
                    y = self.get_height(x, z)
                    if self.get_block((x, y, z)) and self.get_block((x, y, z)).block_type == 'grass':
                        self.generate_tree(x, y + 1, z)

    def generate_tree(self, x, y, z):
        tree_height = random.randint(4, 6)
        for dy in range(tree_height):
            self.add_block((x, y + dy, z), 'wood')
        
        for dx in range(-2, 3):
            for dy in range(-1, 3):
                for dz in range(-2, 3):
                    if abs(dx) + abs(dy) + abs(dz) < 4 + random.random() * 2:
                        self.add_block((x + dx, y + tree_height + dy, z + dz), 'leaves')

    def generate_water_bodies(self):
        for cx in range(-4, 4):
            for cz in range(-4, 4):
                if random.random() < 0.2:
                    self.generate_water_body(cx, cz)

    def generate_water_body(self, cx, cz):
        water_level = random.randint(5, 15)
        for x in range(16):
            for z in range(16):
                world_x = cx * 16 + x
                world_z = cz * 16 + z
                for y in range(water_level):
                    if self.get_block((world_x, y, world_z)) is None:
                        self.add_block((world_x, y, world_z), 'water')

    def add_block(self, position, block_type):
        chunk_pos = (position[0] // 16, position[2] // 16)
        if chunk_pos not in self.chunks:
            self.chunks[chunk_pos] = Chunk(chunk_pos)
        self.chunks[chunk_pos].add_block(position, block_type)
        if block_type == 'water':
            self.fluid_queue.append(position)

    def remove_block(self, position):
        chunk_pos = (position[0] // 16, position[2] // 16)
        if chunk_pos in self.chunks:
            return self.chunks[chunk_pos].remove_block(position)
        return None

    def get_block(self, position):
        chunk_pos = (position[0] // 16, position[2] // 16)
        if chunk_pos in self.chunks:
            local_pos = (position[0] % 16, position[1], position[2] % 16)
            return self.chunks[chunk_pos].blocks.get(local_pos)
        return None

    def get_height(self, x, z):
        for y in range(64, -1, -1):
            if self.get_block((x, y, z)):
                return y
        return 0

    def update_fluids(self):
        new_queue = []
        for position in self.fluid_queue:
            if self.get_block(position) and self.get_block(position).block_type == 'water':
                flowed = self.flow_water(position)
                if flowed:
                    new_queue.extend(flowed)
        self.fluid_queue = new_queue

    def flow_water(self, position):
        x, y, z = position
        flowed_positions = []
        below = (x, y - 1, z)
        if self.get_block(below) is None:
            self.add_block(below, 'water')
            self.remove_block(position)
            flowed_positions.append(below)
        else:
            for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (x + dx, y, z + dz)
                if self.get_block(neighbor) is None:
                    self.add_block(neighbor, 'water')
                    flowed_positions.append(neighbor)
        return flowed_positions

    def draw(self, block_type):
        for chunk in self.chunks.values():
            chunk.draw()

    def collide(self, position):
        x, y, z = position
        for dx in range(-1, 2):
            for dy in range(-2, 3):
                for dz in range(-1, 2):
                    if self.get_block((int(x + dx), int(y + dy), int(z + dz))):
                        return True
        return False

    def regenerate(self):
        self.chunks.clear()
        self.fluid_queue.clear()
        self.generate_world()