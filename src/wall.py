from draw_object import DrawObject
from tri_sprite import TriSprite
import numpy as np
import pyxel

class Wall(DrawObject):
    """
    3D迷路の壁を表現するクラス。
    Members:
        positions (list[list[float]]): 壁の位置座標のリスト。
        size (float): 壁の一辺の長さ。
        half_size (float): サイズの半分（計算用）。
    Methods:
        __init__(): コンストラクタ。壁のパラメータ設定。
        _generate_vertices(): 頂点の生成。隣接する壁の判定も行う。
        _generate_faces(): 面と色の生成。
        _is_adjacent(): 他の壁との隣接判定。
    """
    def __init__(self, positions: list[list[float]], size: float):
        self.positions = positions
        self.size = size
        self.half_size = size / 2
        super().__init__(positions[0])  # 最初の位置を中心として初期化

    def _generate_vertices(self):
        vertices = []
        for pos in self.positions:
            # 各位置に対して8つの頂点を生成
            for z in [-1, 1]:
                for y in [-1, 1]:
                    for x in [-1, 1]:
                        vertex = np.array([
                            pos[0] + x * self.half_size,
                            pos[1] + y * self.half_size,
                            pos[2] + z * self.half_size,
                            1
                        ])
                        vertices.append(vertex)
        return vertices

    def _generate_faces(self):
        faces = []
        colors = []
        cubes_count = len(self.positions)
        
        for i in range(cubes_count):
            base_idx = i * 8  # 各Cubeは8頂点を持つ
            
            # 各面の定義（bottom面を除外）
            cube_faces = {
                'front':  [[base_idx + 0, base_idx + 1, base_idx + 2],
                          [base_idx + 3, base_idx + 2, base_idx + 1]],
                'back':   [[base_idx + 4, base_idx + 6, base_idx + 5],
                          [base_idx + 7, base_idx + 5, base_idx + 6]],
                'top':    [[base_idx + 0, base_idx + 4, base_idx + 1],
                          [base_idx + 5, base_idx + 1, base_idx + 4]],
                'right':  [[base_idx + 1, base_idx + 5, base_idx + 3],
                          [base_idx + 3, base_idx + 5, base_idx + 7]],
                'left':   [[base_idx + 0, base_idx + 2, base_idx + 4],
                          [base_idx + 2, base_idx + 6, base_idx + 4]]
            }
            
            # 各面の色（bottom面を除外）
            face_colors = {
                'front':  [pyxel.COLOR_RED] * 2,
                'back':   [pyxel.COLOR_GREEN] * 2,
                'top':    [pyxel.COLOR_DARK_BLUE] * 2,
                'right':  [pyxel.COLOR_CYAN] * 2,
                'left':   [pyxel.COLOR_YELLOW] * 2
            }

            # 隣接する面のチェック
            for j in range(cubes_count):
                if i != j:
                    if self._is_adjacent(self.positions[i], self.positions[j]):
                        if self.positions[i][0] == self.positions[j][0]:
                            # Z軸方向で隣接
                            if self.positions[i][2] < self.positions[j][2]:
                                cube_faces['back'] = []
                            else:
                                cube_faces['front'] = []
                        elif self.positions[i][2] == self.positions[j][2]:
                            # X軸方向で隣接
                            if self.positions[i][0] < self.positions[j][0]:
                                cube_faces['right'] = []
                            else:
                                cube_faces['left'] = []

            # 残った面を追加
            for face_type in cube_faces:
                faces.extend(cube_faces[face_type])
                colors.extend(face_colors[face_type][:len(cube_faces[face_type])])

        return faces, colors

    def _is_adjacent(self, pos1, pos2):
        return (abs(pos1[0] - pos2[0]) == self.size and pos1[2] == pos2[2]) or \
               (abs(pos1[2] - pos2[2]) == self.size and pos1[0] == pos2[0])

class HighlightedWall(Wall):
    """
    フォーカス時にハイライト表示される壁クラス。壁の面を表示せず、エッジをパープル色で描画。
    
    Members:
        edge_width (float): エッジの太さ。
    
    Methods:
        __init__(): コンストラクタ。エッジ付き壁の初期化。
        get_tri_sprites(): エッジ描画用の三角形スプライト生成。
    """
    def __init__(self, position, tile_size):
        super().__init__([position], tile_size)
        self.position = position
        self.edge_width = 3  # エッジの太さを設定

    def _generate_faces(self):
        # 面は表示しないので空を返す
        return [], []

    def get_tri_sprites(self, view_projection_matrix, screen_width, screen_height):
        vertices = self._generate_vertices()
        
        # エッジを定義（12本の辺）
        edges = [
            (0,1), (1,3), (3,2), (2,0),  # 上面
            (4,5), (5,7), (7,6), (6,4),  # 底面
            (0,4), (1,5), (2,6), (3,7)   # 垂直エッジ
        ]
        
        sprites = []
        for start_idx, end_idx in edges:
            # 頂点を射影変換
            v1 = np.asarray(view_projection_matrix @ vertices[start_idx]).flatten()
            v2 = np.asarray(view_projection_matrix @ vertices[end_idx]).flatten()
            
            """
            # w除算
            if v1[3] > 0:
                v1 = v1 / v1[3]
            else:
                continue
            if v2[3] > 0:
                v2 = v2 / v2[3]
            else:
                continue
            """
            
            # エッジをTriSpriteとして描画
            # 線分を細長い三角形として表現
            dx = v2[0] - v1[0]
            dy = v2[1] - v1[1]
            length = np.sqrt(dx*dx + dy*dy)
            if length > 0:
                nx = -dy * self.edge_width / length  # 法線ベクトル
                ny = dx * self.edge_width / length
                
                # 線分の両側に頂点を配置して三角形を作る
                p1 = (v1[0] - nx/2, v1[1] - ny/2, v1[2], v1[3])
                p2 = (v1[0] + nx/2, v1[1] + ny/2, v1[2], v1[3])
                p3 = (v2[0] - nx/2, v2[1] - ny/2, v2[2], v2[3])
                p4 = (v2[0] + nx/2, v2[1] + ny/2, v2[2], v2[3])
                
                # 2つの三角形で1本の線を表現
                sprites.extend(TriSprite(p1, p2, p3, pyxel.COLOR_PURPLE).clip_triangle(screen_width, screen_height))
                sprites.extend(TriSprite(p2, p4, p3, pyxel.COLOR_PURPLE).clip_triangle(screen_width, screen_height))

        return sprites