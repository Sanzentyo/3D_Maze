from cube import Cube
import numpy as np

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