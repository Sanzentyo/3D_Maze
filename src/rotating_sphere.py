import numpy as np
from sphere import Sphere

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
