import random
import math
from pyglet.gl import *

class Mob:
    def __init__(self, position, mob_type):
        self.position = list(position)
        self.mob_type = mob_type
        self.health = 20
        self.texture = pyglet.image.load(f'textures/{mob_type}.png').get_texture()
        self.movement_cooldown = 0
        self.attack_cooldown = 0
        self.attack_range = 1.5
        self.attack_damage = 2
        self.speed = 2.0

    def update(self, dt, world, player):
        self.movement_cooldown -= dt
        self.attack_cooldown -= dt
        if self.movement_cooldown <= 0:
            self.move(world, player)
            self.movement_cooldown = random.uniform(0.5, 2.0)
        if self.can_attack(player):
            self.attack(player)

    def move(self, world, player):
        dx = random.uniform(-1, 1)
        dz = random.uniform(-1, 1)
        magnitude = math.sqrt(dx**2 + dz**2)
        if magnitude > 0:
            dx /= magnitude
            dz /= magnitude
        new_x = self.position[0] + dx * self.speed
        new_z = self.position[2] + dz * self.speed
        if not world.collide((new_x, self.position[1], new_z)):
            self.position[0] = new_x
            self.position[2] = new_z

    def can_attack(self, player):
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position, player.position)))
        return distance <= self.attack_range and self.attack_cooldown <= 0

    def attack(self, player):
        player.take_damage(self.attack_damage)
        self.attack_cooldown = 1.0  # 1 second cooldown between attacks

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        # Implement death behavior (e.g., drop items, remove from world)
        pass

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(-90, 1, 0, 0)  # Rotate to make the sprite vertical
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-0.5, 0, -1)
        glTexCoord2f(1, 0); glVertex3f(0.5, 0, -1)
        glTexCoord2f(1, 1); glVertex3f(0.5, 0, 1)
        glTexCoord2f(0, 1); glVertex3f(-0.5, 0, 1)
        glEnd()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

class Sheep(Mob):
    def __init__(self, position):
        super().__init__(position, 'sheep')
        self.health = 8
        self.attack_damage = 0  # Sheep don't attack
        self.speed = 1.5

    def update(self, dt, world, player):
        super().update(dt, world, player)
        # Add sheep-specific behavior here (e.g., grazing)

    def die(self):
        # Drop wool and mutton
        pass

class Zombie(Mob):
    def __init__(self, position):
        super().__init__(position, 'zombie')
        self.health = 20
        self.attack_damage = 3
        self.speed = 2.0
        self.aggro_range = 10  # Range at which zombie becomes aggressive

    def update(self, dt, world, player):
        super().update(dt, world, player)
        if self.distance_to(player.position) < self.aggro_range:
            self.move_towards_player(world, player)

    def move_towards_player(self, world, player):
        dx = player.position[0] - self.position[0]
        dz = player.position[2] - self.position[2]
        distance = math.sqrt(dx**2 + dz**2)
        if distance > 0:
            dx /= distance
            dz /= distance
        new_x = self.position[0] + dx * self.speed
        new_z = self.position[2] + dz * self.speed
        if not world.collide((new_x, self.position[1], new_z)):
            self.position[0] = new_x
            self.position[2] = new_z

    def die(self):
        # Drop rotten flesh
        pass

    def distance_to(self, position):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.position, position)))

class Skeleton(Mob):
    def __init__(self, position):
        super().__init__(position, 'skeleton')
        self.health = 20
        self.attack_damage = 2
        self.speed = 1.8
        self.attack_range = 8.0  # Skeletons can attack from a distance

    def update(self, dt, world, player):
        super().update(dt, world, player)
        if self.distance_to(player.position) < self.attack_range:
            self.shoot_arrow(player)

    def shoot_arrow(self, player):
        if self.attack_cooldown <= 0:
            # Implement arrow shooting logic
            player.take_damage(self.attack_damage)
            self.attack_cooldown = 2.0  # 2 seconds cooldown between shots

    def die(self):
        # Drop bones and arrows
        pass

class MobManager:
    def __init__(self, world):
        self.world = world
        self.mobs = []
        self.mob_types = [Sheep, Zombie, Skeleton]

    def spawn_mobs(self, num_mobs):
        for _ in range(num_mobs):
            mob_type = random.choice(self.mob_types)
            x = random.uniform(-64, 64)
            z = random.uniform(-64, 64)
            y = self.world.get_height(x, z) + 1
            self.mobs.append(mob_type((x, y, z)))

    def update(self, dt, player):
        for mob in self.mobs[:]:  # Create a copy of the list to safely remove mobs
            mob.update(dt, self.world, player)
            if mob.health <= 0:
                self.mobs.remove(mob)

    def draw(self):
        for mob in self.mobs:
            mob.draw()