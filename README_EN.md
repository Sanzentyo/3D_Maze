# 3D Maze
A first-person 3D maze escape game created with pyxel. The BGM is generated using [8bit BGM generator](https://github.com/shiromofufactory/8bit-bgm-generator).

- [日本語のドキュメント](./README.md)
- [Detailed Design Document](./DETAILED_DESIGN_EN.md)

## Demo Video
<div><video controls src="https://raw.githubusercontent.com/Sanzentyo/3D_Maze/refs/heads/main/3D_Maze_Demo.mp4" title="3D_Maze_Demo.mp4" muted="false"></video></div>

## How to Run Native Version
First, clone this repository:
```sh
git clone https://github.com/Sanzentyo/3D_Maze.git
```

Then, execute the following commands:
```sh
cd 3D_Maze
pip install requirements.txt # Install required libraries (not needed if pyxel, numpy, pyxel-universal-font are already installed)
python src/App.py # Launch the game
```
If you use [uv](https://github.com/astral-sh/uv), execute the following command:
```sh
uv run src/App.py
```

## Web Version
Due to pyxel specifications and performance considerations, text, scoreboard, and BGM have been removed. Otherwise, it functions the same as the native version.  
https://sanzentyo.github.io/3D_Maze

## Controls
For detailed control information, please refer to the [Detailed Design Document](./DETAILED_DESIGN_EN.md#5-controls).

### Basic Controls
- Movement: WASD keys or Arrow keys
- Toggle Bird View: B key
- Exit Game: ESC key or Q key
- View Control: Mouse movement
- Disable View Control and Show Mouse: Ctrl key
- Focus: F key (requires at least one coin)
- Destroy Wall: Left-click while focusing

### Debug Controls
- Toggle Master View Mode: Ctrl + M keys. In Master View Mode, goal detection and wall collision are disabled
- Vertical Movement: In Master View Mode, Space to ascend, Shift to descend
- Toggle Movement Mode: M key in Master View Mode switches between View Base movement and Yaw Base movement. Normal mode uses Yaw Base movement
- Toggle Wireframe Display: Ctrl + W keys
