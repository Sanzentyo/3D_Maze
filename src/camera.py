"""
3Dシーンのビュー行列や投影行列の計算を行うクラスを定義します。

Classes:
    Camera:
        視点位置や移動・回転、投影行列管理を行うクラス。
        Members:
            position (np.ndarray): カメラ位置 (x, y, z) を保持。
            yaw (float): 水平回転角度[rad]。
            pitch (float): 垂直回転角度[rad]。
            aspect (float): 画面のアスペクト比。
            fov (float): 垂直画角 (度)。
            z_near (float): 近クリップ面の距離。
            z_far (float): 遠クリップ面の距離。
            mouse_sensivity (float): マウス感度。
            view_based_movement (bool): 移動操作を視点ベースで行うかどうか。
            map (Map|None): 当カメラに関連づけられたゲーム空間マップ。
        Methods:
            __init__(): カメラの初期化。
            init_mouse_pos(): マウス座標の初期化。
            process_mouse_movement(): マウス移動による視点回転処理。
            move_and_is_coin_collected(): キーボード入力による移動処理。
            toggle_movement_mode(): 移動モードの切り替え。
            get_translation_matrix(): 平行移動行列の取得。
            get_rotation_matrix(): 回転行列の取得。
            get_view_matrix(): ビュー行列の取得。
            get_view_matrix_inline(): ビュー行列の取得 (インライン版)。
            get_projection_matrix(): 投影行列の取得。
"""

import numpy as np
from global_state import GlobalState
from map import Map  # Mapクラスをインポート

class Camera:
    def __init__(self, position: np.ndarray, yaw: float, pitch: float, aspect: float, fov: float, z_near: float, z_far: float, mouse_sensivity: float = 0.01, prev_mouse_pos: tuple[int, int] = None, view_based_movement: bool = True, map_instance: Map = None):
        self.position = position
        self.yaw = yaw
        self.pitch = pitch
        self.aspect = aspect
        self.fov = fov
        self.z_near = z_near
        self.z_far = z_far
        self.mouse_sensivity = mouse_sensivity
        self.prev_mouse_pos = prev_mouse_pos
        self.view_based_movement = view_based_movement  # 移動モードフラグを初期化
        self.is_shifting = False
        self.map = map_instance  # Mapインスタンスを保持
        
    def init_mouse_pos(self, pos: tuple[int, int]):
        self.prev_mouse_pos = pos

    def process_mouse_movement(self, pos: tuple[int, int]):
        if self.prev_mouse_pos is None:
            self.prev_mouse_pos = pos
            return

        dx = pos[0] - self.prev_mouse_pos[0]
        dy = pos[1] - self.prev_mouse_pos[1]

        self.yaw += dx * self.mouse_sensivity
        self.pitch += dy * self.mouse_sensivity

        if self.pitch > np.pi / 2:
            self.pitch = np.pi / 2
        if self.pitch < -np.pi / 2:
            self.pitch = -np.pi / 2

        self.yaw = self.yaw % (2 * np.pi)
        
        self.prev_mouse_pos = pos

    def move_and_is_coin_collected(self, keyboard_state, global_state:GlobalState=None) -> bool:
        up = 0
        forward = 0
        right = 0
        
        if keyboard_state['forward']:
            forward += 1
        if keyboard_state['backward']:
            forward -= 1
        if keyboard_state['left']:
            right -= 1
        if keyboard_state['right']:
            right += 1
            
        if global_state and not global_state.is_master_view:
            # マスタービューでない場合、上下移動を無効化
            pass
        else:
            if keyboard_state['up']:
                up += 1
            if keyboard_state['down']:
                up -= 1

        forward *= 8
        right *= 8
        up *= 8

        if (global_state and not global_state.is_master_view) or self.view_based_movement:
            # 視点ベースの移動
            (cos_yaw, sin_yaw) = (np.cos(self.yaw), np.sin(self.yaw))
            (cos_pitch, sin_pitch) = (np.cos(self.pitch), np.sin(self.pitch))

            forward_vec = np.array([
                cos_yaw * cos_pitch,
                sin_pitch,
                sin_yaw * cos_pitch
            ])
            right_vec = np.array([
                -sin_yaw,
                0,
                cos_yaw
            ])
            up_vec = np.cross(right_vec, forward_vec)
            up_vec = up_vec / np.linalg.norm(up_vec)
        else:
            # yaw回転のみを考慮した移動
            (cos_yaw, sin_yaw) = (np.cos(self.yaw), np.sin(self.yaw))
            forward_vec = np.array([
                cos_yaw,
                0,
                sin_yaw
            ])
            right_vec = np.array([
                -sin_yaw,
                0,
                cos_yaw
            ])
            up_vec = np.array([0, 1, 0])

        is_coin_collected = False

        if self.map and not global_state.is_master_view:
            # 現在の位置を保存
            current_pos = self.position.copy()
            
            # X方向とZ方向の移動を分離して試行
            # まずX方向
            tentative_x = current_pos[0] + (forward_vec[0] * forward + right_vec[0] * right)
            if self.map.set_camera_position_and_check_coin_collection(tentative_x, current_pos[2]):
                is_coin_collected = True
            
            # 次にZ方向
            tentative_z = current_pos[2] + (forward_vec[2] * forward + right_vec[2] * right)
            if self.map.set_camera_position_and_check_coin_collection(self.map.camera_position[0], tentative_z):
                is_coin_collected = True
            
            # 最終的な位置を取得
            new_pos = self.map.get_camera_position()
            self.position[0] = new_pos[0]
            self.position[2] = new_pos[2]
            
            # Y座標は固定（マスタービューでない場合）
            if not global_state.is_master_view:
                self.position[1] = current_pos[1]
        else:
            # マスタービューモードの場合は制限なし
            self.position += forward_vec * forward + right_vec * right + up_vec * up

        self.position = self.position.astype(float)

        return is_coin_collected

    def toggle_movement_mode(self):
        """移動モードを切り替える"""
        self.view_based_movement = not self.view_based_movement

    def get_translation_matrix(self) -> np.matrix:
        return np.matrix([
            [1, 0, 0, -self.position[0]],
            [0, 1, 0, -self.position[1]],
            [0, 0, 1, -self.position[2]],
            [0, 0, 0, 1]
        ])
    
    def get_rotation_matrix(self) -> np.matrix:
        cos_yaw, sin_yaw = np.cos(self.yaw), np.sin(self.yaw)
        cos_pitch, sin_pitch = np.cos(self.pitch), np.sin(self.pitch)

        # 前方向ベクトル（視線ベクトル）
        f = np.array([
            cos_yaw * cos_pitch,
            sin_pitch,
            sin_yaw * cos_pitch
        ])
        f /= np.linalg.norm(f)

        # 上方向ベクトル
        up = np.array([0, 1, 0])

        # 右方向ベクトル
        s = np.cross(f, up)
        s /= np.linalg.norm(s)

        # 真の上方向ベクトル
        u = np.cross(s, f)
        
        return np.matrix([
            [s[0], s[1], s[2], 0],
            [u[0], u[1], u[2], 0],
            [-f[0], -f[1], -f[2], 0],
            [0, 0, 0, 1]
        ])
    
    def get_view_matrix(self) -> np.matrix:
        return self.get_rotation_matrix() @ self.get_translation_matrix()
    
    def get_view_matrix_inline(self) -> np.matrix:
        cos_yaw, sin_yaw = np.cos(self.yaw), np.sin(self.yaw)
        cos_pitch, sin_pitch = np.cos(self.pitch), np.sin(self.pitch)

        # 前方向ベクトル（視線ベクトル）
        f = np.array([
            cos_yaw * cos_pitch,
            sin_pitch,
            sin_yaw * cos_pitch
        ])
        f /= np.linalg.norm(f)

        # 上方向ベクトル
        up = np.array([0, 1, 0])

        # 右方向ベクトル
        s = np.cross(f, up)
        s /= np.linalg.norm(s)

        # 真の上方向ベクトル
        u = np.cross(s, f)

        # ビュー行列の構築
        return np.matrix([
            [s[0], s[1], s[2], -np.dot(s, self.position)],
            [u[0], u[1], u[2], -np.dot(u, self.position)],
            [-f[0], -f[1], -f[2], np.dot(f, self.position)],
            [0, 0, 0, 1]
        ])
    
    def get_projection_matrix(self) -> np.matrix:
        (sin_fov, cos_fov) = (np.sin(np.radians(self.fov) / 2), np.cos(np.radians(self.fov) / 2))
        h = cos_fov / sin_fov
        w = h / self.aspect
        r = self.z_far / (self.z_near - self.z_far)

        return np.matrix([
            [w, 0, 0, 0],
            [0, h, 0, 0],
            [0, 0, r, r * self.z_near],
            [0, 0, -1.0, 0]
        ]).T