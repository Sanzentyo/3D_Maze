import pyxel
import numpy as np

class TriSprite:
    def __init__(
        self,
        p1: tuple[float, float, float, float],
        p2: tuple[float, float, float, float],
        p3: tuple[float, float, float, float],
        color: int
    ):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.color = color

    def get_depth(self):
        # w除算後のz値（投影後の深度）で平均を取る
        z1 = self.p1[2] / self.p1[3] if self.p1[3] != 0 else float('inf')
        z2 = self.p2[2] / self.p2[3] if self.p2[3] != 0 else float('inf')
        z3 = self.p3[2] / self.p3[3] if self.p3[3] != 0 else float('inf')
        return (z1 + z2 + z3) / 3

    def is_frontface(self) -> bool:
        # w除算して3次元ベクトル化
        v1 = (np.array(self.p2[:3]) / self.p2[3]) - (np.array(self.p1[:3]) / self.p1[3])
        v2 = (np.array(self.p3[:3]) / self.p3[3]) - (np.array(self.p1[:3]) / self.p1[3])
        normal = np.cross(v1, v2)
        # 視線方向(0,0,1)との内積
        if np.linalg.norm(normal) == 0:
            return False
        normal /= np.linalg.norm(normal)
        view_dir = np.array([0, 0, 1])
        return np.dot(normal, view_dir) < 0

    def draw(self, color=None):
        # 既にclip_triangleで正しくクリップされた三角形は2D座標に変換済みとして描画
        if color is None:
            pyxel.tri(self.p1[0], self.p1[1],
                    self.p2[0], self.p2[1],
                    self.p3[0], self.p3[1],
                    self.color)
        else:
            pyxel.tri(self.p1[0], self.p1[1],
                    self.p2[0], self.p2[1],
                    self.p3[0], self.p3[1],
                    color)
    
    def draw_wireframe(self, color=None):
        if color is None:
            pyxel.line(self.p1[0], self.p1[1], self.p2[0], self.p2[1], self.color)
            pyxel.line(self.p2[0], self.p2[1], self.p3[0], self.p3[1], self.color)
            pyxel.line(self.p3[0], self.p3[1], self.p1[0], self.p1[1], self.color)
        else:
            pyxel.line(self.p1[0], self.p1[1], self.p2[0], self.p2[1], color)
            pyxel.line(self.p2[0], self.p2[1], self.p3[0], self.p3[1], color)
            pyxel.line(self.p3[0], self.p3[1], self.p1[0], self.p1[1], color)

    def clip_triangle(self, width: int, height: int) -> list['TriSprite']:
        """
        1. z_near (w>0) の下での近接クリップ (簡易実装)
        2. w除算して2D化
        3. Sutherland–Hodgman法でビュー範囲内をクリップ
        """
        # まずwが正の頂点のみでクリップ (z_near平面に相当)
        clipped_4d = self._clip_near_plane([self.p1, self.p2, self.p3])
        if len(clipped_4d) < 3:
            return []

        # w除算->2D化する際に、z値も保持
        pts_2d = [(p[0]/p[3], p[1]/p[3], p[2]/p[3]) for p in clipped_4d]

        LEFT = -width / 2
        RIGHT = width / 2
        TOP = -height / 2
        BOTTOM = height / 2

        # 2Dクリッピング (Sutherland–Hodgman)
        def inside_left(p):   return p[0] >= LEFT
        def inside_right(p):  return p[0] <= RIGHT
        def inside_top(p):    return p[1] >= TOP
        def inside_bottom(p): return p[1] <= BOTTOM

        def intersect(p1, p2, boundary):
            # p1->p2の交差計算
            x1, y1, z1 = p1
            x2, y2, z2 = p2
            dx, dy = x2 - x1, y2 - y1

            # tを求める
            if boundary == 'left':
                t = (LEFT - x1) / dx if dx else 0
            elif boundary == 'right':
                t = (RIGHT - x1) / dx if dx else 0
            elif boundary == 'top':
                t = (TOP - y1) / dy if dy else 0
            elif boundary == 'bottom':
                t = (BOTTOM - y1) / dy if dy else 0
            else:
                t = 0

            # z値も線形補間
            new_z = z1 + t * (z2 - z1)

            if boundary == 'left':
                return (LEFT, y1 + t*dy, new_z)
            elif boundary == 'right':
                return (RIGHT, y1 + t*dy, new_z)
            elif boundary == 'top':
                return (x1 + t*dx, TOP, new_z)
            elif boundary == 'bottom':
                return (x1 + t*dx, BOTTOM, new_z)
            return p1

        def clip_polygon(pts, inside_func, boundary):
            out = []
            for i in range(len(pts)):
                cur, nxt = pts[i], pts[(i+1) % len(pts)]
                cur_in = inside_func((cur[0], cur[1]))
                nxt_in = inside_func((nxt[0], nxt[1]))
                if cur_in and nxt_in:
                    out.append(nxt)
                elif cur_in and not nxt_in:
                    out.append(intersect(cur, nxt, boundary))
                elif not cur_in and nxt_in:
                    out.append(intersect(cur, nxt, boundary))
                    out.append(nxt)
            return out

        poly_2d = pts_2d
        for func, bd in [(inside_left, 'left'), (inside_right, 'right'),
                         (inside_top, 'top'), (inside_bottom, 'bottom')]:
            poly_2d = clip_polygon(poly_2d, func, bd)
            if len(poly_2d) < 3:
                return []

        # 三角形化して返す（z値を保持）
        clipped_sprites = []
        for i in range(1, len(poly_2d) - 1):
            p1_2d = poly_2d[0]
            p2_2d = poly_2d[i]
            p3_2d = poly_2d[i+1]
            clipped_sprites.append(
                TriSprite(
                    (p1_2d[0], p1_2d[1], p1_2d[2], 1),
                    (p2_2d[0], p2_2d[1], p2_2d[2], 1),
                    (p3_2d[0], p3_2d[1], p3_2d[2], 1),
                    self.color
                )
            )
        return clipped_sprites

    def _clip_near_plane(self, verts_4d: list[tuple[float, float, float, float]]) -> list[tuple[float, float, float, float]]:
        """ w>0 の頂点のみ残す簡易版。Sutherland-Hodgmanと同様に線形補間して差し替え """
        out = []
        for i in range(len(verts_4d)):
            cur = verts_4d[i]
            nxt = verts_4d[(i+1) % len(verts_4d)]
            cur_in = (cur[3] > 0)
            nxt_in = (nxt[3] > 0)

            if cur_in and nxt_in:
                out.append(nxt)
            elif cur_in and not nxt_in:
                out.append(self._intersect_near(cur, nxt))
            elif not cur_in and nxt_in:
                out.append(self._intersect_near(cur, nxt))
                out.append(nxt)
        return out

    def _intersect_near(self, p1, p2):
        """ 単純にp1->p2の線で w=0 面との交点を補間 """
        w1, w2 = p1[3], p2[3]
        if (w2 - w1) == 0:
            return p1
        t = (0 - w1) / (w2 - w1)
        return (
            p1[0] + t * (p2[0] - p1[0]),
            p1[1] + t * (p2[1] - p1[1]),
            p1[2] + t * (p2[2] - p1[2]),
            0.00001  # w=0より少しだけ正にして残す
        )