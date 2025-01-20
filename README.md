# 3D Maze
pyxelで作成された一人称視点の3D迷路脱出ゲームです。BGMについては、[8bit BGM generator](https://github.com/shiromofufactory/8bit-bgm-generator)を利用しています。

### [English Documentation](./README_EN.md)

## デモ動画
https://github.com/user-attachments/assets/408bd84b-8ef7-49dd-9a12-a4e0f4806256

## ネイティブ版の実行方法
```sh
# リポジトリのクローン
git clone https://github.com/Sanzentyo/3D_Maze.git
cd 3D_Maze

# pipを使う場合
pip install -r requirements.txt # 依存パッケージのインストール(既にpyxel, numpy, pyxel-universal-fontがインストールされている場合は不要)
python src/App.py # ゲームの起動

# uvを使う場合
uv run src/App.py
```

## Web版
pyxelの仕様とパフォーマンスの都合上、文字とスコアボード、bgmが削除されています。それ以外はネイティブと同じ動作をします。  
https://sanzentyo.github.io/3D_Maze

## 操作方法

### 基本操作
| 操作 | キー/マウス |
|------|------------|
| 位置の移動 | WASDキー または 矢印キー |
| 視点方向の移動 | マウスの移動 |
| 鳥瞰モードの切り替え | Bキー |
| ゲーム終了 | ESCキー または Qキー |
| 視点移動の無効化とマウスの表示 | Ctrlキー |
| フォーカス | Fキー (Coinを一枚以上取得が必要) |
| 壁の破壊 | フォーカス状態でマウス左クリック |

### デバッグ操作
| 操作 | キー/マウス |
|------|------------|
| マスタービューモードの切り替え | Ctrlキー+Mキー |
| 上下移動 | Space(上昇)、Shift(下降) ※マスタービューモード時のみ |
| 移動方法の切り替え | Mキー ※マスタービューモード時のみ |
| ワイヤーフレーム表示の切り替え | Ctrlキー+Wキー |
