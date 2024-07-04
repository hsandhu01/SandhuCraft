import random
import pyglet
from pyglet.gl import *

class WeatherSystem:
    def __init__(self, window):
        self.window = window
        self.particles = []
        self.weather_type = 'clear'
        self.weather_intensity = 0
        self.change_weather()
        self.weather_duration = random.uniform(60, 300)  # Weather lasts between 1-5 minutes
        self.time_elapsed = 0
        
        # Load textures
        self.rain_texture = pyglet.image.load('textures/rain.png').get_texture()
        self.snow_texture = pyglet.image.load('textures/snow.png').get_texture()

    def update(self, dt):
        self.time_elapsed += dt
        if self.time_elapsed >= self.weather_duration:
            self.change_weather()
            self.time_elapsed = 0
            self.weather_duration = random.uniform(60, 300)

        if self.weather_type != 'clear':
            self.update_particles(dt)
            if random.random() < 0.001:
                self.change_weather()

    def change_weather(self):
        self.weather_type = random.choice(['clear', 'rain', 'snow'])
        self.weather_intensity = random.uniform(0.2, 1.0)
        self.particles.clear()

    def update_particles(self, dt):
        # Remove particles that are out of view
        self.particles = [p for p in self.particles if p.y > 0]

        # Add new particles
        if len(self.particles) < 1000 * self.weather_intensity:
            x = random.uniform(-20, 20)  # Spawn particles in a 40x40 area around the player
            y = 20  # Start particles above the player's view
            z = random.uniform(-20, 20)
            speed = random.uniform(7, 13) * self.weather_intensity
            self.particles.append(WeatherParticle(x, y, z, speed))

        # Update particle positions
        for particle in self.particles:
            particle.update(dt)

    def draw(self):
        if self.weather_type != 'clear':
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_TEXTURE_2D)
            
            if self.weather_type == 'rain':
                glBindTexture(GL_TEXTURE_2D, self.rain_texture.id)
            elif self.weather_type == 'snow':
                glBindTexture(GL_TEXTURE_2D, self.snow_texture.id)
            
            glPushMatrix()
            for particle in self.particles:
                particle.draw(self.weather_type)
            glPopMatrix()
            
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)

    def get_weather_type(self):
        return self.weather_type

    def get_weather_intensity(self):
        return self.weather_intensity

class WeatherParticle:
    def __init__(self, x, y, z, speed):
        self.x = x
        self.y = y
        self.z = z
        self.speed = speed
        self.size = random.uniform(0.1, 0.3)

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < 0:
            self.y = 20  # Reset height when particle reaches the ground

    def draw(self, weather_type):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        if weather_type == 'rain':
            glRotatef(-60, 1, 0, 0)  # Tilt rain particles
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-self.size, -self.size, 0)
        glTexCoord2f(1, 0); glVertex3f(self.size, -self.size, 0)
        glTexCoord2f(1, 1); glVertex3f(self.size, self.size, 0)
        glTexCoord2f(0, 1); glVertex3f(-self.size, self.size, 0)
        glEnd()
        
        glPopMatrix()

class WeatherEffects:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.rain_sound = None
        self.thunder_cooldown = 0

    def update(self, dt, weather_system):
        weather_type = weather_system.get_weather_type()
        intensity = weather_system.get_weather_intensity()

        if weather_type == 'rain':
            if not self.rain_sound:
                self.rain_sound = self.sound_manager.loop('rain')
                self.rain_sound.volume = intensity
            else:
                self.rain_sound.volume = intensity

            self.thunder_cooldown -= dt
            if self.thunder_cooldown <= 0 and random.random() < 0.01 * intensity:
                self.sound_manager.play('thunder')
                self.thunder_cooldown = random.uniform(10, 30)
        else:
            if self.rain_sound:
                self.rain_sound.stop()
                self.rain_sound = None

    def apply_weather_effects(self, player, weather_system):
        weather_type = weather_system.get_weather_type()
        intensity = weather_system.get_weather_intensity()

        if weather_type == 'rain':
            # Slow down player slightly in rain
            player.speed *= (1 - 0.2 * intensity)
        elif weather_type == 'snow':
            # Slow down player more in snow
            player.speed *= (1 - 0.3 * intensity)

        # Reset player speed after applying weather effects
        player.reset_speed()