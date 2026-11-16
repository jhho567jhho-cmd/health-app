import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE = "/home/user/health-app/marketing"
IMG = f"{BASE}/product-images"; OUT = f"{BASE}/video"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30
def F(s, b=True): return ImageFont.truetype(FB if b else FR, s)
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def grad(top, bot):
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1); g.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g.resize((W, H)).convert("RGBA")
def center(d, text, y, font, fill):
    w = d.textlength(text, font=font); d.text(((W - w) / 2, y), text, font=font, fill=fill, direction="rtl", language="he")
prod = Image.open(f"{IMG}/aloe-lips.png").convert("RGBA"); prod.thumbnail((820, 820))
SC = [(2.5, (80,30,44),(190,100,120), "השפתיים מדברות בשקט.", ""),
      (3.0, (80,30,44),(190,100,120), "אלו ליפס", "מרקם נעים למגע"),
      (3.5, (40,20,30),(120,60,80), "לא בשבילכם?", "יש עוד הרבה במבחר בחנות")]
frames = f"{OUT}/frames_lips"; os.makedirs(frames, exist_ok=True)
total = 9 * FPS
for f in range(total):
    t = f / FPS
    start = 0.0
    for dur, top, bot, title, sub in SC:
        if t < start + dur: break
        start += dur
    local = t - start
    img = grad(top, bot)
    ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    ft = F(100)
    while d.textlength(title, font=ft) > 940 and ft.size > 50: ft = F(ft.size - 4)
    dx = int((1 - ease((local - 0.1) / 0.5)) * 300)
    w = d.textlength(title, font=ft); d.text(((W - w)/2 + dx, 260), title, font=ft, fill=(255,255,255,255), direction="rtl", language="he")
    if sub:
        fs = F(50, False)
        while d.textlength(sub, font=fs) > 940 and fs.size > 30: fs = F(fs.size - 2, False)
        w2 = d.textlength(sub, font=fs); d.text(((W-w2)/2, 410), sub, font=fs, fill=(250,230,235,255), direction="rtl", language="he")
    img = Image.alpha_composite(img, ov)
    if start < 5.5:
        s = 1 + 0.03 * max(0, 1 - (local % 0.5) / 0.2)
        q = prod.resize((int(prod.width*s), int(prod.height*s)))
        y0 = 900 - q.height // 2
        sh = Image.new("RGBA", q.size, (0,0,0,0)); sh.paste((0,0,0,255), (0,0), q.split()[3].point(lambda v: int(v*0.45)))
        sh = sh.filter(ImageFilter.GaussianBlur(30))
        img.alpha_composite(sh, ((W-q.width)//2 + 16, y0 + 36)); img.alpha_composite(q, ((W-q.width)//2, y0))
    if t >= 5.5:
        k = ease((t - 5.5) / 0.5)
        ov2 = Image.new("RGBA", (W, H), (0,0,0,0)); d2 = ImageDraw.Draw(ov2)
        d2.rounded_rectangle((120, 1290, W-120, 1480), radius=75, fill=(232,185,74,int(255*k)))
        center(d2, "כל המבחר בחנות", 1320, F(66), (20,40,30,int(255*k)))
        center(d2, "flpil.co.il", 1400, F(56), (20,40,30,int(255*k)))
        img = Image.alpha_composite(img, ov2)
    d3 = ImageDraw.Draw(img)
    center(d3, "החזרה עד 30 יום לפי מדיניות החברה", 1600, F(38, False), (255,255,255,255))
    d3.rounded_rectangle((120, 1700, W-120, 1790), radius=45, fill=(20,40,30,200))
    center(d3, "FOREVER ישראל  |  סוכן מורשה", 1716, F(38, False), (255,255,255,255))
    img.convert("RGB").save(f"{frames}/f{f:05d}.png")
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{frames}/f%05d.png",
    "-c:v","libx264","-pix_fmt","yuv420p","-crf","22","-movflags","+faststart",f"{OUT}/lips_9s.mp4"], check=True)
shutil.rmtree(frames); print("done")
