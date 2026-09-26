import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import tempfile
import math
import time
import random
import csv
import io
import hashlib
import wave
import struct
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# QUIZVIDEO PRO — V4 DYNAMIC SHORTS ENGINE
# ============================================================
st.set_page_config(page_title="QuizVideo Pro", page_icon="🎬", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg,#f8fbff 0%,#eef3fa 55%,#f7f4ff 100%); color:#172033; }
[data-testid="stMain"] { background: transparent; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0b1630 0%,#101d3d 58%,#111a33 100%); border-right: 1px solid #1f3159; }
[data-testid="stSidebar"] * { color:#eef4ff !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:#dbe7ff !important; }
[data-testid="stSidebar"] .stRadio label { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10); border-radius:14px; padding:8px 10px; margin:4px 0; }
label, [data-testid="stMarkdownContainer"] { color:#253047; }
[data-testid="stHeader"] { background: rgba(255,255,255,.78); }
.block-container { max-width: 1220px; padding-top: .55rem; padding-bottom: 1rem; }
h1, h2, h3 { letter-spacing: -0.02em; color:#111827; }
[data-testid="stTabs"] button { font-weight: 800; font-size: 1.02rem; color:#334155; padding:10px 18px; }
[data-testid="stTabs"] [aria-selected="true"] { color:#6d4aff !important; border-bottom-color:#6d4aff !important; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea { border-radius: 14px !important; background:#ffffff !important; color:#172033 !important; border-color:#cbd5e1 !important; }
[data-baseweb="select"] > div { background:#ffffff !important; border-color:#cbd5e1 !important; color:#172033 !important; border-radius:14px !important; }
[data-testid="stButton"] button { border-radius: 14px; min-height: 2.8rem; font-weight: 700; border: 1px solid #cbd5e1; background: linear-gradient(135deg,#ffffff,#f3f6fa); color:#172033; box-shadow:0 4px 12px rgba(15,23,42,.06); }
[data-testid="stButton"] button:hover { border-color:#7c8cff; transform: translateY(-1px); box-shadow:0 8px 18px rgba(15,23,42,.10); }
[data-testid="stFileUploaderDropzone"] { border: 1px dashed #b9c5d6; border-radius: 16px; background: #ffffff; }
.qvp-card { padding: 9px 12px; border: 1px solid #dbe2ec; border-radius: 18px; background: #ffffff; box-shadow: 0 10px 28px rgba(15,23,42,.07); margin: 4px 0 8px; }
.qvp-small { color:#64748b; font-size:.9rem; }
.qvp-side-brand { display:flex; gap:12px; align-items:center; padding:8px 2px 18px; }
.qvp-logo { width:42px; height:42px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:25px; font-weight:900; background:linear-gradient(135deg,#7b4dff,#36b8e8); color:white !important; box-shadow:0 8px 24px rgba(83,67,180,.35); }
.qvp-side-title { font-size:1.18rem; font-weight:800; color:#fff !important; }
.qvp-side-sub { font-size:.72rem; color:#b9c8e8 !important; margin-top:2px; }
.qvp-side-note { margin-top:18px; padding:14px; border:1px solid rgba(255,255,255,.13); border-radius:16px; background:linear-gradient(135deg,rgba(124,77,255,.18),rgba(42,180,216,.10)); font-size:.78rem; line-height:1.45; }
.qvp-hero { display:flex; justify-content:space-between; align-items:center; gap:14px; padding:12px 16px; border:1px solid #dbe4f0; border-radius:24px; background:rgba(255,255,255,.84); box-shadow:0 14px 36px rgba(31,48,82,.08); margin-bottom:18px; }
.qvp-hero h1 { margin:2px 0 3px; font-size:1.55rem; }
.qvp-hero p { margin:0; color:#66748c; }
.qvp-kicker { color:#6751e8; font-size:.78rem; font-weight:800; letter-spacing:.12em; }
.qvp-hero-pill { padding:11px 16px; border-radius:999px; background:#f0edff; color:#5c45d5; font-weight:800; white-space:nowrap; }
.qvp-flow { display:flex; align-items:center; justify-content:center; gap:14px; flex-wrap:wrap; padding:13px 18px; border:1px solid #e1e7f0; border-radius:18px; background:#fff; color:#334155; margin:0 0 20px; box-shadow:0 7px 20px rgba(15,23,42,.04); }
.qvp-flow b { color:#8b78ee; }
.qvp-mini-card { min-height:94px; padding:18px; border:1px solid #ddd7ff; border-radius:17px; background:linear-gradient(135deg,#faf9ff,#f2f8ff); color:#334155; }
.qvp-mini-card span { color:#64748b; font-size:.88rem; }
.qvp-preview-placeholder { height:250px; border:1px dashed #cbd5e1; border-radius:18px; display:flex; align-items:center; justify-content:center; text-align:center; color:#64748b; background:#f8fafc; }
.qvp-economy { padding:13px 16px; border-radius:15px; border:1px solid #d6e7f7; background:#eef8ff; color:#28506d; margin:10px 0 16px; }
.qvp-preview-sticky { z-index:20; }
[data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) > [data-testid="column"]:last-child { position:sticky; top:72px; align-self:flex-start; z-index:30; }
.qvp-preview-panel { padding:14px; border:1px solid #dbe4f0; border-radius:20px; background:rgba(255,255,255,.96); box-shadow:0 14px 34px rgba(15,23,42,.10); }
.qvp-preview-title { font-weight:800; color:#172033; font-size:1.05rem; margin-bottom:8px; }
.qvp-preview-note { color:#64748b; font-size:.82rem; margin-bottom:10px; }
.qvp-editor-tabs [data-testid="stTabs"] button { font-size:.86rem !important; padding:7px 10px !important; }
.qvp-editor-tabs { margin-bottom:8px; }


/* V8.1 — éditeur compact + aperçu plus proche */
.qvp-editor-tabs [data-testid="stVerticalBlock"] { gap: 0.28rem; }
.qvp-editor-tabs [data-testid="stHorizontalBlock"] { gap: 0.45rem; }
.qvp-editor-tabs .stSlider { margin-bottom: -0.15rem; }
.qvp-editor-tabs .stCheckbox { margin-bottom: -0.25rem; }
.qvp-editor-tabs .stCaption { margin-top: -0.2rem; }
.qvp-preview-sticky { top: 1rem !important; }
.qvp-preview-panel { margin-bottom: 0.35rem; }

/* V8.3 — studio compact / navigation always visible */
/* Main module switcher: make the first tab bar look like a real app navigation. */
[data-testid="stMain"] [data-testid="stTabs"]:not(.qvp-editor-tabs [data-testid="stTabs"]) > div:first-child {background:rgba(255,255,255,.97);border:1px solid #d9e2ef;border-radius:16px;padding:6px 8px;box-shadow:0 8px 24px rgba(15,23,42,.08);position:sticky;top:4px;z-index:100;}
[data-testid="stMain"] [data-testid="stTabs"]:not(.qvp-editor-tabs [data-testid="stTabs"]) button {font-weight:850 !important;font-size:1rem !important;padding:10px 14px !important;border-radius:11px !important;}

[data-testid="stAppViewContainer"] .main .block-container {max-width:1500px !important; padding-top:0.55rem !important; padding-bottom:0.7rem !important;}
[data-testid="stHeader"] {background:transparent !important;}
.qvp-studio-nav {position:sticky;top:0;z-index:100;background:rgba(255,255,255,.96);backdrop-filter:blur(12px);border:1px solid #d9e2ef;border-radius:16px;padding:6px 8px;margin:0 0 10px;box-shadow:0 8px 24px rgba(15,23,42,.08);}
.qvp-studio-nav [data-testid="stTabs"] {margin:0 !important;}
.qvp-studio-nav [data-testid="stTabs"] [role="tablist"] {gap:6px;border-bottom:0 !important;}
.qvp-studio-nav [data-testid="stTabs"] button {flex:1;font-weight:800;font-size:1rem !important;padding:10px 12px !important;border-radius:11px !important;border:1px solid transparent !important;}
.qvp-studio-nav [data-testid="stTabs"] button[aria-selected="true"] {background:#172033 !important;color:#fff !important;border-color:#172033 !important;}
.qvp-studio-nav [data-testid="stTabs"] button[aria-selected="false"] {background:#f3f6fb !important;color:#334155 !important;}
.qvp-studio-nav [data-testid="stTabs"] > div:last-child {display:none !important;}
.qvp-hero {padding:10px 14px !important;margin:0 0 8px !important;min-height:0 !important;}
.qvp-card {padding:8px 12px !important;margin:5px 0 !important;}
.qvp-editor-tabs {border:1px solid #dbe4f0;border-radius:16px;padding:8px;background:#fff;}
.qvp-editor-tabs [data-testid="stTabs"] [role="tablist"] {gap:4px;overflow-x:auto;white-space:nowrap;border-bottom:1px solid #e2e8f0;}
.qvp-editor-tabs [data-testid="stTabs"] button {font-weight:750 !important;font-size:.78rem !important;padding:7px 8px !important;border-radius:9px !important;}
.qvp-editor-tabs [data-testid="stTabs"] button[aria-selected="true"] {background:#eef3fa !important;}
.qvp-preview-panel {padding:9px 12px !important;}
.qvp-preview-note {margin-bottom:5px !important;}
.qvp-actionbar {position:sticky;bottom:8px;z-index:90;background:rgba(255,255,255,.97);backdrop-filter:blur(10px);border:1px solid #d9e2ef;border-radius:14px;padding:7px;margin-top:10px;box-shadow:0 8px 22px rgba(15,23,42,.10);}

/* V8.5 Studio : interface compacte, pensée pour 100% de zoom. */
.qvp-studio-header{display:flex;align-items:center;gap:12px;padding:6px 10px;margin:0 0 6px;border-bottom:1px solid #dbe4f0;font-size:.92rem;color:#172033}
.qvp-studio-header span{padding:4px 9px;border-radius:999px;background:#172033;color:#fff;font-weight:800;font-size:.75rem}
.qvp-studio-header small{margin-left:auto;color:#64748b;font-size:.72rem}
.qvp-hero{display:none !important}
[data-testid="stMain"] .stCaption{font-size:.72rem !important;margin-top:2px !important;margin-bottom:4px !important}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]{gap:.38rem !important}
.qvp-preview-panel{padding:8px 10px !important;border-radius:12px !important}
.qvp-preview-title{font-size:.88rem !important;margin-bottom:3px !important}
.qvp-preview-note{font-size:.68rem !important;margin-bottom:4px !important}
.qvp-actionbar{padding:5px 8px !important;margin-top:5px !important}

</style>
""", unsafe_allow_html=True)

WIDTH, HEIGHT, FPS = 1080, 1920, 30
_BASE_CACHE = {}

THEMES = {
    "Bleu Nuit & Or": {"bg": (7, 12, 28), "bg2": (20, 33, 62), "card": (25, 36, 61), "card2": (40, 55, 88), "accent": (255, 205, 64), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (165, 181, 208)},
    "Chocolat Noir & Or": {"bg": (18, 10, 8), "bg2": (65, 35, 20), "card": (52, 31, 22), "card2": (82, 49, 31), "accent": (255, 190, 64), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (199, 170, 145)},
    "Violet Neon": {"bg": (12, 7, 25), "bg2": (50, 17, 72), "card": (43, 22, 65), "card2": (72, 35, 100), "accent": (239, 93, 255), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (199, 171, 222)},
    "Emeraude Mint": {"bg": (4, 18, 15), "bg2": (8, 61, 48), "card": (13, 48, 37), "card2": (21, 75, 57), "accent": (74, 231, 178), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (160, 202, 186)},
    "Noir Carbone": {"bg": (5, 7, 11), "bg2": (28, 32, 42), "card": (25, 28, 36), "card2": (42, 47, 59), "accent": (112, 190, 255), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (166, 176, 194)},
}

VOICES_FR = {
    "Henri - Dynamique": "fr-FR-HenriNeural",
    "Vivienne - Energique": "fr-FR-VivienneNeural",
    "Remy - Standard": "fr-FR-RemyNeural",
}
VOICES_MAP = {
    "Anglais": {"Emma": "en-US-EmmaNeural", "Christopher": "en-US-ChristopherNeural"},
    "Espagnol": {"Alvaro": "es-ES-AlvaroNeural", "Elvira": "es-ES-ElviraNeural"},
    "Arabe": {"Hamed": "ar-SA-HamedNeural", "Salma": "ar-SA-SalmaNeural"},
    "Allemand": {"Killian": "de-DE-KillianNeural", "Klarissa": "de-DE-KlarissaNeural"},
    "Italien": {"Diego": "it-IT-DiegoNeural", "Elsa": "it-IT-ElsaNeural"},
}

# ------------------------- Helpers --------------------------
def get_ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()

def get_font(size):
    candidates = ["Roboto-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"]
    for fn in candidates:
        try:
            if os.path.exists(fn) and os.path.getsize(fn) > 100:
                return ImageFont.truetype(fn, max(12, int(size)))
        except Exception:
            pass
    return ImageFont.load_default()

def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text).replace("\n", " ")).strip()

def text_width(draw, text, font):
    box = draw.textbbox((0, 0), str(text), font=font)
    return box[2] - box[0]

def text_height(font, text="Ag"):
    b = font.getbbox(text)
    return b[3] - b[1]

def wrap_text(text, font, max_width):
    words = clean_text(text).split()
    lines, cur = [], ""
    dummy = ImageDraw.Draw(Image.new("RGB", (2, 2)))
    for word in words:
        candidate = word if not cur else cur + " " + word
        if text_width(dummy, candidate, font) <= max_width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(v)))

def ease_out(v):
    v = clamp(v)
    return 1 - (1 - v) ** 3

def ease_back(v):
    v = clamp(v)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (v - 1) ** 3 + c1 * (v - 1) ** 2

def fit_background(uploaded_file):
    if not uploaded_file:
        return None
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file).convert("RGB")
        ratio = WIDTH / HEIGHT
        src_ratio = img.width / img.height
        if src_ratio > ratio:
            new_h = HEIGHT
            new_w = int(new_h * src_ratio)
        else:
            new_w = WIDTH
            new_h = int(new_w / src_ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = max(0, (new_w - WIDTH) // 2)
        top = max(0, (new_h - HEIGHT) // 2)
        return img.crop((left, top, left + WIDTH, top + HEIGHT))
    except Exception:
        return None

def make_base(theme_name, bg_file=None):
    """Fond vidéo moderne mis en cache pour garder le rendu rapide."""
    theme = THEMES[theme_name]
    if isinstance(bg_file, Image.Image):
        bg = bg_file
        key = None
    elif bg_file is not None:
        bg = fit_background(bg_file)
        key = None
    else:
        bg = None
        key = ("theme", theme_name)

    if bg is not None:
        base = bg.convert("RGBA")
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 105))
        shade = Image.new("L", (WIDTH, HEIGHT), 0)
        sd = ImageDraw.Draw(shade)
        sd.rectangle((70, 120, WIDTH-70, HEIGHT-100), fill=115)
        shade = shade.filter(ImageFilter.GaussianBlur(90))
        overlay.putalpha(shade)
        return Image.alpha_composite(base, overlay).convert("RGB")

    if key in _BASE_CACHE:
        return _BASE_CACHE[key].copy()
    c1, c2 = theme["bg"], theme["bg2"]
    img = Image.new("RGB", (WIDTH, HEIGHT))
    px = img.load()
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        t2 = 0.5 - 0.5 * math.cos(math.pi * t)
        row = tuple(int(c1[i] * (1-t2) + c2[i] * t2) for i in range(3))
        for x in range(WIDTH):
            px[x, y] = row
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-260, -260, 650, 600), fill=(*theme["accent"], 34))
    gd.ellipse((520, 1180, 1380, 2050), fill=(*theme["accent"], 22))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    result = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    _BASE_CACHE[key] = result
    return result.copy()

def add_top_glow(img, theme, strength=1.0):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    a = int(34 * clamp(strength))
    gd.ellipse((110, -420, 970, 520), fill=(*theme["accent"], a))
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

def rounded_text(draw, xy, text, font, fill, outline=None, width=2, radius=20):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=width if outline else 1)
    tw = text_width(draw, text, font)
    th = text_height(font, text)
    draw.text(((x1+x2-tw)/2, (y1+y2-th)/2-4), text, font=font, fill="white")

def draw_thinking_icon(draw, theme, phase=0.0, cx=935, cy=1250, size=44):
    """Icône de réflexion dessinée en formes : aucun emoji/font externe nécessaire."""
    phase=float(phase or 0.0)
    accent=theme.get("accent",(255,205,64))
    pulse=0.5+0.5*math.sin(phase*math.pi*2)
    r=int(size+4*pulse)
    draw.ellipse((cx-r-8,cy-r-8,cx+r+8,cy+r+8), outline=(*accent,90), width=3)
    draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(8,13,27), outline="white", width=4)
    er=max(3,int(r*.10))
    draw.ellipse((cx-int(r*.32)-er,cy-int(r*.18)-er,cx-int(r*.32)+er,cy-int(r*.18)+er), fill="white")
    draw.ellipse((cx+int(r*.32)-er,cy-int(r*.18)-er,cx+int(r*.32)+er,cy-int(r*.18)+er), fill="white")
    draw.line((cx-int(r*.46),cy-int(r*.43),cx-int(r*.16),cy-int(r*.50)), fill=accent, width=4)
    draw.line((cx+int(r*.16),cy-int(r*.50),cx+int(r*.46),cy-int(r*.43)), fill=accent, width=4)
    draw.arc((cx-int(r*.28),cy-int(r*.02),cx+int(r*.30),cy+int(r*.40)),190,340,fill=accent,width=4)
    draw.line((cx+int(r*.15),cy+int(r*.55),cx+int(r*.42),cy+int(r*.82)),fill="white",width=5)
    draw.line((cx+int(r*.42),cy+int(r*.82),cx+int(r*.60),cy+int(r*.65)),fill="white",width=5)


def draw_thinking_face(draw, theme, cx, cy, size=30, phase=0.0, style="Réflexion", color=None):
    """Visage personnalisable : Réflexion, Sourire, Surpris, Clin d'œil ou Simple."""
    a=color or theme["accent"]
    pulse=1.0+0.08*math.sin(float(phase)*math.pi*2)
    r=int(size*pulse)
    # bulle
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(8,14,30,235),outline="white",width=max(2,int(size/8)))
    # yeux
    er=max(2,int(r*0.10))
    for ex in (-int(r*.30), int(r*.30)):
        draw.ellipse((cx+ex-er,cy-int(r*.18)-er,cx+ex+er,cy-int(r*.18)+er),fill="white")
    style=str(style or "Réflexion")
    if style=="Surpris":
        draw.ellipse((cx-int(r*.28),cy-int(r*.05),cx+int(r*.28),cy+int(r*.48)),outline=a,width=max(2,int(size/9)))
    elif style=="Sourire":
        draw.arc((cx-int(r*.34),cy-int(r*.05),cx+int(r*.34),cy+int(r*.45)),10,170,fill=a,width=max(2,int(size/9)))
    elif style=="Clin d'œil":
        draw.line((cx-int(r*.48),cy-int(r*.18),cx-int(r*.12),cy-int(r*.18)),fill=a,width=max(2,int(size/9)))
        draw.arc((cx-int(r*.30),cy-int(r*.02),cx+int(r*.30),cy+int(r*.38)),190,335,fill=a,width=max(2,int(size/9)))
    elif style=="Simple":
        draw.line((cx-int(r*.25),cy+int(r*.22),cx+int(r*.25),cy+int(r*.22)),fill=a,width=max(2,int(size/9)))
    else:
        draw.line((cx-int(r*.48),cy-int(r*.47),cx-int(r*.12),cy-int(r*.55)),fill=a,width=max(2,int(size/8)))
        draw.line((cx+int(r*.12),cy-int(r*.55),cx+int(r*.48),cy-int(r*.47)),fill=a,width=max(2,int(size/8)))
        draw.arc((cx-int(r*.30),cy-int(r*.02),cx+int(r*.30),cy+int(r*.38)),190,335,fill=a,width=max(2,int(size/9)))
    if style in ("Réflexion","Surpris"):
        br=max(4,int(size*.18))
        draw.ellipse((cx+int(r*.65),cy-int(r*.85),cx+int(r*.65)+br,cy-int(r*.85)+br),fill=a)
        draw.ellipse((cx+int(r*.95),cy-int(r*1.15),cx+int(r*.95)+br//2,cy-int(r*1.15)+br//2),fill=a)

def draw_lightning_icon(draw, theme, cx, cy, size=28):
    """Éclair vectoriel pour remplacer ⚡ dans les scènes vidéo."""
    a=theme["accent"]; r=size
    pts=[(cx+int(.15*r),cy-r),(cx-int(.55*r),cy+int(.05*r)),
         (cx-int(.08*r),cy+int(.05*r)),(cx-int(.28*r),cy+r),
         (cx+int(.60*r),cy-int(.18*r)),(cx+int(.05*r),cy-int(.18*r))]
    draw.polygon(pts,fill=a)

def draw_brand(draw, theme, channel, progress=None):
    if channel:
        draw.text((55, 1810), clean_text(channel), font=get_font(28), fill=theme["muted"])
    if progress is not None:
        x, y, w, h = 55, 1745, 970, 12
        draw.rounded_rectangle((x,y,x+w,y+h), radius=6, fill=(65,70,85))
        draw.rounded_rectangle((x,y,x+int(w*clamp(progress)),y+h), radius=6, fill=theme["accent"])

def _highlight_words(question):
    words=clean_text(question).split()
    stop={"quel","quelle","quels","quelles","est","sont","le","la","les","un","une","des","du","de","dans","sur","au","aux","en","à","a","et","ou","pour","par","avec","qui","que","se","ce","cette","cet","d","l","comment","combien","où","on"}
    candidates=[w.strip(".,?!:;()[]«»\"'") for w in words if len(w.strip(".,?!:;()[]«»\"'"))>=5 and w.lower().strip(".,?!:;()[]«»\"'") not in stop]
    return set(c.lower() for c in candidates[:max(2,min(4,len(candidates)))]) if candidates else set()

def draw_header(draw, theme, q_num, total, title="Culture Générale", phase=0.0):
    """Header inspiré du Short de référence : titre, pensée dessinée, compteur."""
    title=clean_text(title) or "Culture Générale"
    if title.lower().startswith("quiz "):
        title=title[5:].strip()
    if len(title)>22: title=title[:22].rstrip()+"…"
    cfg=_layout("quiz")
    tf=get_font(int(cfg.get("title_size",46)))
    label=f"QUIZ {title.upper()}"
    tw=text_width(draw,label,tf)
    icon_size=int(cfg.get("face_size",30)); total_w=tw+max(46,icon_size+28)
    x=max(42,(WIDTH-total_w)/2)
    y=int(cfg.get("title_y",42))+int(4*math.sin(float(phase)*math.pi*2))
    draw.text((x+3,y+5),label,font=tf,fill=(0,0,0))
    draw.text((x,y),label,font=tf,fill="white")
    if cfg.get("face_show",True):
        fx=int(x+tw+max(25,icon_size+8))+int(cfg.get("face_x",0)); fy=int(y+25)+int(cfg.get("face_y",0))
        draw_thinking_face(draw,theme,fx,fy,icon_size,phase,style=cfg.get("face_style","Réflexion"),color=_hex_rgb(cfg.get("face_color"),theme["accent"]))
    sf=get_font(int(cfg.get("score_size",31))); score=f"{q_num}/{total}"; sw=text_width(draw,score,sf); sh=text_height(sf,score)
    by=int(cfg.get("score_y",112)); bw=sw+40; bh=max(42,sh+18); bx=(WIDTH-bw)//2; radius=int(cfg.get("score_radius",22))
    score_bg=_hex_rgb(cfg.get("score_bg"),(7,13,28)); score_color=_hex_rgb(cfg.get("score_color"),theme["accent"])
    draw.rounded_rectangle((bx,by,bx+bw,by+bh),radius=radius,fill=score_bg,outline=score_color,width=int(cfg.get("score_border",2)))
    draw.text(((WIDTH-sw)/2,by+(bh-sh)/2-2),score,font=sf,fill=score_color)


def draw_timer(draw, theme, timer, fraction=1.0, pulse=0.0):
    """Minuteur entièrement personnalisable depuis l'éditeur."""
    cfg=_layout("quiz")
    color=_hex_rgb(cfg.get("timer_color"),theme["accent"])
    if timer<=1: color=_hex_rgb(cfg.get("timer_color"),theme["danger"])
    cx=int(cfg.get("timer_x",540)); cy=int(cfg.get("timer_y",1045)); r=max(18,int(cfg.get("timer_size",58))); pr=int(3+10*clamp(pulse))
    style=str(cfg.get("timer_style","Cercle")); text_size=max(18,int(cfg.get("timer_text_size",55)))
    if style in ("Cercle","Anneau"):
        draw.ellipse((cx-r-pr,cy-r-pr,cx+r+pr,cy+r+pr),outline=color,width=3)
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(7,12,26),outline="white",width=4)
        draw.arc((cx-r+6,cy-r+6,cx+r-6,cy+r-6),-90,-90+int(360*clamp(fraction)),fill=color,width=max(4,int(r*.16)))
    elif style in ("Carré","Barre"):
        draw.rounded_rectangle((cx-r,cy-r,cx+r,cy+r),radius=max(8,int(r*.22)),fill=(7,12,26),outline=color,width=4)
        draw.rectangle((cx-r+6,cy+r-10-int((2*r-16)*clamp(fraction)),cx+r-6,cy+r-6),fill=color)
    elif style=="Pill":
        w=int(r*2.7); h=int(r*1.15)
        draw.rounded_rectangle((cx-w,cy-h,cx+w,cy+h),radius=h,fill=(7,12,26),outline=color,width=4)
        draw.rounded_rectangle((cx-w+6,cy+h-10,cx-w+6+int((2*w-12)*clamp(fraction)),cy+h-6),radius=4,fill=color)
    elif style=="Points":
        for n in range(7):
            x=cx-r+int((2*r)*n/6)
            rr=max(3,int(r*.07))
            draw.ellipse((x-rr,cy-rr,x+rr,cy+rr),fill=color if n<=int(6*clamp(fraction)) else (90,100,120))
    elif style=="Minimal":
        draw.line((cx-r,cy,cx-r+int(2*r*clamp(fraction)),cy),fill=color,width=max(3,int(r*.10)))
    else:
        draw.line((cx-r,cy,cx+r,cy),fill=color,width=max(2,int(r*.08)))
    ts=str(timer); tf=get_font(text_size); th=text_height(tf,ts)
    draw.text((cx-text_width(draw,ts,tf)/2,cy-th/2-3),ts,font=tf,fill=color)
    if cfg.get("timer_show_label",True):
        lbl=clean_text(cfg.get("timer_label","RÉFLÉCHIS")); lf=get_font(int(cfg.get("timer_label_size",23))); lw=text_width(draw,lbl,lf)
        ly=cy+r+18
        draw.text(((WIDTH-lw)/2,ly),lbl,font=lf,fill=_hex_rgb(cfg.get("timer_label_color"),color))

def _hex_rgb(value, fallback=(255,255,255)):
    try:
        h=str(value).strip().lstrip("#")
        if len(h)==6:
            return tuple(int(h[i:i+2],16) for i in (0,2,4))
    except Exception:
        pass
    return fallback

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qvp_settings.json")

def _load_saved_settings():
    if st.session_state.get("_qvp_settings_loaded"):
        return
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved=json.load(f)
        for k,v in saved.items():
            if k not in st.session_state:
                st.session_state[k]=v
    except Exception:
        pass
    st.session_state["_qvp_settings_loaded"]=True

def _save_settings():
    keys=[]
    for k in st.session_state.keys():
        if k.startswith(("q_","v_")):
            keys.append(k)
    data={}
    for k in keys:
        v=st.session_state.get(k)
        if isinstance(v,(str,int,float,bool)):
            data[k]=v
    try:
        tmp=SETTINGS_FILE+".tmp"
        with open(tmp,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
        os.replace(tmp,SETTINGS_FILE)
    except Exception:
        pass

_load_saved_settings()

def _layout(module="quiz"):
    """Réglages visuels pilotés entièrement par l'interface et persistants."""
    prefix="v_" if module=="vocab" else "q_"
    defaults={
        "show_title":True,"title_y":42,"title_size":46,
        "question_y":205,"question_size":47,"question_box_radius":28,
        "answer_y":405,"answer_h":91,"answer_gap":12,"answer_size":30,"answer_radius":20,
        "timer_y":1045,"timer_x":540,"timer_size":58,"timer_style":"Cercle","timer_color":"#FFCD40","timer_text_size":55,"timer_label_y":1110,"timer_label_size":23,"timer_show_label":True,"timer_label":"RÉFLÉCHIS","timer_label_color":"#FFCD40",
        "face_size":30,"face_x":0,"face_y":0,"face_style":"Réflexion","face_color":"#FFCD40","face_show":True,
        "score_y":112,"score_size":31,"score_color":"#FFCD40","score_bg":"#070D1C","score_radius":22,"score_border":2,
        "explanation_y":1135,"explanation_h":380,"explanation_size":31,
        "explanation_radius":24,"show_explanation":True,"show_timer":True,
        "animation":"Glissement","animation_speed":1.0,"animation_strength":1.0,
        "bg_opacity":18,"motion_strength":1.0,"bg_zoom":1.02,"bg_x":0,"bg_y":0,
        "primary":"#FFCD40","answer":"#11305B","answer2":"#143765",
        "correct":"#2EDA7B","text":"#FFFFFF","muted":"#A5B5D0",
    }
    if module=="vocab":
        defaults.update({"title_y":70,"title_size":32,"question_y":500,"question_size":88,
                         "answer_y":760,"answer_size":58,"timer_y":1045,"timer_size":58,
                         "animation":"Glissement","primary":"#FFCD40"})
    out={}
    for k,v in defaults.items():
        out[k]=st.session_state.get(prefix+k,v)
    return out

def _draw_question_rich(draw, question, theme, y=205, phase=0.0):
    cfg=_layout("quiz")
    f=get_font(cfg["question_size"]); lines=wrap_text(question,f,900)[:3]; hi=_highlight_words(question); yy=int(cfg["question_y"])
    box_top=yy-18; box_bottom=yy+len(lines)*int(cfg["question_size"]*1.18)+12
    radius=int(cfg["question_box_radius"])
    box_w=int(cfg.get("question_width",964)); center_x=int(cfg.get("question_x",540)); left=max(20,center_x-box_w//2); right=min(WIDTH-20,center_x+box_w//2)
    draw.rounded_rectangle((left,box_top,right,box_bottom),radius=radius,fill=(6,12,28,218),outline=_hex_rgb(cfg["primary"],theme["accent"]),width=2)
    for line in lines:
        words=line.split(); widths=[text_width(draw,w,f) for w in words]; space=text_width(draw," ",f)
        totalw=sum(widths)+space*max(0,len(words)-1)
        x=center_x-totalw/2+int(5*math.sin(phase*math.pi*2*cfg["motion_strength"]))
        for w,ww in zip(words,widths):
            key=w.strip(".,?!:;()[]«»\"'").lower(); fill=_hex_rgb(cfg["primary"],theme["accent"]) if key in hi else _hex_rgb(cfg["text"],(255,255,255))
            draw.text((x+2,yy+3),w,font=f,fill=(0,0,0)); draw.text((x,yy),w,font=f,fill=fill)
            x+=ww+space
        yy+=int(cfg["question_size"]*1.18)
    return box_bottom

def _draw_answers(draw, options, theme, entrance=1.0, correct_idx=None, reveal_progress=0.0, phase=0.0):
    cfg=_layout("quiz"); left,right=62,1018
    card_h=int(cfg["answer_h"]); gap=int(cfg["answer_gap"]); start_y=int(cfg["answer_y"]); f_opt=get_font(cfg["answer_size"])
    anim=str(cfg["animation"]); speed=max(0.25,float(cfg["animation_speed"])); strength=max(0.0,float(cfg["animation_strength"]))
    for i,opt in enumerate(options[:4]):
        if anim=="Aucune": local=1.0
        else: local=ease_out(clamp((entrance-i*0.07*speed)/(0.48/max(.25,speed))))
        offset=int((1-local)*52*strength) if anim=="Glissement" else 0
        extra=int(7*ease_back(clamp(reveal_progress))) if correct_idx is not None and i==correct_idx else 0
        xpad=0
        if anim=="Glissement": xpad=int((1-local)*40*strength)
        elif anim=="Pop": extra += int((1-local)*10*strength)
        y=start_y+i*(card_h+gap)+offset+int(2*math.sin((phase+i*.13)*math.pi*2*cfg["motion_strength"]))
        correct=(correct_idx is not None and i==correct_idx)
        if correct:
            fill=_hex_rgb(cfg["correct"],theme["success"]); outline=(255,255,255); width=4
        else:
            fill=_hex_rgb(cfg["answer"],(17,48,91)) if i%2==0 else _hex_rgb(cfg["answer2"],(20,55,101)); outline=(210,225,250); width=2
            if correct_idx is not None:
                fill=tuple(int(c*.55) for c in fill); outline=tuple(int(c*.55) for c in outline)
        draw.rounded_rectangle((left-extra+xpad,y-extra,right+extra+xpad,y+card_h+extra),radius=int(cfg["answer_radius"]),fill=fill,outline=outline,width=width)
        badge_size=max(44,int(cfg["answer_size"]*1.75)); bw=badge_size; bh=badge_size; bx=82+xpad; by=int(y+(card_h-bh)/2)
        badge_fill=_hex_rgb(cfg["primary"],theme["accent"]) if not correct else "white"
        draw.rounded_rectangle((bx,by,bx+bw,by+bh),radius=min(int(badge_size*.28),int(cfg["answer_radius"]*.8)),fill=badge_fill)
        lf=get_font(max(18,min(42,int(cfg["answer_size"]*1.02)))); letter=chr(65+i); lc=theme["card"] if not correct else _hex_rgb(cfg["correct"],theme["success"])
        lh=text_height(lf,letter); draw.text((bx+(bw-text_width(draw,letter,lf))/2,by+(bh-lh)/2-2),letter,font=lf,fill=lc)
        text_x=154+xpad; maxw=right-text_x-26; lines=wrap_text(clean_text(opt),f_opt,maxw)[:2]
        th=sum(text_height(f_opt,z) for z in lines)+max(0,len(lines)-1)*3; ty=y+(card_h-th)/2-2
        for line in lines:
            draw.text((text_x+2,ty+3),line,font=f_opt,fill=(0,0,0)); draw.text((text_x,ty),line,font=f_opt,fill=_hex_rgb(cfg["text"],(255,255,255))); ty+=text_height(f_opt,line)+3
        if correct:
            cx=right-38+xpad; cy=y+card_h/2; rr=19
            draw.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill="white")
            draw.line((cx-8,cy,cx-2,cy+7),fill=_hex_rgb(cfg["correct"],theme["success"]),width=4)
            draw.line((cx-2,cy+7,cx+10,cy-9),fill=_hex_rgb(cfg["correct"],theme["success"]),width=4)

def draw_explanation_panel(draw, theme, explanation, progress=1.0):
    cfg=_layout("quiz"); y1=int(cfg["explanation_y"]); y2=min(1710,y1+int(cfg["explanation_h"])); p=ease_out(progress)
    primary=_hex_rgb(cfg["primary"],theme["accent"])
    draw.rounded_rectangle((58,y1,1022,y2),radius=int(cfg["explanation_radius"]),fill=(6,13,28),outline=primary,width=2)
    draw.rounded_rectangle((58,y1,58+int(964*p),y1+6),radius=3,fill=primary)
    cx,cy=98,y1+57
    draw.ellipse((cx-16,cy-22,cx+16,cy+10),outline=primary,width=3)
    draw.line((cx-10,cy+16,cx+10,cy+16),fill=primary,width=3); draw.line((cx-7,cy+23,cx+7,cy+23),fill=primary,width=3)
    draw.text((145,y1+32),"EXPLICATION",font=get_font(min(36,int(cfg["explanation_size"]*.95))),fill=primary)
    f=get_font(int(cfg["explanation_size"])); lines=wrap_text(explanation or "Bravo !",f,865)[:5]; yy=y1+95
    max_visible=max(1,int(len(lines)*p+0.999))
    for line in lines[:max_visible]:
        tw=text_width(draw,line,f); draw.text(((WIDTH-tw)/2,yy),line,font=f,fill=_hex_rgb(cfg["text"],(255,255,255))); yy+=int(cfg["explanation_size"]*1.35)

def draw_inline_timer(draw, theme, cx, cy, timer, fraction=1.0, module="quiz"):
    cfg=_layout(module)
    color=_hex_rgb(cfg.get("timer_color"),theme["accent"])
    if timer is not None and timer <= 1:
        color=_hex_rgb(cfg.get("timer_color"),theme["danger"])
    r=max(18,int(cfg.get("timer_size",58)*0.62))
    style=str(cfg.get("timer_style","Cercle"))
    if style=="Carré":
        draw.rounded_rectangle((cx-r,cy-r,cx+r,cy+r),radius=max(8,int(r*.22)),fill=(7,12,26),outline=color,width=3)
        draw.rectangle((cx-r+5,cy+r-7-int((2*r-14)*clamp(fraction)),cx+r-5,cy+r-5),fill=color)
    elif style=="Pill":
        w=int(r*1.35); h=int(r*.65)
        draw.rounded_rectangle((cx-w,cy-h,cx+w,cy+h),radius=h,fill=(7,12,26),outline=color,width=3)
        draw.rounded_rectangle((cx-w+5,cy+h-7,cx-w+5+int((2*w-10)*clamp(fraction)),cy+h-4),radius=3,fill=color)
    else:
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(7,12,26),outline=color,width=3)
        draw.arc((cx-r+5,cy-r+5,cx+r-5,cy+r-5),-90,-90+int(360*clamp(fraction)),fill=color,width=5)
    tf=get_font(max(24,int(cfg.get("timer_text_size",55)*.72)))
    ts=str(timer)
    th=text_height(tf,ts)
    draw.text((cx-text_width(draw,ts,tf)/2,cy-th/2-2),ts,font=tf,fill=color)


def draw_vocab_cumulative_frame(items, active_idx, theme_name, channel, bg_file=None, timer=None, timer_fraction=1.0, reveal=False, motion=0.0, video_title="Voyage"):
    """Style 2 validé : une seule page cumulative.
    Mot à gauche -> temps de réflexion au centre -> traduction en face après révélation.
    Les lignes terminées restent visibles et les mots futurs restent cachés.
    Les réglages de l'éditeur pilotent aussi ce mode.
    """
    cfg=_layout("vocab"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    alpha=int(clamp(cfg.get("bg_opacity",18),0,90))
    if alpha: base=Image.alpha_composite(base.convert("RGBA"),Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha))).convert("RGB")
    img=add_top_glow(base,theme,1.0+0.18*math.sin(float(motion)*math.pi*2)); draw=ImageDraw.Draw(img)
    total=max(1,len(items)); visible_items=items[:min(active_idx+1,total)]
    if cfg.get("show_title",True):
        title_y=int(cfg.get("title_y",70)); title_size=int(cfg.get("title_size",32))
        draw.text((55,title_y),clean_text(video_title or "Vocabulaire"),font=get_font(title_size),fill=_hex_rgb(cfg.get("text"),(255,255,255)))
    score_y=int(cfg.get("score_y",112)); score_size=int(cfg.get("score_size",31)); score=f"{min(active_idx+1,total)}/{total}"
    draw.rounded_rectangle((WIDTH-150,score_y-8,WIDTH-55,score_y+score_size+10),radius=int(cfg.get("score_radius",22)),fill=_hex_rgb(cfg.get("score_bg"),(7,13,28)),outline=_hex_rgb(cfg.get("score_color"),theme["accent"]),width=2)
    draw.text((WIDTH-135,score_y),score,font=get_font(score_size),fill=_hex_rgb(cfg.get("score_color"),theme["accent"]))
    top=int(cfg.get("answer_y",760)); row_h=max(70,int(cfg.get("answer_h",91))); gap=max(2,int(cfg.get("answer_gap",12)))
    left=42; right=1038; word_size=int(cfg.get("question_size",88)); trans_size=int(cfg.get("answer_size",58)); radius=int(cfg.get("answer_radius",20))
    wf=get_font(word_size); tf=get_font(trans_size); small=get_font(22)
    if len(visible_items)>1:
        max_bottom=1770; needed=top+len(visible_items)*row_h+(len(visible_items)-1)*gap
        if needed>max_bottom:
            row_h=max(58,int((max_bottom-top-(len(visible_items)-1)*gap)/len(visible_items)))
            wf=get_font(max(30,min(word_size,int(row_h*.52)))); tf=get_font(max(24,min(trans_size,int(row_h*.40))))
    for i,item in enumerate(visible_items):
        y=top+i*(row_h+gap); active=(i==active_idx); answered=(i<active_idx) or (i==active_idx and reveal)
        fill=_hex_rgb(cfg.get("answer2" if i%2 else "answer"),theme["card2"]); outline=_hex_rgb(cfg.get("primary"),theme["accent"]) if active else (80,100,130)
        draw.rounded_rectangle((left,y,right,y+row_h),radius=radius,fill=fill,outline=outline,width=3 if active else 1)
        draw.text((62,y+int(row_h*.18)),str(i+1),font=small,fill=_hex_rgb(cfg.get("primary"),theme["accent"]))
        fr=clean_text(item.get("fr", "")); tr=clean_text(item.get("trad", "")); wy=y+int(row_h*.18)
        for line in wrap_text(fr,wf,390)[:2]:
            draw.text((125,wy),line,font=wf,fill=_hex_rgb(cfg.get("text"),(255,255,255))); wy+=int(wf.size*1.02)
        if active and cfg.get("show_timer",True) and timer is not None:
            draw_inline_timer(draw,theme,565,y+row_h//2,timer,timer_fraction,"vocab")
        elif active and not answered:
            draw.text((545,y+int(row_h*.28)),"…",font=get_font(max(28,int(row_h*.38))),fill=_hex_rgb(cfg.get("muted"),theme["muted"]))
        if answered:
            for j,line in enumerate(wrap_text("✓ "+tr,tf,380)[:2]):
                draw.text((650,y+int(row_h*.17)+j*int(tf.size*1.02)),line,font=tf,fill=_hex_rgb(cfg.get("correct"),theme["success"]))
    draw_brand(draw,theme,channel,active_idx/max(1,total))
    draw.text((55,1860),"QuizVideo Pro  •  Vocabulaire Pro",font=get_font(21),fill=_hex_rgb(cfg.get("muted"),theme["muted"]))
    return img

def draw_style2_frame(items, active_idx, theme_name, channel, bg_file=None, timer=None, timer_fraction=1.0, answer_reveal=False, motion=0.0, video_title="Culture Générale"):
    """Quiz Style 2 demandé : une seule page cumulative qui se construit.

    Q1 apparaît seule avec son minuteur. Après révélation, sa bonne réponse reste
    visible. Q2 apparaît alors avec son minuteur, puis Q3, etc. Les questions
    futures restent cachées jusqu'à leur tour.
    """
    cfg=_layout("quiz"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    alpha=int(clamp(cfg["bg_opacity"],0,90))
    if alpha:
        base=Image.alpha_composite(base.convert("RGBA"),Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha))).convert("RGB")
    img=add_top_glow(base,theme,1.0+0.25*math.sin(float(motion)*math.pi*2)); draw=ImageDraw.Draw(img)
    total=len(items)
    visible_items=items[:min(active_idx+1,total)]
    rounded_text(draw,(55,42,1025,112),f"{video_title}  •  {min(active_idx+1,total)}/{total}",get_font(34),_hex_rgb(cfg["text"],(255,255,255)),_hex_rgb(cfg["primary"],theme["accent"]),2,24)

    # Les lignes apparaissent progressivement : aucune question future n'est affichée.
    top=145; row_h=112; gap=9; left=42; right=1038
    qf=get_font(31); af=get_font(28); small=get_font(23)
    for i,item in enumerate(visible_items):
        y=top+i*(row_h+gap)
        if y>1800: break
        active=(i==active_idx)
        answered=(i<active_idx) or (i==active_idx and answer_reveal)
        fill=_hex_rgb(cfg["answer2"] if i%2 else cfg["answer"],theme["card2"])
        outline=_hex_rgb(cfg["primary"],theme["accent"]) if active else (80,100,130)
        width=4 if active else 1
        draw.rounded_rectangle((left,y,right,y+row_h),radius=18,fill=fill,outline=outline,width=width)
        label=f"{i+1}/{total}"
        draw.text((65,y+13),label,font=small,fill=_hex_rgb(cfg["primary"],theme["accent"]))
        q=clean_text(item.get("question",""))
        q_lines=wrap_text(q,qf,545)[:2]
        qx=135; qy=y+10
        for line in q_lines:
            draw.text((qx,qy),line,font=qf,fill="white"); qy+=36

        a=""
        if answered:
            opts=item.get("options",[]); rc=clean_text(item.get("reponse_correcte","A")).upper()[:1]
            try: a=clean_text(opts["ABCD".index(rc)])
            except Exception: a=""
            if a:
                # La bonne réponse apparaît dans un badge vert, sans transformer
                # toute la question en vert.
                answer_lines=wrap_text("✓ "+a,af,315)[:2]
                ay=y+17
                badge_h=78 if len(answer_lines)==1 else 92
                draw.rounded_rectangle((680,y+16,1018,y+16+badge_h),radius=18,fill=_hex_rgb(cfg["correct"],theme["success"]),outline=_hex_rgb(cfg["correct"],theme["success"]),width=2)
                for line in answer_lines:
                    tw=text_width(draw,line,af); draw.text((850-tw/2,ay),line,font=af,fill="white"); ay+=34
        elif active:
            draw.text((700,y+31),"Réfléchis…",font=get_font(24),fill=_hex_rgb(cfg["muted"],theme["muted"]))
            if timer is not None and cfg["show_timer"]:
                draw_inline_timer(draw,theme,950,y+58,timer,timer_fraction,"quiz")

    draw_brand(draw,theme,channel,active_idx/max(1,total))
    draw.text((55,1860),"QuizVideo Pro  •  Vocabulaire Pro",font=get_font(21),fill=_hex_rgb(cfg["muted"],theme["muted"]))
    return img

def draw_quiz_frame(question, options, theme_name, q_num, total, channel, bg_file=None, entrance=1.0, timer=None, timer_fraction=1.0, correct_idx=None, reveal_progress=0.0, pulse=0.0, motion=0.0, video_title="Culture Générale", explanation=None, explanation_progress=0.0):
    cfg=_layout("quiz"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    # Assombrissement réglable : le fond reste visible mais le texte reste lisible.
    alpha=int(clamp(cfg["bg_opacity"],0,90))
    if alpha:
        ov=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha)); base=Image.alpha_composite(base.convert("RGBA"),ov).convert("RGB")
    phase=float(motion or 0.0)*max(.25,float(cfg["motion_strength"]))
    scale=float(cfg.get("bg_zoom",1.02))+0.008*math.sin(phase*math.pi*2)
    nw,nh=int(WIDTH*scale),int(HEIGHT*scale); z=base.resize((nw,nh),Image.Resampling.LANCZOS)
    sx=max(0,min(nw-WIDTH,int((nw-WIDTH)*(0.5+0.12*math.sin(phase*math.pi*2)))+int(cfg.get("bg_x",0))))
    sy=max(0,min(nh-HEIGHT,int((nh-HEIGHT)*(0.5+0.10*math.cos(phase*math.pi*2)))+int(cfg.get("bg_y",0))))
    img=z.crop((sx,sy,sx+WIDTH,sy+HEIGHT)); img=add_top_glow(img,theme,1.0+0.55*pulse); draw=ImageDraw.Draw(img)
    for k in range(9):
        px=int((90+k*121+(phase*34*(1+k%3)))%1000)+40; py=int(250+((k*177+phase*55)%1420)); rr=2+(k%3); draw.ellipse((px-rr,py-rr,px+rr,py+rr),fill=_hex_rgb(cfg["primary"],theme["accent"]))
    if cfg["show_title"]:
        draw_header(draw,theme,q_num,total,video_title,phase)
    _draw_question_rich(draw,question,theme,y=int(cfg["question_y"]),phase=phase)
    _draw_answers(draw,options,theme,entrance,correct_idx,reveal_progress,phase)
    if timer is not None and cfg["show_timer"]:
        draw_timer(draw,theme,timer,timer_fraction,pulse)
    if correct_idx is not None and reveal_progress>0:
        rp=clamp(reveal_progress)
        if rp<0.45:
            alpha=int(95*(1-rp/0.45)); glow=Image.new("RGBA",(WIDTH,HEIGHT),(255,255,255,0)); gd=ImageDraw.Draw(glow); gd.rectangle((42,360,1038,870),outline=(255,255,255,alpha),width=8); glow=glow.filter(ImageFilter.GaussianBlur(12)); img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB"); draw=ImageDraw.Draw(img)
    if correct_idx is not None and explanation and explanation_progress>0 and cfg["show_explanation"]:
        draw_explanation_panel(draw,theme,explanation,explanation_progress)
    draw_brand(draw,theme,channel,(q_num-1)/max(1,total)); draw.text((55,1788),"QuizVideo Pro  •  Vocabulaire Pro",font=get_font(21),fill=_hex_rgb(cfg["muted"],theme["muted"]))
    return img

def draw_hook(text,theme_name,channel,bg_file=None,progress=1.0):
    theme=THEMES[theme_name]
    p=ease_back(progress)
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.2*p)
    draw=ImageDraw.Draw(img)
    # subtle focus circle
    r=int(210*p)
    draw.ellipse((540-r,430-r,540+r,430+r),outline=(*theme["accent"],),width=4)
    badge_w=500; bx=(WIDTH-badge_w)//2; by=250-int(30*(1-p))
    rounded_text(draw,(bx,by,bx+badge_w,by+76),"TESTE-TOI",get_font(34),theme["accent"],None,0,34)
    draw_lightning_icon(draw,theme,bx+42,by+38,18)
    f=get_font(76)
    lines=wrap_text(text,f,850)[:3]
    y=690-int(90*(1-p))
    for line in lines:
        tw=text_width(draw,line,f)
        draw.text(((WIDTH-tw)/2+5,y+6),line,font=f,fill=(0,0,0))
        draw.text(((WIDTH-tw)/2,y),line,font=f,fill="white")
        y+=108
    draw_brand(draw,theme,channel)
    sf=get_font(23)
    draw.text((55,1860),"QuizVideo Pro  •  Vocabulaire Pro",font=sf,fill=theme["muted"])
    return img

def draw_explanation_scene(question,answer,explanation,theme_name,channel,bg_file=None,active_word=-1,pulse=0.0,progress=1.0,q_num=1,total=1,video_title="Culture Générale"):
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.0+0.3*pulse)
    draw=ImageDraw.Draw(img)
    draw_header(draw,theme,q_num,total,video_title)
    # Keep the quiz visible during the explanation, with the correct answer highlighted.
    rounded_text(draw,(60,620,1020,738),f"✓ {answer}",get_font(42),theme["success"],None,0,30)
    words=clean_text(explanation or "Bravo !").split()
    f=get_font(45)
    max_w=900
    lines=[]; cur=[]
    for w in words:
        cand=w if not cur else " ".join(cur+[w])
        if text_width(draw,cand,f)<=max_w: cur.append(w)
        else:
            if cur: lines.append(cur)
            cur=[w]
    if cur: lines.append(cur)
    lines=lines[:5]
    # Explanation deliberately sits low in the frame, like a compact knowledge card.
    box_y1,box_y2=790,1175
    draw.rounded_rectangle((60,box_y1,1020,box_y2),radius=30,fill=theme["card"],outline=theme["accent"],width=3)
    draw.text((145,820),"EXPLICATION",font=get_font(32),fill=theme["accent"])
    # ampoule vectorielle
    draw.ellipse((100,812,128,844),outline=theme["accent"],width=3)
    draw.line((106,850,122,850),fill=theme["accent"],width=3)
    draw.line((110,856,118,856),fill=theme["accent"],width=3)
    yy=885
    idx=0
    for line in lines:
        widths=[text_width(draw,w,f) for w in line]
        space=text_width(draw," ",f); totalw=sum(widths)+space*max(0,len(line)-1)
        x=(WIDTH-totalw)/2
        for w,ww in zip(line,widths):
            active=(idx==active_word)
            col=theme["accent"] if active else "white"
            if active:
                pad=7+int(4*pulse)
                draw.rounded_rectangle((x-pad,yy-5,x+ww+pad,yy+55),radius=12,fill=theme["card2"],outline=theme["accent"],width=2)
            draw.text((x,yy),w,font=f,fill=col)
            x+=ww+space; idx+=1
        yy+=58
    draw_brand(draw,theme,channel,progress)
    sf=get_font(23)
    draw.text((55,1860),"QuizVideo Pro  •  Vocabulaire Pro",font=sf,fill=theme["muted"])
    return img


def draw_vocab_frame(items,idx,langue,theme_name,channel,bg_file=None,phase="mot",timer=None,timer_fraction=1.0,entrance=1.0):
    cfg=_layout("vocab"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    alpha=int(clamp(cfg["bg_opacity"],0,90))
    if alpha: base=Image.alpha_composite(base.convert("RGBA"),Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha))).convert("RGB")
    img=add_top_glow(base,theme); draw=ImageDraw.Draw(img)
    rounded_text(draw,(55,int(cfg["title_y"]),430,int(cfg["title_y"])+65),f"VOCABULAIRE • {idx+1}/{len(items)}",get_font(int(cfg["title_size"])),_hex_rgb(cfg["answer"],theme["card"]),_hex_rgb(cfg["primary"],theme["accent"]),2,26)
    item=items[idx]; fr=clean_text(item.get("fr","")); tr=clean_text(item.get("trad","")); p=ease_out(entrance)
    fbig=get_font(int(cfg["question_size"])); y=int(cfg["question_y"])+int((1-p)*80)
    draw.text(((WIDTH-text_width(draw,fr,fbig))/2,y),fr,font=fbig,fill=_hex_rgb(cfg["primary"],theme["accent"]))
    if phase in ("translation","reveal"):
        ft=get_font(int(cfg["answer_size"])); lines=wrap_text(tr,ft,850); yy=int(cfg["answer_y"])
        for line in lines: draw.text(((WIDTH-text_width(draw,line,ft))/2,yy),line,font=ft,fill=_hex_rgb(cfg["text"],(255,255,255))); yy+=75
    if phase=="countdown" and timer is not None and cfg["show_timer"]: draw_timer(draw,theme,timer,timer_fraction,0.15)
    draw_brand(draw,theme,channel,idx/max(1,len(items))); return img


# ------------------------- TTS ------------------------------
async def _tts(text,voice,path,rate="+15%"):
    comm=edge_tts.Communicate(clean_text(text),voice,rate=rate,boundary="WordBoundary")
    audio=bytearray(); words=[]
    async for chunk in comm.stream():
        if chunk["type"]=="audio": audio.extend(chunk["data"])
        elif chunk["type"]=="WordBoundary":
            word=clean_text(chunk.get("text",""))
            if word:
                start=chunk["offset"]/10_000_000; dur=chunk["duration"]/10_000_000
                words.append({"text":word,"start":start,"end":start+dur})
    with open(path,"wb") as f: f.write(audio)
    return words

def run_async(coro):
    try: loop=asyncio.get_event_loop()
    except RuntimeError:
        loop=asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    if loop.is_running():
        nl=asyncio.new_event_loop()
        try: return nl.run_until_complete(coro)
        finally: nl.close()
    return loop.run_until_complete(coro)

def synthesize_audio(text,voice,path,rate="+15%"):
    return run_async(_tts(text,voice,path,rate))

def audio_duration(path):
    res=subprocess.run([get_ffmpeg(),"-i",path],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    m=re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)",res.stderr)
    if not m: return 1.5
    h,mi,sec=m.groups(); return float(h)*3600+float(mi)*60+float(sec)

# ------------------------- SFX ------------------------------
def make_sfx(tmpdir):
    tic=os.path.join(tmpdir,"tic.wav"); ding=os.path.join(tmpdir,"ding.wav")
    with wave.open(tic,"w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(int(44100*.10)):
            v=int(13000*math.sin(2*math.pi*1100*i/44100)*math.exp(-i/800)); f.writeframes(struct.pack("<h",v))
    with wave.open(ding,"w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(int(44100*.45)):
            v=int(11500*(math.sin(2*math.pi*1318*i/44100)+math.sin(2*math.pi*1568*i/44100))*math.exp(-i/4500))
            f.writeframes(struct.pack("<h",max(-32767,min(32767,v))))
    return tic,ding

def make_sfx_countdown(tic,tmpdir):
    # Un tic à chaque seconde pendant 3 s. Le son final est ajouté séparément
    # pour marquer clairement la fin du temps de réflexion.
    out=os.path.join(tmpdir,"countdown.wav")
    cmd=[get_ffmpeg(),"-y","-i",tic,"-filter_complex","[0:a]adelay=0|0[a0];[0:a]adelay=1000|1000[a1];[0:a]adelay=2000|2000[a2];[a0][a1][a2]amix=inputs=3:duration=longest","-t","3.12",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return out

def make_end_tick(tic,ding,tmpdir):
    out=os.path.join(tmpdir,"reflection_end.wav")
    cmd=[get_ffmpeg(),"-y","-i",ding,"-filter_complex","[0:a]volume=0.75[a]","-map","[a]","-t","0.45",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return out

def make_suspense_music(duration,tmpdir,name,volume=0.08):
    """Petite nappe de suspense générée localement : aucun fichier musical externe."""
    duration=max(0.2,float(duration))
    out=os.path.join(tmpdir,f"{name}.wav")
    vol=max(0.0,min(0.25,float(volume)))
    fade_out=max(0.05,min(0.35,duration*0.18))
    fade_start=max(0.0,duration-fade_out)
    filt=(
        f"[0:a]volume={vol:.3f},lowpass=f=900,afade=t=in:st=0:d=0.12,afade=t=out:st={fade_start:.3f}:d={fade_out:.3f}[a];"
        f"[1:a]volume={vol*0.42:.3f},lowpass=f=1200,afade=t=in:st=0:d=0.12,afade=t=out:st={fade_start:.3f}:d={fade_out:.3f}[b];"
        "[a][b]amix=inputs=2:duration=longest:dropout_transition=0"
    )
    cmd=[get_ffmpeg(),"-y",
         "-f","lavfi","-i",f"sine=frequency=92:sample_rate=44100:duration={duration:.3f}",
         "-f","lavfi","-i",f"sine=frequency=138:sample_rate=44100:duration={duration:.3f}",
         "-filter_complex",filt,"-c:a","pcm_s16le",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return out

def mix_background_music(voice_path,music_path,output,voice_volume=1.0,music_volume=0.10):
    """Mixe la voix et une musique de fond discrète sans écraser la voix."""
    filt=(f"[0:a]volume={voice_volume:.3f}[v];"
          f"[1:a]volume={music_volume:.3f}[m];"
          "[v][m]amix=inputs=2:duration=first:dropout_transition=0")
    cmd=[get_ffmpeg(),"-y","-i",voice_path,"-i",music_path,"-filter_complex",filt,
         "-c:a","aac","-b:a","160k","-shortest",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return output

def mix_voice_sfx(voice_path,sfx_path,output,delay_ms=0,sfx_volume=0.65):
    filt=f"[1:a]volume={sfx_volume},adelay={delay_ms}|{delay_ms}[s];[0:a][s]amix=inputs=2:duration=longest:dropout_transition=0"
    cmd=[get_ffmpeg(),"-y","-i",voice_path,"-i",sfx_path,"-filter_complex",filt,"-c:a","aac","-b:a","160k","-shortest",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def concat_audio_files(audio_files, output):
    """Concatène les segments audio dans l'ordre et réencode en AAC/M4A."""
    inputs=[]
    for p in audio_files: inputs += ["-i",p]
    labels="".join(f"[{i}:a]" for i in range(len(audio_files)))
    filt=f"{labels}concat=n={len(audio_files)}:v=0:a=1[a]"
    cmd=[get_ffmpeg(),"-y",*inputs,"-filter_complex",filt,"-map","[a]","-c:a","aac","-b:a","160k","-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return output


# ---------------------- Video encoding ----------------------
def make_image_video(frames,output,fps=30):
    list_path=output+".txt"
    with open(list_path,"w",encoding="utf-8") as f:
        for path,duration in frames:
            f.write(f"file '{path.replace(chr(92),'/')}'\n")
            f.write(f"duration {max(0.033,float(duration))}\n")
        if frames: f.write(f"file '{frames[-1][0].replace(chr(92),'/')}'\n")
    cmd=[get_ffmpeg(),"-y","-f","concat","-safe","0","-i",list_path,"-vf",f"fps={fps},format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","22",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def mux_audio(video,audio,output,volume=1.0):
    cmd=[get_ffmpeg(),"-y","-i",video,"-i",audio,"-filter:a",f"volume={volume}","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def make_segment(frames,audio,output,tmpdir,volume=1.0):
    raw=os.path.join(tmpdir,os.path.basename(output)+".raw.mp4")
    make_image_video(frames,raw,FPS); return mux_audio(raw,audio,output,volume)

def concat_videos(clips,output,tmpdir):
    lst=os.path.join(tmpdir,"concat.txt")
    with open(lst,"w",encoding="utf-8") as f:
        for p in clips: f.write(f"file '{p.replace(chr(92),'/')}'\n")
    cmd=[get_ffmpeg(),"-y","-f","concat","-safe","0","-i",lst,"-c","copy","-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def save_frames(frames,tmpdir,prefix):
    out=[]
    for i,(img,dur) in enumerate(frames):
        p=os.path.join(tmpdir,f"{prefix}_{i:04d}.png"); img.save(p); out.append((p,dur))
    return out

def frames_for_audio(audio_path,words,frame_fn,duration=None):
    dur=duration or audio_duration(audio_path)
    if not words: return [(frame_fn(-1,0.0),dur)]
    out=[]
    boundaries=[max(0.0,w["start"]) for w in words]
    if boundaries[0]>0.03: out.append((frame_fn(-1,0.0),min(boundaries[0],dur)))
    for i,start in enumerate(boundaries):
        end=boundaries[i+1] if i+1<len(boundaries) else dur
        if end>start: out.append((frame_fn(i,0.15),end-start))
    return out

# ------------------------ Gemini ----------------------------
def parse_json(text):
    text = (text or "").strip().replace("```json", "").replace("```", "").strip()
    # Gemini peut parfois ajouter une courte phrase avant/après le JSON.
    # On récupère le premier tableau JSON complet.
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end <= start:
        raise ValueError("Gemini n'a pas renvoyé un JSON valide.")
    return json.loads(text[start:end + 1])

def _gemini_wait_seconds(error_text, default=5.0):
    """Extrait 'retry in XXs' du message Gemini quand il est présent."""
    text = str(error_text or "")
    patterns = [
        r"retry in\s*([0-9]+(?:\.[0-9]+)?)s",
        r"retry_delay.*?([0-9]+(?:\.[0-9]+)?)s",
        r"([0-9]+(?:\.[0-9]+)?)\s*seconds",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            try:
                return max(1.0, min(60.0, float(m.group(1)) + 0.5))
            except Exception:
                pass
    return max(1.0, min(60.0, float(default)))

def _is_gemini_quota_error(error_text):
    text = str(error_text or "").upper()
    return any(token in text for token in [
        "429", "RESOURCE_EXHAUSTED", "QUOTA EXCEEDED", "RATE LIMIT", "TOO MANY REQUESTS"
    ])

def gemini_generate_text(prompt):
    """Un seul appel Gemini par clic, sans retry automatique.

    Les erreurs 429 sont volontairement remontées immédiatement : refaire
    plusieurs appels automatiquement consomme le quota et peut aggraver
    le problème. Un cooldown global de 13 s aide aussi à rester sous une
    limite de 5 requêtes/minute.
    """
    now = time.time()
    cooldown = 13.0
    last_attempt = float(st.session_state.get("_gemini_last_attempt", 0) or 0)
    remaining = cooldown - (now - last_attempt)
    if remaining > 0:
        raise RuntimeError(
            f"Patiente encore environ {int(math.ceil(remaining))} s avant une nouvelle génération. "
            "Une seule requête Gemini est envoyée par clic."
        )

    # Marqué AVANT l'appel : même si Gemini renvoie 429, un double-clic
    # ou plusieurs reruns ne déclencheront pas immédiatement d'autres appels.
    st.session_state._gemini_last_attempt = now

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = getattr(response, "text", None)
        if not text:
            raise ValueError("Gemini a renvoyé une réponse vide.")
        return text, False
    except Exception as e:
        if _is_gemini_quota_error(e):
            raw=str(e)
            lower=raw.lower()
            # Une limite quotidienne ne se résout pas avec un simple cooldown.
            if any(token in lower for token in ["per day", "per_day", "daily", "requestsperday", "generate_requests_per_day"]):
                msg=(
                    "⏳ Limite quotidienne Gemini atteinte. Il ne faut pas relancer plusieurs fois : "
                    "attends le prochain renouvellement du quota, puis fais un seul clic. "
                    "Cette version ne fait aucun retry automatique."
                )
            else:
                wait=_gemini_wait_seconds(e, default=13.0)
                msg=(
                    f"⏳ Limite Gemini de fréquence atteinte. Attends environ {int(math.ceil(wait))} s avant un seul nouveau clic. "
                    "Cette version ne fait aucun retry automatique."
                )
            raise RuntimeError(msg + f" Détail : {e}") from e
        raise

def parse_quiz_csv(uploaded_file):
    """Lit un CSV manuel avec colonnes question,A,B,C,D,reponse_correcte,explication."""
    raw = uploaded_file.getvalue().decode("utf-8-sig", errors="replace")
    try: dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
    except csv.Error: dialect = csv.excel
    reader = csv.DictReader(io.StringIO(raw), dialect=dialect)
    if not reader.fieldnames: raise ValueError("Le CSV ne contient pas de ligne d'en-tête.")
    fields = {f.strip().lower(): f for f in reader.fieldnames if f}
    required = ["question", "a", "b", "c", "d", "reponse_correcte"]
    missing = [f for f in required if f not in fields]
    if missing: raise ValueError("Colonnes manquantes : " + ", ".join(missing) + ".")
    data=[]
    for row in reader:
        q=clean_text(row.get(fields["question"],"")); opts=[clean_text(row.get(fields[k],"")) for k in ["a","b","c","d"]]
        ans=clean_text(row.get(fields["reponse_correcte"],"A")).upper()[:1]
        exp=clean_text(row.get(fields["explication"],"")) if "explication" in fields else ""
        if q and all(opts) and ans in "ABCD": data.append({"question":q,"options":opts,"reponse_correcte":ans,"explication":exp})
    if not data: raise ValueError("Aucune question valide trouvée dans le CSV.")
    return data[:10]

def csv_template():
    return "question,A,B,C,D,reponse_correcte,explication\nQuelle est la capitale de la France ?,Paris,Londres,Rome,Berlin,A,Paris est la capitale de la France.\n"

def normalize_questions(data):
    """Normalise plusieurs formats Gemini sans jeter les questions valides.

    Gemini peut renvoyer les 4 réponses soit dans ``options`` (liste), soit
    sous forme de clés A/B/C/D. La bonne réponse peut également être renvoyée
    comme lettre, ``A - texte`` ou comme texte de la réponse.
    """
    out=[]
    if not isinstance(data, list):
        return out

    for q in data:
        if not isinstance(q, dict):
            continue

        question = clean_text(q.get("question", q.get("question_text", "")))

        # Format principal : options = [A, B, C, D]
        raw_opts = q.get("options")
        if isinstance(raw_opts, dict):
            opts = [raw_opts.get(k, "") for k in "ABCD"]
        elif isinstance(raw_opts, (list, tuple)):
            opts = list(raw_opts)
        else:
            # Format alternatif : A/B/C/D directement dans l'objet.
            opts = [q.get(k, q.get(k.lower(), "")) for k in "ABCD"]

        opts = [clean_text(x) for x in opts]
        if len(opts) != 4 or not question or not all(opts):
            continue

        raw_ans = q.get("reponse_correcte", q.get("correct_answer", q.get("answer", "A")))
        raw_ans_text = clean_text(raw_ans)
        upper_ans = raw_ans_text.upper()

        # Lettre seule ou forme ``A - ...`` / ``A) ...``.
        m = re.match(r"^\s*([ABCD])(?:\s*[-:.)]\s*.*)?$", upper_ans)
        if m:
            ans = m.group(1)
        else:
            # Si Gemini renvoie directement le texte de la bonne option,
            # on retrouve son index dans les 4 réponses.
            ans = "A"
            for i, opt in enumerate(opts):
                if upper_ans == opt.upper():
                    ans = "ABCD"[i]
                    break

        exp = clean_text(q.get("explication", q.get("explanation", "")))
        out.append({
            "question": question,
            "options": opts,
            "reponse_correcte": ans,
            "explication": exp,
        })

    return out

# ------------------- Cache / édition sans quota -------------------
def _stable_hash(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

def _quiz_generation_key(nb, subject):
    return _stable_hash({"type": "quiz", "model": MODEL_NAME, "nb": int(nb), "subject": clean_text(subject).lower()})

def _vocab_generation_key(nb, subject, language):
    return _stable_hash({"type": "vocab", "model": MODEL_NAME, "nb": int(nb), "subject": clean_text(subject).lower(), "language": language})

def _save_quiz_editor(rows):
    cleaned=[]
    for row in rows:
        q=clean_text(row.get("Question", ""))
        opts=[clean_text(row.get(k, "")) for k in ["A","B","C","D"]]
        ans=clean_text(row.get("Bonne", "A")).upper()[:1]
        exp=clean_text(row.get("Explication", ""))
        if q and all(opts) and ans in "ABCD":
            cleaned.append({"question":q,"options":opts,"reponse_correcte":ans,"explication":exp})
    return cleaned[:15]

def _save_vocab_editor(rows):
    cleaned=[]
    for row in rows:
        fr=clean_text(row.get("Français", ""))
        tr=clean_text(row.get("Traduction", ""))
        if fr and tr:
            cleaned.append({"fr":fr,"trad":tr})
    return cleaned[:15]

api_key=st.sidebar.text_input("Clé API Gemini",type="password")
if api_key: genai.configure(api_key=api_key)
voice_rate=st.sidebar.slider("⚡ Vitesse voix",-10,25,0,format="%+d%%")
tts_rate=f"{voice_rate:+d}%"
st.sidebar.caption(f"Vitesse sélectionnée : {1.0 + voice_rate/100:.2f}×")
MODEL_NAME="gemini-3.6-flash"

MOTIVATION_LINES=[
    "🔥 Encore une ! Ne lâche rien.",
    "⚡ Plus vite ! La prochaine est difficile.",
    "🧠 Concentre-toi… tu peux faire mieux !",
    "🎯 Ton score monte… continue !",
    "💬 Abonne-toi pour le prochain quiz !",
]

def draw_motivation_scene(text,theme_name,channel,bg_file=None,progress=1.0,phase=0.0):
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.15)
    draw=ImageDraw.Draw(img)
    drift=int(22*math.sin(phase*math.pi*2))
    rounded_text(draw,(90+drift,310,990+drift,420),"PAUSE QUIZ",get_font(42),theme["accent"],None,0,30)
    draw_lightning_icon(draw,theme,128+drift,365,18)
    f=get_font(64)
    lines=wrap_text(text,f,850)[:3]
    y=650-int(40*(1-ease_out(phase)))
    for i,line in enumerate(lines):
        x=(WIDTH-text_width(draw,line,f))/2+int(28*math.sin((phase+i*0.15)*math.pi*2))
        draw.text((x,y),line,font=f,fill="white")
        y+=92
    draw_brand(draw,theme,channel,progress)
    # Signature discrète des deux modules de QuizVideo Pro.
    sf=get_font(23)
    draw.text((55,1860),"QuizVideo Pro  •  Vocabulaire Pro",font=sf,fill=theme["muted"])
    return img


# ============================================================
# FONDS THÉMATIQUES AUTOMATIQUES — 0 QUOTA GEMINI
# ============================================================
def _theme_keywords(topic):
    t=clean_text(topic).lower()
    groups={
        "espace":["espace","astronomie","planète","planetes","galaxie","univers","nasa","étoile","etoile"],
        "histoire":["histoire","antiquité","antiquite","moyen âge","moyen age","guerre","empire","roi","reine","pétra","petra","jordanie","monument","civilisation","temple"],
        "geographie":["géographie","geographie","pays","capitale","monde","continent","ville","voyage","aéroport","aeroport","avion","passager","frontière","frontiere","territoire","outre-mer","île","ile","archipel"],
        "science":["science","physique","chimie","biologie","atome","scientifique","corps humain","anatomie"],
        "animaux":["animal","animaux","faune","océan","ocean","insecte","mammifère","mammifere"],
        "sport":["sport","football","soccer","tennis","basket","olympique","olympiques"],
        "art":["art","peinture","musique","cinéma","cinema","littérature","litterature"],
        "food":["cuisine","gastronomie","aliment","aliments","nourriture","recette"],
    }
    for key,words in groups.items():
        if any(w in t for w in words): return key
    return "general"

def generate_theme_background(theme_name,topic):
    """Fond local réellement illustratif selon le sujet. Aucun appel Gemini."""
    key=("auto_bg_v5",theme_name,clean_text(topic).lower())
    if key in _BASE_CACHE: return _BASE_CACHE[key].copy()
    theme=THEMES[theme_name]; kind=_theme_keywords(topic)
    seed=int(hashlib.md5((theme_name+"|"+clean_text(topic)).encode()).hexdigest()[:8],16); rng=random.Random(seed)
    img=Image.new("RGB",(WIDTH,HEIGHT),theme["bg"]); px=img.load(); c1,c2=theme["bg"],theme["bg2"]
    for y in range(HEIGHT):
        t=y/(HEIGHT-1); t2=0.5-0.5*math.cos(math.pi*t)
        row=tuple(int(c1[k]*(1-t2)+c2[k]*t2) for k in range(3))
        for x in range(WIDTH): px[x,y]=row
    art=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0)); d=ImageDraw.Draw(art); accent=theme["accent"]; sec=theme["muted"]
    # profondeur lumineuse
    for (cx,cy,rx,ry,a) in [(160,250,360,300,28),(900,1180,500,520,20),(540,1750,650,260,18)]:
        d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(*accent,a))
    # motif discret commun
    for band in range(7):
        pts=[]; basey=300+band*210
        for x in range(-80,1160,35): pts.append((x,basey+50*math.sin(x/115+band)))
        d.line(pts,fill=(*accent,18),width=10)

    if kind=="geographie":
        # globe reconnaissable + route aérienne
        cx,cy,r=540,1390,285
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(8,20,42,90),outline=(*accent,115),width=7)
        d.ellipse((cx-r+35,cy-r,cx+r-35,cy+r),outline=(*sec,70),width=4)
        d.ellipse((cx-r,cy-r+70,cx+r,cy+r-70),outline=(*sec,65),width=4)
        for off in (-100,0,100): d.arc((cx-r,cy-r+off,cx+r,cy+r+off),205,335,fill=(*accent,45),width=3)
        # continents stylisés
        d.polygon([(380,1250),(450,1205),(515,1240),(495,1305),(430,1325),(395,1290)],fill=(*accent,55))
        d.polygon([(620,1280),(700,1250),(755,1315),(720,1380),(650,1370),(615,1320)],fill=(*sec,45))
        d.polygon([(500,1450),(565,1460),(600,1570),(555,1640),(505,1560)],fill=(*accent,45))
        # trajectoire + avion stylisé
        route=[(180,1530),(330,1390),(470,1430),(640,1280),(835,1190)]
        d.line(route,fill=(*accent,150),width=6)
        for x,y in route: d.ellipse((x-7,y-7,x+7,y+7),fill=(*accent,190))
        ax,ay=820,1195
        d.polygon([(ax,ay),(ax+70,ay-20),(ax+42,ay+3),(ax+78,ay+25),(ax+20,ay+12),(ax-15,ay+45),(ax-2,ay+8)],fill=(*accent,210))
        # petites cartes/repères en haut
        for x,y in [(130,500),(930,420),(180,760),(900,780)]:
            d.rounded_rectangle((x,y,x+90,y+58),radius=12,outline=(*sec,45),width=3)
            d.ellipse((x+35,y+17,x+55,y+37),fill=(*accent,100))
    elif kind=="espace":
        for _ in range(7):
            x=rng.randint(100,980); y=rng.randint(400,1550); r=rng.randint(120,300)
            d.ellipse((x-r,y-r,x+r,y+r),outline=(*accent,48),width=5)
        for _ in range(140):
            x=rng.randint(0,WIDTH); y=rng.randint(120,1800); rr=rng.randint(1,4); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(255,255,255,rng.randint(80,190)))
        cx,cy=540,1300
        d.ellipse((cx-150,cy-150,cx+150,cy+150),fill=(60,100,170,55),outline=(*accent,100),width=6)
        d.arc((cx-230,cy-80,cx+230,cy+80),0,360,fill=(*sec,75),width=5)
    elif kind=="histoire":
        for x in (150,370,590,810):
            d.rectangle((x,820,x+80,1430),fill=(*accent,20),outline=(*accent,60),width=4)
            d.polygon([(x-18,820),(x+40,750),(x+98,820)],fill=(*accent,28),outline=(*accent,60))
        d.rectangle((100,1430,980,1490),fill=(*accent,35))
        d.ellipse((260,440,820,1000),outline=(*sec,40),width=6)
    elif kind=="science":
        cx,cy=540,1370
        for r in (120,230,340): d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*accent,55),width=4)
        for ang in (0,60,120):
            rad=math.radians(ang); d.line((cx+math.cos(rad)*340,cy+math.sin(rad)*340,cx-math.cos(rad)*340,cy-math.sin(rad)*340),fill=(*sec,45),width=4)
        d.ellipse((cx-42,cy-42,cx+42,cy+42),fill=(*accent,130))
    elif kind=="animaux":
        # silhouettes de collines + empreintes stylisées
        for j in range(6):
            pts=[(x,900+j*120+int(35*math.sin(x/100+j))) for x in range(-30,1120,30)]; d.line(pts,fill=(*accent,45),width=9)
        for x,y in [(300,1400),(540,1280),(780,1450)]:
            d.ellipse((x-22,y-38,x+22,y+18),fill=(*sec,55)); d.ellipse((x-65,y-65,x-30,y-25),fill=(*sec,50)); d.ellipse((x+30,y-65,x+65,y-25),fill=(*sec,50))
    elif kind=="sport":
        d.ellipse((540-300,1300-300,540+300,1300+300),outline=(*accent,55),width=8)
        d.line((150,1300,930,1300),fill=(*sec,55),width=6); d.line((540,1000,540,1600),fill=(*sec,45),width=4)
        d.ellipse((495,1255,585,1345),outline=(*accent,100),width=5)
    elif kind=="art":
        for _ in range(10):
            x=rng.randint(100,760); y=rng.randint(900,1500); w=rng.randint(120,280); h=rng.randint(80,180)
            d.rounded_rectangle((x,y,x+w,y+h),radius=30,fill=(*accent,16),outline=(*accent,50),width=4)
    elif kind=="food":
        for x,y,r in [(250,1350,95),(540,1240,120),(800,1400,80),(400,1540,70),(720,1560,100)]:
            d.ellipse((x-r,y-r,x+r,y+r),fill=(*accent,20),outline=(*accent,60),width=4)
            d.ellipse((x-r//3,y-r//3,x+r//3,y+r//3),outline=(*sec,45),width=3)
    else:
        # culture générale : globe + cartes de connaissance
        cx,cy,r=540,1360,275
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*accent,80),width=6)
        d.ellipse((cx-r+35,cy-r,cx+r-35,cy+r),outline=(*sec,45),width=3)
        d.arc((cx-r,cy-120,cx+r,cy+120),0,360,fill=(*sec,45),width=3)
        for x,y in [(120,1050),(840,980),(120,1510),(850,1530)]:
            d.rounded_rectangle((x,y,x+110,y+75),radius=14,fill=(*accent,18),outline=(*accent,45),width=3)
    result=Image.alpha_composite(img.convert("RGBA"),art.filter(ImageFilter.GaussianBlur(0.25))).convert("RGB")
    _BASE_CACHE[key]=result.copy(); return result


def selected_video_background(theme_name,topic,mode,uploaded=None):
    if mode=="Image personnalisée" and uploaded is not None: return fit_background(uploaded)
    if mode=="Généré automatiquement":
        # Une variation change réellement le fond local sans toucher au quota Gemini.
        seed=st.session_state.get("q_variation_seed") or st.session_state.get("v_variation_seed") or 0
        variant_topic=f"{topic} • variation {seed}" if seed else topic
        return generate_theme_background(theme_name,variant_topic)
    return None

# ============================================================
# INTERFACE — DESIGN PREMIUM
# ============================================================
st.sidebar.markdown("""
<div class="qvp-side-brand">
  <div class="qvp-logo">▶</div>
  <div>
    <div class="qvp-side-title">QuizVideo Pro</div>
    <div class="qvp-side-sub">Créez des quiz vidéo captivants</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.caption("🧠 Quiz TikTok Pro  •  🗣️ Vocabulaire Pro")
st.sidebar.markdown("""
<div class="qvp-side-note"><b>✨ Mode économique actif</b><br>
Gemini est utilisé uniquement lorsque vous demandez du nouveau contenu IA.</div>
""", unsafe_allow_html=True)


def _ss_default(key, value):
    """Initialise une valeur de widget une seule fois pour éviter les conflits Streamlit."""
    if key not in st.session_state:
        st.session_state[key]=value

def render_layout_editor(module, key_prefix):
    """Studio compact : une seule famille de réglages est visible à la fois."""
    is_quiz=module=="quiz"; p=key_prefix
    defaults={
        "show_title":True,"title_y":42 if is_quiz else 70,"title_size":46 if is_quiz else 32,
        "question_y":205 if is_quiz else 500,"question_size":47 if is_quiz else 88,
        "answer_y":405 if is_quiz else 760,"answer_h":91,"answer_gap":12,"answer_size":30 if is_quiz else 58,"answer_radius":20,
        "show_explanation":True,"explanation_y":1135,"explanation_h":380,
        "face_show":False,"face_style":"Aucun","face_size":30,"face_x":0,"face_y":0,"face_color":"#FFCD40",
        "score_y":112,"score_size":31,"score_radius":22,"score_color":"#FFCD40","score_bg":"#070D1C",
        "animation":"Glissement","animation_speed":1.0,"animation_strength":1.0,"motion_strength":1.0,
        "show_timer":True,"timer_y":1045,"timer_x":540,"timer_size":58,"timer_text_size":55,"timer_style":"Anneau",
        "timer_show_label":True,"timer_label":"RÉFLÉCHIS","timer_label_size":23,"timer_color":"#FFCD40","timer_label_color":"#FFCD40",
        "primary":"#FFCD40","answer":"#11305B","answer2":"#143765","correct":"#2EDA7B","text":"#FFFFFF","muted":"#A5B5D0",
        "bg_opacity":18,"bg_zoom":1.02,"bg_x":0,"bg_y":0,
        "bg_mode":"✨ Automatique",
    }
    for k,v in defaults.items(): _ss_default(p+k,v)

    st.markdown('<div class="qvp-editor-title">🎨 ÉDITEUR</div>',unsafe_allow_html=True)
    tabs=st.tabs(["🧩 Structure","📐 Position & taille","🎨 Couleurs","🎞️ Animation","⏱️ Minuteur","🌄 Fond"])
    with tabs[0]:
        if is_quiz:
            st.info("**Style 1** — Question → 4 réponses → minuteur → bonne réponse verte → explication.\n\n**Style 2** — Q1 → minuteur → R1 → Q2 → minuteur → R2… cumulatif jusqu’à 15 questions.")
        else:
            st.info("**Style 1** — Mot → minuteur → traduction.\n\n**Style 2 — Cumulatif** — Mot 1 → minuteur → traduction 1 → Mot 2 → minuteur → traduction 2… jusqu’à 15 mots, les précédents restent visibles.")
    with tabs[1]:
        c1,c2=st.columns(2)
        with c1:
            st.markdown("**Question / mot**")
            _ss_default(p+"question_x",540)
            st.slider("Position X",0,1080,st.session_state[p+"question_x"],key=p+"question_x")
            st.slider("Position Y",120,850,st.session_state[p+"question_y"],key=p+"question_y")
            st.slider("Taille",28,100,st.session_state[p+"question_size"],key=p+"question_size")
            if is_quiz:
                st.slider("Largeur",500,1000,964,key=p+"question_width")
                st.slider("Hauteur / rayon",10,60,28,key=p+"question_box_radius")
            st.markdown("**Titre**")
            st.checkbox("Afficher le titre",key=p+"show_title")
            st.slider("Position Y du titre",25,180,st.session_state[p+"title_y"],key=p+"title_y")
            st.slider("Taille du titre",24,72,st.session_state[p+"title_size"],key=p+"title_size")
            if is_quiz:
                st.markdown("**Compteur**")
                st.slider("Position Y",70,220,st.session_state[p+"score_y"],key=p+"score_y")
                st.slider("Taille",20,70,st.session_state[p+"score_size"],key=p+"score_size")
                st.slider("Arrondi",5,45,st.session_state[p+"score_radius"],key=p+"score_radius")
        with c2:
            st.markdown("**Réponses / traduction**")
            if is_quiz:
                st.slider("Position Y",300,900,st.session_state[p+"answer_y"],key=p+"answer_y")
                st.slider("Taille du texte",20,52,st.session_state[p+"answer_size"],key=p+"answer_size")
                st.slider("Espacement",4,30,st.session_state[p+"answer_gap"],key=p+"answer_gap")
                st.slider("Hauteur",55,130,st.session_state[p+"answer_h"],key=p+"answer_h")
            else:
                st.slider("Position Y",650,1100,st.session_state[p+"answer_y"],key=p+"answer_y")
                st.slider("Taille",28,90,st.session_state[p+"answer_size"],key=p+"answer_size")
            st.slider("Arrondi",5,40,st.session_state[p+"answer_radius"],key=p+"answer_radius")
            st.markdown("**Explication**")
            st.checkbox("Afficher l'explication",key=p+"show_explanation")
            st.slider("Position Y",950,1400,st.session_state[p+"explanation_y"],key=p+"explanation_y")
            st.slider("Hauteur",220,520,st.session_state[p+"explanation_h"],key=p+"explanation_h")
    with tabs[2]:
        c1,c2=st.columns(2)
        with c1:
            st.color_picker("Accent / titre",key=p+"primary")
            st.color_picker("Réponses",key=p+"answer")
            if is_quiz: st.color_picker("Deuxième couleur réponses",key=p+"answer2")
        with c2:
            st.color_picker("Bonne réponse",key=p+"correct")
            st.color_picker("Texte",key=p+"text")
            st.color_picker("Texte secondaire",key=p+"muted")
            if is_quiz:
                st.markdown("**Émotion**")
                st.selectbox("Style",["Aucun","Badge quiz","Point d'interrogation","Éclair","Visage"],key=p+"face_style")
                st.checkbox("Afficher",key=p+"face_show")
                st.slider("Taille",18,70,st.session_state[p+"face_size"],key=p+"face_size")
    with tabs[3]:
        c1,c2=st.columns(2)
        with c1:
            st.selectbox("Animation",["Glissement","Pop","Aucune"],key=p+"animation")
            st.slider("Vitesse",0.5,2.0,st.session_state[p+"animation_speed"],0.05,key=p+"animation_speed")
        with c2:
            st.slider("Entrée des éléments",0.0,2.0,st.session_state[p+"animation_strength"],0.05,key=p+"animation_strength")
            st.slider("Mouvement général",0.0,2.0,st.session_state[p+"motion_strength"],0.05,key=p+"motion_strength")
        st.caption("Les animations sont ensuite synchronisées sur la durée réelle des voix au rendu.")
    with tabs[4]:
        st.checkbox("Afficher le compte à rebours",key=p+"show_timer")
        c1,c2=st.columns(2)
        with c1:
            st.slider("Position X",250,830,st.session_state[p+"timer_x"],key=p+"timer_x")
            st.slider("Position Y",800,1250,st.session_state[p+"timer_y"],key=p+"timer_y")
            st.slider("Taille",30,120,st.session_state[p+"timer_size"],key=p+"timer_size")
            st.slider("Taille du chiffre",20,100,st.session_state[p+"timer_text_size"],key=p+"timer_text_size")
        with c2:
            st.selectbox("Style du chronomètre",["Anneau","Barre","Pill","Points","Minimal"],key=p+"timer_style")
            st.checkbox("Afficher le texte",key=p+"timer_show_label")
            st.text_input("Texte",key=p+"timer_label")
            st.slider("Taille du texte",14,42,st.session_state[p+"timer_label_size"],key=p+"timer_label_size")
            st.color_picker("Couleur",key=p+"timer_color")
    with tabs[5]:
        st.radio("Source du fond",["✨ Automatique","🖼️ Personnalisé","◯ Aucun"],horizontal=True,key=p+"bg_mode")
        if st.session_state.get(p+"bg_mode")=="🖼️ Personnalisé":
            st.file_uploader("Image de fond",type=["png","jpg","jpeg"],key=p+"bg_upload")
        c1,c2=st.columns(2)
        with c1:
            st.slider("Assombrissement",0,80,st.session_state[p+"bg_opacity"],key=p+"bg_opacity")
            st.slider("Zoom",1.00,1.25,st.session_state[p+"bg_zoom"],0.01,key=p+"bg_zoom")
        with c2:
            st.slider("Déplacement X",-120,120,st.session_state[p+"bg_x"],key=p+"bg_x")
            st.slider("Déplacement Y",-120,120,st.session_state[p+"bg_y"],key=p+"bg_y")
        st.caption("Le fond automatique reste local et ne consomme pas de quota Gemini.")
    _save_settings()

tab1,tab2=st.tabs(["🧠 Quizz TikTok Pro","🗣️ Vocabulaire Pro"])

with tab1:
    st.markdown('<div class="qvp-studio-header"><b>🎬 QuizVideo Pro</b><span>🧠 QUIZ</span><small>Studio 9:16</small></div>',unsafe_allow_html=True)
    r1,r2,r3,r4=st.columns([1.15,.7,.95,1.15])
    with r1: th_q=st.text_input("Sujet","Culture Générale",key="thq")
    with r2: nb_q=st.slider("Questions",1,15,15,key="nbq")
    with r3: voice_q=VOICES_FR[st.selectbox("Voix",list(VOICES_FR),key="vq")]
    with r4: theme_q=st.selectbox("Style visuel",list(THEMES),key="tq")
    r5,r6,r7,r8=st.columns([1.0,1.25,1.55,1.2])
    with r5: channel_q=st.text_input("Chaîne","@QuizMaster_Pro",key="cq")
    with r6: hook_q=st.text_input("Hook court","Teste tes connaissances !",key="hq")
    with r7: outro_q=st.text_input("CTA final","Quel est ton score ?",key="oq")
    with r8: style_q=st.radio("Structure",["Style 1 — 4 réponses + révélation","Style 2 — Cumulatif"],horizontal=True,key="styleq_compact")
    style_q_full="Style 1 — 4 réponses + révélation" if style_q.startswith("Style 1") else "Style 2 — questions/réponses cumulatives"
    st.caption("Style 1 : Question + 4 réponses → minuteur → révélation + explication.  |  Style 2 : Q1 + minuteur → R1 → Q2 + minuteur → R2… cumulatif.")
    left_q, right_q = st.columns([0.95, 1.05], gap="medium")
    with left_q:
        with st.container(height=390, border=True):
            render_layout_editor("quiz","q_")
    bg_mode_q=st.session_state.get("q_bg_mode","✨ Automatique")
    uploaded_bg_q=st.session_state.get("q_bg_upload")
    bg_mode_clean_q="Généré automatiquement" if bg_mode_q.startswith("✨") else "Image personnalisée" if bg_mode_q.startswith("🖼️") else "Aucun"
    bg_q=selected_video_background(theme_q,th_q,bg_mode_clean_q,uploaded_bg_q)
    with right_q:
        st.markdown('<div class="qvp-preview-anchor"></div><div class="qvp-preview-sticky"><div class="qvp-preview-panel"><div class="qvp-preview-title">👁️ Aperçu fixe</div><div class="qvp-preview-note">Il reste visible pendant que tu modifies les réglages.</div></div></div>', unsafe_allow_html=True)
        if style_q_full.startswith("Style 2"):
            preview_state_q=st.radio("Aperçu",["Q1 + minuteur","Q2 + R1","Q3 + R1/R2"],horizontal=True,key="preview_state_q")
        else:
            preview_state_q=st.radio("État à prévisualiser",["Question + réponses","Compte à rebours","Bonne réponse + explication"],horizontal=True,key="preview_state_q")
        try:
            sample_bg = bg_q if isinstance(bg_q, Image.Image) else selected_video_background(theme_q, th_q, bg_mode_clean_q, uploaded_bg_q)
            if style_q_full.startswith("Style 2"):
                demo=[{"question":"Quelle est la capitale de la France ?","options":["Paris","Londres","Rome","Berlin"],"reponse_correcte":"A"},{"question":"Quelle est la capitale de l'Espagne ?","options":["Paris","Madrid","Rome","Lisbonne"],"reponse_correcte":"B"},{"question":"Quelle est la capitale de l'Italie ?","options":["Milan","Paris","Rome","Madrid"],"reponse_correcte":"C"}]
                if preview_state_q=="Q1 + minuteur":
                    preview=draw_style2_frame(demo,0,theme_q,channel_q,sample_bg,timer=3,timer_fraction=.72,video_title=th_q)
                elif preview_state_q=="Q2 + R1":
                    preview=draw_style2_frame(demo,1,theme_q,channel_q,sample_bg,timer=2,timer_fraction=.5,video_title=th_q)
                else:
                    preview=draw_style2_frame(demo,2,theme_q,channel_q,sample_bg,answer_reveal=True,video_title=th_q)
            elif preview_state_q=="Question + réponses":
                preview = draw_quiz_frame("Quelle est la capitale de la France ?",["Paris","Londres","Rome","Berlin"],theme_q,1,max(1,int(nb_q)),channel_q,sample_bg,entrance=1.0,motion=0.35,video_title=th_q)
            elif preview_state_q=="Compte à rebours":
                preview = draw_quiz_frame("Quelle est la capitale de la France ?",["Paris","Londres","Rome","Berlin"],theme_q,1,max(1,int(nb_q)),channel_q,sample_bg,entrance=1.0,timer=3,timer_fraction=0.72,pulse=0.85,motion=1.0,video_title=th_q)
            else:
                preview = draw_quiz_frame("Quelle est la capitale de la France ?",["Paris","Londres","Rome","Berlin"],theme_q,1,max(1,int(nb_q)),channel_q,sample_bg,entrance=1.0,correct_idx=0,reveal_progress=1.0,pulse=0.15,motion=1.8,video_title=th_q,explanation="Paris est la capitale de la France.",explanation_progress=1.0)
            st.image(preview, caption="Aperçu 9:16 — les changements sont appliqués ici.", use_container_width=True)
        except Exception as e:
            st.caption(f"Aperçu indisponible pour le moment : {e}")
    aq1,aq2,aq3=st.columns([1,1,1])
    with aq1:
        if st.button("🎲 Variation",key="studio_variation_q",use_container_width=True):
            st.session_state["q_variation_seed"]=random.randint(1,999999); st.rerun()
    with aq2:
        if st.button("💾 Enregistrer",key="studio_save_q",use_container_width=True):
            _save_settings(); st.success("Style enregistré.")
    with aq3:
        st.caption("🎬 Générer ci-dessous")
    with st.expander("🎯 Contenu — Questions / réponses", expanded=False):
        mode_q=st.radio("Source du contenu",["🤖 IA Gemini","📄 CSV"],horizontal=True,key="mode_q")
        if mode_q=="🤖 IA Gemini":
            st.caption("💡 Changer le thème, la voix, le fond, le hook ou le CTA ne consomme aucun quota Gemini. Le CSV et les modifications manuelles non plus. Une nouvelle requête Gemini est envoyée uniquement si tu demandes un nouveau contenu IA.")
            gen_key=_quiz_generation_key(nb_q,th_q)
            cached_key=st.session_state.get("q_ai_key")
            if cached_key==gen_key and st.session_state.get("q_data") and st.session_state.get("q_source","").startswith("IA"):
                st.info("♻️ Ce quiz IA est déjà en mémoire : aucun appel Gemini ne sera fait pour les changements de style ou de vidéo.")
            bq1,bq2=st.columns(2)
            with bq1:
                if st.button("♻️ Charger / générer ce quiz",key="genq",use_container_width=True):
                    if cached_key==gen_key and st.session_state.get("q_ai_cache"):
                        st.session_state.q_data=[dict(x) for x in st.session_state.q_ai_cache]
                        st.session_state.q_source=f"IA • {th_q} • cache"
                        st.success("✅ Quiz déjà généré : réutilisation du cache, 0 nouvelle requête Gemini.")
                    elif not api_key:
                        st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                    else:
                        try:
                            prompt=f'''Tu es un créateur expert de quiz Shorts. Génère exactement {nb_q} questions DIFFERENTES en français sur le sujet « {th_q} ».
    Varie les connaissances testées et évite toute répétition entre les questions.
    Chaque objet doit respecter EXACTEMENT cette structure :
    {{"question":"...","options":["réponse A","réponse B","réponse C","réponse D"],"reponse_correcte":"A","explication":"..."}}
    IMPORTANT : options est une LISTE de 4 chaînes dans l'ordre A, B, C, D.
    reponse_correcte est UNIQUEMENT une lettre parmi A, B, C ou D.
    Les 4 options doivent être plausibles et une seule correcte.
    Retourne UNIQUEMENT le tableau JSON, sans ``` et sans texte avant ou après.'''
                            res_text,_=gemini_generate_text(prompt)
                            data=normalize_questions(parse_json(res_text))
                            if len(data)<nb_q: raise ValueError(f"Gemini n'a fourni que {len(data)} questions sur {nb_q}.")
                            st.session_state.q_data=data[:nb_q]
                            st.session_state.q_ai_cache=[dict(x) for x in st.session_state.q_data]
                            st.session_state.q_ai_key=gen_key
                            st.session_state.q_source=f"IA • {th_q}"
                            st.success(f"✅ {len(data)} questions générées. Cette génération est maintenant en cache.")
                        except Exception as e: st.error(f"Erreur Gemini : {e}")
            with bq2:
                if st.button("⚠️ Nouveau lot IA (1 quota)",key="forceq",use_container_width=True):
                    if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                    else:
                        try:
                            prompt=f'''Génère exactement {nb_q} questions DIFFERENTES en français sur « {th_q} ».
    Format strict : [{{"question":"...","options":["A","B","C","D"],"reponse_correcte":"A","explication":"..."}}].
    Une seule bonne réponse. Retourne uniquement le JSON.'''
                            res_text,_=gemini_generate_text(prompt)
                            data=normalize_questions(parse_json(res_text))
                            if len(data)<nb_q: raise ValueError(f"Gemini n'a fourni que {len(data)} questions sur {nb_q}.")
                            st.session_state.q_data=data[:nb_q]
                            st.session_state.q_ai_cache=[dict(x) for x in st.session_state.q_data]
                            st.session_state.q_ai_key=gen_key
                            st.session_state.q_source=f"IA • {th_q}"
                            st.success(f"✅ Nouveau lot IA : {len(data)} questions.")
                        except Exception as e: st.error(f"Erreur Gemini : {e}")
        else:
            st.markdown('<div class="qvp-card"><b>📄 Import CSV</b><div class="qvp-small">Prépare tes questions dans Excel/Google Sheets puis exporte en CSV. Maximum : 15 questions.</div></div>', unsafe_allow_html=True)
            st.download_button("⬇️ Télécharger le modèle CSV", data=csv_template(), file_name="quiz_template.csv", mime="text/csv", key="csvtemplate")
            csv_file=st.file_uploader("Choisir ton fichier CSV",type=["csv"],key="quizcsv")
            if csv_file is not None:
                try:
                    imported=parse_quiz_csv(csv_file); st.session_state.q_data=imported; st.session_state.q_source="CSV manuel"
                    st.success(f"✅ {len(imported)} questions importées.")
                    st.dataframe([{"#":i+1,"Question":q["question"],"A":q["options"][0],"B":q["options"][1],"C":q["options"][2],"D":q["options"][3],"Bonne":q["reponse_correcte"]} for i,q in enumerate(imported)], use_container_width=True, hide_index=True)
                except Exception as e: st.error(f"CSV invalide : {e}")

        if st.session_state.get("q_data"):
            st.success(f"Quiz prêt : {len(st.session_state.q_data)} question(s) • {st.session_state.get('q_source','source manuelle')}")
            st.markdown("### ✏️ Modifier ou ajouter des questions — sans quota Gemini")
            quiz_rows=[{"Question":q["question"],"A":q["options"][0],"B":q["options"][1],"C":q["options"][2],"D":q["options"][3],"Bonne":q["reponse_correcte"],"Explication":q.get("explication","")} for q in st.session_state.q_data]
            edited=st.data_editor(quiz_rows,num_rows="dynamic",use_container_width=True,key="quiz_editor",column_config={
                "Bonne":st.column_config.SelectboxColumn("Bonne",options=["A","B","C","D"],required=True),
                "Question":st.column_config.TextColumn("Question",width="large"),
                "Explication":st.column_config.TextColumn("Explication",width="large")
            },hide_index=True)
            be1,be2=st.columns(2)
            with be1:
                if st.button("💾 Enregistrer les modifications",key="saveqedit",use_container_width=True):
                    saved=_save_quiz_editor(edited)
                    if saved:
                        st.session_state.q_data=saved
                        st.session_state.q_source="Questions modifiées manuellement"
                        st.success(f"✅ {len(saved)} question(s) enregistrée(s), sans appel Gemini.")
                    else: st.error("Aucune question valide à enregistrer.")
            with be2:
                if st.button("↩️ Restaurer le dernier lot IA",key="restoreq",use_container_width=True):
                    if st.session_state.get("q_ai_cache"):
                        st.session_state.q_data=[dict(x) for x in st.session_state.q_ai_cache]
                        st.session_state.q_source=f"IA • {th_q} • restauré"
                        st.success("✅ Lot IA restauré, 0 quota consommé.")
                    else: st.info("Aucun lot IA en cache.")
            act1,act2,act3=st.columns(3)
            with act1:
                if st.button("🎲 Variation",key="variation_q",use_container_width=True):
                    st.session_state["q_variation_seed"]=random.randint(1,999999); st.session_state["q_variation_notice"]=True
                    st.rerun()
            with act2:
                if st.button("💾 Enregistrer",key="save_style_q",use_container_width=True):
                    _save_settings(); st.success("Style enregistré.")
            with act3:
                st.caption("⬇️ Générer ci-dessous")
            if st.session_state.get("q_variation_notice"):
                st.info("🎲 Variation active : utilise le fond, les animations et les réglages actuels pour une nouvelle variante.")
                st.session_state["q_variation_notice"]=False
            if st.button("🎬 Générer le Short Quiz — Mise en page personnalisée",key="makeq"):
                try:
                    with st.spinner("Création du Short Quiz — mise en page personnalisée..."):
                        with tempfile.TemporaryDirectory() as tmp:
                            tic,ding=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,tmp)
                            clips=[]; total=len(st.session_state.q_data)

                            if style_q_full.startswith("Style 2"):
                                # STYLE 2 : une seule page cumulative. Q1 puis R1, Q2 puis R2, etc.
                                # Les questions apparaissent progressivement : seules les questions déjà atteintes restent visibles.
                                items=st.session_state.q_data[:15]
                                total=len(items)
                                for idx,q in enumerate(items):
                                    bg_question=bg_q
                                    corr="ABCD".index(q["reponse_correcte"])
                                    answer_text=clean_text(q["options"][corr])
                                    qa_raw=os.path.join(tmp,f"s2_q_{idx}.mp3")
                                    ans_raw=os.path.join(tmp,f"s2_a_{idx}.mp3")
                                    synthesize_audio(q["question"],voice_q,qa_raw,tts_rate)
                                    synthesize_audio(answer_text,voice_q,ans_raw,tts_rate)
                                    qdur=audio_duration(qa_raw)
                                    adur=audio_duration(ans_raw)
                                    # La question apparaît d'abord, puis le minuteur, puis sa réponse.
                                    frames=[]
                                    q_steps=max(8,int(qdur*12))
                                    for j in range(q_steps):
                                        t=j/max(1,q_steps-1)
                                        frames.append((draw_style2_frame(items,idx,theme_q,channel_q,bg_question,answer_reveal=False,motion=t*.7,video_title=th_q),qdur/q_steps))
                                    cdur=3.12; cd_steps=94
                                    for j in range(cd_steps):
                                        t=j/max(1,cd_steps-1); elapsed=t*cdur
                                        if elapsed < 1.04: sec=3; frac=1-(elapsed/1.04)
                                        elif elapsed < 2.08: sec=2; frac=1-((elapsed-1.04)/1.04)
                                        else: sec=1; frac=1-((elapsed-2.08)/1.04)
                                        timer=0 if elapsed>=3.0 else sec
                                        timer_frac=0.0 if elapsed>=3.0 else frac
                                        frames.append((draw_style2_frame(items,idx,theme_q,channel_q,bg_question,timer,timer_frac,False,t,th_q),cdur/cd_steps))
                                    a_steps=max(8,int(adur*12))
                                    for j in range(a_steps):
                                        t=j/max(1,a_steps-1)
                                        frames.append((draw_style2_frame(items,idx,theme_q,channel_q,bg_question,answer_reveal=True,motion=1.0+t*.5,video_title=th_q),adur/a_steps))
                                    audio=os.path.join(tmp,f"s2_full_{idx}.m4a")
                                    concat_audio_files([qa_raw,countdown_sfx,ans_raw],audio)
                                    out=os.path.join(tmp,f"s2_{idx}.mp4")
                                    make_segment(save_frames(frames,tmp,f"s2f_{idx}"),audio,out,tmp,1.0)
                                    clips.append(out)

                                # Explications seulement après les 15 questions.
                                for idx,q in enumerate(items):
                                    corr="ABCD".index(q["reponse_correcte"])
                                    answer_text=clean_text(q["options"][corr])
                                    exp_text=clean_text(q.get("explication","")) or f"La bonne réponse est {answer_text}."
                                    ea=os.path.join(tmp,f"s2_exp_{idx}.mp3")
                                    synthesize_audio(exp_text,voice_q,ea,tts_rate)
                                    edur=audio_duration(ea)
                                    exp_frames=max(8,int(edur*12))
                                    eframes=[]
                                    for j in range(exp_frames):
                                        t=j/max(1,exp_frames-1)
                                        eframes.append((draw_explanation_scene(q["question"],answer_text,exp_text,theme_q,channel_q,bg_q,progress=t,q_num=idx+1,total=total,video_title=th_q),edur/exp_frames))
                                    eo=os.path.join(tmp,f"s2_exp_{idx}.mp4")
                                    make_segment(save_frames(eframes,tmp,f"s2ef_{idx}"),ea,eo,tmp,1.0)
                                    clips.append(eo)
                            else:
                                # STYLE 1 : question + 4 réponses, minuteur, révélation verte, explication.
                                for idx,q in enumerate(st.session_state.q_data):
                                    corr="ABCD".index(q["reponse_correcte"])
                                    bg_question = selected_video_background(theme_q, q.get("question", th_q), bg_mode_clean_q, uploaded_bg_q)
                                    qa_raw=os.path.join(tmp,f"q_{idx}.mp3")
                                    synthesize_audio(q["question"],voice_q,qa_raw,tts_rate)
                                    qdur=audio_duration(qa_raw)
                                    exp_text=clean_text(q.get("explication","")) or f"La bonne réponse est {q['options'][corr]}."
                                    ea_raw=os.path.join(tmp,f"exp_{idx}.mp3")
                                    synthesize_audio(exp_text,voice_q,ea_raw,tts_rate)
                                    edur=audio_duration(ea_raw)
                                    exp_mix=os.path.join(tmp,f"exp_mix_{idx}.m4a")
                                    mix_voice_sfx(ea_raw,ding,exp_mix,0,0.78)
                                    full_audio=os.path.join(tmp,f"question_full_{idx}.m4a")
                                    concat_audio_files([qa_raw,countdown_sfx,exp_mix],full_audio)
                                    frames=[]
                                    q_steps=max(8,int(qdur*12))
                                    for j in range(q_steps):
                                        t=j/max(1,q_steps-1)
                                        frames.append((draw_quiz_frame(q["question"],q["options"],theme_q,idx+1,total,channel_q,bg_question,entrance=ease_out(t),motion=t*0.9,video_title=th_q),qdur/q_steps))
                                    cdur=3.12; cd_steps=94
                                    for j in range(cd_steps):
                                        t=j/max(1,cd_steps-1); elapsed=t*cdur
                                        if elapsed < 1.04: sec=3; frac=1-(elapsed/1.04)
                                        elif elapsed < 2.08: sec=2; frac=1-((elapsed-1.04)/1.04)
                                        else: sec=1; frac=1-((elapsed-2.08)/1.04)
                                        timer=0 if elapsed>=3.0 else sec; timer_frac=0.0 if elapsed>=3.0 else frac
                                        frames.append((draw_quiz_frame(q["question"],q["options"],theme_q,idx+1,total,channel_q,bg_question,entrance=1.0,timer=timer,timer_fraction=timer_frac,pulse=0.55+0.45*math.sin(t*math.pi*12),motion=1.0+t*1.2,video_title=th_q),cdur/cd_steps))
                                    ex_steps=max(8,int(edur*12))
                                    for j in range(ex_steps):
                                        t=j/max(1,ex_steps-1)
                                        frames.append((draw_quiz_frame(q["question"],q["options"],theme_q,idx+1,total,channel_q,bg_question,entrance=1.0,correct_idx=corr,reveal_progress=min(1,t*3),pulse=0.15*(1-t),motion=2.0+t,video_title=th_q,explanation=exp_text,explanation_progress=t),edur/ex_steps))
                                    out=os.path.join(tmp,f"qfull_{idx}.mp4")
                                    make_segment(save_frames(frames,tmp,f"qfull_{idx}"),full_audio,out,tmp,1.0)
                                    clips.append(out)

                            # CTA très court seulement après le quiz.
                            if clean_text(outro_q):
                                oa=os.path.join(tmp,"outro.m4a")
                                synthesize_audio(outro_q,voice_q,oa,tts_rate)
                                od=audio_duration(oa)
                                if od>0.15:
                                    of=save_frames([(draw_hook(outro_q,theme_q,channel_q,bg_q,p),od/6)
                                                    for p in [0.08,0.22,0.40,0.60,0.82,1.0]],tmp,"outro")
                                    oo=os.path.join(tmp,"outro.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)

                            final=os.path.join(tmp,"quizvideo_pro_custom.mp4")
                            concat_videos(clips,final,tmp)
                            with open(final,"rb") as f: data=f.read()
                            st.success("✅ Short Quiz terminé avec ta mise en page.")
                            st.video(data)
                            st.download_button("⬇️ Télécharger quizvideo_pro_custom.mp4",data=data,file_name="quizvideo_pro_custom.mp4",mime="video/mp4",key="dq7")
                except Exception as e:
                    st.error(f"Erreur pendant le montage V7 : {e}")

with tab2:
    st.markdown('<div class="qvp-studio-header"><b>🎬 QuizVideo Pro</b><span>🗣️ VOCABULAIRE</span><small>Studio 9:16</small></div>',unsafe_allow_html=True)
    a1,a2,a3,a4=st.columns([1.15,.7,1.0,1.15])
    with a1: th_v=st.text_input("Sujet","Voyage",key="thv")
    with a2: nb_v=st.slider("Mots",1,15,15,key="nbv")
    with a3: langue_v=st.selectbox("Langue cible",list(VOICES_MAP),key="lv")
    with a4: theme_v=st.selectbox("Style visuel",list(THEMES),key="tv")
    a5,a6,a7,a8=st.columns([1.0,1.25,1.4,1.25])
    with a5: channel_v=st.text_input("Chaîne","@LingoPulse_Daily",key="cv")
    with a6: hook_v=st.text_input("Hook","Apprends ces mots !",key="hv")
    with a7: outro_v=st.text_input("CTA final","Abonne-toi pour un nouveau mot !",key="ov")
    with a8: style_v=st.radio("Structure",["Style 1 — Mot → minuteur → traduction","Style 2 — Cumulatif"],horizontal=True,key="stylev_compact")
    voice_tr_name=st.selectbox("Voix traduction",list(VOICES_MAP[langue_v]),key="vtr")
    voice_tr=VOICES_MAP[langue_v][voice_tr_name]
    st.caption("Style 1 : Mot → minuteur → traduction.  |  Style 2 : Mot 1 → minuteur → traduction 1 → Mot 2 → minuteur → traduction 2… les précédents restent visibles.")
    left_v, right_v = st.columns([0.95, 1.05], gap="medium")
    with left_v:
        with st.container(height=390, border=True):
            render_layout_editor("vocab","v_")
    bg_mode_v=st.session_state.get("v_bg_mode","✨ Automatique")
    uploaded_bg_v=st.session_state.get("v_bg_upload")
    bg_mode_clean_v="Généré automatiquement" if bg_mode_v.startswith("✨") else "Image personnalisée" if bg_mode_v.startswith("🖼️") else "Aucun"
    bg_v=selected_video_background(theme_v,th_v,bg_mode_clean_v,uploaded_bg_v)
    with right_v:
        st.markdown('<div class="qvp-preview-anchor"></div><div class="qvp-preview-sticky"><div class="qvp-preview-panel"><div class="qvp-preview-title">👁️ Aperçu fixe — Vocabulaire</div><div class="qvp-preview-note">Il reste visible pendant que tu modifies les réglages.</div></div></div>', unsafe_allow_html=True)
        if style_v.startswith("Style 2"):
            preview_state_v=st.radio("Aperçu",["Mot 1 + minuteur","Mot 2 + minuteur + traduction 1","Mot 3 + minuteur + traductions 1–2"],horizontal=True,key="preview_state_v")
        else:
            preview_state_v=st.radio("Aperçu",["Mot","Compte à rebours","Traduction"],horizontal=True,key="preview_state_v")
        try:
            sample_bg_v = bg_v if isinstance(bg_v, Image.Image) else selected_video_background(theme_v, th_v, bg_mode_clean_v, uploaded_bg_v)
            if style_v.startswith("Style 2"):
                sample_items=[{"fr":"Bonjour","trad":"Hello"},{"fr":"Merci","trad":"Thank you"},{"fr":"Voyage","trad":"Travel"}]
                active=0 if preview_state_v=="Mot 1 + minuteur" else 1 if preview_state_v=="Mot 2 + minuteur + traduction 1" else 2
                preview_v=draw_vocab_cumulative_frame(sample_items,active,theme_v,channel_v,sample_bg_v,timer=3 if preview_state_v=="Mot 1 + minuteur" else None,timer_fraction=.72,reveal=False,video_title=th_v)
            else:
                sample_items=[{"fr":"Bonjour","trad":"Hello"}]
                phase_v="mot" if preview_state_v=="Mot" else "countdown" if preview_state_v=="Compte à rebours" else "translation"
                preview_v=draw_vocab_frame(sample_items,0,langue_v,theme_v,channel_v,sample_bg_v,phase_v,3,0.75,1.0)
            st.image(preview_v, caption="Aperçu 9:16 — les changements sont appliqués ici.", use_container_width=True)
        except Exception as e:
            st.caption(f"Aperçu indisponible pour le moment : {e}")
    vg_key=_vocab_generation_key(nb_v,th_v,langue_v)
    av1,av2,av3=st.columns([1,1,1])
    with av1:
        if st.button("🎲 Variation",key="studio_variation_v",use_container_width=True):
            st.session_state["v_variation_seed"]=random.randint(1,999999); st.rerun()
    with av2:
        if st.button("💾 Enregistrer",key="studio_save_v",use_container_width=True):
            _save_settings(); st.success("Style enregistré.")
    with av3:
        st.caption("🎬 Générer ci-dessous")
    with st.expander("🎯 Contenu — Mots / traductions", expanded=False):
        vb1,vb2=st.columns(2)
        with vb1:
            if st.button("♻️ Charger / générer le vocabulaire",key="genv",use_container_width=True):
                if st.session_state.get("v_ai_key")==vg_key and st.session_state.get("v_ai_cache"):
                    st.session_state.v_data=[dict(x) for x in st.session_state.v_ai_cache]
                    st.success("✅ Vocabulaire déjà généré : cache réutilisé, 0 nouvelle requête Gemini.")
                elif not api_key:
                    st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                else:
                    try:
                        prompt=f'''Génère exactement {nb_v} mots français DIFFERENTS avec leur traduction en {langue_v} sur le sujet « {th_v} ». Évite les répétitions et varie le vocabulaire. Retourne UNIQUEMENT un JSON valide: [{{"fr":"...","trad":"..."}}]'''
                        res_text,_=gemini_generate_text(prompt)
                        data=parse_json(res_text)[:nb_v]
                        if len(data)<nb_v: raise ValueError(f"Gemini n'a fourni que {len(data)} mots sur {nb_v}.")
                        st.session_state.v_data=data
                        st.session_state.v_ai_cache=[dict(x) for x in data]
                        st.session_state.v_ai_key=vg_key
                        st.success("✅ Vocabulaire généré et mis en cache.")
                    except Exception as e: st.error(f"Erreur Gemini : {e}")
        with vb2:
            if st.button("⚠️ Nouveau lot IA vocabulaire (1 quota)",key="forcev",use_container_width=True):
                if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                else:
                    try:
                        prompt=f'''Génère exactement {nb_v} mots français différents avec traduction en {langue_v} sur « {th_v} ». Retourne uniquement [{{"fr":"...","trad":"..."}}].'''
                        res_text,_=gemini_generate_text(prompt)
                        data=parse_json(res_text)[:nb_v]
                        if len(data)<nb_v: raise ValueError(f"Gemini n'a fourni que {len(data)} mots sur {nb_v}.")
                        st.session_state.v_data=data
                        st.session_state.v_ai_cache=[dict(x) for x in data]
                        st.session_state.v_ai_key=vg_key
                        st.success("✅ Nouveau lot vocabulaire généré.")
                    except Exception as e: st.error(f"Erreur Gemini : {e}")
        if st.session_state.get("v_data"):
            st.success(f"Vocabulaire prêt : {len(st.session_state.v_data)} mot(s)")
            st.markdown("### ✏️ Modifier ou ajouter des mots — sans quota Gemini")
            vocab_rows=[{"Français":clean_text(x.get("fr","")),"Traduction":clean_text(x.get("trad",""))} for x in st.session_state.v_data]
            edited_v=st.data_editor(vocab_rows,num_rows="dynamic",use_container_width=True,key="vocab_editor",column_config={
                "Français":st.column_config.TextColumn("Français",width="medium"),
                "Traduction":st.column_config.TextColumn("Traduction",width="medium")
            },hide_index=True)
            ve1,ve2=st.columns(2)
            with ve1:
                if st.button("💾 Enregistrer les modifications",key="savevedit",use_container_width=True):
                    saved=_save_vocab_editor(edited_v)
                    if saved:
                        st.session_state.v_data=saved
                        st.success(f"✅ {len(saved)} mot(s) enregistré(s), sans appel Gemini.")
                    else: st.error("Aucun mot valide à enregistrer.")
            with ve2:
                if st.button("↩️ Restaurer le dernier lot IA",key="restorev",use_container_width=True):
                    if st.session_state.get("v_ai_cache"):
                        st.session_state.v_data=[dict(x) for x in st.session_state.v_ai_cache]
                        st.success("✅ Lot IA restauré, 0 quota consommé.")
                    else: st.info("Aucun lot IA en cache.")
            act1,act2,act3=st.columns(3)
            with act1:
                if st.button("🎲 Variation",key="variation_v",use_container_width=True):
                    st.session_state["v_variation_seed"]=random.randint(1,999999); st.success("🎲 Variation visuelle prête.")
            with act2:
                if st.button("💾 Enregistrer",key="save_style_v",use_container_width=True):
                    _save_settings(); st.success("Style enregistré.")
            with act3:
                st.caption("⬇️ Générer ci-dessous")
            if st.button("🎬 Générer la vidéo Vocabulaire V4",key="makev"):
                try:
                    with st.spinner("Création du Short vocabulaire V4..."):
                        with tempfile.TemporaryDirectory() as tmp:
                            tic,ding=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,tmp); clips=[]; items=st.session_state.v_data
                            ha=os.path.join(tmp,"vh.mp3"); synthesize_audio(hook_v,VOICES_FR["Henri - Dynamique"],ha,tts_rate); hd=audio_duration(ha)
                            hf=save_frames([(draw_hook(hook_v,theme_v,channel_v,bg_v,p),max(.04,hd/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]],tmp,"vh")
                            ho=os.path.join(tmp,"vh.mp4"); make_segment(hf,ha,ho,tmp); clips.append(ho)
                            for idx,item in enumerate(items):
                                fa=os.path.join(tmp,f"fr_{idx}.mp3"); synthesize_audio(item['fr'],VOICES_FR["Henri - Dynamique"],fa,tts_rate); fd=audio_duration(fa)
                                if style_v.startswith("Style 2"):
                                    ff=save_frames([(draw_vocab_cumulative_frame(items,idx,theme_v,channel_v,bg_v,reveal=False,motion=p,video_title=th_v),max(.04,fd/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]],tmp,f"vf_{idx}")
                                    fo=os.path.join(tmp,f"fr_{idx}.mp4"); make_segment(ff,fa,fo,tmp); clips.append(fo)
                                    cframes=[]
                                    for sec in (3,2,1):
                                        for step in range(10): cframes.append((draw_vocab_cumulative_frame(items,idx,theme_v,channel_v,bg_v,timer=sec,timer_fraction=1-step/10,reveal=False,motion=step/10,video_title=th_v),.1))
                                    co=os.path.join(tmp,f"count_{idx}.mp4"); make_segment(save_frames(cframes,tmp,f"vc_{idx}"),countdown_sfx,co,tmp,.9); clips.append(co)
                                    ta=os.path.join(tmp,f"tr_{idx}.mp3"); tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate); td=audio_duration(ta)
                                    tf=[(draw_vocab_cumulative_frame(items,idx,theme_v,channel_v,bg_v,reveal=True,motion=p,video_title=th_v),max(.04,td/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]]
                                    tro=os.path.join(tmp,f"tr_{idx}.mp4"); make_segment(save_frames(tf,tmp,f"trf_{idx}"),ta,tro,tmp); clips.append(tro)
                                else:
                                    ff=save_frames([(draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"mot",entrance=p),max(.04,fd/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]],tmp,f"vf_{idx}")
                                    fo=os.path.join(tmp,f"fr_{idx}.mp4"); make_segment(ff,fa,fo,tmp); clips.append(fo)
                                    cframes=[]
                                    for sec in (3,2,1):
                                        for step in range(10): cframes.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"countdown",sec,1-step/10,1.0),.1))
                                    co=os.path.join(tmp,f"count_{idx}.mp4"); make_segment(save_frames(cframes,tmp,f"vc_{idx}"),countdown_sfx,co,tmp,.9); clips.append(co)
                                    ta=os.path.join(tmp,f"tr_{idx}.mp3"); tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate); td=audio_duration(ta)
                                    tf=[]
                                    if tw:
                                        for wi,w in enumerate(tw):
                                            end=tw[wi+1]['start'] if wi+1<len(tw) else td
                                            if end>w['start']: tf.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation",entrance=1.0),end-w['start']))
                                    if not tf: tf=[(draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation",entrance=1.0),td)]
                                    tro=os.path.join(tmp,f"tr_{idx}.mp4"); make_segment(save_frames(tf,tmp,f"trf_{idx}"),ta,tro,tmp); clips.append(tro)
                            oa=os.path.join(tmp,"vo.mp3"); synthesize_audio(outro_v,VOICES_FR["Henri - Dynamique"],oa,tts_rate); od=audio_duration(oa)
                            of=save_frames([(draw_hook(outro_v,theme_v,channel_v,bg_v,p),max(.04,od/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]],tmp,"vo")
                            oo=os.path.join(tmp,"vo.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)
                            final=os.path.join(tmp,"vocabulaire_pro.mp4"); concat_videos(clips,final,tmp)
                            with open(final,"rb") as f: data=f.read()
                            st.success("✅ Short Vocabulaire V4 terminé.")
                            st.video(data)
                            st.download_button("⬇️ Télécharger vocabulaire_pro.mp4",data=data,file_name="vocabulaire_pro.mp4",mime="video/mp4",key="dv4")
                except Exception as e: st.error(f"Erreur pendant le montage : {e}")
