import random
import pyglet
import noise
from pyglet import gl
import os
from PIL import Image

class Block:
    def __init__(self, block_type):
        self.block_type = block_type

class Chunk:
    def __init__(self, position, world):
        self.position = position
        self.world = world
        self.blocks = {}
        self.batch = pyglet.graphics.Batch()
        self.needs_update = True

    def add_block(self, position, block_type):
        local_x, local_y, local_z = (p % 16 for p in position)
        if (local_x, local_y, local_z) not in self.blocks:
            self.blocks[(local_x, local_y, local_z)] = Block(block_type)
            self.needs_update = True

    def remove_block(self, position):
        local_x, local_y, local_z = (p % 16 for p in position)
        if (local_x, local_y, local_z) in self.blocks:
            removed_type = self.blocks[(local_x, local_y, local_z)].block_type
            del self.blocks[(local_x, local_y, local_z)]
            self.needs_update = True
            return removed_type
        return None

    def get_block(self, position):
        local_x, local_y, local_z = (p % 16 for p in position)
        if (local_x, local_y, local_z) in self.blocks:
            return self.blocks[(local_x, local_y, local_z)].block_type
        return None
    
    def update_mesh(self):
        if not self.needs_update:
            return
        self.batch = pyglet.graphics.Batch()
        for (x, y, z), block in self.blocks.items():
            color = self.world.textures[block.block_type]
            vertices = [
                x, y, z,    x+1, y, z,    x+1, y+1, z,    x, y+1, z,  # Front face
                x, y, z+1,  x+1, y, z+1,  x+1, y+1, z+1,  x, y+1, z+1,  # Back face
                x, y, z,    x, y, z+1,    x, y+1, z+1,    x, y+1, z,  # Left face
                x+1, y, z,  x+1, y+1, z,  x+1, y+1, z+1,  x+1, y, z+1,  # Right face
                x, y+1, z,  x+1, y+1, z,  x+1, y+1, z+1,  x, y+1, z+1,  # Top face
                x, y, z,    x+1, y, z,    x+1, y, z+1,    x, y, z+1,  # Bottom face
            ]
            colors = color * 24  # 6 faces * 4 vertices per face
            self.batch.add(24, gl.GL_QUADS, None,
                           ('v3f', vertices),
                           ('c3f', colors))
        self.needs_update = False

    def draw(self):
        self.update_mesh()
        self.batch.draw()

class GameWorld:
    def __init__(self):
        self.chunks = {}
        self.seed = random.randint(0, 9999999)
        self.fluid_queue = set()
        self.load_textures()
        self.generate_world()

    def load_textures(self):
        self.textures = {
            'grass': (0, 0.8, 0),  # Green
            'dirt': (0.5, 0.25, 0),  # Brown
            'stone': (0.5, 0.5, 0.5),  # Gray
            'sand': (0.76, 0.7, 0.5)  # Yellow
        }

    def generate_world(self):
        for cx in range(-4, 4):
            for cz in range(-4, 4):
                self.chunks[(cx, cz)] = Chunk((cx, cz), self)
                for x in range(16):
                    for z in range(16):
                        world_x = cx * 16 + x
                        world_z = cz * 16 + z
                        self.generate_terrain(world_x, world_z)

    def generate_terrain(self, world_x, world_z):
        height = int(noise.pnoise2(world_x / 50, world_z / 50, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed) * 30 + 35)
        print(f"Generating terrain at ({world_x}, {world_z}) with height {height}")
        for y in range(height):
            if y == height - 1:
                block_type = 'grass' if noise.pnoise2(world_x / 100, world_z / 100, octaves=3, base=self.seed) > 0 else 'sand'
            elif y > height - 4:
                block_type = 'dirt'
            else:
                block_type = 'stone'
            self.add_block((world_x, y, world_z), block_type)

    def add_block(self, position, block_type):
        chunk_pos = (position[0] // 16, position[2] // 16)
        if chunk_pos not in self.chunks:
            self.chunks[chunk_pos] = Chunk(chunk_pos, self)
        self.chunks[chunk_pos].add_block(position, block_type)

    def remove_block(self, position):
        chunk_pos = (position[0] // 16, position[2] // 16)
        if chunk_pos in self.chunks:
            return self.chunks[chunk_pos].remove_block(position)
        return None

    def get_block(self, position):
        chunk_pos = (position[0] // 16, position[2] // 16)
        if chunk_pos in self.chunks:
            return self.chunks[chunk_pos].get_block(position)
        return None

    def get_height(self, x, z):
        for y in range(255, -1, -1):
            if self.get_block((int(x), y, int(z))) is not None:
                return y
        return 0

    def draw(self):
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        for chunk in self.chunks.values():
            gl.glPushMatrix()
            gl.glTranslatef(chunk.position[0] * 16, 0, chunk.position[1] * 16)
            chunk.draw()
            gl.glPopMatrix()
        
        # Draw a debug ground plane
        gl.glColor3f(0.5, 0.5, 0.5)  # Gray color
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(-100, 0, -100)
        gl.glVertex3f(100, 0, -100)
        gl.glVertex3f(100, 0, 100)
        gl.glVertex3f(-100, 0, 100)
        gl.glEnd()

        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_DEPTH_TEST)

    def update_fluids(self):
        # Simplified fluid update (no actual simulation)
        pass

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