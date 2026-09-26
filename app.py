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
.qvp-preview-panel { padding:14px; border:1px solid #dbe4f0; border-radius:20px; background:rgba(255,255,255,.96); box-shadow:0 14px 34px rgba(15,23,42,.10); }
.qvp-preview-title { font-weight:800; color:#172033; font-size:1.05rem; margin-bottom:8px; }
.qvp-preview-note { color:#64748b; font-size:.82rem; margin-bottom:10px; }
.qvp-editor-tabs [data-testid="stTabs"] button { font-size:.86rem !important; padding:7px 10px !important; }
.qvp-editor-tabs { margin-bottom:8px; border:1px solid #dbe4f0; border-radius:16px; padding:8px; background:#fff; }
.qvp-actionbar { position:sticky; bottom:8px; z-index:90; background:rgba(255,255,255,.97); backdrop-filter:blur(10px); border:1px solid #d9e2ef; border-radius:14px; padding:7px; margin-top:10px; box-shadow:0 8px 22px rgba(15,23,42,.10); }
.qvp-module-nav-title { font-size:1.05rem; font-weight:900; color:#111827; margin:0 0 4px 2px; }
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

MODEL_NAME = "gemini-1.5-flash"  # Modèle valide

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

def draw_thinking_face(draw, theme, cx, cy, size=30, phase=0.0, style="Réflexion", color=None):
    a=color or theme["accent"]
    pulse=1.0+0.08*math.sin(float(phase)*math.pi*2)
    r=int(size*pulse)
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(8,14,30,235),outline="white",width=max(2,int(size/8)))
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

def draw_lightning_icon(draw, theme, cx, cy, size=28):
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
        if os.path.exists(SETTINGS_FILE):
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
    prefix="v_" if module=="vocab" else "q_"
    defaults={
        "show_title":True,"title_y":42,"title_size":46,
        "question_y":205,"question_size":47,"question_box_radius":28,
        "answer_y":405,"answer_h":91,"answer_gap":12,"answer_size":30,"answer_radius":20,
        "timer_y":1045,"timer_x":540,"timer_size":58,"timer_style":"Anneau","timer_color":"#FFCD40","timer_text_size":55,"timer_label_y":1110,"timer_label_size":23,"timer_show_label":True,"timer_label":"RÉFLÉCHIS","timer_label_color":"#FFCD40",
        "face_size":30,"face_x":0,"face_y":0,"face_style":"Aucun","face_color":"#FFCD40","face_show":True,
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

def draw_header(draw, theme, q_num, total, title="Culture Générale", phase=0.0):
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
    
    sf=get_font(int(cfg.get("score_size",31))); score=f"{q_num}/{total}"; sw=text_width(draw,score,sf); sh=text_height(sf,score)
    by=int(cfg.get("score_y",112)); bw=sw+40; bh=max(42,sh+18); bx=(WIDTH-bw)//2; radius=int(cfg.get("score_radius",22))
    score_bg=_hex_rgb(cfg.get("score_bg"),(7,13,28)); score_color=_hex_rgb(cfg.get("score_color"),theme["accent"])
    draw.rounded_rectangle((bx,by,bx+bw,by+bh),radius=radius,fill=score_bg,outline=score_color,width=int(cfg.get("score_border",2)))
    draw.text(((WIDTH-sw)/2,by+(bh-sh)/2-2),score,font=sf,fill=score_color)

def draw_timer(draw, theme, timer, fraction=1.0, pulse=0.0):
    cfg=_layout("quiz")
    color=_hex_rgb(cfg.get("timer_color"),theme["accent"])
    if timer<=1:
        color=_hex_rgb(cfg.get("timer_color"),theme["danger"])
    cx=int(cfg.get("timer_x",540)); cy=int(cfg.get("timer_y",1045)); r=max(18,int(cfg.get("timer_size",58))); pr=int(2+7*clamp(pulse))
    style=str(cfg.get("timer_style","Anneau")); text_size=max(18,int(cfg.get("timer_text_size",55)))
    frac=clamp(fraction)
    dark=(7,12,26)
    if style=="Anneau":
        draw.ellipse((cx-r-pr,cy-r-pr,cx+r+pr,cy+r+pr),outline=color,width=2)
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=dark,outline=(255,255,255),width=3)
        draw.arc((cx-r+7,cy-r+7,cx+r-7,cy+r-7),-90,-90+int(360*frac),fill=color,width=max(5,int(r*.15)))
    else:
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=dark,outline=color,width=3)
    ts=str(timer); tf=get_font(text_size); th=text_height(tf,ts)
    draw.text((cx-text_width(draw,ts,tf)/2,cy-th/2-3),ts,font=tf,fill=color)

def _draw_question_rich(draw, question, theme, y=205, phase=0.0):
    cfg=_layout("quiz")
    f=get_font(cfg["question_size"]); lines=wrap_text(question,f,900)[:3]; hi=_highlight_words(question); yy=int(cfg["question_y"])
    box_top=yy-18; box_bottom=yy+len(lines)*int(cfg["question_size"]*1.18)+12
    radius=int(cfg["question_box_radius"])
    draw.rounded_rectangle((58,box_top,1022,box_bottom),radius=radius,fill=(6,12,28,218),outline=_hex_rgb(cfg["primary"],theme["accent"]),width=2)
    for line in lines:
        words=line.split(); widths=[text_width(draw,w,f) for w in words]; space=text_width(draw," ",f)
        totalw=sum(widths)+space*max(0,len(words)-1)
        x=(WIDTH-totalw)/2+int(5*math.sin(phase*math.pi*2*cfg["motion_strength"]))
        for w,ww in zip(words,widths):
            key=w.strip(".,?!:;()[]«»\"'").lower(); fill=_hex_rgb(cfg["primary"],theme["accent"]) if key in hi else _hex_rgb(cfg["text"],(255,255,255))
            draw.text((x+2,yy+3),w,font=f,fill=(0,0,0)); draw.text((x,yy),w,font=f,fill=fill)
            x+=ww+space
        yy+=int(cfg["question_size"]*1.18)
    return box_bottom

def _draw_answers(draw, options, theme, entrance=1.0, correct_idx=None, reveal_progress=0.0, phase=0.0):
    cfg=_layout("quiz"); left,right=62,1018
    card_h=int(cfg["answer_h"]); gap=int(cfg["answer_gap"]); start_y=int(cfg["answer_y"]); f_opt=get_font(cfg["answer_size"])
    for i,opt in enumerate(options[:4]):
        y=start_y+i*(card_h+gap)
        correct=(correct_idx is not None and i==correct_idx)
        fill=_hex_rgb(cfg["correct"],theme["success"]) if correct else _hex_rgb(cfg["answer"],(17,48,91))
        draw.rounded_rectangle((left,y,right,y+card_h),radius=int(cfg["answer_radius"]),fill=fill,outline=(210,225,250),width=2)
        letter=chr(65+i)
        draw.text((82,y+15),letter,font=f_opt,fill="white")
        draw.text((154,y+15),clean_text(opt),font=f_opt,fill="white")

def draw_quiz_frame(question, options, theme_name, q_num, total, channel, bg_file=None, entrance=1.0, timer=None, timer_fraction=1.0, correct_idx=None, reveal_progress=0.0, pulse=0.0, motion=0.0, video_title="Culture Générale", explanation=None, explanation_progress=0.0):
    cfg=_layout("quiz"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    img=add_top_glow(base,theme); draw=ImageDraw.Draw(img)
    if cfg["show_title"]:
        draw_header(draw,theme,q_num,total,video_title,motion)
    _draw_question_rich(draw,question,theme,y=int(cfg["question_y"]),phase=motion)
    _draw_answers(draw,options,theme,entrance,correct_idx,reveal_progress,motion)
    if timer is not None and cfg["show_timer"]:
        draw_timer(draw,theme,timer,timer_fraction,pulse)
    draw_brand(draw,theme,channel,(q_num-1)/max(1,total))
    return img

def draw_style2_frame(items, active_idx, theme_name, channel, bg_file=None, timer=None, timer_fraction=1.0, answer_reveal=False, motion=0.0, video_title="Culture Générale"):
    cfg=_layout("quiz"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    img=add_top_glow(base,theme); draw=ImageDraw.Draw(img)
    rounded_text(draw,(55,42,1025,112),f"{video_title} • {min(active_idx+1,len(items))}/{len(items)}",get_font(34),_hex_rgb(cfg["text"],(255,255,255)),_hex_rgb(cfg["primary"],theme["accent"]),2,24)
    return img

def draw_vocab_frame(items,idx,langue,theme_name,channel,bg_file=None,phase="mot",timer=None,timer_fraction=1.0,entrance=1.0):
    cfg=_layout("vocab"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    img=add_top_glow(base,theme); draw=ImageDraw.Draw(img)
    rounded_text(draw,(55,int(cfg["title_y"]),430,int(cfg["title_y"])+65),f"VOCABULAIRE • {idx+1}/{len(items)}",get_font(int(cfg["title_size"])),_hex_rgb(cfg["answer"],theme["card"]),_hex_rgb(cfg["primary"],theme["accent"]),2,26)
    return img

def draw_vocab_cumulative_frame(items, active_idx, theme_name, channel, bg_file=None, timer=None, timer_fraction=1.0, reveal=False, motion=0.0, video_title="Voyage"):
    cfg=_layout("vocab"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    img=add_top_glow(base,theme); draw=ImageDraw.Draw(img)
    rounded_text(draw,(55,35,1025,100),f"VOCABULAIRE • {min(active_idx+1,len(items))}/{len(items)}",get_font(32),_hex_rgb(cfg.get("text"),(255,255,255)),_hex_rgb(cfg.get("primary"),theme["accent"]),2,22)
    return img

# ------------------------- Gemini Handler --------------------
def parse_json(text):
    text = (text or "").strip().replace("```json", "").replace("```", "").strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end <= start:
        raise ValueError("L'IA n'a pas renvoyé un JSON valide.")
    return json.loads(text[start:end + 1])

def gemini_generate_text(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = getattr(response, "text", None)
        if not text:
            raise ValueError("Réponse vide de la part du modèle.")
        return text, False
    except Exception as e:
        raise RuntimeError(f"Erreur API Gemini : {e}")

def normalize_questions(data):
    out=[]
    if not isinstance(data, list): return out
    for q in data:
        if not isinstance(q, dict): continue
        question = clean_text(q.get("question", ""))
        opts = [clean_text(x) for x in q.get("options", [])]
        if len(opts) != 4 or not question: continue
        ans = clean_text(q.get("reponse_correcte", "A")).upper()[:1]
        out.append({"question": question, "options": opts, "reponse_correcte": ans if ans in "ABCD" else "A", "explication": clean_text(q.get("explication",""))})
    return out

# ------------------- Streamlit UI -------------------
api_key = st.sidebar.text_input("Clé API Gemini", type="password")
if api_key:
    genai.configure(api_key=api_key)

st.markdown('<div class="qvp-module-nav-title">🎬 QuizVideo Pro</div>', unsafe_allow_html=True)
app_module = st.radio("Application", ["🧠 Quizz TikTok Pro", "🗣️ Vocabulaire Pro"], horizontal=True)

if app_module == "🧠 Quizz TikTok Pro":
    st.markdown('<div class="qvp-hero"><div><h1>Quiz TikTok Pro</h1><p>Générez vos quiz Shorts facilement</p></div></div>', unsafe_allow_html=True)
    th_q = st.text_input("Sujet du Quiz", "Culture Générale")
    nb_q = st.slider("Nombre de questions", 1, 15, 5)
    theme_q = st.selectbox("Style Visuel", list(THEMES.keys()))
    
    if st.button("🤖 Générer les questions avec IA"):
        if not api_key:
            st.error("Veuillez saisir une clé API Gemini valide dans la barre latérale.")
        else:
            with st.spinner("Génération en cours..."):
                try:
                    prompt = f'Génère {nb_q} questions de quiz sur "{th_q}". Format JSON strict : [{"question": "...", "options": ["A", "B", "C", "D"], "reponse_correcte": "A", "explication": "..."}]'
                    raw_res, _ = gemini_generate_text(prompt)
                    data = normalize_questions(parse_json(raw_res))
                    st.session_state["q_data"] = data
                    st.success(f"{len(data)} questions générées avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")

    if "q_data" in st.session_state and st.session_state["q_data"]:
        st.write("### Aperçu des questions")
        st.json(st.session_state["q_data"])

elif app_module == "🗣️ Vocabulaire Pro":
    st.markdown('<div class="qvp-hero"><div><h1>Vocabulaire Pro</h1><p>Générez vos fiches de vocabulaire</p></div></div>', unsafe_allow_html=True)
    th_v = st.text_input("Sujet de vocabulaire", "Voyage")
    nb_v = st.slider("Nombre de mots", 1, 15, 5)
    langue_v = st.selectbox("Langue cible", list(VOICES_MAP.keys()))

    if st.button("🤖 Générer les mots avec IA"):
        if not api_key:
            st.error("Veuillez saisir une clé API Gemini valide dans la barre latérale.")
        else:
            with st.spinner("Génération en cours..."):
                try:
                    prompt = f'Génère {nb_v} mots de vocabulaire français avec traduction en {langue_v} sur "{th_v}". Format JSON strict : [{"fr": "...", "trad": "..."}]'
                    raw_res, _ = gemini_generate_text(prompt)
                    data = parse_json(raw_res)
                    st.session_state["v_data"] = data
                    st.success(f"{len(data)} mots générés avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")

    if "v_data" in st.session_state and st.session_state["v_data"]:
        st.write("### Aperçu des mots")
        st.json(st.session_state["v_data"])
