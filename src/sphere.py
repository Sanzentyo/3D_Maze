import numpy as np
import pyxel

from draw_object import DrawObject
from tri_sprite import TriSprite

class Sphere(DrawObject):
    """
    3D空間内の球体を表現するクラス。

    Members:
        radius (float): 球体の半径。
        segments (int): 球体の分割数。
        center (np.ndarray): 中心座標。

    Methods:
        _generate_vertices(): 球体の頂点生成。
        _generate_faces(): 球体の面と色の生成。
        get_tri_sprites(): 描画用の三角形スプライト生成。
    """
    def __init__(self, center_position, radius=50, segments=16):
        self.radius = radius
        self.segments = segments
        super().__init__(center_position)

    def _generate_vertices(self):
        vertices = []
        # 緯度経度で分割
        for i in range(self.segments + 1):
            lat = np.pi * (-0.5 + float(i) / self.segments)
            for j in range(self.segments):
                lon = 2 * np.pi * float(j) / self.segments
                x = np.cos(lat) * np.cos(lon)
                y = np.cos(lat) * np.sin(lon)
                z = np.sin(lat)
                vertex = self.center + np.array([
                    x * self.radius,
                    y * self.radius,
                    z * self.radius,
                    0
                ])
                vertices.append(vertex)
        return vertices

    def _generate_faces(self):
        faces = []
        colors = []
        # 四角形を2つの三角形に分割
        for i in range(self.segments):
            for j in range(self.segments):
                # 現在の行の頂点インデックス
                current = i * self.segments + j
                # 次の行の頂点インデックス
                next_row = (i + 1) * self.segments + j
                # 次の列のインデックス（最後の列は最初に戻る）
                next_col = (j + 1) % self.segments
                
                # 2つの三角形を追加
                faces.append([current, next_row, i * self.segments + next_col])
                faces.append([next_row, (i + 1) * self.segments + next_col, i * self.segments + next_col])
                
                # 色を設定（位置に応じて色を変える）
                color1 = pyxel.COLOR_NAVY if i % 2 == j % 2 else pyxel.COLOR_PURPLE
                color2 = pyxel.COLOR_NAVY if i % 2 != j % 2 else pyxel.COLOR_PURPLE
                colors.extend([color1, color2])
        
        return faces, colors

    def get_tri_sprites(self, view_projection_matrix, width, height) -> list[TriSprite]:
        transformed_vertices = []
        for vertex in self.vertices:
            pos = np.array(view_projection_matrix @ vertex).flatten()
            if len(pos) == 4:
                transformed_vertices.append(pos)
            else:
                transformed_vertices.append(np.array([0, 0, 0, np.nan]))

        tri_sprites = []
        for i in range(len(self.faces)):
            face = self.faces[i]
            color = self.colors[i]
            p1_4d = transformed_vertices[face[0]]
            p2_4d = transformed_vertices[face[1]]
            p3_4d = transformed_vertices[face[2]]
            
            tri = TriSprite(
                (p1_4d[0], p1_4d[1], p1_4d[2], p1_4d[3]),
                (p2_4d[0], p2_4d[1], p2_4d[2], p2_4d[3]),
                (p3_4d[0], p3_4d[1], p3_4d[2], p3_4d[3]),
                color
            )
            clipped = tri.clip_triangle(width, height)
            tri_sprites.extend(clipped)

        return tri_sprites

class RotatingSphere(Sphere):
    """
    Sphereを継承し、一定速度で回転する球体オブジェクト。

    Members:
        position (np.ndarray): 球体の中心座標。
        radius (float): 球体の半径。
        segments (int): 球を描画する際の分割数。
        rotation_angle (float): 回転角度を蓄積する変数。
        rotation_axis (np.ndarray): 回転軸の方向ベクトル。
        rotation_speed (float): 回転速度。
        base_vertices (list[np.ndarray]): 基本頂点情報。

    Methods:
        __init__(): コンストラクタ。
        update(): フレームごとに回転角度を更新して頂点を再計算。
        _generate_vertices(): 回転を適用した頂点を生成。
    """
    def __init__(self, center_position, radius=50, segments=16, rotation_axis=np.array([0, 1, 0])):
        self.rotation_angle = 0
        self.rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
        self.rotation_speed = 0.02
        self.base_vertices = None  # 基本頂点を保存
        super().__init__(center_position, radius, segments)
        # 初期頂点を保存
        self.base_vertices = super()._generate_vertices()

    def update(self):
        """フレームごとに回転角度を更新して頂点を再計算"""
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle > 2 * np.pi:
            self.rotation_angle -= 2 * np.pi
        # 頂点を更新
        self.vertices = self._generate_vertices()

    def _generate_vertices(self):
        """回転を適用した頂点を生成"""
        if self.base_vertices is None:
            return super()._generate_vertices()
        
        # 回転行列を生成
        c = np.cos(self.rotation_angle)
        s = np.sin(self.rotation_angle)
        x, y, z = self.rotation_axis
        rotation_matrix = np.array([
            [c + x*x*(1-c),    x*y*(1-c) - z*s,  x*z*(1-c) + y*s, 0],
            [y*x*(1-c) + z*s,  c + y*y*(1-c),    y*z*(1-c) - x*s, 0],
            [z*x*(1-c) - y*s,  z*y*(1-c) + x*s,  c + z*z*(1-c),   0],
            [0,                0,                 0,                1]
        ])

        # 各頂点に回転を適用
        rotated_vertices = []
        for vertex in self.base_vertices:
            # 中心を原点に移動
            centered = vertex - self.center
            # 回転を適用
            rotated = rotation_matrix @ centered
            # 中心位置を戻す
            final = rotated + self.center
            rotated_vertices.append(final)

        return rotated_vertices
    
class PsychedelicSphere(RotatingSphere):
    """
    RotatingSphereを継承し、色を周期的に変化させる球体。

    Members:
        color_phase (float): 色変化に用いる位相。
        color_speed (float): 色変化の速度。
    
    Methods:
        __init__(): コンストラクタ。
        _generate_faces(): 色情報を付与した面を生成。
        update(): 色変化を行う。
    """
    def __init__(self, center_position, radius=50, segments=16, color_speed=0.05):
        super().__init__(center_position, radius, segments)
        self.color_time = 0
        self.color_speed = color_speed

    def _generate_faces(self):
        faces, _ = super()._generate_faces()
        # 初期色を設定
        colors = [pyxel.COLOR_RED] * len(faces)
        return faces, colors

    def update(self):
        super().update()
        self.color_time += self.color_speed
        
        # 時間に基づいて色を変更
        base_colors = [
            pyxel.COLOR_RED,
            pyxel.COLOR_PINK,
            pyxel.COLOR_ORANGE,
            pyxel.COLOR_YELLOW,
            pyxel.COLOR_LIME,
            pyxel.COLOR_GREEN,
            pyxel.COLOR_CYAN,
            pyxel.COLOR_DARK_BLUE,
            pyxel.COLOR_LIGHT_BLUE,
            pyxel.COLOR_PURPLE,
        ]
        
        # 時間に基づいて色をサイクル
        for i in range(len(self.colors)):
            color_index = int((self.color_time + i * 0.1) % len(base_colors))
            self.colors[i] = base_colors[color_index]