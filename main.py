import pyglet
from pyglet.window import key, mouse
from pyglet.gl import *
from game_world import GameWorld
from player import Player
from inventory import Inventory
from gui import GUI
from mobs import Sheep, Zombie
from sound import SoundManager
from save_load import SaveLoadManager
from weather import WeatherSystem
import random
import math

class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(300, 200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.mouse_locked = False
        self.world = GameWorld()
        self.player = Player((0.5, 20, 0.5), self.world)
        self.gui = GUI(self)
        self.mobs = []
        self.sound_manager = SoundManager()
        self.weather_system = WeatherSystem(self)
        self.time_of_day = 0  # 0 to 1, where 0 is dawn and 0.5 is dusk
        
        self.textures = {
            'grass': pyglet.image.load('textures/grass.png').get_texture(),
            'dirt': pyglet.image.load('textures/dirt.png').get_texture(),
            'stone': pyglet.image.load('textures/stone.png').get_texture(),
            'wood': pyglet.image.load('textures/wood.png').get_texture(),
            'leaves': pyglet.image.load('textures/leaves.png').get_texture(),
            'sand': pyglet.image.load('textures/sand.png').get_texture(),
            'water': pyglet.image.load('textures/water.png').get_texture(),
            'coal_ore': pyglet.image.load('textures/coal_ore.png').get_texture(),
            'iron_ore': pyglet.image.load('textures/iron_ore.png').get_texture(),
            'gold_ore': pyglet.image.load('textures/gold_ore.png').get_texture(),
            'diamond_ore': pyglet.image.load('textures/diamond_ore.png').get_texture(),
        }
        
        # Enable texture repeat
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        self.spawn_mobs()

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
        if self.mouse_locked:
            if button == mouse.LEFT:
                block = self.player.mine(self.world)
                if block:
                    self.sound_manager.play('mine')
            elif button == mouse.RIGHT:
                selected_block = self.player.inventory.get_selected_item()
                if selected_block:
                    if self.player.place_block(selected_block):
                        self.player.inventory.remove_item(selected_block)
                        self.sound_manager.play('place')
        self.gui.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.mouse_locked = not self.mouse_locked
            self.set_exclusive_mouse(self.mouse_locked)
        elif symbol in [key._1, key._2, key._3, key._4, key._5]:
            self.player.inventory.select_slot(symbol - key._1)
        elif symbol == key.E:
            self.player.toggle_inventory()
        elif symbol == key.F5:
            self.save_game()
        elif symbol == key.F9:
            self.load_game()

    def update(self, dt):
        self.player.update(dt, self.keys)
        for mob in self.mobs:
            mob.update(dt, self.world, self.player)
        
        self.handle_mob_interactions()
        self.world.update_fluids()
        self.time_of_day = (self.time_of_day + dt / 300) % 1  # Full day/night cycle in 5 minutes
        self.update_lighting()
        self.weather_system.update(dt)
        self.gui.update(self.player, self.time_of_day)

    def handle_mob_interactions(self):
        for mob in self.mobs:
            if isinstance(mob, Zombie) and self.player.distance_to(mob.position) < 1.5:
                self.player.take_damage(5)  # Zombie attacks player
                self.sound_manager.play('hurt')

    def update_lighting(self):
        ambient_light = 0.2 + 0.6 * math.sin(self.time_of_day * math.pi)
        glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(ambient_light, ambient_light, ambient_light, 1.0))

    def on_draw(self):
        self.clear()
        self.set_3d()
        
        glEnable(GL_TEXTURE_2D)
        for block_type, texture in self.textures.items():
            glBindTexture(GL_TEXTURE_2D, texture.id)
            self.world.draw(block_type)
        glDisable(GL_TEXTURE_2D)

        for mob in self.mobs:
            mob.draw()

        self.set_2d()
        self.gui.draw()
        self.weather_system.draw()

    def set_3d(self):
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / height, 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.player.update_camera()

    def set_2d(self):
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

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
        pyglet.clock.schedule_interval(self.update, 1.0 / 60)
        pyglet.app.run()

if __name__ == '__main__':
    window = Game(width=800, height=600, caption='Minecraft Clone', resizable=True)
    glEnable(GL_DEPTH_TEST)
    window.run()