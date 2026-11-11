import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/health-app/marketing"
OUT = f"{BASE}/video"
IMG = f"{BASE}/product-images"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS, DUR = 1080, 1920, 30, 6
INK = (30, 40, 34); WHITE = (255, 255, 255); GREEN = (39, 120, 80)

BUMPERS = {
  "b1_store": dict(bg=(221,239,227), ink=INK, acc=(39,120,80),
      lines=["יש כאן", "יותר ממה שחשבתם."], sub="כל המבחר בחנות במקום אחד",
      prods=["forever-bright-toothgel.png","aloe-lips.png","aloe-ever-shield-deodorant-nobadge.png","aloe-cooling-lotion.png"]),
  "b2_cats": dict(bg=(246,241,234), ink=INK, acc=(150,100,40),
      lines=["טיפוח העור.", "טיפוח אישי."], sub="וגם מהכוורת, משקאות ועוד",
      prods=["aloe-first-spray.png","aloe-body-lotion.png","aloe-lips.png","forever-bright-toothgel.png"]),
  "b3_next": dict(bg=(39,73,58), ink=WHITE, acc=(232,185,74),
      lines=["הדבר הקטן", "הבא שלכם."], sub="לחצו וגלו מה מחכה בחנות",
      prods=["aloe-ever-shield-deodorant-nobadge.png"]),
  "b4_cta": dict(bg=(246,241,234), ink=INK, acc=(39,120,80),
      lines=["כל המבחר.", "במקום אחד."], sub="לחצו לכניסה לחנות",
      prods=["forever-bright-toothgel.png","aloe-lips.png","aloe-ever-shield-deodorant-nobadge.png","aloe-cooling-lotion.png"]),
}

def fit(d, text, size, max_w=980, bold=True):
    s = size
    while s > 30:
        f = ImageFont.truetype(FB if bold else FR, s)
        if d.textlength(text, font=f) <= max_w: return f
        s -= 4
    return ImageFont.truetype(FB if bold else FR, 30)

def center(d, text, y, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill, direction="rtl", language="he")

def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def load(name, big=False):
    p = Image.open(f"{IMG}/{name}").convert("RGBA")
    p.thumbnail((620, 620) if big else (360, 360))
    return p

def render(name, cfg):
    frames = f"{OUT}/framesb_{name}"; os.makedirs(frames, exist_ok=True)
    prods = [load(p, big=(len(cfg["prods"]) == 1)) for p in cfg["prods"]]
    d0 = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    for f in range(DUR * FPS):
        t = f / FPS
        img = Image.new("RGBA", (W, H), cfg["bg"] + (255,)); d = ImageDraw.Draw(img)
        # headline lines slide in one after the other
        for i, line in enumerate(cfg["lines"]):
            start = 0.15 + i * 0.35
            dx = int((1 - ease((t - start) / 0.5)) * 500) * (1 if i % 2 == 0 else -1)
            fnt = fit(d0, line, 150)
            w = d0.textlength(line, font=fnt)
            d.text(((W - w) / 2 + dx, 200 + i * 170), line, font=fnt, fill=cfg["ink"] if i < len(cfg["lines"]) - 1 else cfg["acc"], direction="rtl", language="he")
        head_bottom = 200 + len(cfg["lines"]) * 170
        center(d, cfg["sub"], head_bottom + 20, fit(d0, cfg["sub"], 52, bold=False), cfg["ink"])
        # product layer
        if len(prods) == 1:
            p = prods[0]; s = 1 + 0.04 * max(0, 1 - (t % 0.5) / 0.2)
            p = p.resize((int(p.width*s), int(p.height*s)))
            layer = Image.new("RGBA", (W, H), (0,0,0,0)); layer.paste(p, ((W - p.width)//2, 800), p); img.alpha_composite(layer)
        else:
            cols = 2; cell = 380; top = 720
            for idx, p in enumerate(prods):
                start = 0.8 + idx * 0.25
                k = ease((t - start) / 0.4)
                if k <= 0: continue
                cx = (idx % cols) * cell + (W - cols*cell)//2 + cell//2
                cy = top + (idx // cols) * cell + cell//2
                s = k * (1 + 0.03 * max(0, 1 - (t % 0.5) / 0.2))
                q = p.resize((max(1,int(p.width*s)), max(1,int(p.height*s))))
                layer = Image.new("RGBA", (W, H), (0,0,0,0)); layer.paste(q, (cx - q.width//2, cy - q.height//2), q); img.alpha_composite(layer)
        # CTA + footer
        if t > 4.0 or name.startswith("b4"):
            d.rounded_rectangle((180, 1560, W-180, 1690), radius=65, fill=GREEN)
            center(d, "flpil.co.il", 1584, fit(d0, "flpil.co.il", 96), WHITE)
        center(d, "FOREVER ישראל  |  סוכן מורשה", 1790, fit(d0, "FOREVER ישראל  |  סוכן מורשה", 40, bold=False), INK if cfg["bg"][0] > 150 else WHITE)
        img.convert("RGB").save(f"{frames}/f{f:04d}.png")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{frames}/f%04d.png",
        "-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-movflags","+faststart",f"{OUT}/{name}.mp4"], check=True)
    shutil.rmtree(frames)

if __name__ == "__main__":
    for n, c in BUMPERS.items():
        render(n, c); print("built", n)
