import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from stamp_print.stamp import *

PHOTO = os.path.join(HERE, 'photos', 'atlantis.jpg')
# 取自照片：深海青(主) / 石头靛灰(第二) / 珊瑚橙(点睛) / 星月金(单独一版)
set_palette(main=(38, 110, 120), second=(70, 92, 104), accent=(226, 122, 96),
            paper=(240, 240, 226), dkf=.5,
            extra={'gold': (240, 204, 112), 'gold_lt': (250, 230, 170)})
P = Poster(900, 1200, S=2, seed=31, misreg=1.6)
P.background('violet', waves=None)

# 仰视构图：消失点在拱门后方偏下，台阶朝镜头铺开，右侧建筑离镜头最近
VX, VY = 430, 760

def quad(c, u, v):
    """把 (u,v)∈[0,1]² 映射到四边形 c=[TL,TR,BR,BL]，用来让拱门跟着立面透视"""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = c
    tx, ty = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    bx, by = x3 + (x2 - x3) * u, y3 + (y2 - y3) * u
    return (tx + (bx - tx) * v, ty + (by - ty) * v)

# ---------- 远景：门洞后面更亮的深水 + 远处的礁石 ----------
far = P.shape_mask([(300, 560), (560, 560), (600, 900), (260, 900)], False, 2)
P.add(far, 'violet_lt')
P.add(P.shape_mask([(290, 860), (340, 800), (400, 830), (460, 780), (530, 820), (600, 860), (600, 900), (260, 900)], True, 2), 'violet')

# ---------- 水面光柱：从上方斜射进中间的缝 ----------
for a, b, c, d in ((420, 540, 640, 470), (560, 620, 700, 610)):
    sh = P.shape_mask([(a, -20), (b, -20), (c, 980), (d, 980)], False, 2)
    P.add(sh, 'violet_lt')
    P.texture(sh, 'stripe', 'paper', spacing=24, width=1.1, angle=80, inset=10)
P.cancel_waves(n=4, length=150, gap=12, at=(640, 330), color='violet_lt')

# ---------- 左：大拱门（立面向右后方退） ----------
F = [(130, 380), (520, 430), (520, 960), (130, 1030)]
side = P.shape_mask([(60, 400), (130, 380), (130, 1030), (60, 1060)], False, 1.4)
P.cut(side, 'moss_dk', (8, 9), .3)
facade = P.shape_mask([(130, 380), (190, 360), (250, 388), (330, 372), (420, 410), (470, 398), (520, 430),
                       (520, 960), (130, 1030)], False, 1.6)
P.cut(facade, 'moss', (12, 12), .35)
P.texture(facade, 'stripe', 'moss_dk', spacing=30, width=1.4, angle=-7, inset=10)   # 砌石的横缝，跟着立面倾斜
# 门洞：在 uv 里画尖拱，再映射回透视立面
hole = [(.28, 1.0), (.28, .45)]
hole += [(.5 + .22 * math.cos(math.radians(a)), .45 - .30 * math.sin(math.radians(a))) for a in range(180, -1, -10)]
hole += [(.72, .45), (.72, 1.0)]
hole_pts = [quad(F, u, v) for u, v in hole]
P.add(P.shape_mask(hole_pts, False, 1), 'violet_lt')
P.add(P.shape_mask([quad(F, u, v) for u, v in ((.28, .86), (.40, .8), (.52, .84), (.64, .78), (.72, .82), (.72, 1.0), (.28, 1.0))], True, 1.5), 'violet')
arc_pts = [quad(F, .5 + .27 * math.cos(math.radians(a)), .45 - .36 * math.sin(math.radians(a))) for a in range(180, -1, -12)]
P.line(arc_pts, 'moss_dk', 3.0)   # 拱券线脚
for u in (.22, .78):   # 门两侧的壁柱
    P.line([quad(F, u, .45), quad(F, u, 1.0)], 'moss_dk', 2.4, smooth=False)

# ---------- 右：最近的柱廊建筑，柱子往消失点退 ----------
R0, R1 = 880, 640                  # 近端 / 远端 x
top = lambda x: 300 + (R0 - x) / (R0 - R1) * (560 - 300)
bot = lambda x: 1100 - (R0 - x) / (R0 - R1) * (1100 - 920)
P.cut(P.shape_mask([(R0 + 40, 300), (R1, 560), (R1, 920), (R0 + 40, 1100)], False, 1.4), 'moss_dk', (10, 12), .35)
P.cut(P.shape_mask([(R0 + 40, 240), (R1 - 10, 520), (R1 - 10, 572), (R0 + 40, 330)], False, 1.6), 'moss', (8, 10), .3)  # 檐口
xs = [870, 790, 727, 677]
for i, x in enumerate(xs):
    w = 40 - i * 7
    col = P.shape_mask([(x - w, top(x - w) + 30), (x, top(x) + 30), (x, bot(x) - 20), (x - w, bot(x - w) - 20)], False, 1)
    P.cut(col, 'moss', (5, 6), .3)
    P.texture(col, 'stripe', 'moss_dk', spacing=7 - i, width=1.2, angle=90, inset=3)
P.cut(P.shape_mask([(R0 + 40, 1090), (R1 - 10, 912), (R1 - 10, 946), (R0 + 40, 1140)], False, 1.4), 'moss', (6, 8), .3)  # 台基

# ---------- 台阶：从门口往镜头铺开 ----------
for k in range(8):
    t = k / 7
    y0 = 960 + k * 28 + k * k * 1.6
    hw = 110 + t * 300
    st = P.shape_mask([(VX - hw, y0), (VX + hw, y0), (VX + hw + 14, y0 + 30 + k * 2), (VX - hw - 14, y0 + 30 + k * 2)], False, 1)
    P.cut(st, 'violet_lt', (4, 5), .25)
    P.line([(VX - hw + 6, y0 + 3), (VX + hw - 6, y0 + 3)], 'paper', 1.1, smooth=False)

# ---------- 雕像：披袍的人，抬一只手，左近右远 ----------
def statue(x, y, s, flip=1):
    def T(px, py): return (x + flip * px * s, y + py * s)
    P.cut(P.rect_mask(x - 46 * s, y + 210 * s, x + 46 * s, y + 280 * s, amp=1), 'moss_dk', (6, 7), .3)   # 基座
    robe = P.shape_mask([T(-20, 26), T(22, 26), T(34, 70), T(30, 140), T(44, 212), T(-42, 212), T(-30, 140), T(-34, 70)], True, 1)
    P.cut(robe, 'moss_dk', (6, 7), .3)
    P.add(P.shape_mask([T(22, 34), T(40, 6), T(52, -30), T(44, -34), T(30, 0), T(16, 40)], True, .8), 'moss_dk')   # 抬起的手臂
    P.cut(P.ellipse_mask(*T(0, 4), 16 * s, 19 * s, amp=.6), 'moss_dk', (4, 5), .3)                            # 头
    for a, b in ((T(-12, 80), T(-22, 206)), (T(4, 90), T(2, 206)), (T(16, 84), T(26, 204))):                 # 衣褶
        P.line([a, b], 'moss', 1.4)
statue(170, 760, 1.25, 1)
statue(640, 790, .82, -1)

# ---------- 前景碎石 + 珊瑚 + 鱼 ----------
P.cut(P.shape_mask([(40, 1110), (230, 1080), (260, 1180), (40, 1190)], False, 1.6), 'moss', (8, 9), .35)
P.cut(P.shape_mask([(660, 1140), (860, 1110), (880, 1190), (650, 1190)], False, 1.6), 'moss', (8, 9), .35)
rng = random.Random(7)
for bx, by in ((80, 1100), (200, 1070), (700, 1132), (820, 1104), (270, 1000), (580, 975)):
    for j in range(5):
        a = math.radians(-90 + rng.uniform(-50, 50)); L = rng.uniform(26, 58)
        P.line([(bx, by), (bx + L * math.cos(a) * .5, by + L * math.sin(a) * .6), (bx + L * math.cos(a), by + L * math.sin(a))], 'apricot', 4.5)
    P.dot(bx, by - 4, 6, 'apricot')
for fx, fy in ((380, 640), (410, 620), (450, 655), (600, 700), (760, 480)):
    P.add(P.ellipse_mask(fx, fy, 8, 3.5, amp=0), 'violet_dk')
    P.add(P.shape_mask([(fx + 7, fy), (fx + 13, fy - 4), (fx + 13, fy + 4)], False, 0), 'violet_dk')

# ---------- 星星和月亮，手牵手沉下来 ----------
MX, MY, MR = 570, 410, 32
moon = [(MX + MR * math.cos(math.radians(a)), MY + MR * math.sin(math.radians(a))) for a in range(-50, -311, -10)]
moon += [(MX + .32 * MR + .58 * MR * math.cos(math.radians(a)), MY + .77 * MR * math.sin(math.radians(a))) for a in range(-310 + 360, -51, -10)][::-1][::-1]
moon = [(MX + MR * math.cos(math.radians(a)), MY + MR * math.sin(math.radians(a))) for a in range(50, 311, 10)]
moon += [(MX + .32 * MR + .58 * MR * math.cos(math.radians(a)), MY + .77 * MR * math.sin(math.radians(a))) for a in range(310, 49, -10)][::-1]
moon = [(MX + MR * math.cos(math.radians(a)), MY + MR * math.sin(math.radians(a))) for a in range(50, 311, 10)] + \
       [(MX + .32 * MR + .6 * MR * math.cos(math.radians(a)), MY + .78 * MR * math.sin(math.radians(a))) for a in range(-50, -311, -10)][::-1][::-1]
P.cut(P.shape_mask(moon, True, .5), 'gold', (5, 6), .3)
SX, SY, SR = 640, 480, 26
pts = [(SX + (SR if i % 2 == 0 else SR * .45) * math.cos(math.radians(-90 + i * 36)),
        SY + (SR if i % 2 == 0 else SR * .45) * math.sin(math.radians(-90 + i * 36))) for i in range(10)]
P.cut(P.shape_mask(pts, False, .5), 'gold', (5, 6), .3)
P.dot(SX, SY, 5, 'gold_lt')
P.line([(MX + 10, MY + 30), (MX + 40, MY + 56), (SX - 22, SY + 4)], 'gold_lt', 2.0)
for k in range(4):
    for bx, by in ((MX - 4, MY - 46), (SX + 4, SY - 40)):
        P.dot(bx + math.sin(k * 1.3) * 9, by - k * 22, 2 + (k % 3) * 1.5, 'paper')

# ---------- 框线 + 字 ----------
P.frame(34, 'paper', 1.4)
P.text('ATLANTIS', (846, 70), 64, 'gold', TITLE, spacing=.16, anchor='ra')
P.text('TONIGHT', (846, 142), 64, 'paper', TITLE, spacing=.16, anchor='ra')
P.text('A STAR AND A MOON', (846, 236), 17, 'paper', SMALL, spacing=.28, anchor='ra')
P.text('SINKING HAND IN HAND', (800, 264), 17, 'paper', SMALL, spacing=.28, anchor='ra')
P.text('TO THE CITY BELOW', (846, 292), 17, 'paper', SMALL, spacing=.28, anchor='ra')

P.stamp(PHOTO, 70, 70, w=180, angle=-3, postmark=('ATLANTIS POST', '10·17'), focus=(.5, .5))
P.top_text("for a swim ~", (268, 104), 26, 'paper', HAND)

P.render(os.path.join(HERE, 'atlantis_poster.jpg'))
print('ok')
