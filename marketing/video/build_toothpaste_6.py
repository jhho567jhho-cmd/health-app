import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/health-app/marketing"
OUT = f"{BASE}/video"
PROD = f"{BASE}/product-images/forever-bright-toothgel.png"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30
INK = (30, 40, 34); WHITE = (255, 255, 255); GOLD = (232, 185, 74); GREEN = (39, 120, 80)

SCENES = [  # 6 second cut
  (3, (221,239,227), "הבוקר שלך", "מתחיל כאן.", (39,120,80)),
  (3, (39,73,58), "FOREVER BRIGHT", "מוזמנים להכיר בחנות", GOLD),
]

def font(s, bold=True): return ImageFont.truetype(FB if bold else FR, s)
def fit(text, size, bold=True, max_w=980):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    s = size
    while s > 28:
        f = font(s, bold)
        if d.textlength(text, font=f) <= max_w: return f
        s -= 4
    return font(28, bold)
def center(d, text, y, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill, direction="rtl", language="he")
def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def is_dark(c): return sum(c) < 400

prod = Image.open(PROD).convert("RGBA"); prod.thumbnail((640, 640))
frames_dir = f"{OUT}/frames6"; os.makedirs(frames_dir, exist_ok=True)

f_idx = 0
for dur, bg, title, cap, acc in SCENES:
    ink = WHITE if is_dark(bg) else INK
    for k in range(dur * FPS):
        t = k / FPS
        img = Image.new("RGBA", (W, H), bg + (255,)); d = ImageDraw.Draw(img)
        # top brand strip
        center(d, "FOREVER ISRAEL", 110, fit("FOREVER ISRAEL", 46, True), acc)
        # title slides in
        dx = int((1 - ease((t - 0.1) / 0.5)) * 400)
        ft = fit(title, 128)
        w = d.textlength(title, font=ft)
        d.text(((W - w) / 2 + dx, 300), title, font=ft, fill=ink, direction="rtl", language="he")
        # product pops in, beat pulse
        s = ease((t - 0.3) / 0.5) * (1 + 0.03 * max(0, 1 - (t % 0.5) / 0.2))
        if s > 0:
            p = prod.resize((max(1,int(prod.width*s)), max(1,int(prod.height*s))))
            layer = Image.new("RGBA", (W, H), (0,0,0,0)); layer.paste(p, ((W - p.width)//2, 720 - p.height//4), p); img.alpha_composite(layer)
        # caption fades in
        if t > 0.8:
            fc = fit(cap, 56, bold=False)
            center(d, cap, 1480, fc, ink)
        # footer
        center(d, "FOREVER ישראל  |  סוכן מורשה", 1790, fit("FOREVER ישראל  |  סוכן מורשה", 38, False), ink)
        img.convert("RGB").save(f"{frames_dir}/f{f_idx:05d}.png")
        f_idx += 1

subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{frames_dir}/f%05d.png",
    "-c:v","libx264","-pix_fmt","yuv420p","-crf","22","-movflags","+faststart",f"{OUT}/toothpaste_6s.mp4"], check=True)
shutil.rmtree(frames_dir)
print("done", f_idx / FPS, "seconds")
