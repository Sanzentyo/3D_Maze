from abc import ABC, abstractmethod
import pyxel
import numpy as np
from camera import Camera
from map import Map
from sphere import RotatingSphere, PsychedelicSphere
from cube import RotatingCube
from typing import List
from tri_sprite import TriSprite
from global_state import GlobalState
from draw_object import DrawObject
import time

def init_sound():
    # ★ 効果音をセットする行を追加
    pyxel.sounds[30].set("b3", "N", "7", "N", 10)   # bird toggle
    pyxel.sounds[31].set("f3", "T", "7", "F", 8)   # coin
    pyxel.sounds[32].set("a1", "N", "7", "N", 10)   # wall destroy
    pyxel.sounds[33].set("c3", "N", "7", "N", 10)   # start

class Scene(ABC):
    """
    シーンの抽象基底クラス

    Members:
        なし (抽象クラスのため)

    Methods:
        update(): シーンごとの状態更新を行う。
        draw(): シーンごとの描画処理を行う。
        get_tri_sprites(): 3Dオブジェクトから三角形スプライトを取得。
        draw_tri_sprites(): 三角形スプライトを描画する。
        render_3d_scene(): カメラ視点で3Dシーンをレンダリングする。
    """
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def get_tri_sprites(self, objects: List[DrawObject], view_projection_matrix: np.ndarray) -> List[TriSprite]:
        """3Dオブジェクトからtri_spriteのリストを取得"""
        sprites = []
        for obj in objects:
            sprites.extend(obj.get_tri_sprites(view_projection_matrix, pyxel.width, pyxel.height))
        return sprites

    def draw_tri_sprites(self, sprites: List[TriSprite], is_view_wireframe=False, is_back_culling=True):
        """tri_spriteのリストを描画"""
        for tri_sprite in sprites:
            if not is_back_culling or tri_sprite.is_frontface():
                clipped = tri_sprite.clip_triangle(pyxel.width, pyxel.height)
                for c in clipped:
                    # スクリーン座標系への変換
                    c.p1 = (c.p1[0] + pyxel.width / 2, c.p1[1] + pyxel.height / 2, c.p1[2], c.p1[3])
                    c.p2 = (c.p2[0] + pyxel.width / 2, c.p2[1] + pyxel.height / 2, c.p2[2], c.p2[3])
                    c.p3 = (c.p3[0] + pyxel.width / 2, c.p3[1] + pyxel.height / 2, c.p3[2], c.p3[3])
                    c.draw()
                    if is_view_wireframe:
                        c.draw_wireframe(color=pyxel.COLOR_BLACK)


    def render_3d_scene(self, camera: Camera, object_groups: List[List[DrawObject]], is_view_wireframe=False, is_back_culling=True):
        """3Dシーンのレンダリング
        object_groups: 描画優先度順のオブジェクトグループのリスト"""
        view_matrix = camera.get_view_matrix()
        projection_matrix = camera.get_projection_matrix()
        view_projection_matrix = projection_matrix @ view_matrix

        all_sprites = []
        
        # 各グループのスプライトを取得してソート
        for group in object_groups:
            sprites = self.get_tri_sprites(group, view_projection_matrix)
            sprites.sort(key=lambda x: -x.get_depth())
            all_sprites.extend(sprites)

        # 描画
        self.draw_tri_sprites(all_sprites, is_view_wireframe=is_view_wireframe, is_back_culling=is_back_culling)

class StartScene(Scene):
    """
    ゲーム開始シーン（軽量版）

    Members:
        center (tuple[int,int]): タイトル表示の中心座標。
        psychedelic_sphere (PsychedelicSphere): タイトル画面の装飾球体。
        title_camera (Camera): タイトル画面用カメラ。
        global_state (GlobalState): 入力状態を持つ。
        tile_size (int): 背景タイルサイズ。

    Methods:
        __init__(): シンプルなコンストラクタ（BGM等は使用しない）。
        update(): 入力を確認してシーン遷移を行う。
        draw(): キャラクターや背景を描画する。
    """
    def __init__(self, global_state:GlobalState):
        #self.writer: puf.Writer = puf.Writer("misaki_gothic.ttf")
        self.center = (pyxel.width//2, pyxel.height//4)
        self.psychedelic_sphere = PsychedelicSphere(np.array([pyxel.width//2, pyxel.height//2-360, 0]), 300, 18)
        self.title_camera = Camera(
            position=np.array([0, 0, 0]),
            yaw=0,
            pitch=0,
            aspect=pyxel.width/pyxel.height,
            fov=90,
            z_near=0.005,
            z_far=1000,
            view_based_movement=False
        )
        self.global_state = global_state

        self.tile_size = 80
        

    def update(self):
        self.global_state.update()

        if pyxel.btnp(pyxel.KEY_SPACE):
            # 効果音を再生
            pyxel.play(3, 33)

            return GameScene(self.global_state)
        return self

    def draw(self):
        offset_x = (pyxel.frame_count / 2) % self.tile_size
        offset_y = (pyxel.frame_count / 2) % self.tile_size
        for x in range(-self.tile_size, pyxel.width, self.tile_size):
            for y in range(-self.tile_size, pyxel.height, self.tile_size):
                pyxel.rect(x + offset_x, y + offset_y, self.tile_size, self.tile_size, pyxel.COLOR_NAVY if (x//self.tile_size + y//self.tile_size) % 2 == 0 else pyxel.COLOR_GRAY)

        
        self.psychedelic_sphere.update()
        self.render_3d_scene(
            self.title_camera,
            [[self.psychedelic_sphere]],
            is_view_wireframe=self.global_state.is_view_wireframe
        )

class GameScene(Scene):
    """メインプレイシーン（軽量版）

    Members:
        map (Map): 迷路マップデータ。
        camera (Camera): プレイヤーの視点。
        planes (list[Plane]): 床面となるPlaneのリスト。
        walls (list[DrawObject]): 壁オブジェクトのリスト。
        spheres (list[RotatingSphere]): 回転球体のリスト。
        is_bird_view (bool): 鳥瞰モードかどうか。
        highlighted_wall (DrawObject|None): ハイライトされている壁。
        coin_count (int): コインの初期総数。
        is_goal_reached (bool): ゴール済みかどうか。

    Methods:
        __init__(): 迷路やカメラなどを初期化する（BGM処理なし）。
        update(): 入力や壁破壊などの状態更新を行う。
        draw(): 3DオブジェクトとUI要素を描画する。
        _highlight_wall_in_front(): 正面にある壁をハイライトする。
        _destroy_highlighted_wall(): ハイライト中の壁を破壊する。
    """
    def __init__(self, global_state):
        # マップを生成
        self.map = Map.generate_maze_map(15, 15, [0, 0, 0], 100, coin_count=3)
        
        # カメラの初期位置を取得（スタート位置）
        start_pos = self.map.get_start_position()
        initial_yaw, initial_pitch = self.map.get_initial_view_direction()
        
        self.camera = Camera(
            position=np.array(start_pos),
            yaw=initial_yaw,
            pitch=initial_pitch,
            aspect=pyxel.width/pyxel.height,
            fov=90,
            z_near=0.005,
            z_far=1000,
            view_based_movement=False,
            map_instance=self.map
        )
        
        self.camera.init_mouse_pos((pyxel.mouse_x, pyxel.mouse_y))
        
        # 描画オブジェクトを設定
        self.planes = self.map.get_floor_objects()
        self.walls = self.map.get_wall_objects()   
        self.spheres = [RotatingSphere(pos, radius=30, segments=8) 
                       for pos in self.map.sphere_positions]
        
        self.start_time = time.time()
        self.elapsed_time = 0
        self.global_state: GlobalState = global_state

        self.is_transitioning = False
        self.transition_start_time = 0
        self.transition_duration = 30  # 30フレームで遷移する
        self.is_bird_view = False
        
        # 視点遷移用の状態を保存
        self.original_position = None
        self.original_yaw = None
        self.original_pitch = None
        self.target_position = None
        self.target_yaw = None
        self.target_pitch = None
        
        # プレイヤー位置表示用のキューブを修正
        self.player_cube:RotatingCube = RotatingCube(
            position=np.array([0, -25, 0]),  # Y座標を-25に変更（床の高さに合わせる）
            size=30,  # サイズを30に縮小
            color=pyxel.COLOR_ORANGE
        )
        self.show_player_cube = False

        self.normal_fov = 90
        self.bird_fov = 50

        self.coin_count = len([pos for row in self.map.map_data for pos in row if pos == '.'])

        self.highlighted_wall = None
        #self.writer = puf.Writer("misaki_gothic.ttf")  # フォントファイル名は適宜調整してください
        self.path_points = []
        self.last_recorded_time = time.time()  # フレームカウントから時間に変更
        self.path_record_interval = 0.2  # 記録間隔を1秒に設定
        self.is_goal_reached = False

    def update(self):
        self.global_state.update()
        
        if pyxel.btnp(pyxel.KEY_Q):
            return None
        
        self.camera.view_based_movement = self.global_state.is_view_based_movement

        if not self.global_state.is_master_view and pyxel.btnp(pyxel.KEY_B):
            if not self.is_transitioning:
                pyxel.play(3, 30)  # 切り替え時の効果音再生
                self.is_transitioning = True
                self.transition_start_time = pyxel.frame_count
                
                if not self.is_bird_view:
                    # 通常視点から鳥瞰視点への遷移開始
                    self.original_position = self.camera.position.copy()
                    self.original_yaw = self.camera.yaw
                    self.original_pitch = self.camera.pitch
                    
                    bird_pos, (bird_yaw, bird_pitch) = self.map.get_bird_view()
                    self.target_position = np.array(bird_pos)
                    self.target_yaw = bird_yaw
                    self.target_pitch = bird_pitch
                    
                    # プレイヤーの位置にキューブを表示（Y座標を調整）
                    self.player_cube.position = self.original_position.copy()
                    self.show_player_cube = True
                else:
                    # 鳥瞰視点から通常視点への遷移開始
                    self.target_position = self.original_position
                    self.target_yaw = self.original_yaw
                    self.target_pitch = self.original_pitch
                    
                    bird_pos, (bird_yaw, bird_pitch) = self.map.get_bird_view()
                    self.original_position = np.array(bird_pos)
                    self.original_yaw = bird_yaw
                    self.original_pitch = bird_pitch
        
        if self.is_transitioning:
            # 遷移アニメーション中の処理
            progress = min(1.0, (pyxel.frame_count - self.transition_start_time) / self.transition_duration)
            
            # 線形補間で位置と視点を更新
            self.camera.position = self.original_position + (self.target_position - self.original_position) * progress
            self.camera.yaw = self.original_yaw + (self.target_yaw - self.original_yaw) * progress
            self.camera.pitch = self.original_pitch + (self.target_pitch - self.original_pitch) * progress
            
            # FOVの補間を追加
            if not self.is_bird_view:
                # 通常視点から鳥瞰視点への遷移
                self.camera.fov = self.normal_fov + (self.bird_fov - self.normal_fov) * progress
            else:
                # 鳥瞰視点から通常視点への遷移
                self.camera.fov = self.bird_fov + (self.normal_fov - self.bird_fov) * progress
            
            if progress >= 1.0:
                self.is_transitioning = False
                self.is_bird_view = not self.is_bird_view
                if not self.is_bird_view:
                    self.show_player_cube = False
        
        if not self.is_transitioning:
            # 通常の更新処理
            if not self.is_bird_view:
                self.camera.process_mouse_movement((pyxel.mouse_x, pyxel.mouse_y))
                if self.camera.move_and_is_coin_collected(self.global_state.keyboard_state, self.global_state):
                    pyxel.play(3, 31)  # coin 効果音再生
                    # コイン取得後に球体オブジェクトを更新
                    self.spheres = [RotatingSphere(pos, radius=30, segments=8) 
                                for pos in self.map.sphere_positions]
                
        # キューブの回転アニメーション
        if self.show_player_cube:
            self.player_cube.update()
            
        # 球体の回転アニメーション
        for sphere in self.spheres:
            sphere.update()
            
        # ハイライトかつ壁破壊の処理を追加
        if not self.is_transitioning:
            if self.global_state.keyboard_state['focus'] and self.coin_count - self.map.get_remaining_coins() > 0:
                # コインを1枚以上所持している場合のみ Tキーでハイライト
                self._highlight_wall_in_front()
            else:
                # Tキーが押されなくなったらハイライトを削除
                self.highlighted_wall = None
                

            # ハイライト表示中に左クリックで壁破壊
            if self.highlighted_wall and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                pyxel.play(3, 32)  # ★ 効果音再生
                # 壁破壊処理
                self._destroy_highlighted_wall()

        # パス記録の判定を時間ベースに変更
        current_time = time.time()
        if hasattr(self, 'camera') and (current_time - self.last_recorded_time >= self.path_record_interval):
            if not self.is_bird_view and not self.is_transitioning:
                pos_4d = np.array([self.camera.position[0], 
                                50, 
                                self.camera.position[2], 
                                1.0])
            else:
                pos_4d = np.array([self.player_cube.position[0],
                                50,
                                self.player_cube.position[2],
                                1.0])

            self.path_points.append(pos_4d)
            self.last_recorded_time = current_time

        # ゴール到達判定
        if self.map.check_goal_reached(self.camera.position[0], self.camera.position[2]):

            # 先に鳥瞰視点へ移行
            if not self.is_bird_view:
                self.path_points.append(np.array([self.camera.position[0], 50, self.camera.position[2], 1.0]))

                # 鳥瞰視点に切り替えるための処理を挟む
                self.is_bird_view = True
                bird_pos, (bird_yaw, bird_pitch) = self.map.get_bird_view()
                self.camera.position = np.array(bird_pos)
                self.camera.yaw = bird_yaw
                self.camera.pitch = bird_pitch
                self.camera.fov = self.bird_fov

            self.is_goal_reached = True

            # ScoreSceneへ移行
            return ScoreScene(self, self.elapsed_time, self.global_state)

        self.elapsed_time = time.time() - self.start_time
        return self

    def _highlight_wall_in_front(self):
        """
        カメラの正面方向にあるタイルを判定し、
        もし壁(#)なら HighlightedWall をセットする例
        """
        camera_pos = self.camera.position
        tile_size = self.map.tile_size
        
        # カメラ前方1タイル分を確認
        forward_vec = np.array([
            np.cos(self.camera.yaw),
            0,
            np.sin(self.camera.yaw)
        ])
        check_pos = camera_pos + forward_vec * tile_size
        
        # タイル座標を取得
        offset = tile_size / 2
        mx = int((offset + check_pos[0] + len(self.map.map_data[0]) * tile_size / 2) / tile_size)
        mz = int((offset + check_pos[2] + len(self.map.map_data) * tile_size / 2) / tile_size)
        
        # 範囲内かどうか
        if 0 <= mx < len(self.map.map_data[0]) and 0 <= mz < len(self.map.map_data):
            # 端の壁はスキップ
            rows = len(self.map.map_data)
            cols = len(self.map.map_data[0])
            if mz in (0, rows - 1) or mx in (0, cols - 1):
                return

            # 隣接が ' ' または '.' の場所があるかチェック
            if (self.map.map_data[mz][mx] == '#' and
                ((self.map.map_data[mz][mx - 1] in [' ', '.']) or
                 (self.map.map_data[mz][mx + 1] in [' ', '.']) or
                 (self.map.map_data[mz - 1][mx] in [' ', '.']) or
                 (self.map.map_data[mz + 1][mx] in [' ', '.']))):
                # ワールド座標計算
                ox = -len(self.map.map_data[0]) * tile_size / 2
                oz = -len(self.map.map_data) * tile_size / 2
                wx = ox + mx * tile_size
                wz = oz + mz * tile_size
                from wall import HighlightedWall
                self.highlighted_wall = HighlightedWall([wx, self.map.origin_pos[1], wz], tile_size)

    def _destroy_highlighted_wall(self):
        """
        ハイライトしている壁の '#' タイルを ' ' に変更してマップ更新し、
        walls/floor など再取得後にコインを1枚減らす
        """
        tile_size = self.map.tile_size
        offset = tile_size / 2
        x, _, z = self.highlighted_wall.position
        mx = int((offset + x + len(self.map.map_data[0]) * tile_size / 2) / tile_size)
        mz = int((offset + z + len(self.map.map_data) * tile_size / 2) / tile_size)

        # 対象タイルを ' ' に置き換え
        row_list = list(self.map.map_data[mz])
        row_list[mx] = ' '
        self.map.map_data[mz] = ''.join(row_list)

        # 再処理
        self.map.floor_objects = []
        self.map.wall_positions = []
        self.map.sphere_positions = []
        self.map._process_map()

        # GameScene 側で再取得
        self.planes = self.map.get_floor_objects()
        self.walls = self.map.get_wall_objects()
        self.spheres = [RotatingSphere(pos, radius=30, segments=8) 
                        for pos in self.map.sphere_positions]

        # ハイライト解除 & コインを1枚減らす
        self.highlighted_wall = None
        self.coin_count -= 1

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # 3Dシーンの描画（床、壁+球体の順）
        if self.show_player_cube:
            draw_objects = [self.planes, self.walls + self.spheres + [self.player_cube]]
        else:
            draw_objects = [self.planes, self.walls + self.spheres]
            
        self.render_3d_scene(
            self.camera,
            draw_objects,
            is_view_wireframe=self.global_state.is_view_wireframe
        )

        # エッジ付きのハイライト壁があれば最後に描画
        if self.highlighted_wall:
            self.render_3d_scene(
                self.camera,
                [[self.highlighted_wall]],
                is_view_wireframe=self.global_state.is_view_wireframe,
                is_back_culling=False
            )

        # UIの描画
        if not self.is_goal_reached:
            # モードの表示
            #if (self.is_bird_view or self.is_transitioning) and not self.global_state.is_master_view:
                #self.writer.draw(10, pyxel.height - 30, "Bird View", 20, pyxel.COLOR_WHITE)
            #elif self.global_state.is_master_view:
            #    view_mode = "View Based" if self.camera.view_based_movement else "Yaw Based"
                #self.writer.draw(10, pyxel.height - 30, f"{view_mode} Movement", 20, pyxel.COLOR_WHITE)

            # コイン数を表示
            remaining = self.map.get_remaining_coins()
            collected = self.coin_count - remaining
            #self.writer.draw(10, 10, f"Coins: {collected}/{self.coin_count}", 45, pyxel.COLOR_WHITE)

            # 時間表示（ミリ秒まで含める）
            minutes = int(self.elapsed_time // 60)
            seconds = int(self.elapsed_time % 60)
            milliseconds = int((self.elapsed_time % 1) * 1000)
            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            #self.writer.draw(pyxel.width - 190, 10, time_str, 40, pyxel.COLOR_WHITE)

            if not self.is_bird_view:
                # 十字のスコープを表示
                pyxel.rect(pyxel.width // 2 - 10, pyxel.height // 2 - 1, 20, 3, pyxel.COLOR_WHITE)
                pyxel.rect(pyxel.width // 2 - 1, pyxel.height // 2 - 10, 3, 20, pyxel.COLOR_WHITE)

    def draw_path(self):
        vp_matrix = self.camera.get_projection_matrix() @ self.camera.get_view_matrix()
        for i in range(len(self.path_points)):
            current = np.array(vp_matrix @ self.path_points[i]).flatten()  # flatten()を追加
            if current[3] > 0:
                x1 = current[0] / current[3] + pyxel.width / 2
                y1 = current[1] / current[3] + pyxel.height / 2
                pyxel.circ(int(x1), int(y1), 5, pyxel.COLOR_ORANGE)
                if i > 0:
                    prev = np.array(vp_matrix @ self.path_points[i - 1]).flatten()  # flatten()を追加
                    if prev[3] > 0:
                        x0 = prev[0] / prev[3] + pyxel.width / 2
                        y0 = prev[1] / prev[3] + pyxel.height / 2
                    pyxel.line(int(x0), int(y0), int(x1), int(y1), pyxel.COLOR_ORANGE)

class ScoreScene(Scene):
    """スコア表示シーン（軽量版）

    Members:
        game_scene (GameScene): スコアを参照する元となるゲームシーン。
        global_state (GlobalState): 全体の入力状態。
        is_score_view (bool): スコア表示中かどうか。

    Methods:
        __init__(): スコアシーンを初期化する（スコアボード要素なし）。
        update(): シーン遷移や再スタート操作を管理する。
        draw(): 最終結果を表示する。
    """
    def __init__(self, game_scene:GameScene, elapsed_time, global_state:GlobalState):
        # GameSceneを保持し、スコアとともに管理
        self.game_scene = game_scene
        self.global_state = global_state
        self.is_score_view = True

        # 鳥瞰視点用の変数を追加
        self.is_transitioning = False
        self.transition_start_time = 0
        self.transition_duration = 30
        self.is_bird_view = True  # ScoreScene に来た時点で鳥瞰視点を想定
        self.original_position = None
        self.original_yaw = None
        self.original_pitch = None
        self.target_position = None
        self.target_yaw = None
        self.target_pitch = None

    def update(self):
        # スコアシーンでもキー入力関連をチェック
        self.global_state.update()

        # スコアシーンでのスコアボード表示切り替え
        if pyxel.btnp(pyxel.KEY_TAB):
            self.is_score_view = not self.is_score_view

        # 鳥瞰視点切り替え
        if not self.is_transitioning and pyxel.btnp(pyxel.KEY_B):
            self.is_transitioning = True
            self.transition_start_time = pyxel.frame_count
            camera = self.game_scene.camera

            if not self.is_bird_view:
                # 通常視点から鳥瞰視点
                self.original_position = camera.position.copy()
                self.original_yaw = camera.yaw
                self.original_pitch = camera.pitch
                bird_pos, (bird_yaw, bird_pitch) = self.game_scene.map.get_bird_view()
                self.target_position = np.array(bird_pos)
                self.target_yaw = bird_yaw
                self.target_pitch = bird_pitch
            else:
                # 鳥瞰視点から通常視点
                self.target_position = self.original_position
                self.target_yaw = self.original_yaw
                self.target_pitch = self.original_pitch
                bird_pos, (bird_yaw, bird_pitch) = self.game_scene.map.get_bird_view()
                self.original_position = np.array(bird_pos)
                self.original_yaw = bird_yaw
                self.original_pitch = bird_pitch

        if self.is_transitioning:
            camera = self.game_scene.camera
            progress = min(1.0, (pyxel.frame_count - self.transition_start_time) / self.transition_duration)
            camera.position = self.original_position + (self.target_position - self.original_position) * progress
            camera.yaw = self.original_yaw + (self.target_yaw - self.original_yaw) * progress
            camera.pitch = self.original_pitch + (self.target_pitch - self.original_pitch) * progress

            if not self.is_bird_view:
                camera.fov = self.game_scene.normal_fov + (self.game_scene.bird_fov - self.game_scene.normal_fov) * progress
            else:
                camera.fov = self.game_scene.bird_fov + (self.game_scene.normal_fov - self.game_scene.bird_fov) * progress

            if progress >= 1.0:
                self.is_transitioning = False
                self.is_bird_view = not self.is_bird_view

        if pyxel.btnp(pyxel.KEY_R):
            return GameScene(self.global_state)

        return self

    def draw(self):
        # まずはGameSceneをそのまま描画
        self.game_scene.draw()
        self.game_scene.draw_path()