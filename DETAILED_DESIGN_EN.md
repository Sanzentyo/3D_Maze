# 3D Maze Detailed Design Document

[日本語版](./DETAILED_DESIGN.md)

## Table of Contents
1. [Overview](#1-overview)
2. [Overall Program Structure](#2-overall-program-structure)
3. [Key Processing Flows](#3-key-processing-flows)
4. [Class List](#4-class-list)
5. [Controls](#5-controls)

## 1. Overview
This document outlines the internal structure of the 3D Maze project, focusing on classes, methods, and variables.  
The project implements a simplified 3D rendering system on Pyxel, with functionality organized into distinct classes.

## 2. Overall Program Structure
The application is divided into three main scenes: `StartScene`, `GameScene`, and `ScoreScene`, each managing its own display and information.  
The `App` class initializes Pyxel and controls the main loop, handling updates and rendering of the current scene.

## 3. Key Processing Flows
### 3.1 Game Loop
1. `App.update()` is called each frame, executing the current scene's `update()`
2. `App.draw()` is called each frame, executing the current scene's `draw()`

### 3.2 3D Rendering Flow
1. `Scene.render_3d_scene()` obtains camera view matrix (`Camera.get_view_matrix()`) and projection matrix (`Camera.get_projection_matrix()`)
2. Matrices are combined to create `view_projection_matrix`
3. For each object group:
   - Convert 3D objects to `TriSprite` array using `get_tri_sprites()`
   - Sort by depth (`TriSprite.get_depth()`)
   - Execute drawing with `draw_tri_sprites()`:
     - Optional backface culling (`TriSprite.is_frontface()`)
     - View range clipping (`TriSprite.clip_triangle()`)
     - Convert to screen coordinates and draw with `TriSprite.draw()`
     - In wireframe mode, also execute `TriSprite.draw_wireframe()`

### 3.3 Player Movement Flow
1. `GameScene.update()` calls `Camera.move_and_is_coin_collected()` to update camera position based on keyboard input
2. `Map.set_camera_position_and_check_coin_collection()` executes:
   - Separate X and Z direction movement attempts
   - Wall collision detection using `Map.is_position_passable()`
   - Coin collection check with `Map.check_coin_collection()`
   - Set new position if movement is possible
3. Camera rotation updates based on mouse input via `Camera.process_mouse_movement()`

### 3.4 Typical Scenarios

#### 3.4.1 Coin Collection
1. `GameScene.update()` calls `Camera.move_and_is_coin_collected()` for coin collection detection during movement
2. On collection, plays sound effect and replaces coin ('.') with space (' ') in map data
3. Regenerates map objects and updates `GameScene` draw objects (floor, walls, spheres)

#### 3.4.2 Bird View Toggle (B key)
1. `GameScene.update()` detects B key input and starts transition animation
2. Linear interpolation over 30 frames for:
   - Camera position: current → `Map.get_bird_view()` position
   - Camera angle: current yaw/pitch → downward angle
   - FOV: normal 90° → bird view 50°
3. Shows player position as cube during bird view

#### 3.4.3 Master View Mode Toggle (Ctrl+M keys)
1. `GlobalState.update()` detects Ctrl+M input and toggles `is_master_view`
2. Master view enables:
   - Skip wall collision detection
   - Vertical movement with Space/Shift keys
   - Movement mode toggle with M key

#### 3.4.4 Wall Destruction (Coin + Focus + Left Click)
1. Pressing F key with ≥1 coin highlights forward wall
2. Left click while highlighted:
   - Plays sound effect
   - Replaces '#' with ' ' in map data
   - Regenerates map and draw objects
   - Consumes one coin

#### 3.4.5 Goal Reaching
1. `Map.check_goal_reached()` checks goal arrival, transitions to `ScoreScene` if reached
2. `ScoreScene` displays movement trail and score, allows retry or return to title

### 3.4.6 BGM Playback
1. Each scene initializes corresponding BGM data in `bgm_data` variable
2. Scene's `update()` checks if BGM isn't playing (`pyxel.play_pos(0) is None`):
   - For each `bgm_data` element (per audio channel):
     - Set sound data with `pyxel.sounds[ch].set(*sound)`
     - Start loop playback with `pyxel.play(ch, ch, loop=True)`
3. During scene transitions:
   - Stop current BGM with `pyxel.stop()`
   - New scene's `__init__()` sets and plays new BGM
4. BGM stops with `pyxel.stop()` on game exit (Q key) or retry from ScoreScene

BGM data in `bgm_data.py` includes:
- `start_scene_bgm_data`: Title screen BGM
- `game_scene_bgm_data`: Gameplay BGM
- `score_scene_bgm_data`: Score screen BGM

## 4. Class List

### 4.1 `App` (Main Application Class)
- Role: Initializes and manages entire Pyxel application
- Key variables:
  - `scene`: Current scene
  - `global_state`: Global state management
  - `width`, `height`: Screen dimensions
- Key methods:
  - `__init__()`: Initializes Pyxel, scene, and sound
  - `update()`: Executes current scene update
  - `draw()`: Executes current scene rendering

### 4.2 `Scene` (Scene Base Class)
- Role: Abstract base class providing common scene functionality
- Key methods:
  - `update()`: Updates scene state (abstract method)
  - `draw()`: Renders scene (abstract method)
  - `get_tri_sprites()`: Gets triangle sprites from 3D objects
  - `draw_tri_sprites()`: Renders triangle sprites
  - `render_3d_scene()`: Renders 3D scene using camera information

### 4.3 `StartScene` (Start Screen Class, derives from `Scene`)
- Role: Manages title screen
- Key variables:
  - `writer`: Text rendering utility
  - `psychedelic_sphere`: Decorative sphere for title
  - `title_camera`: Title screen camera
- Key methods:
  - `update()`: Starts game on Space key press
  - `draw()`: Renders title and demo screen

### 4.4 `GameScene` (Game Screen Class, derives from `Scene`)
- Role: Manages main gameplay
- Key variables:
  - `map`: Maze data and management
  - `camera`: Player view camera
  - `planes`: Floor objects
  - `walls`: Wall objects
  - `spheres`: Coin (sphere) objects
  - `player_cube`: Player position indicator for bird view
- Key methods:
  - `update()`: Updates game state (movement, collision, mode switches)
  - `draw()`: Renders 3D scene and UI
  - `_highlight_wall_in_front()`: Highlights wall in front
  - `_destroy_highlighted_wall()`: Handles wall destruction

### 4.5 `ScoreScene` (Score Screen Class, derives from `Scene`)
- Role: Displays results after reaching goal
- Key variables:
  - `game_scene`: Reference to completed game scene
  - `scoreboard`: UI for score display
- Key methods:
  - `update()`: Tab to switch score display, R to retry
  - `draw()`: Renders movement trail and score

### 4.6 `Map` (Map Class)
- Role: Manages maze and collision detection
- Key variables:
  - `map_data`: Maze string data ('#':wall, '.':coin, 's':start, 'g':goal)
  - `tile_size`: Size of each tile
  - `origin_pos`: Map reference coordinates
  - `camera_position`: Current camera position
- Key methods:
  - `generate_maze_map()`: Generates random maze
  - `is_position_passable()`: Checks if position is walkable
  - `check_coin_collection()`: Checks coin collection
  - `check_goal_reached()`: Checks goal arrival

### 4.7 `Camera` (Camera Class)
- Role: Controls 3D viewpoint
- Key variables:
  - `position`: Position coordinates
  - `yaw`: Horizontal angle
  - `pitch`: Vertical angle
  - `view_based_movement`: View-dependent movement flag
- Key methods:
  - `process_mouse_movement()`: Handles view rotation by mouse
  - `move_and_is_coin_collected()`: Updates position and checks coins
  - `get_view_matrix()`: Calculates view matrix
  - `get_projection_matrix()`: Calculates projection matrix

### 4.8 `GlobalState` (Global State Class)
- Role: Manages input states and mode flags
- Key variables:
  - `keyboard_state`: Key input states
  - `is_master_view`: Master view flag
  - `is_view_wireframe`: Wireframe display flag
  - `is_view_based_movement`: View-dependent movement flag
- Key methods:
  - `update()`: Updates input states
  - `toggle_wireframe()`: Toggles wireframe display
  - `toggle_master_view()`: Toggles master view mode

### 4.9 `DrawObject` (3D Draw Object Base Class)
- Role: Abstract base class providing common 3D object functionality
- Key variables:
  - `center`: Center coordinates [x, y, z, 1]
  - `vertices`: Vertex list
  - `faces`: Face vertex index list
  - `colors`: Face color information
- Key methods:
  - `_generate_vertices()`: Generates vertices (abstract method)
  - `_generate_faces()`: Generates faces and colors (abstract method)
  - `get_tri_sprites()`: Generates triangle sprite list

### 4.10 `Plane` (derives from `DrawObject`)
- Role: Represents floors and ceilings
- Key variables:
  - `plane_width`: Plane width
  - `plane_height`: Plane height
  - `color`: Drawing color
- Key methods:
  - `_generate_vertices()`: Generates 4 vertices
  - `_generate_faces()`: Creates 2 triangles
  - `get_tri_sprites()`: Generates plane triangle sprites

### 4.11 `EdgePlane` (derives from `Plane`)
- Role: Represents planes with borders
- Key variables:
  - `edge_width`: Edge width
  - `center_color`: Center area color
  - `edge_color`: Edge area color
- Key methods:
  - `_generate_vertices()`: Generates vertices with edges
  - `_generate_faces()`: Generates center and edge faces

### 4.12 `Wall` (derives from `DrawObject`)
- Role: Represents maze walls
- Key variables:
  - `positions`: List of wall positions
  - `size`: Wall side length
- Key methods:
  - `_generate_vertices()`: Generates vertices considering adjacent walls
  - `_generate_faces()`: Generates visible faces and colors
  - `_is_adjacent()`: Checks wall adjacency

### 4.13 `HighlightedWall` (derives from `Wall`)
- Role: Wall with highlight effect for focus mode
- Key variables:
  - `edge_width`: Edge thickness
  - `position`: Wall position
- Key methods:
  - `get_tri_sprites()`: Generates triangle sprites for edge drawing
  - `_generate_faces()`: Generates edge-only faces

### 4.14 `Cube` (derives from `DrawObject`)
- Role: Cubic object for player position display
- Key variables:
  - `size`: Side length
  - `half_size`: Half size (for calculations)
- Key methods:
  - `_generate_vertices()`: Generates 8 vertices
  - `_generate_faces()`: Generates 6 faces (12 triangles)
  - `is_adjacent()`: Checks adjacency with other cubes

### 4.15 `RotatingCube` (derives from `Cube`)
- Role: Animated rotating cube
- Key variables:
  - `rotation_angle`: Current rotation angle
  - `rotation_speed`: Rotation speed
  - `base_vertices`: Initial vertex data
- Key methods:
  - `update()`: Updates rotation angle and Y-axis scale
  - `_generate_vertices()`: Generates rotation-applied vertices

### 4.16 `Sphere` (derives from `DrawObject`)
- Role: Spherical object for coins
- Key variables:
  - `radius`: Sphere radius
  - `segments`: Subdivision count
- Key methods:
  - `_generate_vertices()`: Generates vertices using latitude/longitude
  - `_generate_faces()`: Subdivides sphere surface and sets colors
  - `get_tri_sprites()`: Generates sphere triangle sprites

### 4.17 `RotatingSphere` (derives from `Sphere`)
- Role: Animated rotating sphere
- Key variables:
  - `rotation_angle`: Rotation angle
  - `rotation_axis`: Rotation axis
  - `rotation_speed`: Rotation speed
- Key methods:
  - `update()`: Updates rotation angle
  - `_generate_vertices()`: Generates rotation matrix-applied vertices

### 4.18 `PsychedelicSphere` (derives from `RotatingSphere`)
- Role: Color-changing rotating sphere
- Key variables:
  - `color_time`: Color change time management
  - `color_speed`: Color change speed
- Key methods:
  - `update()`: Updates rotation and color
  - `_generate_faces()`: Sets time-dependent colors

### 4.19 `TriSprite` (Triangle Sprite Class)
- Role: Basic shape for projecting and drawing 3D triangles in 2D
- Key variables:
  - `p1`, `p2`, `p3`: Triangle vertex coordinates (x, y, z, w)
  - `color`: Color information for Pyxel drawing
- Key methods:
  - `get_depth()`: Calculates depth value (distance from camera)
  - `is_frontface()`: Checks if front-facing (for backface culling)
  - `draw()`: Draws triangle
  - `draw_wireframe()`: Draws as wireframe
  - `clip_triangle()`: Clips triangle within view range
  - `_clip_near_plane()`: Clips against near plane
  - `_intersect_near()`: Calculates near plane intersection

## 5. Controls
### 5.1 Gameplay Controls
- Movement: WASD keys or Arrow keys
- Toggle Bird View: B key
- Exit Game: ESC key or Q key
- View Control: Mouse movement
- Disable View Control and Show Mouse: Ctrl key
- Focus: F key (requires at least one coin)
- Destroy Wall: Left-click while focusing

### 5.2 Debug Controls
- Toggle Master View Mode: Ctrl + M keys (disables goal detection and wall collision)
- Vertical Movement: In Master View Mode, Space to ascend, Shift to descend
- Toggle Movement Mode: M key in Master View Mode switches between View Base and Yaw Base movement
- Toggle Wireframe Display: Ctrl + W keys
