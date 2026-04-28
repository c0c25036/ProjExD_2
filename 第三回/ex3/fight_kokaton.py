import os
import random
import sys
import time
import pygame as pg
import math

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate



class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書 
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }


    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)   

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = tuple(sum_mv) 
        screen.blit(self.img, self.rct) 

class Beam:
    def __init__(self, bird: "Bird"):
        # こうかとんの向き
        vx, vy = bird.dire
        self.vx, self.vy = vx, vy

        # 角度を計算（pygame は y 軸が下向きなので -vy）
        theta = math.degrees(math.atan2(-vy, vx))

        # ビーム画像を回転
        img0 = pg.image.load("fig/beam.png")
        self.img = pg.transform.rotozoom(img0, theta, 1.0)
        self.rct = self.img.get_rect()

        # こうかとんの中心から向きに応じてずらす
        bx = bird.rct.centerx + bird.rct.width * (vx / 5)
        by = bird.rct.centery + bird.rct.height * (vy / 5)
        self.rct.center = (bx, by)
    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)

        if check_bound(self.rct) != (True, True):
            return False

        screen.blit(self.img, self.rct)
        return True
# ビームクラス:
    # """
    # こうかとんが放つビームに関するクラス
    # """
    # def イニシャライザ(self, bird:"Bird"):
    #     """
    #     ビーム画像Surfaceを生成する
    #     引数 bird：ビームを放つこうかとん（Birdインスタンス）
    #     """
    #     self.img = pg.画像のロード(f"fig/beam.png")
    #     self.rct = self.img.Rectの取得()
    #     self.ビームの中心縦座標 = こうかとんの中心縦座標
    #     self.ビームの左座標 = こうかとんの右座標
    #     self.vx, self.vy = +5, 0

    # def update(self, screen: pg.Surface):
    #     """
    #     ビームを速度ベクトルself.vx, self.vyに基づき移動させる
    #     引数 screen：画面Surface
    #     """
    #     if check_bound(self.rct) == (True, True):
    #         self.rct.move_ip(self.vx, self.vy)
    #         screen.blit(self.img, self.rct)    
class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    def __init__(self):
        self.fonto = pg.font.SysFont(None, 30)
        self.color = (0, 0, 255)
        self.value = 0
        self.img = self.fonto.render(f"Score: {self.value}", True, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        self.img = self.fonto.render(f"Score: {self.value}", True, self.color)
        screen.blit(self.img, self.rct)

# 追加機能3：爆発エフェクト
class Explosion:
    def __init__(self, center: tuple[int, int]):
        # 爆発画像（元画像）
        img0 = pg.image.load("fig/explosion.gif")

        # 上下左右に flip した画像を作る
        img1 = pg.transform.flip(img0, True, False)   # 左右反転
        img2 = pg.transform.flip(img0, False, True)   # 上下反転
        img3 = pg.transform.flip(img1, False, True)   # 上下左右反転

        # Surface をリストに格納
        self.imgs = [img0, img1, img2, img3]

        # 爆発位置
        self.rct = self.imgs[0].get_rect()
        self.rct.center = center

        # 爆発の寿命
        self.life = 20   # 20フレーム表示（調整可）

    def update(self, screen: pg.Surface):
        # life が 0 なら何もしない
        if self.life <= 0:
            return

        # 画像を交互に切り替える
        img = self.imgs[self.life % 4]
        screen.blit(img, self.rct)

        # 寿命を減らす
        self.life -= 1

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    score = Score()
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []  # ゲーム初期化時にはビームは存在しない
    explosions = []
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))

        screen.blit(bg_img, [0, 0])
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        # --- こうかとんと爆弾の衝突判定（複数対応） ---
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(2)
                return

        
        
        # --- 練習3：ビームが爆弾に当たったときの処理 ---
        for bi, beam in enumerate(beams):
            for bo, bomb in enumerate(bombs):
                if beam is None or bomb is None:
                    continue
                if beam.rct.colliderect(bomb.rct):
                    bird.change_img(6, screen)
                    explosions.append(Explosion(bomb.rct.center))  
                    bombs[bo] = None
                    beams[bi] = None
                    score.value += 1   # スコア機能がある場合
                    break
        bombs = [b for b in bombs if b is not None]
        beams = [b for b in beams if b is not None]
        # --- 爆弾の update ---
        for bomb in bombs:
            bomb.update(screen)
        # --- ビームの update ---
        new_beams = []
        for beam in beams:
            if beam.update(screen):   # True → 画面内、False → 画面外
                new_beams.append(beam)
        beams = new_beams
        # --- Explosion update ---
        for ex in explosions:
            ex.update(screen)

        # life が残っているものだけ残す
        explosions = [ex for ex in explosions if ex.life > 0]

        score.update(screen)
        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
