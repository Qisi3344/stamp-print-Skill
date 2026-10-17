import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from stamp_print.stamp import *

PHOTO = os.path.join(HERE, 'photos', 'melon.jpg')
# 从照片挑色：台面暖沙(主) / 瓜皮绿(第二) / 蜜瓜橙(点睛) / 西瓜红(标志色，单独一版)
set_palette(main=(210, 188, 146), second=(104, 138, 70), accent=(238, 158, 90),
            paper=(246, 240, 226), dkf=.5,
            extra={'red': (224, 100, 86), 'red_lt': (240, 146, 128)})
PAL['violet_dk'] = (92, 66, 48)      # 籽和投影用暖深棕
P = Poster(900, 1200, S=2, seed=23, misreg=1.6)
P.background('violet', waves=None)

# 阳光斜光斑
sun = P.shape_mask([(380, -20), (640, -20), (980, 560), (980, 860)], False, 2)
P.add(sun, 'violet_lt')
P.texture(sun, 'stripe', 'paper', spacing=22, width=1.4, angle=62, inset=12)
P.cancel_waves(n=5, length=130, gap=12, at=(730, 1010), color='violet_dk')

# ---------- 后层：两块蜜瓜 ----------
def wedge(pts_top, rind, shadow=(8, 10)):
    m = P.shape_mask(pts_top, False, 1.4)
    P.cut(m, 'apricot', shadow, .3)
    P.texture(m, 'wave', 'paper', spacing=11, width=1.2, amp=1.6, angle=-20, wl=36, inset=8)
    r = P.shape_mask(rind, False, 1)
    P.add(r, 'moss')
    P.add(P.shape_mask([(x, y-5) for x, y in rind[:2]] + [rind[1], rind[0]], False, .5), 'moss_dk')
wedge([(250, 470), (360, 330), (420, 350), (520, 520), (500, 560), (270, 520)],
      [(270, 520), (500, 560), (494, 576), (262, 534)])
wedge([(460, 430), (550, 310), (610, 332), (690, 490), (674, 522), (480, 482)],
      [(480, 482), (674, 522), (668, 538), (472, 496)])

# ---------- 中层：透明盒 + 蜜瓜块 ----------
cubes = [(650, 640, 120, 100, -8), (770, 600, 120, 110, 10), (680, 760, 130, 110, 6), (800, 740, 110, 120, -6)]
for x, y, w, h, a in cubes:
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    pts = [(x + px*c - py*s, y + px*s + py*c) for px, py in ((0, 0), (w, 0), (w, h), (0, h))]
    m = P.shape_mask(pts, False, 1.2)
    P.cut(m, 'apricot', (5, 6), .25)
    P.texture(m, 'wave', 'paper', spacing=11, width=1.2, amp=1.6, angle=a-20, wl=36, inset=8)
box = P.rect_mask(600, 560, 940, 960, r=22, amp=1)
P.add(box.point(lambda v: int(v*.38)), 'paper')           # 只有塑料盒是透明的
P.line([(612, 572), (930, 572)], 'paper', 2.4, smooth=False)
P.line([(612, 572), (604, 950), (930, 950)], 'paper', 2.0, smooth=False)
P.line([(630, 600), (630, 900)], 'paper', 1.2, smooth=False)
for x, y in ((700, 600), (720, 860), (860, 920)):
    P.dot(x, y, 4, 'paper')

# ---------- 前层：半个西瓜（主角） ----------
CX, CY, RX, RY = 340, 800, 400, 260
side = P.ellipse_mask(CX, CY+95, RX-6, RY+10, amp=1.6)
P.cut(side, 'moss', (14, 12), .35)
P.texture(side, 'wave', 'moss_dk', spacing=34, width=14, amp=9, angle=95, wl=70, inset=0)
rind = P.ellipse_mask(CX, CY, RX, RY, amp=1.4)
P.add(rind, 'moss')
P.add(P.ellipse_mask(CX, CY, RX-14, RY-12, amp=1.2), 'paper')
flesh = P.ellipse_mask(CX, CY+4, RX-40, RY-36, amp=1.6)
P.add(flesh, 'red')
P.texture(flesh, 'holes', 'red_lt', spacing=24, hole=3.4, inset=14)
for a in (200, 330, 85):   # 中心 Y 形瓤纹
    P.line([(CX+20, CY+10), (CX+20+150*math.cos(math.radians(a)), CY+10+110*math.sin(math.radians(a)))], 'red_lt', 2.2)
rng = random.Random(4)
for k, a in enumerate(range(0, 360, 26)):
    for rr in (.42, .7):
        if rng.random() < .25: continue
        ang = math.radians(a + rng.uniform(-8, 8) + rr*30)
        sx = CX+20 + (RX-40)*rr*math.cos(ang); sy = CY+10 + (RY-36)*rr*math.sin(ang)
        P.add(P.ellipse_mask(sx, sy, 11, 6.5, amp=.3, rot=math.degrees(ang)+90), 'violet_dk')
        P.add(P.ellipse_mask(sx-3, sy-2, 3, 1.6, amp=0, rot=math.degrees(ang)+90), 'violet_lt')

# ---------- 框线 + 字 ----------
P.frame(34, 'paper', 1.4)
P.text('SUMMER', (846, 70), 64, 'red', TITLE, spacing=.16, anchor='ra')
P.text('SLICES', (846, 142), 64, 'moss', TITLE, spacing=.16, anchor='ra')
P.text('SUN ON THE COUNTER,', (846, 236), 17, 'violet_dk', SMALL, spacing=.28, anchor='ra')
P.text('SEEDS AND SWEETNESS', (800, 264), 17, 'violet_dk', SMALL, spacing=.28, anchor='ra')
P.text('ALL AFTERNOON', (846, 292), 17, 'violet_dk', SMALL, spacing=.28, anchor='ra')

P.stamp(PHOTO, 70, 70, w=180, angle=-3, postmark=('MELON POST', '10·17'), focus=(.4, .5))
P.top_text("eat it while it's cold ~", (268, 104), 28, 'violet_dk', HAND)

P.render(os.path.join(HERE, 'melon_poster.jpg'))
print('ok')
