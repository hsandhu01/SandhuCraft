class CraftingSystem:
    def __init__(self):
        self.recipes = {
            'wooden_planks': {'ingredients': {'wood': 1}, 'output': ('wooden_planks', 4)},
            'stick': {'ingredients': {'wooden_planks': 2}, 'output': ('stick', 4)},
            'wooden_pickaxe': {'ingredients': {'wooden_planks': 3, 'stick': 2}, 'output': ('wooden_pickaxe', 1)},
            'stone_pickaxe': {'ingredients': {'cobblestone': 3, 'stick': 2}, 'output': ('stone_pickaxe', 1)},
            'iron_pickaxe': {'ingredients': {'iron_ingot': 3, 'stick': 2}, 'output': ('iron_pickaxe', 1)},
            'furnace': {'ingredients': {'cobblestone': 8}, 'output': ('furnace', 1)},
            'torch': {'ingredients': {'coal': 1, 'stick': 1}, 'output': ('torch', 4)},
            'crafting_table': {'ingredients': {'wooden_planks': 4}, 'output': ('crafting_table', 1)},
            'chest': {'ingredients': {'wooden_planks': 8}, 'output': ('chest', 1)},
            'bed': {'ingredients': {'wooden_planks': 3, 'wool': 3}, 'output': ('bed', 1)},
        }

    def can_craft(self, recipe, inventory):
        if recipe not in self.recipes:
            return False
        for item, count in self.recipes[recipe]['ingredients'].items():
            if inventory.count(item) < count:
                return False
        return True

    def craft(self, recipe, inventory):
        if self.can_craft(recipe, inventory):
            for item, count in self.recipes[recipe]['ingredients'].items():
                inventory.remove_item(item, count)
            output_item, output_count = self.recipes[recipe]['output']
            inventory.add_item(output_item, output_count)
            return True
        return False

    def get_available_recipes(self, inventory):
        available_recipes = []
        for recipe in self.recipes:
            if self.can_craft(recipe, inventory):
                available_recipes.append(recipe)
        return available_recipes

class Furnace:
    def __init__(self):
        self.fuel = 0
        self.progress = 0
        self.input_slot = None
        self.fuel_slot = None
        self.output_slot = None
        self.smelting_recipes = {
            'iron_ore': 'iron_ingot',
            'gold_ore': 'gold_ingot',
            'sand': 'glass',
        }
        self.fuel_values = {
            'coal': 80,
            'wood': 15,
            'stick': 5,
        }

    def add_fuel(self, item, count):
        if item in self.fuel_values:
            self.fuel += self.fuel_values[item] * count
            return True
        return False

    def can_smelt(self):
        return (self.input_slot is not None and
                self.input_slot[0] in self.smelting_recipes and
                self.fuel > 0 and
                (self.output_slot is None or
                 (self.output_slot[0] == self.smelting_recipes[self.input_slot[0]] and
                  self.output_slot[1] < 64)))

    def smelt(self):
        if self.can_smelt():
            self.progress += 1
            self.fuel -= 1
            if self.progress >= 200:  # Smelting takes 200 ticks
                self.progress = 0
                output_item = self.smelting_recipes[self.input_slot[0]]
                if self.output_slot is None:
                    self.output_slot = (output_item, 1)
                else:
                    self.output_slot = (output_item, self.output_slot[1] + 1)
                self.input_slot = (self.input_slot[0], self.input_slot[1] - 1)
                if self.input_slot[1] == 0:
                    self.input_slot = None
            return True
        return False

    def get_progress(self):
        return self.progress / 200  # Return progress as a percentage

    def get_fuel_level(self):
        return self.fuel / 80  # Assuming coal is the standard fuel, return fuel level as a percentage of one coal