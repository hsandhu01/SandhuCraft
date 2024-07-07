import random
import math
import pyglet
from pyglet import gl
from pyglet.window import key, mouse
from pyglet.math import Vec3
from pyglet.graphics import Batch
from pyglet.text import Label
import traceback
import sys

pyglet.options['shadow_window'] = False

from game_world import GameWorld
from player import Player
from inventory import Inventory
from gui import GUI
from mobs import Sheep, Zombie
from save_load import SaveLoadManager
from weather import WeatherSystem

class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Print debug information
        version = gl.glGetString(gl.GL_VERSION)
        if isinstance(version, bytes):
            print(f"OpenGL Version: {version.decode()}")
        else:
            print(f"OpenGL Version: {version}")
        print(f"Pyglet version: {pyglet.version}")
        print(f"Python version: {sys.version}")
        
        self.set_minimum_size(300, 200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.exclusive = False
        self.set_exclusive_mouse(self.exclusive)
        self.world = GameWorld()
        self.player = Player(Vec3(0.5, 150.0, 0.5))  # Increased Y value
        self.player.position[1] = self.world.get_height(self.player.position[0], self.player.position[2]) + 2
        print(f"Player initial position: {self.player.get_position()}")
        self.gui = GUI(self)
        self.mobs = []
        self.weather_system = WeatherSystem(self)
        self.time_of_day = 0  # 0 to 1, where 0 is dawn and 0.5 is dusk
        self.ambient_light = 0.5

        self.batch = Batch()
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.info_label = Label('', x=10, y=self.height - 10, batch=self.batch)

        self.spawn_mobs()

        # Set up OpenGL context
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

    def spawn_mobs(self):
        for _ in range(20):  # Spawn 20 sheep
            x = random.uniform(-64, 64)
            z = random.uniform(-64, 64)
            y = self.world.get_height(x, z) + 1
            self.mobs.append(Sheep((x, y, z)))
        
        for _ in range(10):  # Spawn 10 zombies
            x = random.uniform(-64, 64)
            z = random.uniform(-64, 64)
            y = self.world.get_height(x, z) + 1
            self.mobs.append(Zombie((x, y, z)))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.exclusive:
            if button == mouse.LEFT:
                block = self.player.mine(self.world)
            elif button == mouse.RIGHT:
                selected_block = self.player.inventory.get_selected_item()
                if selected_block:
                    self.player.place_block(selected_block, self.world)
        self.gui.on_mouse_press(x, y, button, modifiers)
        print(f"Mouse pressed at ({x}, {y})")

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.exclusive = not self.exclusive
            self.set_exclusive_mouse(self.exclusive)
        elif symbol in [key._1, key._2, key._3, key._4, key._5]:
            self.player.inventory.select_slot(symbol - key._1)
        elif symbol == key.E:
            self.player.toggle_inventory()
        elif symbol == key.F5:
            self.save_game()
        elif symbol == key.F9:
            self.load_game()

    def update(self, dt):
        self.player.update(dt, self.keys, self.world)
        for mob in self.mobs:
            mob.update(dt, self.world, self.player)
        
        self.world.ensure_chunks_around_player(self.player.position)
        
        self.handle_mob_interactions()
        self.world.update_fluids()
        self.time_of_day = (self.time_of_day + dt / 300) % 1  # Full day/night cycle in 5 minutes
        self.update_lighting()
        self.weather_system.update(dt)
        self.info_label.y = self.height - 10  # Update label position if window is resized

    def handle_mob_interactions(self):
        for mob in self.mobs:
            if isinstance(mob, Zombie) and self.player.distance_to(mob.position) < 1.5:
                self.player.take_damage(5)  # Zombie attacks player

    def update_lighting(self):
        self.ambient_light = 0.2 + 0.6 * math.sin(self.time_of_day * math.pi)

    def on_draw(self):
        self.clear()
        gl.glClearColor(0.5, 0.7, 1.0, 1.0)  # Light blue sky color
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glViewport(0, 0, self.width, self.height)
        
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(65, self.width / self.height, 0.1, 1000)
        
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        self.world.ensure_chunks_around_player(self.player.position)
        self.player.update_camera(self)
        
        # Debug rendering
        gl.glColor3f(1, 0, 0)  # Red color
        gl.glPointSize(10)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex3f(0, 0, 0)  # Origin point
        gl.glEnd()
        
        self.world.draw()
        
        for mob in self.mobs:
            mob.draw()
        
        self.set_2d()
        self.batch.draw()
        self.fps_display.draw()
        self.draw_player_info()

    def set_2d(self):
        width, height = self.get_size()
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def draw_player_info(self):
        x, y, z = self.player.get_position()
        self.info_label.text = f"Player Position: ({x:.2f}, {y:.2f}, {z:.2f})"
        self.info_label.text += f"\nChunks loaded: {len(self.world.chunks)}"
        self.info_label.text += f"\nRendered vertices: {self.world.rendered_vertices}"
        self.info_label.draw()

    def save_game(self):
        SaveLoadManager.save_game(self.player, self.world)
        print("Game saved!")

    def load_game(self):
        save_data = SaveLoadManager.load_game()
        if save_data:
            self.player.position = save_data['player']['position']
            self.player.health = save_data['player']['health']
            self.player.inventory.items = save_data['player']['inventory']
            self.world.seed = save_data['world']['seed']
            self.world.regenerate()
            for block_data in save_data['world']['modified_blocks']:
                self.world.add_block(tuple(block_data['position']), block_data['block_type'])
            print("Game loaded!")
        else:
            print("No save file found.")

    def run(self):
        pyglet.clock.schedule(self.update)
        pyglet.app.run()

if __name__ == '__main__':
    window = Game(800, 600, caption='Minecraft Clone', resizable=True)
    window.run()
