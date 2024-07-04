import pyglet

class Inventory:
    def __init__(self):
        self.slots = [None] * 36  # 36 inventory slots
        self.hotbar_slots = 9  # First 9 slots are the hotbar
        self.selected_slot = 0
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
            'wooden_planks': pyglet.image.load('textures/wooden_planks.png').get_texture(),
            'stick': pyglet.image.load('textures/stick.png').get_texture(),
            'wooden_pickaxe': pyglet.image.load('textures/wooden_pickaxe.png').get_texture(),
            'stone_pickaxe': pyglet.image.load('textures/stone_pickaxe.png').get_texture(),
            'iron_pickaxe': pyglet.image.load('textures/iron_pickaxe.png').get_texture(),
            'furnace': pyglet.image.load('textures/furnace.png').get_texture(),
            'coal': pyglet.image.load('textures/coal.png').get_texture(),
            'iron_ingot': pyglet.image.load('textures/iron_ingot.png').get_texture(),
            'gold_ingot': pyglet.image.load('textures/gold_ingot.png').get_texture(),
            'diamond': pyglet.image.load('textures/diamond.png').get_texture(),
        }

    def add_item(self, item, amount=1):
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = (item, amount)
                return True
            elif slot[0] == item and slot[1] < 64:
                new_amount = min(slot[1] + amount, 64)
                self.slots[i] = (item, new_amount)
                amount -= (new_amount - slot[1])
                if amount == 0:
                    return True
        return False

    def remove_item(self, item, amount=1):
        for i, slot in enumerate(self.slots):
            if slot is not None and slot[0] == item:
                if slot[1] > amount:
                    self.slots[i] = (item, slot[1] - amount)
                    return True
                elif slot[1] == amount:
                    self.slots[i] = None
                    return True
                else:
                    amount -= slot[1]
                    self.slots[i] = None
        return False

    def get_selected_item(self):
        return self.slots[self.selected_slot]

    def select_slot(self, slot):
        if 0 <= slot < self.hotbar_slots:
            self.selected_slot = slot

    def count(self, item):
        return sum(slot[1] for slot in self.slots if slot is not None and slot[0] == item)

    def get_items(self):
        return [slot for slot in self.slots if slot is not None]

    def draw(self, window):
        # Draw hotbar
        for i in range(self.hotbar_slots):
            x = 10 + i * 40
            y = 10
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2f', (x, y, x+40, y, x+40, y+40, x, y+40)),
                ('c3f', (0.5, 0.5, 0.5) * 4)
            )
            if i == self.selected_slot:
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                    ('v2f', (x-2, y-2, x+42, y-2, x+42, y+42, x-2, y+42)),
                    ('c3f', (1, 1, 1) * 4)
                )
            if self.slots[i]:
                item, count = self.slots[i]
                if item in self.textures:
                    self.textures[item].blit(x+4, y+4, width=32, height=32)
                    pyglet.text.Label(str(count), x=x+34, y=y+2, color=(255, 255, 255, 255)).draw()

    def draw_full_inventory(self, window):
        # Draw full inventory
        for i, slot in enumerate(self.slots):
            x = 10 + (i % 9) * 40
            y = window.height - 50 - (i // 9) * 40
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2f', (x, y, x+40, y, x+40, y+40, x, y+40)),
                ('c3f', (0.5, 0.5, 0.5) * 4)
            )
            if slot:
                item, count = slot
                if item in self.textures:
                    self.textures[item].blit(x+4, y+4, width=32, height=32)
                    pyglet.text.Label(str(count), x=x+34, y=y+2, color=(255, 255, 255, 255)).draw()

    def handle_click(self, x, y, button, modifiers):
        # Handle clicks in the inventory
        for i, slot in enumerate(self.slots):
            slot_x = 10 + (i % 9) * 40
            slot_y = self.window.height - 50 - (i // 9) * 40
            if slot_x <= x < slot_x + 40 and slot_y <= y < slot_y + 40:
                # Handle item movement logic here
                pass

    def swap_items(self, slot1, slot2):
        self.slots[slot1], self.slots[slot2] = self.slots[slot2], self.slots[slot1]

    def split_stack(self, slot):
        if self.slots[slot] is not None:
            item, count = self.slots[slot]
            split_amount = count // 2
            if split_amount > 0:
                self.slots[slot] = (item, count - split_amount)
                for i, other_slot in enumerate(self.slots):
                    if other_slot is None:
                        self.slots[i] = (item, split_amount)
                        break