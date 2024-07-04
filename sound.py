import pyglet

class SoundManager:
    def __init__(self):
        self.sounds = {
            'walk': self.load_sound('walk.wav'),
            'jump': self.load_sound('jump.wav'),
            'mine': self.load_sound('mine.wav'),
            'place': self.load_sound('place.wav'),
            'hurt': self.load_sound('hurt.wav'),
        }

    def play(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def loop(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            return self.sounds[sound_name].play()
        return None

    def load_sound(self, filename):
        try:
            return pyglet.media.load(f'sounds/{filename}', streaming=False)
        except Exception as e:
            print(f"Error loading sound {filename}: {e}")
            return None