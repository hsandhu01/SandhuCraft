import random
import math

class Mob:
    def __init__(self, position, mob_type):
        self.position = list(position)
        self.mob_type = mob_type
        self.health = 20
        self.speed = 2
        self.direction = [0, 0, 0]
        self.update_interval = random.uniform(0.5, 2.0)
        self.time_since_last_update = 0

    def update(self, dt, world, player):
        self.time_since_last_update += dt
        if self.time_since_last_update >= self.update_interval:
            self.update_direction(world, player)
            self.time_since_last_update = 0

        new_position = [
            self.position[0] + self.direction[0] * self.speed * dt,
            self.position[1] + self.direction[1] * self.speed * dt,
            self.position[2] + self.direction[2] * self.speed * dt
        ]

        if not world.collide(new_position):
            self.position = new_position

    def update_direction(self, world, player):
        pass  # To be implemented by subclasses

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        # Handle mob death (e.g., drop items, remove from world)
        pass

    def distance_to(self, other_position):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position, other_position)))

    def draw(self):
        # Simplified drawing (no actual rendering)
        pass

class Sheep(Mob):
    def __init__(self, position):
        super().__init__(position, 'sheep')
        self.wool_grown = True

    def update_direction(self, world, player):
        # Simple random movement
        self.direction = [
            random.uniform(-1, 1),
            0,  # No vertical movement
            random.uniform(-1, 1)
        ]
        # Normalize the direction vector
        magnitude = math.sqrt(sum(d*d for d in self.direction))
        self.direction = [d / magnitude for d in self.direction]

    def shear(self):
        if self.wool_grown:
            self.wool_grown = False
            return 'wool'
        return None

    def update(self, dt, world, player):
        super().update(dt, world, player)
        if not self.wool_grown:
            if random.random() < 0.001:  # Small chance to regrow wool each update
                self.wool_grown = True

class Zombie(Mob):
    def __init__(self, position):
        super().__init__(position, 'zombie')
        self.attack_range = 1.5
        self.attack_cooldown = 0
        self.attack_interval = 1.0  # Attack once per second

    def update_direction(self, world, player):
        # Move towards the player
        direction = [
            player.position[0] - self.position[0],
            0,  # No vertical movement
            player.position[2] - self.position[2]
        ]
        magnitude = math.sqrt(sum(d*d for d in direction))
        self.direction = [d / magnitude for d in direction] if magnitude > 0 else [0, 0, 0]

    def update(self, dt, world, player):
        super().update(dt, world, player)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        if self.distance_to(player.position) <= self.attack_range and self.attack_cooldown == 0:
            self.attack(player)

    def attack(self, player):
        player.take_damage(5)  # Zombie deals 5 damage
        self.attack_cooldown = self.attack_interval