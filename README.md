# 3D Maze
pyxelで作成された一人称視点の3D迷路脱出ゲームです。BGMについては、[8bit BGM generator](https://github.com/shiromofufactory/8bit-bgm-generator)を利用しています。

[English Documentation](./README_EN.md)

## デモ動画
<div><video controls src="https://raw.githubusercontent.com/Sanzentyo/3D_Maze/refs/heads/main/3D_Maze_Demo.mp4" title="3D_Maze_Demo.mp4" muted="false"></video></div>

## ネイティブ版の実行方法
まず、このリポジトリをクローンしてください。
```sh
git clone https://github.com/Sanzentyo/3D_Maze.git
```
その後、以下のコマンドを実行してください。
```sh
cd 3D_Maze
pip install requirements.txt # 必要なライブラリのインストール(pyxel, numpy, pyxel-universal-fontがインストールされているなら不要)
python src/App.py # ゲームの起動
```

## Web版
pyxelの仕様とパフォーマンスの都合上、文字とスコアボード、bgmが削除されています。それ以外はネイティブと同じ動作をします。
https://sanzentyo.github.io/3D_Maze

## 操作方法
- 移動： WASDキー または 矢印キー
- 鳥瞰モード(Bird View)の切り替え: Bキー
- ゲーム終了: ESCキー または Qキー
- マウス移動: カメラの向きを変更
- フォーカス: Coinを一枚以上取得した状態で、Fキー
- 壁の破壊: フォーカス状態で、マウス左クリック

## 操作方法(デバッグ用)
- マスタービューモードの切り替え: Ctrlキー+Mキー。マスタービューモード時は、ゴール判定や壁との衝突判定をしない。
- 上下移動: マスタービューモード時、Spaceで上昇、Shiftで下降
- 移動方法の切り替え: マスタービューモード時に、Mキーで視点ベース方向の移動(View Base)とYaw方向だけを考慮した移動(Yaw Base)。通常時(非マスタービューモード時)はYaw Baseで移動する。
- ワイヤーフレーム表示の切り替え: Ctrlキー+Wキー