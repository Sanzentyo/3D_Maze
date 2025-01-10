import numpy as np
import pyxel

from draw_object import DrawObject
from tri_sprite import TriSprite

class Plane(DrawObject):
    """
    平面オブジェクトを表すクラス。
    
    Members:
        plane_width (float): 平面の横幅。
        plane_height (float): 平面の縦幅。
        color (int): Pyxelのカラーパレット番号。
    Methods:
        __init__(): コンストラクタ。
        _generate_vertices(): 頂点の生成。
        _generate_faces(): 面の生成。
        get_tri_sprites(): 三角形スプライトの生成。
    """
    def __init__(self, center_position, width=200, height=200, color=pyxel.COLOR_GRAY):
        self.plane_width = width
        self.plane_height = height
        self.color = color
        super().__init__(center_position)

    def _generate_vertices(self):
        half_width = self.plane_width / 2
        half_height = self.plane_height / 2
        # 4つの頂点のみを生成
        vertices = [
            self.center + np.array([-half_width, 0, -half_height, 0]),  # 左上
            self.center + np.array([half_width, 0, -half_height, 0]),   # 右上
            self.center + np.array([-half_width, 0, half_height, 0]),   # 左下
            self.center + np.array([half_width, 0, half_height, 0]),    # 右下
        ]
        return vertices

    def _generate_faces(self):
        # 2つの三角形で四角形を表現
        faces = [
            [0, 2, 1],  # 左上の三角形
            [1, 2, 3],  # 右下の三角形
        ]
        colors = [self.color, self.color]
        return faces, colors

    def get_tri_sprites(self, view_projection_matrix, width, height) -> list[TriSprite]:
        transformed_vertices = []
        for vertex in self.vertices:
            pos = np.array(view_projection_matrix @ vertex).flatten()
            if len(pos) == 4:
                transformed_vertices.append(pos)
            else:
                transformed_vertices.append(np.array([0, 0, 0, np.nan]))

        tri_sprites:list[TriSprite] = []
        for i in range(len(self.faces)):
            face = self.faces[i]
            p1_4d = transformed_vertices[face[0]]
            p2_4d = transformed_vertices[face[1]]
            p3_4d = transformed_vertices[face[2]]
            
            tri = TriSprite(
                (p1_4d[0], p1_4d[1], p1_4d[2], p1_4d[3]),
                (p2_4d[0], p2_4d[1], p2_4d[2], p2_4d[3]),
                (p3_4d[0], p3_4d[1], p3_4d[2], p3_4d[3]),
                self.color
            )
            clipped = tri.clip_triangle(width, height)
            tri_sprites.extend(clipped)

        return tri_sprites