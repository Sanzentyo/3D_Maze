import numpy as np
from plane import Plane, EdgePlane
from sphere import Sphere
import pyxel
from maze_generator import MazeGenerator, StartEndStrategy

class Map:
    """
    迷路やコインの配置、スタート・ゴール位置を管理。

    Members:
        map_data (list[str]): 壁や床を文字で定義したマップデータ。
        tile_size (float): マップ1マスのサイズ。
        origin_pos (list[float]): マップ描画基点(ワールド座標)。
        camera_position (np.ndarray): カメラの現在位置を反映する。
        sphere_positions (list[np.ndarray]): ステージ上の球体の座標リスト。
        floor_objects (list[Plane]): 床オブジェクトのリスト。
        wall_positions (list[np.ndarray]): 壁の位置座標リスト。
        start_position (list[float]): スタート位置の座標。
        goal_position (list[float]): ゴール位置の座標。

    Methods:
        generate_maze_map(): 迷路を生成してMapインスタンスを返す。
        __init__(): コンストラクタ。
        _process_map(): マップデータからオブジェクト生成。
        get_wall_groups(): 隣接する壁をグループ化。
        get_draw_objects(): 描画オブジェクトのリストを返す。
        get_floor_objects(): 床オブジェクトのリストを返す。
        get_wall_objects(): 壁オブジェクトのリストを返す。
        get_sphere_objects(): Sphereオブジェクトのリストを返す。
        get_start_position(): スタート位置の座標を返す。
        get_initial_view_direction(): スタート地点から見るべき方向を返す。
        get_bird_view(): 鳥瞰図の位置と向きを返す。
        is_position_passable(): 指定された座標が移動可能かどうかを確認。
        check_coin_collection(): コイン取得判定を行う。
        check_goal_reached(): カメラ位置がゴールタイル上にあるかを判定。
        set_camera_position_and_check_coin_collection(): カメラの新しい位置を設定し、衝突判定とコイン取得判定を行う。
        get_remaining_coins(): 残りのコイン数を返す。
        get_camera_position(): 現在のカメラの位置を取得。
    """
    @classmethod
    def generate_maze_map(cls, width, height, origin_pos, tile_size, 
                         coin_count=None, strategy=StartEndStrategy.DIAGONAL,
                         start_pos=None, end_pos=None, min_distance=None):
        """迷路を生成してMapインスタンスを返す"""
        generator = MazeGenerator(width, height)
        map_data = generator.generate(
            coin_count=coin_count,
            strategy=strategy,
            start_pos=start_pos,
            end_pos=end_pos,
            min_distance=min_distance
        )
        return cls(map_data, origin_pos, tile_size)

    def __init__(self, map_data: list[str], origin_pos: list[float], tile_size: float):
        self.map_data = map_data
        self.origin_pos = origin_pos
        self.tile_size = tile_size
        self.floor_objects = []
        self.wall_positions = []
        self.sphere_positions = []
        self.camera_position = None  # 初期化時にはNoneに設定
        self.start_position = None   # スタート位置を保存する変数を追加
        self._process_map()
        
        # スタート位置が見つかった場合、カメラの初期位置として設定
        if self.start_position:
            self.camera_position = self.start_position.copy()
        else:
            self.camera_position = origin_pos.copy()

    def _process_map(self):
        rows = len(self.map_data)
        cols = len(self.map_data[0])
        
        # マップの中心を原点に合わせるためのオフセットを計算
        offset_x = -cols * self.tile_size / 2
        offset_z = -rows * self.tile_size / 2

        for row in range(rows):
            for col in range(cols):
                # タイル位置を計算（原点を中心とした配置）
                x = offset_x + col * self.tile_size
                z = offset_z + row * self.tile_size

                tile = self.map_data[row][col]
                if tile == '#':
                    self.wall_positions.append([x, self.origin_pos[1], z])
                elif tile == '.':
                    self.sphere_positions.append([x, self.origin_pos[1] - 10, z])
                    self.floor_objects.append(
                        Plane([x, 50, z],
                              width=self.tile_size,
                              height=self.tile_size,
                              color=pyxel.COLOR_NAVY if (row + col) % 2 == 0 else pyxel.COLOR_GRAY)
                    )
                elif tile == 's':
                    # スタート位置を記録（原点からの相対位置）
                    self.start_position = [x, -5, z]
                    self.floor_objects.append(
                        EdgePlane([x, 50, z],
                                    width=self.tile_size,
                                    height=self.tile_size,
                                    center_color=pyxel.COLOR_LIGHT_BLUE,
                                    edge_color=pyxel.COLOR_NAVY if (row + col) % 2 == 0 else pyxel.COLOR_GRAY,
                                    edge_width=10)
                    )
                elif tile == 'g':
                    # ゴール位置を記録
                    self.goal_position = [x, self.origin_pos[1] - 10, z]
                    # ゴール位置にも床を配置
                    self.floor_objects.append(
                        EdgePlane([x, 50, z],
                                    width=self.tile_size,
                                    height=self.tile_size,
                                    center_color=pyxel.COLOR_YELLOW,
                                    edge_color=pyxel.COLOR_NAVY if (row + col) % 2 == 0 else pyxel.COLOR_GRAY,
                                    edge_width=10)
                    )
                else:  # 空白の場合
                    self.floor_objects.append(
                        Plane([x, 50, z],
                              width=self.tile_size,
                              height=self.tile_size,
                              color=pyxel.COLOR_NAVY if (row + col) % 2 == 0 else pyxel.COLOR_GRAY)
                    )

    def get_wall_groups(self) -> list[list[list[float]]]:
        """隣接する壁をグループ化"""
        visited = set()
        wall_groups = []
        
        def get_neighbors(pos):
            x, y, z = pos
            neighbors = []
            for wall_pos in self.wall_positions:
                if tuple(wall_pos) not in visited and \
                   ((abs(wall_pos[0] - x) == self.tile_size and wall_pos[2] == z) or
                    (abs(wall_pos[2] - z) == self.tile_size and wall_pos[0] == x)):
                    neighbors.append(wall_pos)
            return neighbors

        for wall_pos in self.wall_positions:
            if tuple(wall_pos) in visited:
                continue
                
            # 新しいグループを開始
            group = [wall_pos]
            visited.add(tuple(wall_pos))
            stack = get_neighbors(wall_pos)
            
            while stack:
                current = stack.pop()
                if tuple(current) not in visited:
                    group.append(current)
                    visited.add(tuple(current))
                    stack.extend(get_neighbors(current))
            
            wall_groups.append(group)
        
        return wall_groups

    def get_draw_objects(self) -> list:
        """描画オブジェクトのリストを返す"""
        from wall import Wall
        draw_objects = []
        
        # 床オブジェクトを追加
        draw_objects.extend(self.floor_objects)
        
        # 壁グループからWallオブジェクトを生成
        for group in self.get_wall_groups():
            draw_objects.append(Wall(group, self.tile_size))
        
        return draw_objects

    def get_floor_objects(self) -> list:
        """床オブジェクトのリストを返す"""
        return self.floor_objects

    def get_wall_objects(self) -> list:
        """壁オブジェクトのリストを返す"""
        from wall import Wall
        wall_objects = []
        for group in self.get_wall_groups():
            wall_objects.append(Wall(group, self.tile_size))
        return wall_objects

    def get_sphere_objects(self) -> list[Sphere]:
        """Sphereオブジェクトのリストを返す"""
        return [Sphere(pos, radius=30, segments=4) for pos in self.sphere_positions]

    def get_start_position(self) -> list[float]:
        """スタート位置の座標を返す"""
        if self.start_position:
            return self.start_position.copy()
        return [0, -5, 0]  # スタート位置が未設定の場合のデフォルト値

    def get_initial_view_direction(self) -> tuple[float, float]:
        """
        スタート地点から見るべき方向を返す（yaw, pitch）
        ゴール方向を向くように計算
        """
        dx = self.goal_position[0] - self.start_position[0]
        dz = self.goal_position[2] - self.start_position[2]
        
        # yawの計算（水平方向の角度）
        yaw = np.arctan2(dz, dx)
        
        # pitchの計算（垂直方向の角度）
        # dy = self.goal_position[1] - self.start_position[1]
        # dist = np.sqrt(dx*dx + dz*dz)
        # pitch = np.arctan2(dy, dist)
        pitch = -0.1  # 少し下向きに固定
        
        return yaw, pitch
    
    def get_bird_view(self) -> tuple[float, float]:
        """
        鳥瞰図の位置と向きを返す
        位置はマップの中心、向きは真下
        """
        return [
            self.origin_pos[0]-self.tile_size/2,
            self.origin_pos[1] - 1000,
            self.origin_pos[2]-self.tile_size/2
        ], (np.pi / 2, np.pi / 2)

    def is_position_passable(self, x: float, z: float) -> bool:
        """指定された座標が移動可能かどうかを確認"""
        tile_size = self.tile_size
        offset = tile_size / 2
        map_x = int((offset + x + len(self.map_data[0]) * tile_size / 2) / tile_size)
        map_z = int((offset + z + len(self.map_data) * tile_size / 2) / tile_size)
        if 0 <= map_x < len(self.map_data[0]) and 0 <= map_z < len(self.map_data):
            return self.map_data[map_z][map_x] in [' ', '.', 's', 'g']
        return False

    def check_coin_collection(self, x: float, z: float) -> bool:
        """コイン取得判定を行う"""
        tile_size = self.tile_size
        offset = tile_size / 2
        
        # マップ座標への変換（is_position_passableと同じ方式）
        map_x = int((offset + x + len(self.map_data[0]) * tile_size / 2) / tile_size)
        map_z = int((offset + z + len(self.map_data) * tile_size / 2) / tile_size)
        
        # マップ範囲チェック
        if not (0 <= map_x < len(self.map_data[0]) and 0 <= map_z < len(self.map_data)):
            return False
            
        # タイル内での相対位置を計算（オフセット付き）
        tile_pos_x = offset + x + len(self.map_data[0]) * tile_size / 2
        tile_pos_z = offset + z + len(self.map_data) * tile_size / 2
        local_x = tile_pos_x % tile_size
        local_z = tile_pos_z % tile_size
        
        # 中心からの距離をチェック（タイルサイズの1/4を判定範囲とする）
        center_x = tile_size / 2
        center_z = tile_size / 2
        detection_size = tile_size / 4

        if (abs(local_x - center_x) <= detection_size and 
            abs(local_z - center_z) <= detection_size):
            if self.map_data[map_z][map_x] == '.':
                # マップデータを更新（コインを空白に変更）
                self.map_data[map_z] = (
                    self.map_data[map_z][:map_x] + 
                    ' ' + 
                    self.map_data[map_z][map_x+1:]
                )
                # マップオブジェクトを更新
                self.floor_objects = []
                self.wall_positions = []
                self.sphere_positions = []
                self._process_map()
                return True
        return False

    def check_goal_reached(self, x: float, z: float) -> bool:
        """
        カメラ位置がゴールタイル('g')上にあるかを判定
        """
        tile_size = self.tile_size
        offset = tile_size / 2
        map_x = int((offset + x + len(self.map_data[0]) * tile_size / 2) / tile_size)
        map_z = int((offset + z + len(self.map_data) * tile_size / 2) / tile_size)
        
        # タイル内での相対位置を計算（オフセット付き）
        tile_pos_x = offset + x + len(self.map_data[0]) * tile_size / 2
        tile_pos_z = offset + z + len(self.map_data) * tile_size / 2
        local_x = tile_pos_x % tile_size
        local_z = tile_pos_z % tile_size
        
        # 中心からの距離をチェック（タイルサイズの1/2を判定範囲とする）
        center_x = tile_size / 2
        center_z = tile_size / 2
        detection_size = tile_size / 2

        if (0 <= map_x < len(self.map_data[0]) and 0 <= map_z < len(self.map_data) and
            abs(local_x - center_x) <= detection_size and 
            abs(local_z - center_z) <= detection_size):
            return self.map_data[map_z][map_x] == 'g'
        return False

    def set_camera_position_and_check_coin_collection(self, x: float, z: float) -> bool:
        """カメラの新しい位置を設定し、衝突判定とコイン取得判定を行う"""
        is_collected = False

        # X方向の移動をチェック
        if self.is_position_passable(x, self.camera_position[2]):
            self.camera_position[0] = x
            if self.check_coin_collection(x, self.camera_position[2]):
                is_collected = True
        
        # Z方向の移動をチェック
        if self.is_position_passable(self.camera_position[0], z):
            self.camera_position[2] = z
            if self.check_coin_collection(self.camera_position[0], z):
                is_collected = True

        return is_collected

    def get_remaining_coins(self) -> int:
        """残りのコイン数を返す"""
        return sum(row.count('.') for row in self.map_data)

    def get_camera_position(self) -> list[float]:
        """現在のカメラの位置を取得"""
        return self.camera_position.copy()
