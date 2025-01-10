"""
3D空間内の球体を表現するクラスを定義するファイルです。

Classes:
    Sphere:
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

import numpy as np
import pyxel

from draw_object import DrawObject
from tri_sprite import TriSprite

class Sphere(DrawObject):
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
