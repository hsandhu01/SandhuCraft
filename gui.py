import pyglet
from pyglet.gl import *

class GUI:
    def __init__(self, window):
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.labels = []
        self.buttons = []

    def add_label(self, text, x, y):
        label = pyglet.text.Label(text, x=x, y=y, batch=self.batch)
        self.labels.append(label)
        return label

    def add_button(self, text, x, y, width, height, callback):
        button = Button(text, x, y, width, height, callback, self.batch)
        self.buttons.append(button)
        return button

    def draw(self):
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.hit_test(x, y):
                btn.callback()

class Button:
    def __init__(self, text, x, y, width, height, callback, batch):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.callback = callback
        self.background = pyglet.shapes.Rectangle(x, y, width, height, color=(100, 100, 100), batch=batch)
        self.label = pyglet.text.Label(text, x=x+width//2, y=y+height//2, anchor_x='center', anchor_y='center', batch=batch)

    def hit_test(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height