# 3D Maze 詳細設計書

[English Version](./DETAILED_DESIGN_EN.md)

## 目次
1. [概要](#1-概要)
2. [プログラム全体構造](#2-プログラム全体構造)
3. [重要な処理フロー](#3-重要な処理フロー)
4. [クラス一覧](#4-クラス一覧)
5. [操作方法](#5-操作方法)

## 1. 概要
本ドキュメントでは、3D Maze プロジェクトの内部構造について、クラス・メソッド・変数を中心に整理した詳細設計を示します。  
主に以下の機能を提供しており、Pyxel 上で 3D 表示を簡易的に実装する仕組みをクラス単位で定義しています。  

## 2. プログラム全体構造
アプリケーションは大きく `StartScene`, `GameScene`, `ScoreScene` の 3 つのシーンに分かれ、それぞれで画面や情報を管理します。  
最初に `App` クラスが Pyxel の初期化とメインループを制御し、現在のシーンの更新・描画処理を行います。

## 3. 重要な処理フロー
### 3.1 ゲームループ
1. `App.update()` がフレームごとに呼び出され、現在のシーンの `update()` を実行し、その中で現在のシーン(self.scene)の`update()`を呼び出す  
2. `App.draw()` がフレームごとに呼び出され、現在のシーン(self.scene)の `draw()` を実行  

### 3.2 3D 描画フロー
1. `Scene.render_3d_scene()` でカメラのビュー行列 (`Camera.get_view_matrix()`) と投影行列 (`Camera.get_projection_matrix()`) を取得
2. 取得した行列を合成して `view_projection_matrix` を生成
3. オブジェクトグループごとに以下の処理を実行:
   - `get_tri_sprites()` で 3D オブジェクトを `TriSprite` の配列に変換
   - 深度値でソート (`TriSprite.get_depth()`)
   - `draw_tri_sprites()` で以下の描画処理を実行:
     - 必要に応じてバックフェースカリング (`TriSprite.is_frontface()`)
     - `TriSprite.clip_triangle()` でビュー範囲内のクリッピング処理
     - スクリーン座標系に変換して `TriSprite.draw()` で描画
     - ワイヤーフレームモード時は `TriSprite.draw_wireframe()` も実行

### 3.3 プレイヤー移動フロー
1. `GameScene.update()` 内で `Camera.move_and_is_coin_collected()` を呼び出し、キーボード入力に基づいてカメラ位置を更新
2. `Map.set_camera_position_and_check_coin_collection()` で以下を実行:
   - X方向とZ方向の移動を分離して試行
   - 各方向で `Map.is_position_passable()` を使って壁との衝突判定
   - `Map.check_coin_collection()` でコイン取得判定
   - 移動可能な場合は新しい位置を設定
3. カメラの回転は `Camera.process_mouse_movement()` でマウス入力に基づいて更新

### 3.4 典型的なシナリオ

#### 3.4.1 コインを取得した場合
1. `GameScene.update()` で `Camera.move_and_is_coin_collected()` を呼び出し、移動中のコイン取得判定を行う
2. コイン取得時は効果音を再生し、マップデータ上のコイン('.')を空白(' ')に置換
3. マップオブジェクトを再生成し、`GameScene` の描画オブジェクト（床・壁・球体）を更新

#### 3.4.2 鳥瞰モードへの切り替え (Bキー)
1. `GameScene.update()` で B キーの入力を検知し、遷移アニメーションを開始
2. 30フレームかけて以下のパラメータを線形補間:
   - カメラ位置: 現在位置 → `Map.get_bird_view()` の位置
   - カメラ角度: 現在の yaw/pitch → 真下を向く角度
   - 画角(FOV): 通常90度 → 鳥瞰用50度
3. 鳥瞰視点中はプレイヤー位置をキューブで表示

#### 3.4.3 マスタービューモードへの切り替え (Ctrl+Mキー)
1. `GlobalState.update()` で Ctrl+M 入力を検知し、`is_master_view` を切り替え
2. マスタービュー中は以下の機能が有効に:
   - 壁との衝突判定をスキップ
   - Space/Shiftキーでの上下移動
   - M キーで視点ベース/Yawベース移動の切り替え

#### 3.4.4 壁の破壊 (コイン所持+フォーカス+左クリック)
1. コインを1枚以上所持している状態で F キーを押すと、前方の壁をハイライト表示
2. ハイライト中に左クリックで:
   - 効果音を再生
   - マップデータの '#' を ' ' に置換
   - マップと描画オブジェクトを再生成
   - コインを1枚消費

#### 3.4.5 ゴール到達時
1. `Map.check_goal_reached()` でゴール到達判定を行い、ゴールに到達した場合は `ScoreScene` に遷移
2. `ScoreScene` では、移動軌跡の描画とスコア表示を行い、リトライやタイトルに戻ることができる

### 3.4.6 BGMの再生
1. 各シーン（StartScene, GameScene, ScoreScene）の初期化時に、対応するBGMデータを`bgm_data`変数にセット
2. シーンの`update()`メソッド内で、BGMが再生されていない場合（`pyxel.play_pos(0) is None`）に以下の処理を実行:
   - `bgm_data`の各要素（音声チャンネルごとのデータ）に対して:
     - `pyxel.sounds[ch].set(*sound)`で音声データをセット
     - `pyxel.play(ch, ch, loop=True)`でループ再生を開始
3. シーン遷移時（例：StartSceneからGameSceneへ）に以下の処理を実行:
   - 現在再生中のBGMを`pyxel.stop()`で停止
   - 新しいシーンの`__init__()`内で新たなBGMをセット・再生
4. ゲーム終了時（Qキー押下時）やScoreSceneからGameSceneへのリトライ時にも`pyxel.stop()`でBGMを停止

BGMデータは`bgm_data.py`ファイルに定義され、各シーンで以下のように使用されます:
- `start_scene_bgm_data`: タイトル画面用BGM
- `game_scene_bgm_data`: ゲームプレイ中のBGM
- `score_scene_bgm_data`: スコア画面用BGM


## 4. クラス一覧

### 4.1 `App` (メインアプリケーションクラス)
- 役割: Pyxel アプリケーション全体の初期化・ループ管理  
- 主な変数:  
  - `scene`: 現在のシーン
  - `global_state`: グローバル状態管理
  - `width`, `height`: 画面サイズ
- 主なメソッド:  
  - `__init__()`: Pyxel の初期化、シーン設定、サウンド初期化
  - `update()`: 現在のシーンの更新処理を実行 
  - `draw()`: 現在のシーンの描画処理を実行

### 4.2 `Scene` (シーン基底クラス)
- 役割: 各シーンの共通処理を提供する抽象基底クラス
- 主なメソッド:  
  - `update()`: シーンの状態更新（抽象メソッド）
  - `draw()`: シーンの描画（抽象メソッド）
  - `get_tri_sprites()`: 3D オブジェクトから三角形スプライトを取得
  - `draw_tri_sprites()`: 三角形スプライトを描画
  - `render_3d_scene()`: カメラ情報を用いて 3D シーンをレンダリング

### 4.3 `StartScene` (スタート画面クラス、`Scene`の派生クラス)
- 役割: タイトル画面の管理  
- 主な変数:
  - `writer`: テキスト描画用
  - `psychedelic_sphere`: タイトル装飾用の球体
  - `title_camera`: タイトル画面用カメラ
- 主なメソッド:  
  - `update()`: Space キーでゲーム開始
  - `draw()`: タイトルやデモ画面の描画

### 4.4 `GameScene` (ゲーム画面クラス、`Scene`の派生クラス)
- 役割: メインゲームの進行管理
- 主な変数:   
  - `map`: 迷路データと管理
  - `camera`: プレイヤー視点用カメラ
  - `planes`: 床オブジェクト
  - `walls`: 壁オブジェクト 
  - `spheres`: コイン（球体）オブジェクト
  - `player_cube`: 鳥瞰視点時のプレイヤー位置表示
- 主なメソッド:  
  - `update()`: ゲーム状態の更新（移動・衝突・モード切替など）
  - `draw()`: 3D シーンと UI の描画
  - `_highlight_wall_in_front()`: 前方の壁のハイライト表示
  - `_destroy_highlighted_wall()`: 壁の破壊処理

### 4.5 `ScoreScene` (リザルト画面クラス、`Scene`の派生クラス)
- 役割: ゴール後の結果表示  
- 主な変数:
  - `game_scene`: 終了したゲームシーンの参照
  - `scoreboard`: スコア表示用 UI
- 主なメソッド:  
  - `update()`: Tab でスコア表示切替、R でリトライ
  - `draw()`: 移動軌跡とスコアの描画

### 4.6 `Map` (マップクラス)
- 役割: 迷路の管理と衝突判定
- 主な変数:
  - `map_data`: 迷路の文字列データ('#':壁, '.':コイン, 's':スタート, 'g':ゴール)
  - `tile_size`: タイルの大きさ
  - `origin_pos`: マップの基準座標
  - `camera_position`: 現在のカメラ位置
- 主なメソッド:  
  - `generate_maze_map()`: ランダム迷路の生成
  - `is_position_passable()`: 移動可能判定
  - `check_coin_collection()`: コイン取得判定
  - `check_goal_reached()`: ゴール到達判定

### 4.7 `Camera` (カメラクラス)
- 役割: 3D 視点の制御  
- 主な変数:  
  - `position`: 位置座標
  - `yaw`: 水平角度
  - `pitch`: 垂直角度
  - `view_based_movement`: 視点依存移動フラグ
- 主なメソッド:  
  - `process_mouse_movement()`: マウスによる視点回転
  - `move_and_is_coin_collected()`: 位置更新とコイン判定
  - `get_view_matrix()`: ビュー行列の計算
  - `get_projection_matrix()`: 投影行列の計算

### 4.8 `GlobalState` (グローバル状態クラス)
- 役割: 入力状態やモードフラグの管理
- 主な変数:
  - `keyboard_state`: キー入力状態
  - `is_master_view`: マスタービューフラグ
  - `is_view_wireframe`: ワイヤーフレーム表示フラグ
  - `is_view_based_movement`: 視点依存移動フラグ
- 主なメソッド:
  - `update()`: 入力状態の更新
  - `toggle_wireframe()`: ワイヤーフレーム表示切替
  - `toggle_master_view()`: マスタービューモード切替

### 4.9 `DrawObject` (3D描画オブジェクト基底クラス)
- 役割: 3Dオブジェクトの共通機能を提供する抽象基底クラス
- 主な変数:
  - `center`: 中心座標 [x, y, z, 1]
  - `vertices`: 頂点リスト
  - `faces`: 面を構成する頂点インデックスリスト
  - `colors`: 面ごとの色情報
- 主なメソッド:
  - `_generate_vertices()`: 頂点の生成（抽象メソッド）
  - `_generate_faces()`: 面と色の生成（抽象メソッド） 
  - `get_tri_sprites()`: 三角形スプライトのリストを生成

### 4.10 `Plane` (`DrawObject`の派生クラス)
- 役割: 床や天井などの平面を表現
- 主な変数:
  - `plane_width`: 平面の横幅
  - `plane_height`: 平面の縦幅
  - `color`: 描画色
- 主なメソッド:
  - `_generate_vertices()`: 4頂点の生成
  - `_generate_faces()`: 2つの三角形で構成
  - `get_tri_sprites()`: 平面の三角形スプライト生成

### 4.11 `EdgePlane` (`Plane`の派生クラス)
- 役割: 縁取り付きの平面を表現
- 主な変数:
  - `edge_width`: エッジの幅
  - `center_color`: 中央部分の色
  - `edge_color`: エッジ部分の色
- 主なメソッド:
  - `_generate_vertices()`: エッジ付き平面の頂点生成
  - `_generate_faces()`: 中央部とエッジ部の面生成

### 4.12 `Wall` (`DrawObject`の派生クラス)
- 役割: 迷路の壁を表現
- 主な変数:
  - `positions`: 壁の位置座標リスト
  - `size`: 壁の一辺の長さ
- 主なメソッド:
  - `_generate_vertices()`: 隣接壁を考慮した頂点生成 
  - `_generate_faces()`: 表示する面と色の生成
  - `_is_adjacent()`: 壁同士の隣接判定

### 4.13 `HighlightedWall` (`Wall`の派生クラス)
- 役割: フォーカス時にハイライト表示される壁
- 主な変数:
  - `edge_width`: エッジの太さ
  - `position`: 壁の位置
- 主なメソッド:
  - `get_tri_sprites()`: エッジ描画用の三角形スプライト生成
  - `_generate_faces()`: エッジのみの面生成

### 4.14 `Cube` (`DrawObject`の派生クラス) 
- 役割: プレイヤー位置表示などの立方体オブジェクト
- 主な変数:
  - `size`: 一辺の長さ
  - `half_size`: サイズの半分（計算用）
- 主なメソッド:
  - `_generate_vertices()`: 8頂点の生成
  - `_generate_faces()`: 6面12三角形の生成
  - `is_adjacent()`: 他の立方体との隣接判定

### 4.15 `RotatingCube` (`Cube`の派生クラス)
- 役割: 回転する立方体
- 主な変数:
  - `rotation_angle`: 現在の回転角度
  - `rotation_speed`: 回転速度
  - `base_vertices`: 初期頂点情報
- 主なメソッド:
  - `update()`: 回転角度の更新とY軸方向拡大
  - `_generate_vertices()`: 回転を適用した頂点の生成

### 4.16 `Sphere` (`DrawObject`の派生クラス)
- 役割: コインなどの球体オブジェクト
- 主な変数:
  - `radius`: 球の半径
  - `segments`: 分割数
- 主なメソッド:
  - `_generate_vertices()`: 緯度経度による頂点生成
  - `_generate_faces()`: 球面の三角形分割と色設定
  - `get_tri_sprites()`: 球体の三角形スプライト生成

### 4.17 `RotatingSphere` (`Sphere`の派生クラス)
- 役割: 回転する球体
- 主な変数:
  - `rotation_angle`: 回転角度
  - `rotation_axis`: 回転軸
  - `rotation_speed`: 回転速度
- 主なメソッド:
  - `update()`: 回転角度の更新
  - `_generate_vertices()`: 回転行列を適用した頂点生成

### 4.18 `PsychedelicSphere` (`RotatingSphere`の派生クラス)
- 役割: 色が変化する回転球体
- 主な変数:
  - `color_time`: 色変化の時間管理
  - `color_speed`: 色変化の速度
- 主なメソッド:
  - `update()`: 回転と色の更新
  - `_generate_faces()`: 時間依存の色設定

### 4.19 `TriSprite` (三角形スプライトクラス)
- 役割: 3D空間の三角形を2D表示に投影し、描画するための基本図形
- 主な変数:
  - `p1`, `p2`, `p3`: 三角形の頂点座標 (x, y, z, w)
  - `color`: Pyxelで描画する際の色情報
- 主なメソッド:
  - `get_depth()`: 深度値（カメラからの距離）の計算
  - `is_frontface()`: 表面判定（バックフェースカリング用）
  - `draw()`: 三角形の描画
  - `draw_wireframe()`: ワイヤーフレームとしての描画
  - `clip_triangle()`: ビュー範囲内での三角形のクリッピング処理
  - `_clip_near_plane()`: 近接クリップ面でのクリッピング
  - `_intersect_near()`: 近接クリップ面との交点計算


## 5. 操作方法
### 5.1 ゲームプレイ
- 移動： WASDキー または 矢印キー
- 鳥瞰モード(Bird View)の切り替え: Bキー
- ゲーム終了: ESCキー または Qキー
- 視点移動: マウスの移動
- 視点移動の無効化とマウスの表示: Ctrlキー
- フォーカス: Coinを一枚以上取得した状態で、Fキー
- 壁の破壊: フォーカス状態で、マウス左クリック

### 5.2 デバッグ用操作
- マスタービューモードの切り替え: Ctrlキー+Mキー。マスタービューモード時は、ゴール判定や壁との衝突判定をしない。
- 上下移動: マスタービューモード時、Spaceで上昇、Shiftで下降
- 移動方法の切り替え: マスタービューモード時に、Mキーで視点ベース方向の移動(View Base)とYaw方向だけを考慮した移動(Yaw Base)。通常時(非マスタービューモード時)はYaw Baseで移動する。
- ワイヤーフレーム表示の切り替え: Ctrlキー+Wキー