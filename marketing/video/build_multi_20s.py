import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE = "/home/user/health-app/marketing"
IMG = f"{BASE}/product-images"
OUT = f"{BASE}/video"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30
GOLD = (232, 185, 74); WHITE = (255, 255, 255)
def F(s, b=True): return ImageFont.truetype(FB if b else FR, s)
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

SCENES = [
  dict(bg=((14,48,38),(60,130,100)), prod="forever-bright-toothgel.png", title="FOREVER BRIGHT", sub="ג'ל לצחצוח שיניים · ללא פלואוריד", size=760),
  dict(bg=((70,24,36),(190,90,110)), prod="aloe-lips.png", title="אלו ליפס", sub="שפתון עם אלוורה ושעווה · מרקם נעים למגע", size=900),
  dict(bg=((18,36,60),(70,120,170)), prod="aloe-ever-shield-deodorant-nobadge.png", title="אלו אוור-שילד", sub="דאודורנט · ריח עדין ונעים", size=760),
  dict(bg=((12,58,66),(60,160,170)), prod="aloe-cooling-lotion.png", title="אלו קולינג לושן", sub="מנטול ואקליפטוס · מרקם קליל", size=760),
]
SEC = 4.5
END = 2.0

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
    p = Image.open(f"{IMG}/{name}").convert("RGBA")
    p.thumbnail((size, size))
    return p

prods = [load(s["prod"], s["size"]) for s in SCENES]
frames_dir = f"{OUT}/frames_multi"; os.makedirs(frames_dir, exist_ok=True)
n = 0
total = int((SEC * len(SCENES) + END) * FPS)
for f in range(total):
    t = f / FPS
    idx = min(int(t // SEC), len(SCENES) - 1)
    local = t - idx * SEC
    if t >= SEC * len(SCENES):
        img = grad((14,48,38),(60,130,100))
        ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
        k = ease((t - SEC * len(SCENES)) / 0.5)
        center(d, "כל המבחר בחנות", 760, F(90), (255,255,255,int(255*k)))
        d.rounded_rectangle((180, 900, W-180, 1050), radius=75, fill=(232,185,74,int(255*k)))
        center(d, "flpil.co.il", 935, F(96), (20,40,30,int(255*k)))
        center(d, "FOREVER ישראל  |  סוכן מורשה", 1790, F(40,False), (255,255,255,255))
        img = Image.alpha_composite(img, ov)
    else:
        s = SCENES[idx]
        top, bot = s["bg"]
        img = grad(top, bot)
        ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
        ft = F(104)
        while d.textlength(s["title"], font=ft) > 940 and ft.size > 50:
            ft = F(ft.size - 4)
        dx = int((1 - ease((local - 0.1) / 0.5)) * 400)
        w = d.textlength(s["title"], font=ft)
        d.text(((W - w)/2 + dx, 200), s["title"], font=ft, fill=WHITE, direction="rtl", language="he")
        fs = F(46, False)
        while d.textlength(s["sub"], font=fs) > 940 and fs.size > 28:
            fs = F(fs.size - 2, False)
        w2 = d.textlength(s["sub"], font=fs)
        d.text(((W-w2)/2, 350), s["sub"], font=fs, fill=(230,245,236,255), direction="rtl", language="he")
        p = prods[idx]
        pulse = 1 + 0.04 * max(0, 1 - (local % 0.5) / 0.2)
        q = p.resize((int(p.width*pulse), int(p.height*pulse)))
        base_y = 760 - q.height // 2 + int((1 - ease((local - 0.2) / 0.6)) * 300)
        sh = Image.new("RGBA", q.size, (0,0,0,0)); sh.paste((0,0,0,255), (0,0), q.split()[3].point(lambda v: int(v*0.45)))
        sh = sh.filter(ImageFilter.GaussianBlur(30))
        img.alpha_composite(sh, ((W - q.width)//2 + 16, base_y + 36))
        img.alpha_composite(q, ((W - q.width)//2, base_y))
        d.rounded_rectangle((120, 1500, W-120, 1600), radius=50, fill=(20,40,30,200))
        center(d, "FOREVER ישראל  |  סוכן מורשה", 1520, F(40,False), (255,255,255,255))
        img = Image.alpha_composite(img, ov)
    img.convert("RGB").save(f"{frames_dir}/f{f:05d}.png")
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{frames_dir}/f%05d.png",
    "-c:v","libx264","-pix_fmt","yuv420p","-crf","22","-movflags","+faststart",f"{OUT}/multi_20s.mp4"], check=True)
shutil.rmtree(frames_dir)
print("done", total / FPS)
