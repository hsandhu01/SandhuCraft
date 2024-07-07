import random
import pyglet
import noise
from pyglet.math import Vec3, Mat4
from pyglet import gl
import os
import logging

logging.basicConfig(level=logging.DEBUG)

class Block:
    def __init__(self, block_type):
        self.block_type = block_type

class Chunk:
    def __init__(self, position, world):
        self.position = position
        self.world = world
        self.blocks = {}
        self.bounding_box = None
        self.batch = pyglet.graphics.Batch()
        self.needs_update = True
        self.rendered_vertices = 0

    def add_block(self, position, block_type):
        local_x, local_y, local_z = (p % 16 for p in position)
        if (local_x, local_y, local_z) not in self.blocks:
            self.blocks[(local_x, local_y, local_z)] = Block(block_type)
            self.needs_update = True
            logging.debug(f"Added block {block_type} at {position}")

    def remove_block(self, position):
        local_x, local_y, local_z = (p % 16 for p in position)
        if (local_x, local_y, local_z) in self.blocks:
            removed_type = self.blocks[(local_x, local_y, local_z)].block_type
            del self.blocks[(local_x, local_y, local_z)]
            self.needs_update = True
            logging.debug(f"Removed block {removed_type} at {position}")
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
        self.bounding_box = self.calculate_bounding_box()
        self.rendered_vertices = 0
        vertex_count = 0
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
            vertex_count += 24
        self.rendered_vertices = vertex_count
        logging.debug(f"Updated chunk mesh at {self.position} with {vertex_count} vertices.")
        self.needs_update = False

    def calculate_bounding_box(self):
        if not self.blocks:
            return None
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        for x, y, z in self.blocks.keys():
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            min_z = min(min_z, z)
            max_x = max(max_x, x + 1)
            max_y = max(max_y, y + 1)
            max_z = max(max_z, z + 1)
        return (Vec3(min_x, min_y, min_z), Vec3(max_x, max_y, max_z))

    def is_visible(self, frustum):
        if not self.bounding_box:
            return False
        min_point, max_point = self.bounding_box
        for i in range(6):
            out = 0
            out += (frustum[i].dot(Vec3(min_point.x, min_point.y, min_point.z)) < 0.0) 
            out += (frustum[i].dot(Vec3(max_point.x, min_point.y, min_point.z)) < 0.0) 
            out += (frustum[i].dot(Vec3(min_point.x, max_point.y, min_point.z)) < 0.0) 
            out += (frustum[i].dot(Vec3(max_point.x, max_point.y, min_point.z)) < 0.0) 
            out += (frustum[i].dot(Vec3(min_point.x, min_point.y, max_point.z)) < 0.0) 
            out += (frustum[i].dot(Vec3(max_point.x, min_point.y, max_point.z)) < 0.0) 
            out += (frustum[i].dot(Vec3(min_point.x, max_point.y, max_point.z)) < 0.0) 
            out += (frustum[i].dot(Vec3(max_point.x, max_point.y, max_point.z)) < 0.0) 
            if out == 8:
                return False
        return True

    def draw(self):
        self.update_mesh()
        self.batch.draw()
        logging.debug(f"Drew chunk at {self.position} with {self.rendered_vertices} vertices")

class GameWorld:
    def __init__(self):
        self.chunks = {}
        self.seed = random.randint(0, 9999999)
        self.fluid_queue = set()
        self.load_textures()
        self.render_distance = 8  # Chunks
        self.rendered_vertices = 0
        self.generate_world()

    def load_textures(self):
        self.textures = {
            'grass': (0, 0.8, 0),  # Green
            'dirt': (0.5, 0.25, 0),  # Brown
            'stone': (0.5, 0.5, 0.5),  # Gray
            'sand': (0.76, 0.7, 0.5)  # Yellow
        }

    def generate_world(self):
        pass  # We'll generate chunks on-demand now

    def ensure_chunks_around_player(self, player_position):
        px, _, pz = player_position
        cx, cz = int(px) // 16, int(pz) // 16
        for x in range(cx - self.render_distance, cx + self.render_distance + 1):
            for z in range(cz - self.render_distance, cz + self.render_distance + 1):
                if (x, z) not in self.chunks:
                    self.generate_chunk(x, z)
        
        # Unload distant chunks
        chunks_to_unload = []
        for chunk_pos in self.chunks:
            if max(abs(chunk_pos[0] - cx), abs(chunk_pos[1] - cz)) > self.render_distance:
                chunks_to_unload.append(chunk_pos)
        for chunk_pos in chunks_to_unload:
            del self.chunks[chunk_pos]

    def generate_chunk(self, cx, cz):
        self.chunks[(cx, cz)] = Chunk((cx, cz), self)
        for x in range(16):
            for z in range(16):
                world_x = cx * 16 + x
                world_z = cz * 16 + z
                self.generate_terrain(world_x, world_z)

    def generate_terrain(self, world_x, world_z):
        height = int(noise.pnoise2(world_x / 50, world_z / 50, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed) * 30 + 35)
        logging.debug(f"Generating terrain at ({world_x}, {world_z}) with height {height}")
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
        gl.glCullFace(gl.GL_BACK)
        gl.glFrontFace(gl.GL_CCW)
        
        frustum = self.calculate_frustum()
        logging.debug(f"Drawing {len(self.chunks)} chunks")
        self.rendered_vertices = 0
        for chunk in self.chunks.values():
            if chunk.is_visible(frustum):
                gl.glPushMatrix()
                gl.glTranslatef(chunk.position[0] * 16, 0, chunk.position[1] * 16)
                chunk.draw()
                self.rendered_vertices += chunk.rendered_vertices
                gl.glPopMatrix()

    def calculate_frustum(self):
        proj = (gl.GLfloat * 16)()
        gl.glGetFloatv(gl.GL_PROJECTION_MATRIX, proj)
        modl = (gl.GLfloat * 16)()
        gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, modl)
        
        clip = [0] * 16
        for i in range(4):
            for j in range(4):
                clip[i * 4 + j] = sum(proj[i + k * 4] * modl[k * 4 + j] for k in range(4))
        
        frustum = []
        for i in range(6):
            plane = Vec3(clip[3, 0] - clip[i // 2, 0],
                         clip[3, 1] - clip[i // 2, 1],
                         clip[3, 2] - clip[i // 2, 2])
            d = clip[3, 3] - clip[i // 2, 3]
            magnitude = plane.mag()
            frustum.append(Vec3(plane.x / magnitude, plane.y / magnitude, plane.z / magnitude))
        return frustum

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
