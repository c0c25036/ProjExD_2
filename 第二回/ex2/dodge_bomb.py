import os
import sys
import pygame as pg
import random

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    yoko = True
    tate = True
    if rct.left < 0 or rct.right > WIDTH:
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:
        tate = False
    return yoko,tate

def gameover(screen: pg.Surface) -> None:
    """ゲームオーバー画面を表示する"""
    black_surf = pg.Surface((WIDTH, HEIGHT))
    black_surf.fill((0, 0, 0))
    black_surf.set_alpha(200)

    font = pg.font.Font(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rct = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))

    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)
    cry_rct = cry_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))

    screen.blit(black_surf, (0, 0))
    screen.blit(text, text_rct)
    screen.blit(cry_img, cry_rct)
    pg.display.update()

    pg.time.wait(5000)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """爆弾の拡大画像リストと加速度リストを返す"""
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]

    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)

    return bb_imgs, bb_accs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()

    kk_imgs = {
    (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 0.9),
    (0, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 0.9),
    (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),
    (+5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 180, 0.9),
}

    bb_img = pg.Surface((20, 20))
    bb_img.set_colorkey((0, 0, 0))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_rct = bb_img.get_rect()
    bb_rct.center = (
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT)
    )
    vx, vy = +5, +5
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, [0, 0])

        # DELTA辞書を使った移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if sum_mv != [0, 0] and tuple(sum_mv) in kk_imgs:
            kk_img = kk_imgs[tuple(sum_mv)]

        
        old_rct = kk_rct.copy()
        if not all(check_bound(kk_rct)):
            kk_rct = old_rct  
        
        # 爆弾の拡大・加速
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]

        # Rect のサイズ更新
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        # 移動
        bb_rct.move_ip(avx, avy)


        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
