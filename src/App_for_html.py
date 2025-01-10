"""
アプリケーションのメインクラスを定義するファイルです。

Classes:
    App:
        アプリケーション全体の管理を行うクラス。
        Members:
            width (int): 画面の幅。
            height (int): 画面の高さ。
            global_state (GlobalState): グローバル状態管理。
            scene: 現在のシーン。
        Methods:
            __init__(): コンストラクタ。
            update(): ゲームの状態更新。
            draw(): 画面の描画。
"""

import pyxel
from scene_for_html import StartScene, init_sound
from global_state import GlobalState

class App:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.global_state = GlobalState()
        self.is_view_wireframe = False
        pyxel.init(width, height)
        init_sound()
        self.scene = StartScene(self.global_state)
        pyxel.run(self.update, self.draw)

    def update(self):
        next_scene = self.scene.update()
        if next_scene is None:
            pyxel.quit()
        self.scene = next_scene

    def draw(self):
        self.scene.draw()

App(720, 720)