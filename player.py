from pyglet.math import Vec3
from pyglet.window import key
import math
from inventory import Inventory
from crafting import CraftingSystem

class Player:
    def __init__(self, position):
        self.position = position if isinstance(position, Vec3) else Vec3(*position)
        self.rotation = Vec3(0.0, 0.0, 0.0)
        self.speed = 5
        self.gravity = -9.8
        self.dy = 0
        self.jump_speed = 5
        self.height = 1.8
        self.health = 20
        self.max_health = 20
        self.hunger = 20
        self.max_hunger = 20
        self.inventory = Inventory()
        self.crafting_system = CraftingSystem()
        self.mining_cooldown = 0
        self.attack_cooldown = 0
        self.damage_cooldown = 0
        self.jumped = False
        self.flying = False
        self.sprint_multiplier = 1.5
        self.crouching = False
        self.crouch_multiplier = 0.5

    def update(self, dt, keys, world):
        # Apply gravity if not flying
        if not self.flying:
            self.dy += self.gravity * dt
            new_y = self.position.y + self.dy * dt
        else:
            new_y = self.position.y
            if keys[key.SPACE]:
                new_y += self.speed * dt
            if keys[key.LSHIFT]:
                new_y -= self.speed * dt

        # Update position
        self.move(dt, keys, new_y, world)

        # Update cooldowns
        self.mining_cooldown = max(0, self.mining_cooldown - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_cooldown = max(0, self.damage_cooldown - dt)

        # Update hunger
        self.update_hunger(dt)

    def move(self, dt, keys, new_y, world):
        speed = self.speed
        if keys[key.LSHIFT] and not self.flying:
            self.crouching = True
            speed *= self.crouch_multiplier
        else:
            self.crouching = False

        if keys[key.LCTRL]:
            speed *= self.sprint_multiplier

        # Calculate movement
        strafe = (keys[key.D] - keys[key.A]) * speed * dt
        forward = (keys[key.W] - keys[key.S]) * speed * dt

        # Apply rotation to movement
        rotY = -self.rotation.y / 180 * math.pi
        dx = strafe * math.cos(rotY) + forward * math.sin(rotY)
        dz = -strafe * math.sin(rotY) + forward * math.cos(rotY)

        # Check for collisions and update position
        new_x = self.position.x + dx
        new_z = self.position.z + dz

        if not world.collide((new_x, self.position.y, self.position.z)):
            self.position.x = new_x
        if not world.collide((self.position.x, new_y, self.position.z)):
            self.position.y = new_y
            self.jumped = False
        else:
            self.position.y = math.ceil(self.position.y - 0.5)
            self.dy = 0
            self.jumped = False
        if not world.collide((self.position.x, self.position.y, new_z)):
            self.position.z = new_z

        # Handle jumping
        if keys[key.SPACE] and not self.jumped and not self.flying:
            self.dy = self.jump_speed
            self.jumped = True

    def update_hunger(self, dt):
        self.hunger = max(0, self.hunger - dt * 0.1)  # Decrease hunger over time
        if self.hunger <= 0:
            self.take_damage(dt)  # Take damage when starving

    def mouse_motion(self, dx, dy):
        dx /= 8
        dy /= 8
        self.rotation.x = max(-90, min(90, self.rotation.x - dy))
        self.rotation.y += dx

    def get_sight_vector(self):
        rotX, rotY = self.rotation.x, self.rotation.y
        m = math.cos(math.radians(rotX))
        dy = math.sin(math.radians(rotX))
        dx = math.cos(math.radians(rotY - 90)) * m
        dz = math.sin(math.radians(rotY - 90)) * m
        return (dx, dy, dz)

    def get_targeted_block(self, world, max_distance=8):
        m = 8
        x, y, z = self.position
        dx, dy, dz = self.get_sight_vector()
        previous = None
        for _ in range(max_distance * m):
            key = (int(x), int(y), int(z))
            if key != previous and world.get_block(key):
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def mine(self, world):
        if self.mining_cooldown <= 0:
            target, _ = self.get_targeted_block(world)
            if target:
                block = world.get_block(target)
                if block:
                    self.inventory.add_item(block)
                    world.remove_block(target)
                    self.mining_cooldown = 0.3
                    return block
        return None

    def place_block(self, block_type, world):
        if self.attack_cooldown <= 0:
            target, previous = self.get_targeted_block(world)
            if previous:
                world.add_block(previous, block_type)
                self.attack_cooldown = 0.3
                return True
        return False

    def attack(self, mobs):
        if self.attack_cooldown <= 0:
            for mob in mobs:
                if self.distance_to(mob.position) < 2:
                    mob.take_damage(5)
                    self.attack_cooldown = 0.5

    def take_damage(self, amount):
        if self.damage_cooldown <= 0:
            self.health = max(0, self.health - amount)
            self.damage_cooldown = 1.0
            if self.health <= 0:
                self.die()

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def eat(self, food_item):
        if food_item in self.inventory.items and self.inventory.items[food_item] > 0:
            self.inventory.remove_item(food_item)
            if food_item == 'apple':
                self.hunger = min(self.max_hunger, self.hunger + 4)
            elif food_item == 'bread':
                self.hunger = min(self.max_hunger, self.hunger + 5)
            elif food_item == 'cooked_beef':
                self.hunger = min(self.max_hunger, self.hunger + 8)
            # Add more food items as needed

    def die(self):
        # Implement death behavior (e.g., respawn, drop items)
        self.position = Vec3(0, 20.0, 0)  # Respawn at a default position
        self.health = self.max_health
        self.hunger = self.max_hunger

    def distance_to(self, position):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position, position)))

    def toggle_flying(self):
        self.flying = not self.flying
        if self.flying:
            self.dy = 0

    def craft(self, recipe):
        return self.crafting_system.craft(recipe, self.inventory)

    def update_camera(self):
        # This method is left empty as we're not using actual rendering
        pass

    def get_position(self):
        return self.position

    def get_rotation(self):
        return self.rotation

    def reset_speed(self):
        self.speed = 5  # Reset to default speed