import random
import pyglet
import noise
from pyglet import gl

class Block:
    def __init__(self, block_type):
        self.block_type = block_type

class Chunk:
    def __init__(self, position):
        self.position = position
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
            # Simple cube rendering for each block
            vertices = [
                x, y, z,    x+1, y, z,    x+1, y+1, z,    x, y+1, z,  # Front face
                x, y, z+1,  x+1, y, z+1,  x+1, y+1, z+1,  x, y+1, z+1,  # Back face
            ]
            self.batch.add(4, gl.GL_QUADS, None, ('v3f', vertices[:12]))
            self.batch.add(4, gl.GL_QUADS, None, ('v3f', vertices[12:]))
        self.needs_update = False

    def draw(self):
        self.update_mesh()
        self.batch.draw()

class GameWorld:
    def __init__(self):
        self.chunks = {}
        self.seed = random.randint(0, 9999999)
        self.fluid_queue = set()
        self.generate_world()

    def generate_world(self):
        for cx in range(-4, 4):
            for cz in range(-4, 4):
                self.chunks[(cx, cz)] = Chunk((cx, cz))
                for x in range(16):
                    for z in range(16):
                        world_x = cx * 16 + x
                        world_z = cz * 16 + z
                        self.generate_terrain(world_x, world_z)

    def generate_terrain(self, world_x, world_z):
        height = int(noise.pnoise2(world_x / 50, world_z / 50, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed) * 15 + 20)
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
            self.chunks[chunk_pos] = Chunk(chunk_pos)
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
        # Find the highest non-air block at the given x, z coordinates
        for y in range(255, -1, -1):
            if self.get_block((int(x), y, int(z))) is not None:
                return y
        return 0  # Return 0 if no blocks found (void)

    def draw(self):
        for chunk in self.chunks.values():
            gl.glPushMatrix()
            gl.glTranslatef(chunk.position[0] * 16, 0, chunk.position[1] * 16)
            chunk.draw()
            gl.glPopMatrix()

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