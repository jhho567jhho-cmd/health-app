import subprocess, shutil, os
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/health-app/marketing"
OUT = f"{BASE}/video"
FR = f"{OUT}/frames"
SRC = f"{BASE}/product-images/aloe-ever-shield-deodorant.png"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30

MINT, DEEP, CREAM = (221, 239, 227), (39, 73, 58), (246, 241, 234)
GOLD, INK, WHITE = (232, 185, 74), (30, 40, 34), (255, 255, 255)

# Crop away the award badge on the right of the source image; the stick is in x<580.
prod = Image.open(SRC).convert("RGBA").crop((0, 0, 580, 1080))
prod.thumbnail((700, 700))

f_huge = ImageFont.truetype(FONT_B, 150)
f_big = ImageFont.truetype(FONT_B, 110)
f_mid = ImageFont.truetype(FONT, 58)
f_small = ImageFont.truetype(FONT, 42)

def ease(t):  # ease-out cubic, t in [0,1]
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def text_c(d, s, y, font, fill, dx=0):
    w = d.textlength(s, font=font)
    d.text(((W - w) / 2 + dx, y), s, font=font, fill=fill, direction="rtl", language="he")

def scene_bg(i, bg):
    return Image.new("RGB", (W, H), bg)

def shadow(img, pos):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: int(v * 0.25))
    sh.paste((0, 0, 0, 255), (0, 0), a)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(sh.filter(__import__("PIL.ImageFilter").ImageFilter.GaussianBlur(18)), (pos[0] + 14, pos[1] + 30), sh.filter(__import__("PIL.ImageFilter").ImageFilter.GaussianBlur(18)))
    return layer

os.makedirs(FR, exist_ok=True)
total = 9 * FPS
for f in range(total):
    t = f / FPS
    if t < 3:
        img = scene_bg(0, MINT).convert("RGBA"); d = ImageDraw.Draw(img)
        # text slides in from opposite sides
        dx1 = int((1 - ease((t - 0.1) / 0.6)) * 400)
        dx2 = -int((1 - ease((t - 0.3) / 0.6)) * 400)
        text_c(d, "פרט קטן,", 230, f_huge, INK, dx=dx1)
        text_c(d, "הבדל גדול", 400, f_huge, (39, 120, 80), dx=dx2)
        y = int(H - ease((t - 0.5) / 0.9) * (H - 760) - 0)  # rises to y=760
        y = max(760, y)
        p = prod
        pos = ((W - p.width) // 2, y)
        img.alpha_composite(shadow(p, pos))
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)), (0, 0))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer.paste(p, pos, p)
        img.alpha_composite(layer)
    elif t < 6:
        img = scene_bg(1, DEEP).convert("RGBA"); d = ImageDraw.Draw(img)
        # gold circle behind product, pops in
        r = int(380 * ease((t - 3) / 0.4))
        cx, cy = W // 2, 1000
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD)
        text_c(d, "ריח נעים", 230, f_huge, WHITE)
        text_c(d, "תחושת רעננות לאורך היום", 420, f_mid, (200, 230, 210))
        pos = ((W - prod.width) // 2, 1000 - prod.height // 2)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer.paste(prod, pos, prod)
        img.alpha_composite(layer)
    else:
        img = scene_bg(2, CREAM).convert("RGBA"); d = ImageDraw.Draw(img)
        pos = ((W - prod.width) // 2, 430)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer.paste(prod, pos, prod)
        img.alpha_composite(layer)
        text_c(d, "לחנות המלאה", 1200, f_big, INK)
        # CTA pill
        btn_y = 1360
        d.rounded_rectangle((180, btn_y, W - 180, btn_y + 150), radius=75, fill=(39, 120, 80))
        text_c(d, "flpil.co.il", btn_y + 28, f_big, WHITE)
        text_c(d, "FOREVER ישראל  |  סוכן מורשה", 1620, f_small, INK)
    img.convert("RGB").save(f"{FR}/f{f:04d}.png", optimize=False)

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart",
                f"{OUT}/deodorant_v2.mp4"], check=True)
shutil.rmtree(FR)
print("ok")
