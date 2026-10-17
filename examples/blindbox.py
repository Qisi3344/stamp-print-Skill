import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from stamp_print.stamp import *

PHOTO = os.path.join(HERE, 'photos', 'blindbox.jpg')
# 取自她发的快递箱：牛皮纸棕(主) / 夜空靛蓝(第二，月亮釉) / 草莓红(点睛) / 叶绿(单独一版)
set_palette(main=(196, 160, 118), second=(78, 98, 136), accent=(224, 96, 108),
            paper=(247, 241, 228), dkf=.55,
            extra={'leaf': (104, 146, 98)})
P = Poster(900, 1200, S=2, seed=17, misreg=1.6)
P.background('violet', waves=None)

# ---------- 后层：纸箱 + 四个格子 ----------
box = P.rect_mask(100, 350, 800, 1112, r=14, amp=1.2)
P.cut(box, 'violet_dk', (9, 11), .33)
CW, CH, GAP = 321, 352, 12
cells = [(124, 372), (124 + CW + GAP, 372), (124, 372 + CH + GAP), (124 + CW + GAP, 372 + CH + GAP)]
for x0, y0 in cells:
    P.add(P.rect_mask(x0, y0, x0 + CW, y0 + CH, r=6, amp=.8), 'violet_lt')
    # 泡沫护角
    for sx, sy, ox, oy in ((1, 1, x0, y0), (-1, 1, x0 + CW, y0), (1, -1, x0, y0 + CH), (-1, -1, x0 + CW, y0 + CH)):
        pts = [(8, 8), (62, 8), (62, 26), (26, 26), (26, 62), (8, 62)]
        P.cut(P.shape_mask([(ox + sx * a, oy + sy * b) for a, b in pts], False, .8), 'paper', (3, 4), .2)

def star(cx, cy, R, r, rot=-90):
    pts = []
    for i in range(10):
        a = math.radians(rot + i * 36); rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

# ---------- 格1（左上）：月亮小狼杯 ----------
cx, cy = cells[0][0] + CW / 2, cells[0][1] + CH / 2 + 8
P.add(P.ellipse_mask(cx + 84, cy + 4, 44, 50, amp=.8), 'moss')                 # 把手
P.add(P.ellipse_mask(cx + 84, cy + 4, 25, 31, amp=.6), 'violet_lt')
for sx in (-1, 1):                                                              # 狼耳
    ear = P.shape_mask([(cx + sx * 78, cy - 60), (cx + sx * 66, cy - 122), (cx + sx * 24, cy - 76)], False, 1)
    P.cut(ear, 'moss', (4, 5), .3)
    P.add(P.shape_mask([(cx + sx * 66, cy - 78), (cx + sx * 62, cy - 106), (cx + sx * 42, cy - 80)], False, .6), 'apricot')
body = P.rect_mask(cx - 88, cy - 82, cx + 78, cy + 84, r=30, amp=1.2)
P.cut(body, 'moss', (9, 11), .35)
P.texture(body, 'holes', 'moss_dk', spacing=24, hole=2.2, inset=12)
P.add(P.ellipse_mask(cx - 6, cy - 4, 42, 42, amp=.5), 'paper')                 # 月牙
P.add(P.ellipse_mask(cx + 12, cy - 10, 37, 37, amp=.5), 'moss')
P.add(P.ellipse_mask(cx - 6, cy - 4, 42, 42, amp=.5).point(lambda v: 0), 'paper')
for dx, dy, r in ((38, -40, 4), (-52, 34, 3), (30, 46, 3)):
    P.dot(cx + dx, cy + dy, r, 'paper')

# ---------- 格2（右上）：草莓罐 ----------
cx, cy = cells[1][0] + CW / 2, cells[1][1] + CH / 2 + 20
berry = P.shape_mask([(cx - 98, cy - 52), (cx - 66, cy - 88), (cx + 66, cy - 88), (cx + 98, cy - 52),
                      (cx + 62, cy + 62), (cx, cy + 100), (cx - 62, cy + 62)], True, 1.4)
P.cut(berry, 'apricot', (9, 11), .35)
P.texture(berry, 'holes', 'paper', spacing=26, hole=3.4, inset=14)
cap = P.shape_mask([(cx - 70, cy - 84), (cx - 40, cy - 116), (cx - 12, cy - 92), (cx + 14, cy - 122),
                    (cx + 42, cy - 92), (cx + 72, cy - 112), (cx + 66, cy - 78), (cx, cy - 66)], False, 1)
P.cut(cap, 'leaf', (4, 5), .3)
P.add(P.rect_mask(cx - 7, cy - 142, cx + 7, cy - 104, r=5, amp=.6), 'leaf')

# ---------- 格3（左下）：猫头鹰小罐（夜澜） ----------
cx, cy = cells[2][0] + CW / 2, cells[2][1] + CH / 2 + 12
for sx in (-1, 1):
    P.cut(P.shape_mask([(cx + sx * 84, cy - 52), (cx + sx * 78, cy - 126), (cx + sx * 30, cy - 92)], False, 1), 'moss', (4, 5), .3)
P.cut(P.ellipse_mask(cx, cy, 98, 112, amp=1.4), 'moss', (9, 11), .35)
belly = P.ellipse_mask(cx, cy + 44, 58, 62, amp=1)
P.add(belly, 'paper')
P.texture(belly, 'wave', 'moss', spacing=13, width=1.3, amp=1.6, angle=0, wl=30, inset=8)
for sx in (-1, 1):
    P.add(P.ellipse_mask(cx + sx * 40, cy - 34, 33, 33, amp=.6), 'paper')
    P.dot(cx + sx * 40, cy - 34, 13, 'violet_dk')
    P.dot(cx + sx * 44, cy - 39, 4, 'paper')
P.add(P.shape_mask([(cx - 11, cy - 12), (cx + 11, cy - 12), (cx, cy + 12)], False, .5), 'apricot')

# ---------- 格4（右下）：星空盘 ----------
cx, cy = cells[3][0] + CW / 2, cells[3][1] + CH / 2 + 4
P.cut(P.ellipse_mask(cx, cy + 14, 134, 104, amp=1.2), 'moss', (9, 11), .35)
night = P.ellipse_mask(cx, cy + 6, 108, 80, amp=1)
P.add(night, 'moss_dk')
P.add(P.ellipse_mask(cx - 32, cy - 6, 38, 34, amp=.4), 'paper')                 # 月牙
P.add(P.ellipse_mask(cx - 18, cy - 12, 33, 30, amp=.4), 'moss_dk')
for dx, dy, R in ((44, -30, 15), (62, 18, 10), (-20, 40, 11), (6, 22, 7)):
    P.add(P.shape_mask(star(cx + dx, cy + dy, R, R * .45), False, .4), 'paper')
P.add(P.shape_mask(star(cx + 20, cy - 8, 9, 4), False, .4), 'apricot')
for dx, dy in ((-70, -30), (-60, 40), (80, -6), (30, 50)):
    P.dot(cx + dx, cy + dy, 2.4, 'paper')

# ---------- 框线 + 字 ----------
P.frame(34, 'paper', 1.4)
P.text('BLIND BOX', (846, 70), 60, 'apricot', TITLE, spacing=.16, anchor='ra')
P.text('CERAMICS', (846, 138), 60, 'moss', TITLE, spacing=.16, anchor='ra')
P.text('FOUR LITTLE SURPRISES,', (846, 232), 17, 'violet_dk', SMALL, spacing=.28, anchor='ra')
P.text('WRAPPED IN BUBBLES,', (800, 260), 17, 'violet_dk', SMALL, spacing=.28, anchor='ra')
P.text('MADE FOR ONE MOON', (846, 288), 17, 'violet_dk', SMALL, spacing=.28, anchor='ra')

P.stamp(PHOTO, 70, 70, w=180, angle=-3, postmark=('QAMAR POST', '10·17'), focus=(.5, .5))
P.top_text("open slowly ~", (268, 104), 28, 'violet_dk', HAND)

P.render(os.path.join(HERE, 'blindbox_poster.jpg'))
print('ok')
