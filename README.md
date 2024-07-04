# Sandhucraft

Sandhucraft is a Minecraft-inspired voxel-based sandbox game built with Python and Pyglet. Explore a procedurally generated world, mine resources, craft items, and build structures in this engaging 3D environment.

![Sandhucraft Screenshot](screenshot.png)

## Features

- Procedurally generated 3D world
- Day/night cycle
- Weather system (rain, snow)
- Basic crafting system
- Resource gathering (mining)
- Block placement and destruction
- Simple mob AI (sheep and zombies)
- Inventory management
- Terrain features:
  - Trees
  - Caves
  - Ore deposits
  - Water bodies
- Save/load game functionality

## Requirements

- Python 3.7+
- Pyglet
- noise

## Installation

1. Clone the repository:
git clone https://github.com/hsandhu01/Sandhucraft.git
cd Sandhucraft
Copy
2. Install the required packages:
pip install pyglet noise
Copy
## Running the Game

To start Sandhucraft, run the following command in the project directory:
python main.py
Copy
## Controls

- WASD: Move
- Space: Jump
- Left mouse button: Break blocks
- Right mouse button: Place blocks
- E: Toggle inventory
- 1-5: Select hotbar items
- ESC: Toggle mouse capture
- F5: Save game
- F9: Load game

## Project Structure

- `main.py`: Main game loop and initialization
- `game_world.py`: World generation and management
- `player.py`: Player controls and physics
- `inventory.py`: Inventory system
- `crafting.py`: Crafting mechanics
- `mobs.py`: Mob AI and behavior
- `gui.py`: In-game user interface
- `weather.py`: Weather system
- `sound.py`: Sound effects and music
- `save_load.py`: Save/load game functionality

## Contributing

Contributions to Sandhucraft are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Minecraft (Mojang Studios)
- Built with [Pyglet](http://pyglet.org/)
- Uses [noise](https://pypi.org/project/noise/) for terrain generation

## TODO

- Implement multiplayer functionality
- Add more complex structures (villages, dungeons)
- Expand crafting system
- Introduce more diverse biomes
- Implement a combat system
- Add more mob types