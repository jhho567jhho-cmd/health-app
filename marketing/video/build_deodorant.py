import subprocess, os
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/health-app/marketing"
OUT = f"{BASE}/video"
PROD = f"{BASE}/product-images/aloe-ever-shield-deodorant.png"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1080, 1920
BG = (246, 241, 234)
INK = (43, 43, 43)
ACCENT = (94, 125, 91)

def centered(draw, text, y, font, fill):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill, direction="rtl", language="he")

def product_layer():
    p = Image.open(PROD).convert("RGBA")
    p.thumbnail((760, 760))
    return p

def slide(name, title, subtitle, footer=None, show_product=True):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(FONT_B, 92)
    f_sub = ImageFont.truetype(FONT, 58)
    f_small = ImageFont.truetype(FONT, 40)
    centered(d, title, 230, f_title, INK)
    centered(d, subtitle, 360, f_sub, ACCENT)
    if show_product:
        p = product_layer()
        img.paste(p, ((W - p.width) // 2, 720), p)
    if footer:
        centered(d, footer, 1620, f_small, INK)
    img.save(f"{OUT}/{name}.png")

slide("s1", "אלו אוור-שילד", "דאודורנט עם אלוורה", show_product=True)
slide("s2", "ריח נעים", "תחושת רעננות לאורך היום", show_product=True)
slide("s3", "FOREVER ישראל", "לחנות המלאה בקישור", footer="flpil.co.il  |  סוכן מורשה", show_product=True)

# Motion: slow zoom per slide, 4 seconds each, then concat
clips = []
for i in (1, 2, 3):
    out = f"{OUT}/clip{i}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", f"{OUT}/s{i}.png",
        "-vf", "zoompan=z='min(zoom+0.0009,1.08)':d=120:s=1080x1920:fps=30",
        "-t", "4", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", out], check=True)
    clips.append(out)

with open(f"{OUT}/list.txt", "w") as f:
    for c in clips:
        f.write(f"file '{c}'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/deodorant_draft.mp4"], check=True)
print("ok")
