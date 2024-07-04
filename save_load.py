import json
import os
import pickle

class SaveLoadManager:
    @staticmethod
    def save_game(player, world, mobs, filename='save.json'):
        save_data = {
            'player': {
                'position': list(player.position),
                'rotation': list(player.rotation),
                'health': player.health,
                'hunger': player.hunger,
                'inventory': player.inventory.slots,
            },
            'world': {
                'seed': world.seed,
                'modified_blocks': [
                    {'position': list(pos), 'block_type': block.block_type}
                    for chunk in world.chunks.values()
                    for pos, block in chunk.blocks.items()
                    if block.block_type != world.get_default_block_type(pos)
                ]
            },
            'mobs': [
                {
                    'type': type(mob).__name__,
                    'position': list(mob.position),
                    'health': mob.health
                }
                for mob in mobs
            ]
        }

        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

        # Save larger data separately using pickle
        with open(filename + '.pkl', 'wb') as f:
            pickle.dump(world.chunks, f)

        print(f"Game saved to {filename} and {filename}.pkl")

    @staticmethod
    def load_game(filename='save.json'):
        if not os.path.exists(filename) or not os.path.exists(filename + '.pkl'):
            print("No save file found.")
            return None

        with open(filename, 'r') as f:
            save_data = json.load(f)

        # Load larger data using pickle
        with open(filename + '.pkl', 'rb') as f:
            chunks = pickle.load(f)

        save_data['world']['chunks'] = chunks

        print(f"Game loaded from {filename} and {filename}.pkl")
        return save_data

    @staticmethod
    def apply_loaded_data(save_data, player, world, mob_manager):
        # Apply player data
        player.position = save_data['player']['position']
        player.rotation = save_data['player']['rotation']
        player.health = save_data['player']['health']
        player.hunger = save_data['player']['hunger']
        player.inventory.slots = save_data['player']['inventory']

        # Apply world data
        world.seed = save_data['world']['seed']
        world.chunks = save_data['world']['chunks']
        
        # Regenerate any missing chunks
        world.ensure_chunks_around_player(player)

        # Apply mob data
        mob_manager.mobs.clear()
        for mob_data in save_data['mobs']:
            mob_type = getattr(__import__('mobs'), mob_data['type'])
            mob = mob_type(mob_data['position'])
            mob.health = mob_data['health']
            mob_manager.mobs.append(mob)

    @staticmethod
    def delete_save(filename='save.json'):
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(filename + '.pkl'):
            os.remove(filename + '.pkl')
        print(f"Save files {filename} and {filename}.pkl deleted.")

class AutoSave:
    def __init__(self, game, interval=300):  # 5 minutes default
        self.game = game
        self.interval = interval
        self.time_since_last_save = 0

    def update(self, dt):
        self.time_since_last_save += dt
        if self.time_since_last_save >= self.interval:
            self.save()
            self.time_since_last_save = 0

    def save(self):
        SaveLoadManager.save_game(self.game.player, self.game.world, self.game.mobs)
        print("Auto-save completed.")