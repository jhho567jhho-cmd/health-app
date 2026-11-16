import os, shutil, subprocess, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE = "/home/user/health-app/marketing"
IMG = f"{BASE}/product-images"; OUT = f"{BASE}/video"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30
GOLD = (232,185,74); WHITE = (255,255,255)
def F(s, b=True): return ImageFont.truetype(FB if b else FR, s)
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def grad(top, bot):
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1); g.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * (t ** 1.1)) for i in range(3)))
    return g.resize((W, H)).convert("RGBA")
def center(d, text, y, font, fill):
    w = d.textlength(text, font=font); d.text(((W - w) / 2, y), text, font=font, fill=fill, direction="rtl", language="he")
def fit(d, text, size, bold=True, max_w=940):
    f = F(size, bold)
    while d.textlength(text, font=f) > max_w and f.size > 30: f = F(f.size - 2, bold)
    return f
prod = Image.open(f"{IMG}/aloe-lips.png").convert("RGBA"); prod.thumbnail((860, 860))
# soft floor reflection of the product
refl = prod.transpose(Image.FLIP_TOP_BOTTOM).point(lambda v: v)
refl_a = refl.split()[3].point(lambda v: int(v * 0.18))
refl.putalpha(refl_a)
refl = refl.filter(ImageFilter.GaussianBlur(6))
SC = [
 (2.6, ((74,26,40),(176,84,104)), "השפתיים מדברות בשקט.", "מרקם נעים, בכל מקום"),
 (3.0, ((52,20,32),(150,70,90)), "אלו ליפס", "שפתון עם אלוורה ושעווה"),
 (3.4, ((34,16,24),(110,52,70)), "יש עוד הרבה במבחר", "כל המבחר בחנות"),
]
frames = f"{OUT}/frames_lp"; os.makedirs(frames, exist_ok=True)
random.seed(3)
dots = [(random.randint(0,W), random.randint(0,H), random.randint(2,5)) for _ in range(70)]
TOTAL = 9 * FPS
for f in range(TOTAL):
    t = f / FPS
    start = 0.0
    for dur, (top, bot), title, sub in SC:
        if t < start + dur: break
        start += dur
    local = t - start
    img = grad(top, bot)
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    for x, y, r in dots:
        yy = (y + t * 18 * (r/3)) % H
        d.ellipse((x-r, yy-r, x+r, yy+r), fill=(255,255,255,70))
    img = Image.alpha_composite(img, ov)
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    dx = int((1 - ease((local - 0.1) / 0.5)) * 360)
    ft = fit(d, title, 100)
    w = d.textlength(title, font=ft); d.text(((W-w)/2 + dx, 250), title, font=ft, fill=WHITE, direction="rtl", language="he")
    d.line((W/2 - 110, 390, W/2 + 110, 390), fill=GOLD + (255,), width=4)
    fs = fit(d, sub, 48, bold=False)
    w2 = d.textlength(sub, font=fs); d.text(((W-w2)/2, 420), sub, font=fs, fill=(250,232,236,255), direction="rtl", language="he")
    img = Image.alpha_composite(img, ov)
    if start < 5.6:
        s = 1 + 0.025 * max(0, 1 - (local % 0.5) / 0.2)
        q = prod.resize((int(prod.width*s), int(prod.height*s)))
        y0 = 860 - q.height // 2
        sh = Image.new("RGBA", q.size, (0,0,0,0)); sh.paste((0,0,0,255), (0,0), q.split()[3].point(lambda v: int(v*0.42)))
        sh = sh.filter(ImageFilter.GaussianBlur(28))
        lay = Image.new("RGBA", (W, H), (0,0,0,0))
        lay.paste(sh, ((W-q.width)//2 + 14, y0 + 40), sh)
        lay.paste(q, ((W-q.width)//2, y0), q)
        rr = refl.resize(q.size)
        lay.paste(rr, ((W-q.width)//2, y0 + q.height), rr)
        img = Image.alpha_composite(img, lay)
    if t >= 5.6:
        k = ease((t - 5.6) / 0.5)
        ov2 = Image.new("RGBA", (W, H), (0,0,0,0)); d2 = ImageDraw.Draw(ov2)
        d2.rounded_rectangle((150, 1290, W-150, 1470), radius=90, fill=(232,185,74,int(255*k)))
        center(d2, "כל המבחר בחנות", 1318, F(64), (30,20,24,int(255*k)))
        center(d2, "flpil.co.il", 1398, F(54, False), (30,20,24,int(255*k)))
        img = Image.alpha_composite(img, ov2)
    d3 = ImageDraw.Draw(img)
    center(d3, "החזרה עד 30 יום לפי מדיניות החברה", 1600, F(36, False), WHITE)
    d3.rounded_rectangle((120, 1700, W-120, 1790), radius=45, fill=(20,20,24,200))
    center(d3, "סוכן מורשה", 1716, F(38, False), WHITE)
    img.convert("RGB").save(f"{frames}/f{f:05d}.png")
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{frames}/f%05d.png",
    "-c:v","libx264","-pix_fmt","yuv420p","-crf","21","-movflags","+faststart",f"{OUT}/lips_polished_9s.mp4"], check=True)
shutil.rmtree(frames); print("done")
