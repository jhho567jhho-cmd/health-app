import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE = "/home/user/health-app/marketing"
IMG = f"{BASE}/product-images"
OUT = f"{BASE}/video"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30
WHITE = (255,255,255); INK = (30,40,34); GOLD = (232,185,74)
def F(s, b=True): return ImageFont.truetype(FB if b else FR, s)
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def grad(top, bot):
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g.resize((W, H)).convert("RGBA")
def center(d, text, y, font, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill, direction="rtl", language="he")
def load(name, size):
    p = Image.open(f"{IMG}/{name}").convert("RGBA"); p.thumbnail((size, size)); return p

# original tote bag drawn in code: rounded body, handles, zip line
def bag_layer():
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    x0, y0, x1, y1 = 190, 1080, 890, 1640
    d.arc((330, 860, 750, 1200), start=180, end=360, fill=(245,236,220,255), width=34)
    d.rounded_rectangle((x0, y0, x1, y1), radius=60, fill=(245,236,220,255))
    d.line((x0+40, y0+60, x1-40, y0+60), fill=(200,185,160,255), width=6)
    d.rectangle((x0+40, y0+100, x1-40, y0+160), fill=(214,198,172,255))
    return ov

prods = [("forever-bright-toothgel.png", "ג'ל שיניים", 360),
         ("aloe-ever-shield-deodorant-nobadge.png", "דאודורנט", 340),
         ("aloe-lips.png", "שפתון", 420)]
pimgs = [load(p, s) for p, _, s in prods]
frames = f"{OUT}/frames_bag"; os.makedirs(frames, exist_ok=True)
bag = bag_layer()
TOTAL = 12 * FPS
for f in range(TOTAL):
    t = f / FPS
    img = grad((36,70,60),(150,200,180))
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    if t < 2.5:
        center(d, "מה יש בתיק שלכם", 380, F(92), WHITE)
        center(d, "בבוקר?", 500, F(92), GOLD)
    img = Image.alpha_composite(img, ov)
    if t >= 2.0:
        # products rise out of the bag one by one
        for i, (p, label, _) in enumerate(prods):
            start = 2.0 + i * 1.1
            k = ease((t - start) / 0.7)
            if k <= 0: continue
            q = pimgs[i]
            cx = W // 2 + (-260 if i == 0 else 260 if i == 2 else 0)
            y_top = 1340 - int(k * (q.height * 0.75 + 220)) if i != 1 else 1340 - int(k * (q.height * 0.8 + 260))
            if i == 0: y_top = 1000 - int(k * 40)
            layer = Image.new("RGBA", (W, H), (0,0,0,0))
            layer.paste(q, (cx - q.width//2, y_top - q.height//2), q)
            img = Image.alpha_composite(img, layer)
            tl = ImageDraw.Draw(img)
            fl = F(44, False)
            w = tl.textlength(label, font=fl)
            tl.text((cx - w/2, y_top + q.height//2 + 8), label, font=fl, fill=WHITE, direction="rtl", language="he")
        img = Image.alpha_composite(img, bag)
    if t >= 8.0:
        k = ease((t - 8.0) / 0.5)
        ov2 = Image.new("RGBA", (W, H), (0,0,0,0)); d2 = ImageDraw.Draw(ov2)
        center(d2, "כל המבחר בחנות", 260, F(84), (255,255,255,int(255*k)))
        d2.rounded_rectangle((180, 380, W-180, 530), radius=75, fill=(232,185,74,int(255*k)))
        center(d2, "flpil.co.il", 415, F(92), (20,40,30,int(255*k)))
        img = Image.alpha_composite(img, ov2)
    d3 = ImageDraw.Draw(img)
    d3.rounded_rectangle((120, 1700, W-120, 1790), radius=45, fill=(20,40,30,200))
    center(d3, "FOREVER ישראל  |  סוכן מורשה", 1716, F(38, False), WHITE)
    img.convert("RGB").save(f"{frames}/f{f:05d}.png")
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{frames}/f%05d.png",
    "-c:v","libx264","-pix_fmt","yuv420p","-crf","22","-movflags","+faststart",f"{OUT}/bag_12s.mp4"], check=True)
shutil.rmtree(frames)
print("done")
