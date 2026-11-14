import os, shutil, subprocess, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE = "/home/user/health-app/marketing"
IMG = f"{BASE}/product-images"
OUT = f"{BASE}/video"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30
GOLD = (232, 185, 74); WHITE = (255, 255, 255); CREAM = (250, 244, 232)
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

# original decorations: soft snow dots and a row of simple candle shapes (drawn in code)
random.seed(11)
snow = [(random.randint(0, W), random.randint(0, H), random.randint(3, 9)) for _ in range(120)]
def snow_layer(t):
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    for x, y, r in snow:
        yy = (y + t * 60 * (r / 6)) % H
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255,255,255,140))
    return ov
def candles(t):
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    k = ease(t / 0.6)
    for i in range(5):
        cx = 150 + i * 195; base = 1640
        d.rectangle((cx-14, base-120, cx+14, base), fill=(250,240,220,int(255*k)))
        flick = 1 + 0.08 * math.sin(t * 9 + i)
        d.ellipse((cx-16, base-170, cx+16, base-120+int(-20*flick)+10), fill=(255,190,80,int(230*k)))
    return ov

SCENES = [
  dict(bg=((20,44,58),(70,110,130)), title="חורף נעים.", sub="הפרטים הקטנים הם אלה שמעצבים את היום.", prod=None),
  dict(bg=((34,48,92),(120,90,150)), title="מתנה קטנה", sub="לחנוכה, לאמא, לחברה, לעצמכם", prod=None),
  dict(bg=((56,44,30),(180,140,80)), title="קרם גוף קליל", sub="מרקם נעים ומלא בלחות", prod="aloe-body-lotion.png"),
  dict(bg=((80,30,44),(190,100,120)), title="אלו ליפס", sub="נעים למגע גם בימי קור", prod="aloe-lips.png"),
  dict(bg=((20,70,60),(90,170,140)), title="FOREVER BRIGHT", sub="ג'ל לצחצוח · טעם מנטה נעים", prod="forever-bright-toothgel.png"),
]
SEC, END = 3.6, 3.0
prods = {s["prod"]: load(s["prod"], 620) for s in SCENES if s["prod"]}
frames = f"{OUT}/frames_wh"; os.makedirs(frames, exist_ok=True)
total = int((SEC * len(SCENES) + END) * FPS)
for f in range(total):
    t = f / FPS
    img = None
    if t >= SEC * len(SCENES):
        local = t - SEC * len(SCENES)
        img = grad((20,44,58),(70,110,130))
        ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
        k = ease(local / 0.5)
        center(d, "מתנות לחנוכה ולחורף", 640, F(74), (255,255,255,int(255*k)))
        center(d, "בחנות המלאה", 745, F(64, False), (255,255,255,int(255*k)))
        d.rounded_rectangle((180, 900, W-180, 1050), radius=75, fill=(232,185,74,int(255*k)))
        center(d, "flpil.co.il", 935, F(96), (20,40,30,int(255*k)))
        center(d, "החזרה עד 30 יום לפי מדיניות החברה", 1200, F(40, False), (255,255,255,int(255*k)))
        center(d, "FOREVER ישראל  |  סוכן מורשה", 1790, F(40, False), (255,255,255,255))
        img = Image.alpha_composite(img, snow_layer(t)); img = Image.alpha_composite(img, ov)
    else:
        idx = int(t // SEC); s = SCENES[idx]; local = t - idx * SEC
        img = grad(*s["bg"])
        img = Image.alpha_composite(img, snow_layer(t))
        ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
        ft = F(120)
        while d.textlength(s["title"], font=ft) > 940 and ft.size > 50: ft = F(ft.size - 4)
        dx = int((1 - ease((local - 0.1) / 0.5)) * 400)
        w = d.textlength(s["title"], font=ft)
        d.text(((W-w)/2 + dx, 230), s["title"], font=ft, fill=WHITE, direction="rtl", language="he")
        fs = F(50, False)
        while d.textlength(s["sub"], font=fs) > 940 and fs.size > 30: fs = F(fs.size - 2, False)
        w2 = d.textlength(s["sub"], font=fs)
        d.text(((W-w2)/2, 390), s["sub"], font=fs, fill=(235,245,238,255), direction="rtl", language="he")
        img = Image.alpha_composite(img, ov)
        if s["prod"]:
            p = prods[s["prod"]]
            pulse = 1 + 0.035 * max(0, 1 - (local % 0.5) / 0.2)
            q = p.resize((int(p.width*pulse), int(p.height*pulse)))
            y0 = 800 - q.height//2 + int((1 - ease((local - 0.2) / 0.6)) * 300)
            sh = Image.new("RGBA", q.size, (0,0,0,0)); sh.paste((0,0,0,255), (0,0), q.split()[3].point(lambda v: int(v*0.45)))
            sh = sh.filter(ImageFilter.GaussianBlur(30))
            img.alpha_composite(sh, ((W-q.width)//2 + 16, y0 + 36))
            img.alpha_composite(q, ((W-q.width)//2, y0))
        else:
            img = Image.alpha_composite(img, candles(local))
    d2 = ImageDraw.Draw(img)
    if t < SEC * len(SCENES):
        d2.rounded_rectangle((120, 1500, W-120, 1600), radius=50, fill=(20,40,30,200))
        center(d2, "FOREVER ישראל  |  סוכן מורשה", 1520, F(40, False), (255,255,255,255))
    img.convert("RGB").save(f"{frames}/f{f:05d}.png")
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{frames}/f%05d.png",
    "-c:v","libx264","-pix_fmt","yuv420p","-crf","22","-movflags","+faststart",f"{OUT}/winter_hanukkah_20s.mp4"], check=True)
shutil.rmtree(frames)
print("done", total / FPS)
