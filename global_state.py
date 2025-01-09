import pyxel

class GlobalState:
    def __init__(self):
        self.is_view_wireframe = False # CTRL + Wで切り替え
        self.is_master_view = False # CTRL + Mで切り替え
        self.is_view_based_movement = True # マスタービュー時のみ M で切り替え
        self.keyboard_state = {}
        
    def update(self):
        # ワイヤーフレーム表示切り替え
        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_W):
            self.toggle_wireframe()

        if self.is_master_view and pyxel.btn(pyxel.KEY_M):
            self.toggle_view_based_movement()
            
        # マスタービュー切り替え
        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_M):
            self.toggle_master_view()

        # キーボード状態の更新
        self.keyboard_state = {
            'forward': pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP),
            'backward': pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN),
            'left': pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT),
            'right': pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT),
            'up': pyxel.btn(pyxel.KEY_SHIFT),# and self.is_master_view,   # マスタービュー時のみ有効
            'down': pyxel.btn(pyxel.KEY_SPACE),# and self.is_master_view, # マスタービュー時のみ有効
            'ctrl': pyxel.btn(pyxel.KEY_CTRL),
            'mouse_left': pyxel.btn(pyxel.MOUSE_BUTTON_LEFT),
            'focus': pyxel.btn(pyxel.KEY_F)
        }
        
    def toggle_wireframe(self):
        self.is_view_wireframe = not self.is_view_wireframe
        
    def toggle_master_view(self):
        self.is_master_view = not self.is_master_view

    def toggle_view_based_movement(self):
        self.is_view_based_movement = not self.is_view_based_movement