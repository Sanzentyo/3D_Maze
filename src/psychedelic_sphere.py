import pyxel
from rotating_sphere import RotatingSphere

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
