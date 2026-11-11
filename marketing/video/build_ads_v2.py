import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/health-app/marketing"
OUT = f"{BASE}/video"
IMG = f"{BASE}/product-images"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS = 1080, 1920, 30
CREAM = (246, 241, 234); GOLD = (232, 185, 74); WHITE = (255, 255, 255)
INK = (30, 40, 34); GREEN_BTN = (39, 120, 80)

ADS = {
  "toothpaste": dict(src="forever-bright-toothgel.png", crop=None,
      hook=("הבוקר שלך", "מתחיל כאן"), mid="פשוט. נעים. שלך.",
      sub="ג'ל צחצוח עם אלוורה ופרופוליס", bg1=(221,239,227), acc=(39,120,80),
      bg2=(39,73,58), mid_color=WHITE, out="ad2_toothpaste.mp4"),
  "lips": dict(src="aloe-lips.png", crop=None,
      hook=("השפתיים", "מדברות בשקט."), mid="נעים למגע.",
      sub="שפתון אלו ליפס", bg1=(250,231,231), acc=(150,50,70),
      bg2=(72,40,50), mid_color=WHITE, out="ad2_lips.mp4"),
  "deodorant": dict(src="aloe-ever-shield-deodorant.png", crop=(0,0,580,1080),
      hook=("ריח טוב", "הוא הדבר הראשון שזוכרים"), mid="רעננות נעימה.",
      sub="דאודורנט אלו אוור-שילד", bg1=(226,236,246), acc=(30,80,140),
      bg2=(27,49,73), mid_color=WHITE, out="ad2_deodorant.mp4"),
  "cooling": dict(src="aloe-cooling-lotion.png", crop=None,
      hook=("קרירות", "שמרגישים."), mid="תחושה קרירה ורעננה.",
      sub="אלו קולינג לושן: מנטול ואקליפטוס", bg1=(220,240,242), acc=(20,120,130),
      bg2=(14,60,68), mid_color=WHITE, out="ad2_cooling.mp4"),
}

def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT, size)

def fit_font(text, max_size, max_w=980, bold=True):
    s = max_size
    while s > 30:
        f = font(s, bold)
        if ImageDraw.Draw(Image.new("RGB",(1,1))).textlength(text, font=f) <= max_w:
            return f
        s -= 4
    return font(30, bold)

def text_c(d, s, y, f, fill):
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2, y), s, font=f, fill=fill, direction="rtl", language="he")

def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def load_product(cfg):
    p = Image.open(f"{IMG}/{cfg['src']}").convert("RGBA")
    if cfg["crop"]:
        p = p.crop(cfg["crop"])
    p.thumbnail((700, 700))
    return p

def paste(img, p, pos):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer.paste(p, pos, p)
    img.alpha_composite(layer)

def beat(t):
    # 0.5s beat: quick scale punch that decays after each beat
    return 1 + 0.06 * max(0.0, 1 - (t % 0.5) / 0.18)

def punch_size(p, t):
    s = beat(t)
    return p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)

def flash(img, t):
    # white flash that decays after each scene cut (0s, 3s, 6s)
    for cut in (0.0, 3.0, 6.0):
        dt = t - cut
        if 0 <= dt < 0.2:
            a = int(140 * (1 - dt / 0.2))
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
            return

def build(name, cfg):
    frames = f"{OUT}/frames2_{name}"
    os.makedirs(frames, exist_ok=True)
    prod = load_product(cfg)
    total = 9 * FPS
    for f in range(total):
        t = f / FPS
        if t < 3:
            img = Image.new("RGBA", (W, H), cfg["bg1"] + (255,)); d = ImageDraw.Draw(img)
            f1 = fit_font(cfg["hook"][0], 130); f2 = fit_font(cfg["hook"][1], 130)
            dx1 = int((1 - ease((t - 0.1) / 0.6)) * 400)
            dx2 = -int((1 - ease((t - 0.3) / 0.6)) * 400)
            w1 = d.textlength(cfg["hook"][0], font=f1); w2 = d.textlength(cfg["hook"][1], font=f2)
            d.text(((W - w1) / 2 + dx1, 220), cfg["hook"][0], font=f1, fill=INK, direction="rtl", language="he")
            d.text(((W - w2) / 2 + dx2, 400), cfg["hook"][1], font=f2, fill=cfg["acc"], direction="rtl", language="he")
            y = max(760, int(H - ease((t - 0.5) / 0.9) * (H - 760)))
            pp = punch_size(prod, t)
            paste(img, pp, ((W - pp.width) // 2, y))
            flash(img, t)
        elif t < 6:
            img = Image.new("RGBA", (W, H), cfg["bg2"] + (255,)); d = ImageDraw.Draw(img)
            r = int(380 * ease((t - 3) / 0.4)); cx, cy = W // 2, 1000
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD)
            text_c(d, cfg["mid"], 230, fit_font(cfg["mid"], 110), cfg["mid_color"])
            text_c(d, cfg["sub"], 420, font(58, False), (210, 225, 215))
            pp = punch_size(prod, t)
            paste(img, pp, ((W - pp.width) // 2, 1000 - pp.height // 2))
            flash(img, t)
        else:
            img = Image.new("RGBA", (W, H), CREAM + (255,)); d = ImageDraw.Draw(img)
            pp = punch_size(prod, t)
            paste(img, pp, ((W - pp.width) // 2, 430))
            flash(img, t)
            text_c(d, "מוזמנים להכיר", 1200, fit_font("מוזמנים להכיר", 110), INK)
            d.rounded_rectangle((180, 1360, W - 180, 1510), radius=75, fill=GREEN_BTN)
            text_c(d, "flpil.co.il", 1388, font(100), WHITE)
            text_c(d, "FOREVER ישראל  |  סוכן מורשה", 1620, font(42, False), INK)
        img.convert("RGB").save(f"{frames}/f{f:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{frames}/f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart",
                    f"{OUT}/{cfg['out']}"], check=True)
    shutil.rmtree(frames)

if __name__ == "__main__":
    ADS.pop("lotion", None)
    for n, c in ADS.items():
        if n == "lotion":
            continue
        build(n, c)
        print("built", c["out"])
