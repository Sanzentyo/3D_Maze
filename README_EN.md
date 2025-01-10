# 3D Maze
A first-person 3D maze escape game created with pyxel. The BGM is generated using [8bit BGM generator](https://github.com/shiromofufactory/8bit-bgm-generator).

[日本語のドキュメント](./README.md)

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

## Web Version
Due to pyxel specifications and performance considerations, text, scoreboard, and BGM have been removed. Otherwise, it functions the same as the native version.  
https://sanzentyo.github.io/3D_Maze

## Controls
- Movement: WASD keys or Arrow keys
- Toggle Bird View: B key
- Exit Game: ESC key or Q key
- Mouse Movement: Change camera direction
- Focus: Press F key with at least one coin collected
- Destroy Wall: Left-click while focusing

## Debug Controls
- Toggle Master View Mode: Ctrl + M keys. In Master View Mode, goal detection and wall collision are disabled.
- Vertical Movement: In Master View Mode, Space to ascend, Shift to descend
- Toggle Movement Mode: In Master View Mode, M key switches between View Base movement and Yaw Base movement. In normal mode (non-Master View Mode), movement is always Yaw Base.
- Toggle Wireframe Display: Ctrl + W keys
