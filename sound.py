import pyglet

class SoundManager:
    def __init__(self):
        self.sounds = {
            'walk': self.load_sound('walk.wav'),
            'jump': self.load_sound('jump.wav'),
            'mine': self.load_sound('mine.wav'),
            'place': self.load_sound('place.wav'),
            'hurt': self.load_sound('hurt.wav'),
            'eat': self.load_sound('eat.wav'),
            'zombie': self.load_sound('zombie.wav'),
            'sheep': self.load_sound('sheep.wav'),
            'skeleton': self.load_sound('skeleton.wav'),
            'craft': self.load_sound('craft.wav'),
            'splash': self.load_sound('splash.wav'),
            'fall': self.load_sound('fall.wav'),
            'door_open': self.load_sound('door_open.wav'),
            'door_close': self.load_sound('door_close.wav'),
            'chest_open': self.load_sound('chest_open.wav'),
            'chest_close': self.load_sound('chest_close.wav'),
        }
        
        self.music = {
            'background': self.load_music('background_music.mp3'),
            'cave': self.load_music('cave_music.mp3'),
        }
        
        self.current_music = None
        self.music_player = pyglet.media.Player()
        self.music_player.loop = True
        
        self.volume = 1.0
        self.music_volume = 0.5

    def load_sound(self, filename):
        return pyglet.media.load(f'sounds/{filename}', streaming=False)

    def load_music(self, filename):
        return pyglet.media.load(f'music/{filename}')

    def play(self, sound_name):
        if sound_name in self.sounds:
            sound = self.sounds[sound_name].play()
            sound.volume = self.volume

    def play_music(self, music_name):
        if music_name in self.music and music_name != self.current_music:
            self.music_player.queue(self.music[music_name])
            if not self.music_player.playing:
                self.music_player.play()
            self.current_music = music_name
        self.music_player.volume = self.music_volume

    def stop_music(self):
        self.music_player.pause()
        self.current_music = None

    def set_volume(self, volume):
        self.volume = max(0, min(1, volume))

    def set_music_volume(self, volume):
        self.music_volume = max(0, min(1, volume))
        self.music_player.volume = self.music_volume

    def update(self, player, world):
        # Check player's environment and play appropriate music
        if player.position.y < 20:  # Arbitrary depth to consider as "cave"
            self.play_music('cave')
        else:
            self.play_music('background')

class FootstepSound:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.step_interval = 0.5  # Time between footsteps
        self.time_since_last_step = 0

    def update(self, dt, player_moving):
        if player_moving:
            self.time_since_last_step += dt
            if self.time_since_last_step >= self.step_interval:
                self.sound_manager.play('walk')
                self.time_since_last_step = 0
        else:
            self.time_since_last_step = 0

class AmbientSounds:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.ambient_interval = 15  # Time between ambient sounds
        self.time_since_last_ambient = 0

    def update(self, dt, player, world, mobs):
        self.time_since_last_ambient += dt
        if self.time_since_last_ambient >= self.ambient_interval:
            self.play_ambient_sound(player, world, mobs)
            self.time_since_last_ambient = 0

    def play_ambient_sound(self, player, world, mobs):
        # Check environment and play appropriate ambient sounds
        if player.position.y < 20:  # In a cave
            self.sound_manager.play('skeleton')  # Example: play skeleton sound in caves
        else:
            nearby_mobs = [mob for mob in mobs if player.distance_to(mob.position) < 20]
            if nearby_mobs:
                mob = random.choice(nearby_mobs)
                self.sound_manager.play(mob.mob_type)