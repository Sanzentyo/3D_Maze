# 3D Maze
A first-person 3D maze escape game created with pyxel. The BGM is generated using [8bit BGM generator](https://github.com/shiromofufactory/8bit-bgm-generator).

### [日本語のドキュメント](./README.md)

## Demo Video
<div><video controls src="https://raw.githubusercontent.com/Sanzentyo/3D_Maze/refs/heads/main/3D_Maze_Demo.mp4" title="3D_Maze_Demo.mp4" muted="false"></video></div>

## How to Run Native Version
```sh
# Clone the repository
git clone https://github.com/Sanzentyo/3D_Maze.git
cd 3D_Maze

# Using pip
pip install -r requirements.txt # Install dependencies (not needed if pyxel, numpy, pyxel-universal-font are already installed)
python src/App.py # Launch the game

# Using uv
uv run src/App.py
```

## Web Version
Due to pyxel specifications and performance considerations, text, scoreboard, and BGM have been removed. Otherwise, it functions the same as the native version.  
https://sanzentyo.github.io/3D_Maze

## Controls

### Basic Controls
| Action | Key/Mouse |
|--------|-----------|
| Movement | WASD keys or Arrow keys |
| View Control | Mouse movement |
| Toggle Bird View | B key |
| Exit Game | ESC key or Q key |
| Disable View Control and Show Mouse | Ctrl key |
| Focus | F key (requires at least one coin) |
| Destroy Wall | Left-click while focusing |

### Debug Controls
| Action | Key/Mouse |
|--------|-----------|
| Toggle Master View Mode | Ctrl + M keys |
| Vertical Movement | Space (ascend), Shift (descend) *Master View Mode only |
| Toggle Movement Mode | M key *Master View Mode only |
| Toggle Wireframe Display | Ctrl + W keys |
