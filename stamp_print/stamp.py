"""邮票印花 Stamp Print —— 复古套色剪纸海报引擎（Hark 为绮思自研，2026-10-17）
纯 numpy/scipy/PIL。坐标一律按 900x1200 设计稿给，内部按 S 倍渲染。

用法见 examples/cat.py
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from scipy import ndimage

import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts') + os.sep
TITLE = F + 'AbrilFatface-Regular.ttf'      # 复古衬线大写标题
SMALL = F + 'PlayfairDisplaySC-Regular.ttf'  # 小号衬线大写短句
HAND = F + 'Caveat.ttf'                      # 英文手写批注
HAND_ZH = F + 'LongCang-Regular.ttf'         # 中文手写批注

# 四色套印（+同色系深浅）。violet 系合计约 55%，apricot ≤15%
PAL = {
    'violet':   (140, 132, 166),   # 暮色灰紫 主色
    'violet_lt': (172, 165, 192),  # 浅灰紫（同版浅网）
    'violet_dk': (86, 79, 112),    # 深灰紫（线条/阴影/深块）
    'apricot':  (236, 160, 98),    # 杏子橙 点睛
    'moss':     (132, 148, 96),    # 苔绿 第二大色
    'moss_dk':  (92, 108, 70),
    'paper':    (244, 238, 226),   # 纸白
    'sky':      (112, 148, 204),   # 哑光天空蓝（照片里标志性的蓝天用它）
    'sky_lt':   (150, 180, 222),
}
PLATE = {  # 同一块版 = 同一个错位
    'violet': 'v', 'violet_lt': 'v', 'violet_dk': 'v',
    'apricot': 'a', 'moss': 'm', 'moss_dk': 'm', 'paper': 'p', 'sky': 's', 'sky_lt': 's',
}


def catmull(pts, n=18, closed=True):
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.array, (P[i-1], P[i], P[i+1], P[i+2]))
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t*t, t*t*t
            out.append(0.5*((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t2 + (-p0+3*p1-3*p2+p3)*t3))
    if not closed:
        out.append(np.array(P[-2]))
    return np.array(out)


class Poster:
    def __init__(self, W=900, H=1200, S=2, seed=1, bg='violet', misreg=1.6):
        self.W, self.H, self.S = W, H, S
        self.rng = random.Random(seed); np.random.seed(seed)
        self.layers = []   # (mask L image, color, plate)
        r = self.rng
        self.off = {k: ((r.uniform(-1, 1))*misreg*S, (r.uniform(-1, 1))*misreg*S) for k in sorted(set(PLATE.values()))}
        self.off['p'] = (self.off['p'][0]*.4, self.off['p'][1]*.4)
        self.bg = bg

    # ---------- 基础 ----------
    def m(self):
        return Image.new('L', (self.W*self.S, self.H*self.S), 0)

    def sc(self, pts):
        return [(x*self.S, y*self.S) for x, y in pts]

    def wobble(self, pts, amp=1.6, closed=True):
        """剪刀边：沿曲线加低频起伏 + 极细抖动"""
        pts = np.array(pts, float)
        n = len(pts)
        t = np.linspace(0, 2*math.pi, n, endpoint=False)
        d = np.zeros(n)
        for k in (3, 7, 13):
            d += amp/(k**.35) * np.sin(k*t + self.rng.uniform(0, 6.28))
        d += np.random.normal(0, amp*.12, n)
        nxt = np.roll(pts, -1, 0); prv = np.roll(pts, 1, 0)
        tan = nxt - prv
        nrm = np.stack([-tan[:, 1], tan[:, 0]], 1)
        nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9)
        return pts + nrm*d[:, None]

    def shape_mask(self, pts, smooth=True, amp=1.6):
        m = self.m(); d = ImageDraw.Draw(m)
        p = catmull(pts) if smooth else np.array(pts, float)
        if smooth or amp:
            if not smooth:  # 直边也要剪刀感：先加密
                q = []
                for i in range(len(p)):
                    a, b = p[i], p[(i+1) % len(p)]
                    for t in np.linspace(0, 1, 12, endpoint=False):
                        q.append(a + (b-a)*t)
                p = np.array(q)
            p = self.wobble(p, amp)
        d.polygon(self.sc([tuple(x) for x in p]), fill=255)
        return m

    def ellipse_mask(self, cx, cy, rx, ry, amp=1.2, rot=0):
        pts = []
        for i in range(14):
            a = 2*math.pi*i/14
            x, y = rx*math.cos(a), ry*math.sin(a)
            c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            pts.append((cx + x*c - y*s, cy + x*s + y*c))
        return self.shape_mask(pts, True, amp)

    def rect_mask(self, x0, y0, x1, y1, r=0, amp=1.2):
        if r <= 0:
            return self.shape_mask([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], False, amp)
        pts = []
        for cx, cy, a0 in ((x1-r, y0+r, -90), (x1-r, y1-r, 0), (x0+r, y1-r, 90), (x0+r, y0+r, 180)):
            for k in range(4):
                a = math.radians(a0 + k*30)
                pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        return self.shape_mask(pts, False, amp)

    def add(self, mask, color, clip=None):
        if clip is not None:
            mask = ImageChops.multiply(mask, clip)
        self.layers.append((mask, color, PLATE[color]))
        return mask

    # ---------- 剪纸 ----------
    def cut(self, mask, color, shadow=(7, 9), shadow_alpha=.33):
        """一张剪纸：先铺平涂投影（深灰紫，纯色不渐变），再贴色块"""
        if shadow:
            sh = ImageChops.offset(mask, int(shadow[0]*self.S), int(shadow[1]*self.S))
            sh = sh.point(lambda v: int(v*shadow_alpha))
            self.layers.append((sh, 'violet_dk', 'v'))
        return self.add(mask, color)

    def erode(self, mask, px):
        return mask.filter(ImageFilter.MinFilter(int(px*self.S)//2*2+1))

    # ---------- 纹样（只在 clip 里，自动内缩不碰边） ----------
    def texture(self, clip, kind, color, spacing=14, width=1.6, angle=0, amp=3,
                center=None, inset=5, hole=4, wl=40):
        S = self.S
        tm = self.m(); d = ImageDraw.Draw(tm)
        box = clip.getbbox()
        if not box:
            return
        x0, y0, x1, y1 = [v/S for v in box]
        cx, cy = (x0+x1)/2, (y0+y1)/2
        R = math.hypot(x1-x0, y1-y0)
        w = max(1, int(width*S))
        ph = self.rng.uniform(0, 6.28)
        if kind in ('wave', 'stripe'):
            ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            k = -R
            while k < R:
                pts = []
                for u in np.arange(-R, R, 3):
                    v = k + (amp*math.sin(u/wl*2*math.pi + ph + k*.05) if kind == 'wave' else 0)
                    v += self.rng.uniform(-.25, .25)
                    pts.append(((cx + u*ca - v*sa)*S, (cy + u*sa + v*ca)*S))
                d.line(pts, fill=255, width=w, joint='curve')
                k += spacing
        elif kind == 'arc':   # 顺着形体的同心起伏弧线（毛流、木纹）
            ox, oy = center or (cx, cy)
            r = spacing
            while r < R*1.5:
                pts = []
                for a in np.linspace(0, 2*math.pi, int(r*1.2)+30):
                    rr = r + amp*math.sin(a*6 + ph + r*.07)
                    pts.append(((ox + rr*math.cos(a))*S, (oy + rr*math.sin(a))*S))
                d.line(pts, fill=255, width=w, joint='curve')
                r += spacing
        elif kind == 'grid':
            for x in np.arange(x0 - spacing, x1 + spacing, spacing):
                d.line([((x+self.rng.uniform(-.4, .4))*S, y0*S), ((x+self.rng.uniform(-.4, .4))*S, y1*S)], fill=255, width=w)
            for y in np.arange(y0 - spacing, y1 + spacing, spacing):
                d.line([(x0*S, (y+self.rng.uniform(-.4, .4))*S), (x1*S, (y+self.rng.uniform(-.4, .4))*S)], fill=255, width=w)
        elif kind == 'holes':  # 打孔器圆孔，大小不一
            yy = y0; row = 0
            while yy < y1:
                xx = x0 + (spacing/2 if row % 2 else 0)
                while xx < x1:
                    r = hole*self.rng.uniform(.55, 1.15)
                    jx, jy = self.rng.uniform(-2, 2), self.rng.uniform(-2, 2)
                    d.ellipse([(xx+jx-r)*S, (yy+jy-r)*S, (xx+jx+r)*S, (yy+jy+r)*S], fill=255)
                    xx += spacing
                yy += spacing*.87; row += 1
        elif kind == 'dash':   # 成组竖向短虚线
            for x in np.arange(x0, x1, spacing):
                for y in np.arange(y0, y1, spacing*1.6):
                    if self.rng.random() < .75:
                        d.line([(x*S, y*S), (x*S, (y+spacing*.7)*S)], fill=255, width=w)
        c = self.erode(clip, inset) if inset else clip
        self.add(tm, color, c)

    # ---------- 手绘细线 ----------
    def line(self, pts, color='violet_dk', width=1.8, smooth=True, jitter=.6):
        m = self.m(); d = ImageDraw.Draw(m)
        p = catmull(pts, 16, closed=False) if (smooth and len(pts) > 2) else np.array(pts, float)
        p = p + np.random.normal(0, jitter*.4, p.shape)
        # 线宽略起伏：分段画
        for i in range(len(p)-1):
            ww = width*(0.8 + 0.4*math.sin(i*.35 + self.rng.random()))
            d.line([tuple(p[i]*self.S), tuple(p[i+1]*self.S)], fill=255, width=max(1, int(ww*self.S)))
        return self.add(m, color)

    def leaf(self, base, tip, bend=0.25, width=14, color='moss', vein='moss_dk', shadow=None):
        """细长叶片：沿弯曲中线两侧收尖；可选中脉"""
        bx, by = base; tx, ty = tip
        mx, my = (bx+tx)/2, (by+ty)/2
        nx, ny = -(ty-by), (tx-bx)
        L = math.hypot(nx, ny) + 1e-9
        cx, cy = mx + nx/L*bend*L, my + ny/L*bend*L
        mid = []
        for t in np.linspace(0, 1, 14):
            x = (1-t)**2*bx + 2*(1-t)*t*cx + t*t*tx
            y = (1-t)**2*by + 2*(1-t)*t*cy + t*t*ty
            mid.append((x, y))
        mid = np.array(mid)
        tan = np.gradient(mid, axis=0); nr = np.stack([-tan[:, 1], tan[:, 0]], 1)
        nr /= np.linalg.norm(nr, axis=1, keepdims=True) + 1e-9
        prof = np.sin(np.linspace(0.15, 1, 14)*math.pi)**.7 * width/2
        prof[-1] = 0
        left = mid + nr*prof[:, None]; right = mid - nr*prof[:, None]
        poly = list(map(tuple, left)) + list(map(tuple, right[::-1]))
        mk = self.shape_mask(poly, False, .5)
        if shadow: self.cut(mk, color, shadow, .25)
        else: self.add(mk, color)
        if vein:
            self.line([tuple(p) for p in mid[1:-2]], vein, 1.1, jitter=.2)
        return mk

    def dot(self, x, y, r, color):
        return self.add(self.ellipse_mask(x, y, r, r, amp=.4), color)

    # ---------- 背景 ----------
    def background(self, color='violet', waves=('tr', 6), dots=0):
        self.add(Image.new('L', (self.W*self.S, self.H*self.S), 255), color)
        if waves:
            corner, n = waves
            self.cancel_waves(corner, n)

    def cancel_waves(self, corner='tr', n=6, color='violet_lt', length=330, gap=13, at=None):
        x0 = self.W - length - 40 if 'r' in corner else 40
        y0 = 60 if 't' in corner else self.H - 60 - n*gap
        if at: x0, y0 = at
        for i in range(n):
            pts = [(x0 + u, y0 + i*gap + 4*math.sin(u/22 + i*.3)) for u in range(0, length, 4)]
            self.line(pts, color, 2.2, smooth=False, jitter=.2)

    def frame(self, inset=34, color='paper', width=1.6):
        a, b = inset, inset
        W, H = self.W - inset, self.H - inset
        self.line([(a, b), (W, b), (W, H), (a, H), (a, b)], color, width, smooth=False, jitter=.3)

    # ---------- 邮票（小原图） ----------
    def stamp(self, photo_path, x, y, w=180, ratio=4/3, angle=-3, crop=None,
              border=11, perf=5.2, postmark=('SILL POST', '2026'), focus=(.5, .45)):
        """真实邮票比例 3:4 竖版；原图保持摄影质感。crop=(l,t,r,b) 0-1 可选"""
        S = self.S
        h = int(w*ratio)
        ph = Image.open(photo_path).convert('RGB')
        if crop:
            W0, H0 = ph.size
            ph = ph.crop((int(crop[0]*W0), int(crop[1]*H0), int(crop[2]*W0), int(crop[3]*H0)))
        iw, ih = (w-2*border)*S, (h-2*border)*S
        pw, phh = ph.size
        s = max(iw/pw, ih/phh)
        ph = ph.resize((int(pw*s)+1, int(phh*s)+1), Image.LANCZOS)
        fx = int((ph.width - iw)*focus[0]); fy = int((ph.height - ih)*focus[1])
        ph = ph.crop((fx, fy, fx+iw, fy+ih))
        card = Image.new('RGBA', (w*S, h*S), PAL['paper'] + (255,))
        card.paste(ph, (border*S, border*S))
        # 齿孔
        dm = Image.new('L', card.size, 255); dd = ImageDraw.Draw(dm)
        r = perf*S/2
        for X in np.arange(0, w*S+1, perf*S*1.75):
            for Y in (0, h*S):
                dd.ellipse([X-r, Y-r, X+r, Y+r], fill=0)
        for Y in np.arange(0, h*S+1, perf*S*1.75):
            for X in (0, w*S):
                dd.ellipse([X-r, Y-r, X+r, Y+r], fill=0)
        card.putalpha(dm)
        self._stamp = (card, x, y, angle, w, h, postmark)

    def _place_stamp(self, img):
        card, x, y, angle, w, h, pm = self._stamp
        S = self.S
        rc = card.rotate(angle, resample=Image.BICUBIC, expand=True)
        # 平涂投影
        sh = Image.new('RGBA', rc.size, PAL['violet_dk'] + (0,))
        sh.putalpha(rc.split()[3].point(lambda v: int(v*.38)))
        img.alpha_composite(sh, (int((x+6)*S), int((y+8)*S)))
        img.alpha_composite(rc, (int(x*S), int(y*S)))
        if pm:  # 半透明圆邮戳 + 波浪线，压在邮票右下角
            cx, cy, R = x + w*.86, y + h*.80, 46
            ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            col = PAL['violet_dk'] + (150,)
            for rr, ww in ((R, 2.4), (R-12, 1.4)):
                d.ellipse([(cx-rr)*S, (cy-rr)*S, (cx+rr)*S, (cy+rr)*S], outline=col, width=int(ww*S))
            f = ImageFont.truetype(SMALL, int(11*S))
            txt = '  ' + pm[0] + '  ·  '
            for i, ch in enumerate(txt*1):
                a = math.radians(-200 + i*(250/len(txt)))
                px, py = cx + (R-6.5)*math.cos(a), cy + (R-6.5)*math.sin(a)
                g = Image.new('RGBA', (int(16*S), int(16*S)), (0, 0, 0, 0))
                ImageDraw.Draw(g).text((8*S, 8*S), ch, font=f, fill=col, anchor='mm')
                g = g.rotate(-math.degrees(a) - 90, resample=Image.BICUBIC)
                ov.alpha_composite(g, (int(px*S - 8*S), int(py*S - 8*S)))
            f2 = ImageFont.truetype(SMALL, int(15*S))
            d.text((cx*S, cy*S), pm[1], font=f2, fill=col, anchor='mm')
            for i in range(4):
                pts = [((cx+R+4+u)*S, (cy-14+i*9 + 3*math.sin(u/9))*S) for u in range(0, 95, 3)]
                d.line(pts, fill=col, width=int(1.6*S))
            img.alpha_composite(ov)

    # ---------- 字 ----------
    def text(self, s, xy, size, color='paper', font=TITLE, spacing=0.0, anchor='la'):
        """spacing = 字距（em 倍数），疏排标题用 .18–.3"""
        S = self.S
        m = self.m(); d = ImageDraw.Draw(m)
        f = ImageFont.truetype(font, int(size*S))
        x, y = xy[0]*S, xy[1]*S
        if spacing == 0:
            d.text((x, y), s, font=f, fill=255, anchor=anchor)
        else:
            tw = sum(f.getlength(c) for c in s) + spacing*size*S*(len(s)-1)
            if anchor[0] == 'm': x -= tw/2
            if anchor[0] == 'r': x -= tw
            for c in s:
                d.text((x, y), c, font=f, fill=255, anchor='l' + anchor[1])
                x += f.getlength(c) + spacing*size*S
        return self.add(m, color)

    # ---------- 渲染 ----------
    def render(self, path=None, grain=.05):
        S = self.S
        W, H = self.W*S, self.H*S
        acc = np.zeros((H, W, 3), np.float32) + np.array(PAL['paper'], np.float32)
        stamp_at = getattr(self, '_stamp_index', None)
        for i, (mask, col, plate) in enumerate(self.layers):
            dx, dy = self.off[plate]
            a = np.asarray(mask, np.float32)/255.
            a = ndimage.shift(a, (dy, dx), order=1, mode='constant')
            c = np.array(PAL[col], np.float32)
            acc = acc*(1-a[..., None]) + c*a[..., None]
        # 纸纤维 + 极轻墨色不匀（不是颗粒）
        n = ndimage.gaussian_filter(np.random.normal(0, 1, (H, W)).astype(np.float32), 1.2*S)
        n2 = ndimage.gaussian_filter(np.random.normal(0, 1, (H//8, W//8)).astype(np.float32), 6)
        n2 = np.array(Image.fromarray(n2).resize((W, H), Image.BILINEAR))
        acc *= (1 + grain*.6*n[..., None]/n.std() * .25 + grain*n2[..., None]/n2.std()*.35)
        fib = np.zeros((H, W), np.float32)
        img = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8)).convert('RGBA')
        dfib = ImageDraw.Draw(Image.fromarray(fib))
        if hasattr(self, '_stamp'):
            self._place_stamp(img)
        for (mask, col, plate) in getattr(self, '_top', []):
            dx, dy = self.off[plate]
            lay = Image.new('RGBA', img.size, PAL[col] + (0,))
            lay.putalpha(ImageChops.offset(mask, int(dx), int(dy)))
            img.alpha_composite(lay)
        img = img.convert('RGB')
        if path:
            img.save(path, quality=95)
        return img

    def top_text(self, *a, **k):
        """压在邮票上面的字（手写批注）"""
        n = len(self.layers)
        self.text(*a, **k)
        lay = self.layers.pop()
        self._top = getattr(self, '_top', []) + [lay]


def palette_from_photo(path, k=6, sat=.72, light=(.30, .82), show=True):
    """从照片取主色（k-means），压成哑光套色。返回 [(rgb, 占比)]，按占比排序。
    之后由人挑：主色(约55%,+浅/深两档)、第二色、点睛色(≤15%)、纸白，写进 PAL。"""
    import colorsys
    im = Image.open(path).convert('RGB'); im.thumbnail((160, 160))
    X = np.asarray(im, np.float32).reshape(-1, 3)
    rng = np.random.default_rng(0); C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(25):
        lab = ((X[:, None] - C[None])**2).sum(2).argmin(1)
        C = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(k)])
    out = []
    for i in np.argsort(-np.bincount(lab, minlength=k)):
        h, l, s = colorsys.rgb_to_hls(*(C[i]/255))
        l = min(max(l, light[0]), light[1]); s = s*sat
        rgb = tuple(int(v*255) for v in colorsys.hls_to_rgb(h, l, s))
        out.append((rgb, round(float((lab == i).mean()), 3)))
    if show:
        for rgb, p in out: print(rgb, p)
    return out


def set_palette(main, second, accent, paper=(244, 238, 226), extra=None, dkf=.62):
    """main/second/accent 给 rgb；自动派生浅/深档。名字沿用 violet*/moss*/apricot 以兼容旧脚本"""
    def sh(c, f): return tuple(int(max(0, min(255, v*f + (255 if f > 1 else 0)*(0)))) for v in c)
    lt = lambda c: tuple(int(v + (255-v)*.28) for v in c)
    dk = lambda c: tuple(int(v*dkf) for v in c)
    PAL.update({'violet': main, 'violet_lt': lt(main), 'violet_dk': dk(main),
                'moss': second, 'moss_dk': dk(second), 'apricot': accent, 'paper': paper})
    if extra:
        # extra = {'red': (rgb), 'red_lt': (rgb)}；同前缀共用一块版
        for k, v in extra.items():
            PAL[k] = v; PLATE[k] = 'x_' + k.split('_')[0]
