"""
3Dオブジェクトの抽象基底クラスを定義します。

Classes:
    DrawObject(ABC):
        3Dオブジェクト基底クラス。
        Members:
            center (np.ndarray): ワールド座標系での中心位置 [x, y, z, 1]。
            vertices (list[np.ndarray]): オブジェクトの頂点リスト。
            faces (list[list[int]]): 頂点インデックスによる面の集合。
            colors (list[int]): 面ごとの描画色。
        Methods:
            __init__(): コンストラクタ。
            _generate_vertices(): 頂点生成の抽象メソッド。
            _generate_faces(): 面と色の生成の抽象メソッド。
            get_tri_sprites(): 三角形スプライトのリストを取得。
"""

import numpy as np
from abc import ABC, abstractmethod
from tri_sprite import TriSprite

class DrawObject(ABC):
    def __init__(self, center_position):
        self.center = np.array([*center_position, 1])
        self.vertices = self._generate_vertices()
        self.faces, self.colors = self._generate_faces()

    @abstractmethod
    def _generate_vertices(self):
        pass

    @abstractmethod
    def _generate_faces(self):
        pass

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
