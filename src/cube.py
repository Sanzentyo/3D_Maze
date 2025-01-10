import numpy as np
import pyxel

from draw_object import DrawObject
from tri_sprite import TriSprite

class Cube(DrawObject):
    """
    3D空間内の立方体を表現する基本クラス。

    Members:
        size (float): 立方体の一辺の長さ。
        half_size (float): サイズの半分（計算用）。
        center (np.ndarray): 中心座標。
        
    Methods:
        __init__(): コンストラクタ。立方体のパラメータ設定。
        _generate_vertices(): 頂点の生成。立方体の各頂点を計算。
        _generate_faces(): 立方体の面と色の生成。
        get_tri_sprites(): 描画用の三角形スプライト生成。
        is_adjacent(): 他の立方体との隣接判定。
    """
    def __init__(self, center_position, size=100):
        self.size = size
        self.half_size = size / 2
        super().__init__(center_position)

    def _generate_vertices(self):
        vertices = []
        for z in [-1, 1]:
            for y in [-1, 1]:
                for x in [-1, 1]:
                    vertex = self.center + np.array([
                        x * self.half_size,
                        y * self.half_size,
                        z * self.half_size,
                        0
                    ])
                    vertices.append(vertex)
        return vertices

    def _generate_faces(self):
        faces = [
            [0, 1, 2], [3, 2, 1],  # 前面
            [4, 6, 5], [7, 5, 6],  # 背面
            [0, 4, 1], [5, 1, 4],  # 上面
            [2, 3, 6], [6, 3, 7],  # 下面
            [1, 5, 3], [3, 5, 7],  # 右面
            [0, 2, 4], [2, 6, 4]   # 左面
        ]
        colors = [
            pyxel.COLOR_RED, pyxel.COLOR_RED,
            pyxel.COLOR_GREEN, pyxel.COLOR_GREEN,
            pyxel.COLOR_DARK_BLUE, pyxel.COLOR_DARK_BLUE,
            pyxel.COLOR_WHITE, pyxel.COLOR_WHITE,
            pyxel.COLOR_CYAN, pyxel.COLOR_CYAN,
            pyxel.COLOR_YELLOW, pyxel.COLOR_YELLOW
        ]
        return faces, colors

    def get_tri_sprites(self, view_projection_matrix, width, height) -> list[TriSprite]:
        transformed_vertices = []
        for vertex in self.vertices:
            pos = np.array(view_projection_matrix @ vertex).flatten()
            # wが0以下でも破棄せず、そのまま格納
            if len(pos) == 4:
                transformed_vertices.append(pos)
            else:
                # フォールバック: 不正な頂点とみなす
                transformed_vertices.append(np.array([0, 0, 0, np.nan]))

        tri_sprites = []
        for i in range(len(self.faces)):
            face = self.faces[i]
            color = self.colors[i]
            # 3頂点を取得
            p1_4d = transformed_vertices[face[0]]
            p2_4d = transformed_vertices[face[1]]
            p3_4d = transformed_vertices[face[2]]
            # TriSpriteを4D座標のまま生成し、clip_triangleで処理
            tri = TriSprite(
                (p1_4d[0], p1_4d[1], p1_4d[2], p1_4d[3]),
                (p2_4d[0], p2_4d[1], p2_4d[2], p2_4d[3]),
                (p3_4d[0], p3_4d[1], p3_4d[2], p3_4d[3]),
                color
            )
            # 画面幅・高さ指定で三角形を2Dクリップ
            clipped = tri.clip_triangle(width, height)
            tri_sprites.extend(clipped)

        return tri_sprites

    def is_adjacent(self, other, size):
        return (abs(self.center[0] - other.center[0]) == size and self.center[2] == other.center[2]) or (abs(self.center[2] - other.center[2]) == size and self.center[0] == other.center[0])

class RotatingCube(Cube):
    """
    Cubeを継承し、回転運動を行う。

    Members:
        position (np.ndarray): 立方体の中心座標 [x, y, z, 1]。
        size (float): 立方体の一辺の長さ。
        color (int): Pyxelカラーパレット番号。
        rotation_angle (float): 回転を管理する角度。
        rotation_speed (float): 回転速度。
        base_vertices (list[np.ndarray]): 基本頂点情報。
        
    Methods:
        __init__(): コンストラクタ。
        update(): フレームごとに回転角度を更新。
        _generate_vertices(): 回転を適用した頂点を生成。
    """
    def __init__(self, position, size=100, color=None):
        self.rotation_angle = 0
        self.rotation_speed = 0.05
        self.base_vertices = None
        super().__init__(position, size)
        if color is not None:
            # 全ての面の色を指定された色に変更
            self.colors = [color] * len(self.faces)
        # 初期頂点を保存
        self.base_vertices = super()._generate_vertices()

    def update(self):
        """フレームごとに回転角度を更新"""
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle > 2 * np.pi:
            self.rotation_angle -= 2 * np.pi
        # 頂点を更新
        self.vertices = self._generate_vertices()

    def _generate_vertices(self):
        """回転を適用した頂点を生成"""
        if self.base_vertices is None:
            return super()._generate_vertices()
        
        # Y軸周りの回転行列を生成
        c = np.cos(self.rotation_angle)
        s = np.sin(self.rotation_angle)
        rotation_matrix = np.array([
            [c,  0, s, 0],
            [0,  1, 0, 0],
            [-s, 0, c, 0],
            [0,  0, 0, 1]
        ])
        
        # Y軸方向に拡大する行列を生成
        scale_matrix = np.diag([1, 1.5, 1, 1])

        # 各頂点に回転を適用
        rotated_vertices = []
        for vertex in self.base_vertices:
            scaled = scale_matrix @ vertex
            rotated = rotation_matrix @ scaled
            rotated[:3] += self.position
            rotated_vertices.append(rotated)

        return rotated_vertices