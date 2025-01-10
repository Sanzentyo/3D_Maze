"""
エッジ付きの平面を表現するクラスを定義するファイルです。

Classes:
    EdgePlane:
        縁取り付きの平面を表現するクラス。Planeクラスの拡張。
        Members:
            edge_width (float): エッジの幅。
            center_color (int): 中央部分の色。
            edge_color (int): エッジ部分の色。
        Methods:
            __init__(): コンストラクタ。
            _generate_vertices(): エッジ付き平面の頂点生成。
            _generate_faces(): 中央部とエッジ部の面生成。
            get_tri_sprites(): 描画用の三角形スプライト生成。
"""

import numpy as np
import pyxel
from plane import Plane
from tri_sprite import TriSprite

class EdgePlane(Plane):
    def __init__(self, center_position, width=200, height=200, 
                 center_color=pyxel.COLOR_GRAY, edge_color=pyxel.COLOR_RED,
                 edge_width=10):
        self.edge_width = edge_width
        self.center_color = center_color
        self.edge_color = edge_color
        super().__init__(center_position, width, height, center_color)

    def _generate_vertices(self):
        half_width = self.plane_width / 2
        half_height = self.plane_height / 2
        edge = self.edge_width

        # 外側の頂点
        vertices = [
            self.center + np.array([-half_width, 0, -half_height, 0]),  # 0: 左上外
            self.center + np.array([half_width, 0, -half_height, 0]),   # 1: 右上外
            self.center + np.array([half_width, 0, half_height, 0]),    # 2: 右下外
            self.center + np.array([-half_width, 0, half_height, 0]),   # 3: 左下外
            # 内側の頂点
            self.center + np.array([-half_width + edge, 0, -half_height + edge, 0]),  # 4: 左上内
            self.center + np.array([half_width - edge, 0, -half_height + edge, 0]),   # 5: 右上内
            self.center + np.array([half_width - edge, 0, half_height - edge, 0]),    # 6: 右下内
            self.center + np.array([-half_width + edge, 0, half_height - edge, 0]),   # 7: 左下内
        ]
        return vertices

    def _generate_faces(self):
        # 中央の四角形（2つの三角形）を中央の色で描画
        center_faces = [
            [4, 7, 5],  # 中央左上三角形
            [5, 7, 6],  # 中央右下三角形
        ]
        
        # エッジ部分の三角形をエッジの色で描画
        edge_faces = [
            [0, 4, 1], [1, 4, 5],  # 上エッジ
            [1, 5, 2], [2, 5, 6],  # 右エッジ
            [2, 6, 3], [3, 6, 7],  # 下エッジ
            [3, 7, 0], [0, 7, 4],  # 左エッジ
        ]

        # 面と色の配列を作成
        faces = center_faces + edge_faces
        colors = [self.center_color] * len(center_faces) + [self.edge_color] * len(edge_faces)
        
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
            color = self.colors[i]  # 各面に対応する色を使用
            p1_4d = transformed_vertices[face[0]]
            p2_4d = transformed_vertices[face[1]]
            p3_4d = transformed_vertices[face[2]]
            
            tri = TriSprite(
                (p1_4d[0], p1_4d[1], p1_4d[2], p1_4d[3]),
                (p2_4d[0], p2_4d[1], p2_4d[2], p2_4d[3]),
                (p3_4d[0], p3_4d[1], p3_4d[2], p3_4d[3]),
                color  # ここで各面の色を適用
            )
            clipped = tri.clip_triangle(width, height)
            tri_sprites.extend(clipped)

        return tri_sprites
