"""
迷路の生成を行うクラスを定義するファイルです。

Classes:
    StartEndStrategy(Enum):
        スタートとゴールの配置戦略を定義する列挙型。
        Values:
            DIAGONAL: 対角配置
            RANDOM: ランダム配置
            MANUAL: 手動指定
            MIN_DISTANCE: 最小距離保証

    MazeGenerator:
        迷路の生成を管理するクラス。
        Members:
            width (int): 迷路の幅。
            height (int): 迷路の高さ。
            maze (list[list[str]]): 迷路データ。
        Methods:
            __init__(): コンストラクタ。
            _get_empty_spaces(): 空きマスの位置を取得。
            _calculate_distance(): 2点間のマンハッタン距離を計算。
            _are_adjacent(): 2つの位置が隣接しているかチェック。
            _place_start_end(): スタートとゴールを配置。
            generate(): 迷路の生成実行。
"""

import random
from enum import Enum
from typing import Tuple, Optional

class StartEndStrategy(Enum):
    DIAGONAL = "diagonal"          # 対角に配置
    RANDOM = "random"             # ランダムに配置
    MANUAL = "manual"             # 明示的に指定
    MIN_DISTANCE = "min_distance"  # 最小距離を保証

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [['#' for x in range(width)] for y in range(height)]
        
    def _get_empty_spaces(self) -> list[Tuple[int, int]]:
        """空きマスの位置をリストで返す"""
        return [(x, y) for y in range(self.height) 
               for x in range(self.width) if self.maze[y][x] == ' ']

    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """2点間のマンハッタン距離を計算"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _are_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """2つの位置が隣接しているかチェック"""
        return self._calculate_distance(pos1, pos2) == 1

    def _place_start_end(self, strategy: StartEndStrategy, 
                        start_pos: Optional[Tuple[int, int]], 
                        end_pos: Optional[Tuple[int, int]],
                        min_distance: Optional[int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """指定された戦略でスタートとゴールを配置"""
        empty_spaces = self._get_empty_spaces()
        
        if strategy == StartEndStrategy.DIAGONAL:
            # 左上に最も近い空きマスと右下に最も近い空きマスを選択
            start = min(empty_spaces, key=lambda p: p[0] + p[1])
            end = max(empty_spaces, key=lambda p: p[0] + p[1])
            
        elif strategy == StartEndStrategy.RANDOM:
            # ランダムに2つ選択（隣接チェック付き）
            while True:
                start, end = random.sample(empty_spaces, 2)
                if not self._are_adjacent(start, end):
                    break
                    
        elif strategy == StartEndStrategy.MANUAL:
            # 指定された位置をチェック
            if not (start_pos and end_pos and
                   start_pos in empty_spaces and
                   end_pos in empty_spaces):
                raise ValueError("Invalid start or end position")
            start, end = start_pos, end_pos
            
        elif strategy == StartEndStrategy.MIN_DISTANCE:
            # 指定された最小距離を満たすようにランダムに配置
            if not min_distance:
                min_distance = (self.width + self.height) // 4
            max_attempts = 100
            for _ in range(max_attempts):
                start, end = random.sample(empty_spaces, 2)
                if self._calculate_distance(start, end) >= min_distance:
                    break
            else:
                raise ValueError("Could not find positions with required minimum distance")
                
        return start, end

    def generate(self, coin_count=None, 
                strategy: StartEndStrategy = StartEndStrategy.DIAGONAL,
                start_pos: Tuple[int, int] = None,
                end_pos: Tuple[int, int] = None,
                min_distance: int = None) -> list[str]:
        # まず迷路を掘る（元の実装）
        start_x = 1
        start_y = 1
        self.maze[start_y][start_x] = ' '

        stack = [(start_x, start_y)]
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

        while stack:
            current_x, current_y = stack[-1]
            random.shuffle(directions)
            
            can_dig = False
            for dx, dy in directions:
                new_x = current_x + dx
                new_y = current_y + dy
                
                if (0 < new_x < self.width-1 and 
                    0 < new_y < self.height-1 and 
                    self.maze[new_y][new_x] == '#'):
                    self.maze[new_y][new_x] = ' '
                    self.maze[current_y + dy//2][current_x + dx//2] = ' '
                    stack.append((new_x, new_y))
                    can_dig = True
                    break
            
            if not can_dig:
                stack.pop()

        # スタート・ゴール位置を決定
        start, end = self._place_start_end(strategy, start_pos, end_pos, min_distance)
        
        # スタート・ゴールを配置
        self.maze[start[1]][start[0]] = 's'
        self.maze[end[1]][end[0]] = 'g'

        # コインを配置
        empty_spaces = [(x, y) for y in range(self.height) for x in range(self.width) 
                       if self.maze[y][x] == ' ']
        
        if coin_count is None:
            coin_count = len(empty_spaces) // 30
        coin_count = min(coin_count, len(empty_spaces))
        
        for x, y in random.sample(empty_spaces, coin_count):
            self.maze[y][x] = '.'

        return [''.join(row) for row in self.maze]
