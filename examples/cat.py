import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from stamp_print.stamp import *

P = Poster(900, 1200, S=2, seed=7, misreg=1.6)
P.background('violet', waves=None)

# ---------- 后层：窗 + 下墙 ----------
wall = P.rect_mask(-20, 1010, 920, 1220, amp=2)
P.cut(wall, 'moss', shadow=None)
P.texture(wall, 'wave', 'moss_dk', spacing=15, width=1.5, amp=3, wl=60, inset=0)

win = P.rect_mask(70, 380, 590, 940, r=14, amp=1.6)
P.cut(win, 'paper', shadow=(8, 10))
glass = P.rect_mask(94, 404, 566, 915, r=6, amp=1.2)
P.add(glass, 'violet_dk')
P.texture(glass, 'dash', 'violet', spacing=16, width=1.6, inset=10)
P.add(P.rect_mask(88, 612, 572, 630, amp=.8), 'paper')          # 窗格横档
P.line([(102, 418), (102, 600)], 'violet_lt', 1.2)                 # 玻璃反光细线
P.line([(116, 418), (116, 520)], 'violet_lt', 1.0)

# 右侧墙面：一块浅灰紫墙垛 + 邮政波浪戳纹
pil = P.rect_mask(640, 360, 860, 1010, amp=1.6)
P.cut(pil, 'violet_lt', shadow=(6, 0), shadow_alpha=.22)
P.texture(pil, 'holes', 'violet', spacing=26, hole=3.2, inset=16)
P.cancel_waves(n=5, length=230, gap=12, at=(600, 905), color='violet_dk')

# ---------- 中层：吊兰 + 碗 ----------
import math as _m
base = (228, 800)
blades = [((60, 520), .10), ((110, 470), .15), ((170, 440), .06), ((250, 430), -.08),
          ((330, 470), -.14), ((380, 560), -.18), ((40, 650), .18), ((410, 690), -.22),
          ((140, 560), .05), ((300, 560), -.05)]
for i, (tip, b) in enumerate(blades):
    P.leaf(base, tip, bend=b, width=22 if i % 3 else 26,
           color='moss' if i % 2 else 'moss_dk', vein='paper' if i % 2 == 0 else 'moss_dk',
           shadow=(5, 6) if i < 4 else None)
pot = P.shape_mask([(150, 790), (306, 790), (290, 925), (166, 925)], False, 1.4)
P.cut(pot, 'apricot', shadow=(7, 8))
P.texture(pot, 'stripe', 'paper', spacing=13, width=2.2, angle=90, inset=7)
P.add(P.rect_mask(142, 782, 314, 806, r=6, amp=1), 'apricot')

bowl = P.shape_mask([(330, 878), (440, 878), (430, 922), (340, 922)], True, 1)
P.cut(bowl, 'paper', shadow=(5, 5))
P.texture(bowl, 'grid', 'violet_lt', spacing=8, width=1.2, inset=4)
P.add(P.ellipse_mask(385, 879, 56, 7, amp=.6), 'violet_lt')

# ---------- 前层：木架 ----------
shelf = P.rect_mask(-20, 922, 800, 966, amp=1.6)
P.cut(shelf, 'apricot', shadow=(0, 12), shadow_alpha=.4)
P.texture(shelf, 'wave', 'violet_dk', spacing=9, width=1.3, amp=2, wl=90, inset=5)
brace = P.shape_mask([(640, 966), (800, 966), (870, 1240), (780, 1240)], False, 1.6)
P.cut(brace, 'apricot', shadow=(8, 0), shadow_alpha=.35)
P.texture(brace, 'wave', 'violet_dk', spacing=10, width=1.2, amp=2, angle=74, wl=80, inset=6)

# ---------- 前层：猫（主角） ----------
body = P.shape_mask([(470, 600), (560, 572), (640, 600), (690, 690), (712, 820), (705, 912),
                     (640, 926), (520, 928), (430, 920), (405, 860), (418, 760), (440, 670)], True, 2)
P.cut(body, 'violet_dk', shadow=(10, 6), shadow_alpha=.3)
P.texture(body, 'arc', 'violet', spacing=17, width=3.2, amp=4, center=(480, 905), inset=8)
bib = P.shape_mask([(575, 590), (640, 600), (668, 700), (650, 830), (618, 900), (590, 780), (560, 650)], True, 1.6)
P.add(bib, 'paper')
P.texture(bib, 'wave', 'violet_lt', spacing=12, width=1.0, amp=2, angle=80, wl=30, inset=8)
# 尾巴沿木架前沿卷过来
tail = P.shape_mask([(430, 905), (520, 902), (610, 906), (660, 918), (650, 940), (560, 940), (470, 936), (432, 930)], True, 1)
P.cut(tail, 'violet_dk', shadow=(0, 6), shadow_alpha=.3)
P.texture(tail, 'stripe', 'violet', spacing=18, width=4, angle=100, inset=4)
# 前爪
for x in (590, 640):
    P.add(P.ellipse_mask(x, 918, 22, 10, amp=.6), 'paper')
    P.line([(x-6, 912), (x-6, 925)], 'violet_lt', 1)
    P.line([(x+6, 912), (x+6, 925)], 'violet_lt', 1)

# 头
for ex, tipx in ((545, 528), (655, 676)):
    ear = P.shape_mask([(ex-28, 488), (tipx, 418), (ex+30, 480)], False, 1)
    P.add(ear, 'violet_dk')
    P.add(P.shape_mask([(ex-14, 482), (tipx+ (4 if tipx < 600 else -4), 438), (ex+14, 478)], False, .6), 'violet_lt')
head = P.shape_mask([(520, 500), (600, 462), (680, 498), (700, 560), (668, 610), (600, 628), (532, 610), (502, 556)], True, 1.6)
P.cut(head, 'violet_dk', shadow=(8, 6), shadow_alpha=.3)
P.texture(head, 'arc', 'violet', spacing=14, width=2.4, amp=2, center=(600, 380), inset=10)
blaze = P.shape_mask([(592, 480), (610, 480), (628, 560), (650, 600), (600, 620), (550, 600), (574, 560)], True, 1.2)
P.add(blaze, 'paper')
for cx in (565, 637):
    P.add(P.ellipse_mask(cx, 548, 15, 11, amp=.4), 'apricot')
    P.add(P.ellipse_mask(cx, 548, 3.2, 9, amp=.2), 'violet_dk')
P.add(P.shape_mask([(592, 578), (610, 578), (601, 590)], False, .3), 'apricot')
P.line([(601, 590), (601, 598), (590, 604)], 'violet_dk', 1.4)
P.line([(601, 598), (612, 604)], 'violet_dk', 1.4)
for y, d in ((588, -4), (598, 2)):
    P.line([(560, y), (505, y+d)], 'paper', 1.0)
    P.line([(642, y), (697, y+d)], 'paper', 1.0)

# ---------- 框线 + 字 ----------
P.frame(34, 'paper', 1.4)
P.text('SITTING', (846, 92), 66, 'paper', TITLE, spacing=.16, anchor='ra')
P.text('PRETTY', (846, 168), 66, 'apricot', TITLE, spacing=.16, anchor='ra')
P.text('A QUIET AFTERNOON', (846, 266), 17, 'paper', SMALL, spacing=.28, anchor='ra')
P.text('ON THE SILL,', (790, 294), 17, 'paper', SMALL, spacing=.28, anchor='ra')
P.text('NO RUSH AT ALL', (846, 322), 17, 'paper', SMALL, spacing=.28, anchor='ra')

# 邮票：左上，3:4，约 20% 画宽
P.stamp(os.path.join(HERE, 'photos', 'cat.jpg'), 70, 74, w=180, angle=-3,
        postmark=('WINDOW POST', '10·17'), focus=(.6, .45))
P.top_text('wish you were here ~', (268, 300), 30, 'paper', HAND)

P.render(os.path.join(HERE, 'cat_poster.jpg'))
print('ok')
