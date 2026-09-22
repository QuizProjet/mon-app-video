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
st.title("🎬 QuizVideo Pro")
st.caption("Créateur de Shorts 9:16 • Quiz dynamique + Vocabulaire")

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
.block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 4rem; }
h1, h2, h3 { letter-spacing: -0.02em; color:#111827; }
[data-testid="stTabs"] button { font-weight: 800; font-size: 1.02rem; color:#334155; padding:10px 18px; }
[data-testid="stTabs"] [aria-selected="true"] { color:#6d4aff !important; border-bottom-color:#6d4aff !important; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea { border-radius: 14px !important; background:#ffffff !important; color:#172033 !important; border-color:#cbd5e1 !important; }
[data-baseweb="select"] > div { background:#ffffff !important; border-color:#cbd5e1 !important; color:#172033 !important; border-radius:14px !important; }
[data-testid="stButton"] button { border-radius: 14px; min-height: 2.8rem; font-weight: 700; border: 1px solid #cbd5e1; background: linear-gradient(135deg,#ffffff,#f3f6fa); color:#172033; box-shadow:0 4px 12px rgba(15,23,42,.06); }
[data-testid="stButton"] button:hover { border-color:#7c8cff; transform: translateY(-1px); box-shadow:0 8px 18px rgba(15,23,42,.10); }
[data-testid="stFileUploaderDropzone"] { border: 1px dashed #b9c5d6; border-radius: 16px; background: #ffffff; }
.qvp-card { padding: 18px 20px; border: 1px solid #dbe2ec; border-radius: 18px; background: #ffffff; box-shadow: 0 10px 28px rgba(15,23,42,.07); margin: 8px 0 18px; }
.qvp-small { color:#64748b; font-size:.9rem; }
.qvp-side-brand { display:flex; gap:12px; align-items:center; padding:8px 2px 18px; }
.qvp-logo { width:42px; height:42px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:25px; font-weight:900; background:linear-gradient(135deg,#7b4dff,#36b8e8); color:white !important; box-shadow:0 8px 24px rgba(83,67,180,.35); }
.qvp-side-title { font-size:1.18rem; font-weight:800; color:#fff !important; }
.qvp-side-sub { font-size:.72rem; color:#b9c8e8 !important; margin-top:2px; }
.qvp-side-note { margin-top:18px; padding:14px; border:1px solid rgba(255,255,255,.13); border-radius:16px; background:linear-gradient(135deg,rgba(124,77,255,.18),rgba(42,180,216,.10)); font-size:.78rem; line-height:1.45; }
.qvp-hero { display:flex; justify-content:space-between; align-items:center; gap:20px; padding:26px 30px; border:1px solid #dbe4f0; border-radius:24px; background:rgba(255,255,255,.84); box-shadow:0 14px 36px rgba(31,48,82,.08); margin-bottom:18px; }
.qvp-hero h1 { margin:4px 0 6px; font-size:2.25rem; }
.qvp-hero p { margin:0; color:#66748c; }
.qvp-kicker { color:#6751e8; font-size:.78rem; font-weight:800; letter-spacing:.12em; }
.qvp-hero-pill { padding:11px 16px; border-radius:999px; background:#f0edff; color:#5c45d5; font-weight:800; white-space:nowrap; }
.qvp-flow { display:flex; align-items:center; justify-content:center; gap:14px; flex-wrap:wrap; padding:13px 18px; border:1px solid #e1e7f0; border-radius:18px; background:#fff; color:#334155; margin:0 0 20px; box-shadow:0 7px 20px rgba(15,23,42,.04); }
.qvp-flow b { color:#8b78ee; }
.qvp-mini-card { min-height:94px; padding:18px; border:1px solid #ddd7ff; border-radius:17px; background:linear-gradient(135deg,#faf9ff,#f2f8ff); color:#334155; }
.qvp-mini-card span { color:#64748b; font-size:.88rem; }
.qvp-preview-placeholder { height:250px; border:1px dashed #cbd5e1; border-radius:18px; display:flex; align-items:center; justify-content:center; text-align:center; color:#64748b; background:#f8fafc; }
.qvp-economy { padding:13px 16px; border-radius:15px; border:1px solid #d6e7f7; background:#eef8ff; color:#28506d; margin:10px 0 16px; }
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

def draw_thinking_icon(draw, theme, phase=0.0, cx=935, cy=1250):
    """Dessine une petite icône de réflexion animée sans dépendre d'un emoji/font externe."""
    phase = float(phase or 0.0)
    pulse = 0.5 + 0.5 * math.sin(phase * math.pi * 2)
    r = int(34 + 4 * pulse)
    accent = theme.get("accent", (255, 205, 64))
    # Bulle de réflexion
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(10, 15, 25), outline=accent, width=4)
    # Trois points qui pulsent légèrement
    dot_r = 5
    spacing = 15
    for i in range(3):
        local = 0.5 + 0.5 * math.sin(phase * math.pi * 2 + i * 0.9)
        rr = max(3, int(dot_r + 2 * local))
        dx = cx + (i - 1) * spacing
        draw.ellipse((dx-rr, cy-rr, dx+rr, cy+rr), fill=accent)
    # Petite queue de bulle
    draw.polygon([(cx-18, cy+r-1), (cx-30, cy+r+15), (cx-3, cy+r-7)], fill=accent)

def draw_brand(draw, theme, channel, progress=None):
    if channel:
        draw.text((55, 1810), clean_text(channel), font=get_font(28), fill=theme["muted"])
    if progress is not None:
        x, y, w, h = 55, 1745, 970, 12
        draw.rounded_rectangle((x,y,x+w,y+h), radius=6, fill=(65,70,85))
        draw.rounded_rectangle((x,y,x+int(w*clamp(progress)),y+h), radius=6, fill=theme["accent"])

def draw_header(draw, theme, q_num, total, title="Quiz Culture Générale"):
    title=clean_text(title) or "Quiz"
    if len(title)>28: title=title[:28].rstrip()+"…"
    title_text=f"Quiz {title}" if not title.lower().startswith("quiz") else title
    tf=get_font(62)
    lines=wrap_text(title_text,tf,850)[:2]
    y=70
    for line in lines:
        tw=text_width(draw,line,tf)
        # shadow + white title for the strong Shorts look
        draw.text(((WIDTH-tw)/2+5,y+7),line,font=tf,fill=(0,0,0))
        draw.text(((WIDTH-tw)/2,y),line,font=tf,fill="white")
        y+=66
    score=f"{q_num}/{total}"
    sf=get_font(54)
    sw=text_width(draw,score,sf)
    draw.text(((WIDTH-sw)/2,205),score,font=sf,fill=theme["accent"])
    # small thinking icon, without relying on an emoji font
    draw_thinking_icon(draw,theme,phase=(q_num*0.17)%1.0,cx=960,cy=115)

def draw_timer(draw, theme, timer, fraction=1.0, pulse=0.0):
    # Countdown inspired by the reference: large, readable and visually urgent.
    if timer <= 0:
        color=theme["danger"]
    elif timer == 1:
        color=theme["danger"]
    elif timer == 2:
        color=(249,115,22)
    else:
        color=theme["accent"]
    cx, cy, r = 540, 1370, 78
    draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(10,15,25), outline=(245,248,252), width=6)
    box=(cx-r+6,cy-r+6,cx+r-6,cy+r-6)
    draw.arc(box, -90, -90 + int(360*clamp(fraction)), fill=color, width=11)
    if pulse > 0:
        pr=int(5+18*pulse)
        draw.ellipse((cx-r-pr,cy-r-pr,cx+r+pr,cy+r+pr), outline=color, width=3)
    tf=get_font(66+int(8*pulse))
    ts=str(timer)
    draw.text((cx-text_width(draw,ts,tf)/2,cy-42),ts,font=tf,fill=color)


def draw_quiz_frame(question, options, theme_name, q_num, total, channel, bg_file=None, entrance=1.0, timer=None, timer_fraction=1.0, correct_idx=None, reveal_progress=0.0, pulse=0.0, motion=0.0, video_title="Culture Générale"):
    theme=THEMES[theme_name]
    base=make_base(theme_name,bg_file)
    # Subtle camera drift/zoom: the frame never feels frozen during the reflection.
    phase=clamp(motion)
    scale=1.0+0.018*math.sin(phase*math.pi*2)
    bw,bh=base.size
    nw,nh=int(bw*scale),int(bh*scale)
    if nw>bw or nh>bh:
        zoom=base.resize((nw,nh),Image.Resampling.LANCZOS)
        sx=int((nw-bw)*0.5 + 14*math.sin(phase*math.pi*2))
        sy=int((nh-bh)*0.5 + 10*math.cos(phase*math.pi*2))
        img=zoom.crop((sx,sy,sx+bw,sy+bh))
    else:
        img=base.copy()
    img=add_top_glow(img,theme,1.0+0.40*pulse)
    draw=ImageDraw.Draw(img)
    draw_header(draw,theme,q_num,total,video_title)

    f_q=get_font(58)
    q_lines=wrap_text(question,f_q,900)[:3]
    q_y=315
    q_e=ease_out(entrance)
    q_offset=int((1-q_e)*65)
    # Question movement accelerates slightly as the reflection advances.
    drift_x=int(18*math.sin((phase*1.15)*math.pi*2))
    drift_y=int(7*math.sin((phase*2.0)*math.pi*2))
    for li,line in enumerate(q_lines):
        tw=text_width(draw,line,f_q)
        local_x=(WIDTH-tw)/2+drift_x+int(4*math.sin((phase+li*.12)*math.pi*4))
        draw.text((local_x+4,q_y+q_offset+drift_y+5),line,font=f_q,fill=(0,0,0))
        draw.text((local_x,q_y+q_offset+drift_y),line,font=f_q,fill="white")
        q_y+=78

    # Four answers are visible together from the first frame.
    left,right=60,1020
    card_h,gap=118,18
    start_y=650
    for i,opt in enumerate(options[:4]):
        local=ease_out(clamp((entrance-i*0.035)/0.50))
        y=start_y+i*(card_h+gap)+int((1-local)*70)
        card_motion=int(8*math.sin((phase+i*0.08)*math.pi*2)) if (timer is not None or correct_idx is None) else 0
        y+=card_motion
        correct=(correct_idx is not None and i==correct_idx)
        dim=(correct_idx is not None and not correct)
        if correct:
            rp=ease_back(reveal_progress)
            fill=theme["success"]; outline=(255,255,255); width=5; extra=int(9*rp)
        else:
            fill=theme["card"] if i%2==0 else theme["card2"]; outline=theme["accent"]; width=3; extra=0
        if dim:
            fill=tuple(max(0,int(c*0.45)) for c in fill); outline=tuple(max(0,int(c*0.45)) for c in outline)
        draw.rounded_rectangle((left-extra,y-extra,right+extra,y+card_h+extra),radius=25,fill=fill,outline=outline,width=width)
        label=f"{chr(65+i)}  -  {clean_text(opt)}"
        f_opt=get_font(39)
        lines=wrap_text(label,f_opt,right-left-58)[:2]
        th=sum(text_height(f_opt,x) for x in lines)+max(0,len(lines)-1)*8
        ty=y+(card_h-th)/2-3
        for line in lines:
            draw.text((96,ty),line,font=f_opt,fill="white")
            ty+=text_height(f_opt,line)+8
        if correct:
            r=27; cx=right-48; cy=y+card_h/2
            draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill="white")
            tick=get_font(32); ts="✓"
            draw.text((cx-text_width(draw,ts,tick)/2,cy-20),ts,font=tick,fill=theme["success"])

    if timer is not None:
        draw_thinking_icon(draw,theme,phase,cx=935,cy=1250)
        draw_timer(draw,theme,timer,timer_fraction,pulse)

    if correct_idx is not None:
        p=ease_back(reveal_progress)
        by=1235-int(12*p)
        draw.rounded_rectangle((255,by,825,1320),radius=30,fill=theme["success"])
        txt="✓ BONNE RÉPONSE"; f=get_font(38+int(4*p))
        draw.text(((WIDTH-text_width(draw,txt,f))/2,by+22),txt,font=f,fill="white")

    draw_brand(draw,theme,channel,(q_num-1)/max(1,total))
    sf=get_font(23)
    draw.text((55,1860),"QuizVideo Pro  •  Vocabulaire Pro",font=sf,fill=theme["muted"])
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
    rounded_text(draw,(bx,by,bx+badge_w,by+76),"🎯 TESTE-TOI",get_font(34),theme["accent"],None,0,34)
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
    draw.text((95,820),"💡 EXPLICATION",font=get_font(32),fill=theme["accent"])
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
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme)
    draw=ImageDraw.Draw(img)
    rounded_text(draw,(55,70,430,135),f"VOCABULAIRE • {idx+1}/{len(items)}",get_font(32),theme["card"],theme["accent"],2,26)
    item=items[idx]; fr=clean_text(item.get("fr","")); tr=clean_text(item.get("trad",""))
    p=ease_out(entrance)
    fbig=get_font(88)
    y=500+int((1-p)*80)
    draw.text(((WIDTH-text_width(draw,fr,fbig))/2,y),fr,font=fbig,fill=theme["accent"])
    if phase in ("translation","reveal"):
        ft=get_font(58)
        lines=wrap_text(tr,ft,850); yy=760
        for line in lines:
            draw.text(((WIDTH-text_width(draw,line,ft))/2,yy),line,font=ft,fill="white"); yy+=75
    if phase=="countdown" and timer is not None:
        draw_timer(draw,theme,timer,timer_fraction,0.15)
    draw_brand(draw,theme,channel,idx/max(1,len(items)))
    return img

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
    return cleaned[:10]

def _save_vocab_editor(rows):
    cleaned=[]
    for row in rows:
        fr=clean_text(row.get("Français", ""))
        tr=clean_text(row.get("Traduction", ""))
        if fr and tr:
            cleaned.append({"fr":fr,"trad":tr})
    return cleaned[:10]

api_key=st.sidebar.text_input("Clé API Gemini",type="password")
if api_key: genai.configure(api_key=api_key)
voice_rate=st.sidebar.slider("⚡ Vitesse voix",0,30,15)
tts_rate=f"+{voice_rate}%"
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
    rounded_text(draw,(90+drift,310,990+drift,420),"⚡ PAUSE QUIZ",get_font(42),theme["accent"],None,0,30)
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
        "histoire":["histoire","antiquité","antiquite","moyen âge","moyen age","guerre","empire","roi","reine"],
        "geographie":["géographie","geographie","pays","capitale","monde","continent","ville","voyage"],
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
    'Crée un fond 9:16 stylisé localement selon le sujet. Aucun appel API.'
    key=("auto_bg_v3",theme_name,clean_text(topic).lower())
    if key in _BASE_CACHE: return _BASE_CACHE[key].copy()
    theme=THEMES[theme_name]
    img=make_base(theme_name).convert("RGBA")
    ov=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    accent=theme["accent"]; muted=theme["muted"]; kind=_theme_keywords(topic)
    seed=int(hashlib.md5((theme_name+"|"+clean_text(topic)).encode()).hexdigest()[:8],16)
    rng=random.Random(seed)
    for _ in range(100):
        x=rng.randint(-80,WIDTH+80); y=rng.randint(0,HEIGHT); r=rng.randint(2,12)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*accent,rng.randint(18,60)))
    if kind=="espace":
        for _ in range(6):
            x=rng.randint(0,WIDTH); y=rng.randint(250,1650); r=rng.randint(90,260)
            d.ellipse((x-r,y-r,x+r,y+r),outline=(*accent,42),width=4)
    elif kind=="geographie":
        cx,cy=540,820
        for rx,ry in [(300,300),(300,135),(135,300)]:
            d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(*accent,45),width=5)
        d.line((cx-300,cy,cx+300,cy),fill=(*muted,35),width=4)
    elif kind=="histoire":
        for x in range(110,1000,175):
            d.polygon([(x,1080),(x+70,650),(x+140,1080)],fill=(*accent,18),outline=(*accent,40))
            d.rectangle((x+25,820,x+115,1080),fill=(*muted,12))
    elif kind=="science":
        cx,cy=540,850
        for r in (120,220,320): d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*accent,40),width=4)
        d.ellipse((cx-42,cy-42,cx+42,cy+42),fill=(*accent,90))
    elif kind=="animaux":
        for j in range(7):
            pts=[(x,500+j*145+int(30*math.sin(x/90+j))) for x in range(-40,1120,40)]
            d.line(pts,fill=(*accent,42),width=6)
    elif kind=="sport":
        for r in (120,250,380): d.arc((540-r,850-r,540+r,850+r),210,330,fill=(*accent,50),width=7)
    elif kind=="art":
        for _ in range(8):
            x=rng.randint(100,850); y=rng.randint(450,1400); w=rng.randint(130,360); h=rng.randint(80,220)
            d.rounded_rectangle((x,y,x+w,y+h),radius=35,outline=(*accent,42),width=5)
    elif kind=="food":
        for _ in range(8):
            x=rng.randint(150,850); y=rng.randint(450,1450); r=rng.randint(35,90)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(*accent,18),outline=(*accent,42),width=4)
    else:
        for _ in range(7):
            x=rng.randint(100,850); y=rng.randint(350,1500)
            d.rounded_rectangle((x,y,x+rng.randint(140,320),y+rng.randint(70,180)),radius=35,outline=(*accent,34),width=4)
    vign=Image.new("L",(WIDTH,HEIGHT),0); vd=ImageDraw.Draw(vign)
    vd.rectangle((80,150,1000,1780),fill=105); vign=vign.filter(ImageFilter.GaussianBlur(100))
    result=Image.alpha_composite(img,ov)
    dark=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0)); dark.putalpha(vign)
    result=Image.alpha_composite(result,dark).convert("RGB")
    _BASE_CACHE[key]=result.copy()
    return result

def selected_video_background(theme_name,topic,mode,uploaded=None):
    if mode=="Image personnalisée" and uploaded is not None: return fit_background(uploaded)
    if mode=="Généré automatiquement": return generate_theme_background(theme_name,topic)
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
st.sidebar.markdown("### 🧭 Modules")
st.sidebar.caption("🧠 Quiz TikTok Pro  •  🗣️ Vocabulaire Pro")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 Mes projets")
st.sidebar.caption("Vos quiz et réglages restent dans votre session.")
st.sidebar.markdown("### ⚙️ Paramètres")
st.sidebar.caption("Les changements visuels ne consomment pas de quota.")
st.sidebar.markdown("""
<div class="qvp-side-note"><b>✨ Mode économique actif</b><br>
Gemini est utilisé uniquement lorsque vous demandez du nouveau contenu IA.</div>
""", unsafe_allow_html=True)

tab1,tab2=st.tabs(["🧠 Quizz TikTok Pro","🗣️ Vocabulaire Pro"])

with tab1:
    st.markdown('<div class="qvp-hero"><div><div class="qvp-kicker">🎬 CRÉATEUR DE SHORTS 9:16</div><h1>Quiz TikTok Pro</h1><p>Créez des quiz rapides, élégants et captivants.</p></div><div class="qvp-hero-pill">✨ Créez • Apprenez • Partagez</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="qvp-card"><b>🎬 Studio Quiz</b><div class="qvp-small">Question → 4 réponses → 3·2·1 → révélation → explication → CTA</div></div>', unsafe_allow_html=True)
    hook_q=st.text_input("Hook","IMPOSSIBLE d'avoir 10 sur 10 !",key="hq")
    channel_q=st.text_input("Nom de la chaîne","@QuizMaster_Pro",key="cq")
    c1,c2=st.columns(2)
    with c1:
        voice_q=VOICES_FR[st.selectbox("Voix",list(VOICES_FR),key="vq")]
        theme_q=st.selectbox("Style visuel",list(THEMES),key="tq")
    with c2:
        nb_q=st.slider("Nombre de questions",1,10,10,key="nbq")
        th_q=st.text_input("Sujet du quiz","Culture Générale",key="thq")
    outro_q=st.text_input("CTA final","Quel est ton score ? Écris-le en commentaire !",key="oq")
    st.caption("💡 Le CSV accepte aussi la colonne « explication » : elle sera lue après la révélation et affichée dans la vidéo.")
    st.markdown("### 🖼️ Fond de la vidéo")
    bg_mode_q=st.radio(
        "Choisir le fond",
        ["✨ Généré automatiquement selon le thème","🖼️ Image personnalisée","◯ Aucun"],
        horizontal=True,key="bg_mode_q"
    )
    uploaded_bg_q=None
    if bg_mode_q=="🖼️ Image personnalisée":
        uploaded_bg_q=st.file_uploader("Télécharger une image 9:16",type=["png","jpg","jpeg"],key="bgq")
    bg_mode_clean_q=("Généré automatiquement" if bg_mode_q.startswith("✨")
                     else "Image personnalisée" if bg_mode_q.startswith("🖼️")
                     else "Aucun")
    bg_q=selected_video_background(theme_q,th_q,bg_mode_clean_q,uploaded_bg_q)
    if bg_mode_clean_q=="Généré automatiquement":
        st.caption("✨ Fond visuel créé localement selon le sujet et le style — 0 quota Gemini.")
    elif bg_mode_clean_q=="Image personnalisée" and uploaded_bg_q:
        st.success("✅ Fond personnalisé prêt.")
    mode_q=st.radio("Source des questions",["🤖 IA Gemini","📄 Importer un CSV"],horizontal=True,key="mq")

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
        st.markdown('<div class="qvp-card"><b>📄 Import CSV</b><div class="qvp-small">Prépare tes questions dans Excel/Google Sheets puis exporte en CSV. Maximum : 10 questions.</div></div>', unsafe_allow_html=True)
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
        if st.button("🎬 Générer le Short Quiz V5",key="makeq"):
            try:
                with st.spinner("Création du Short dynamique V5..."):
                    with tempfile.TemporaryDirectory() as tmp:
                        tic,ding=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,tmp)
                        clips=[]; total=len(st.session_state.q_data)

                        # Hook: animation courte au lieu d'une carte statique.
                        ha=os.path.join(tmp,"hook.mp3"); synthesize_audio(hook_q,voice_q,ha,tts_rate); hd=audio_duration(ha)
                        hf=save_frames([(draw_hook(hook_q,theme_q,channel_q,bg_q,p),max(0.04,hd/8)) for p in [0.05,0.18,0.35,0.55,0.75,0.92,1.0]],tmp,"hook")
                        hout=os.path.join(tmp,"hook.mp4"); make_segment(hf,ha,hout,tmp); clips.append(hout)

                        for idx,q in enumerate(st.session_state.q_data):
                            corr="ABCD".index(q["reponse_correcte"])
                            # 1) Question: voix + arrivée animée des cartes.
                            qa_raw=os.path.join(tmp,f"q_{idx}.mp3")
                            synthesize_audio(q['question'],voice_q,qa_raw,tts_rate); qdur=audio_duration(qa_raw)
                            qmusic=make_suspense_music(qdur,tmp,f"qmusic_{idx}",0.10)
                            qa=os.path.join(tmp,f"q_{idx}_mix.m4a"); mix_background_music(qa_raw,qmusic,qa,music_volume=0.10)
                            qframes=[]
                            for p in [0.0,0.12,0.25,0.40,0.58,0.76,1.0]:
                                qframes.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=p,video_title=th_q),min(0.08,max(0.033,qdur/12))))
                            # Le dernier frame porte le reste de la voix.
                            used=sum(d for _,d in qframes); qframes[-1]=(qframes[-1][0],max(0.05,qdur-used+qframes[-1][1]))
                            qo=os.path.join(tmp,f"question_{idx}.mp4"); make_segment(save_frames(qframes,tmp,f"qf_{idx}"),qa,qo,tmp); clips.append(qo)

                            # 2) Réflexion: vrai timer animé 3 -> 2 -> 1, ring qui se vide.
                            countdown_frames=[]
                            frame_no=0
                            for sec in (3,2,1):
                                for step in range(0,10):
                                    frac=1-step/10
                                    pulse=1-step/10
                                    motion=frame_no/30.0
                                    countdown_frames.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=1.0,timer=sec,timer_fraction=frac,pulse=pulse,motion=motion,video_title=th_q),0.1))
                                    frame_no+=1
                            # 0 is shown at the exact end of reflection before the final sound.
                            countdown_frames.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=1.0,timer=0,timer_fraction=0.0,pulse=1.0,motion=frame_no/30.0,video_title=th_q),0.12))
                            countdown_music=make_suspense_music(3.12,tmp,f"countmusic_{idx}",0.09)
                            countdown_audio=os.path.join(tmp,f"countdown_mix_{idx}.m4a")
                            mix_background_music(countdown_sfx,countdown_music,countdown_audio,voice_volume=1.0,music_volume=0.10)
                            co=os.path.join(tmp,f"countdown_{idx}.mp4"); make_segment(save_frames(countdown_frames,tmp,f"timer_{idx}"),countdown_audio,co,tmp,.78); clips.append(co)
                            end_sfx=make_end_tick(tic,ding,tmp)
                            end_frame=draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=1.0,timer=0,timer_fraction=0.0,pulse=1.0,motion=1.0,video_title=th_q)
                            end_path=save_frames([(end_frame,0.45)],tmp,f"end_{idx}")
                            end_clip=os.path.join(tmp,f"end_{idx}.mp4"); make_segment(end_path,end_sfx,end_clip,tmp,.9); clips.append(end_clip)

                            # 3) Révélation avec petit zoom vert + ding.
                            reveal_frames=[]
                            reveal_points=[0.0,0.15,0.35,0.60,0.82,1.0]
                            for rp in reveal_points:
                                reveal_frames.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=1.0,correct_idx=corr,reveal_progress=rp,pulse=0.25*(1-rp),motion=rp,video_title=th_q),0.12))
                            reveal_raw=os.path.join(tmp,f"reveal_voice_{idx}.mp3")
                            exp_text=f"La bonne réponse est {q['reponse_correcte']}. {q['options'][corr]}. {q.get('explication','') or 'Bravo !'}"
                            ea=os.path.join(tmp,f"exp_{idx}.mp3"); ewords=synthesize_audio(exp_text,voice_q,ea,tts_rate); edur=audio_duration(ea)
                            # Ding superposé au début de l'explication.
                            mixed=os.path.join(tmp,f"exp_mix_{idx}.m4a"); mix_voice_sfx(ea,ding,mixed,0,0.8)
                            # 6 images x 0.12 s = 0.72 s minimum pour éviter une durée négative.
                            reveal_dur=max(0.72,min(0.95,edur*0.14))
                            each=reveal_dur/len(reveal_frames)
                            reveal_frames=[(img,each) for img,_ in reveal_frames]
                            ro=os.path.join(tmp,f"reveal_{idx}.mp4"); make_segment(save_frames(reveal_frames,tmp,f"reveal_{idx}"),mixed,ro,tmp); clips.append(ro)

                            # 4) Explication: carte verte conservée + mots surlignés au rythme de la voix.
                            tf=[]
                            if ewords:
                                for wi,w in enumerate(ewords):
                                    start=max(0,w["start"]); end=ewords[wi+1]["start"] if wi+1<len(ewords) else edur
                                    if end>start:
                                        tf.append((draw_explanation_scene(q['question'],q['options'][corr],exp_text,theme_q,channel_q,bg_q,active_word=wi,pulse=0.12,progress=(idx+1)/total,q_num=idx+1,total=total,video_title=th_q),end-start))
                            if not tf: tf=[(draw_explanation_scene(q['question'],q['options'][corr],exp_text,theme_q,channel_q,bg_q,active_word=-1,progress=(idx+1)/total,q_num=idx+1,total=total,video_title=th_q),edur)]
                            eo=os.path.join(tmp,f"explanation_{idx}.mp4"); make_segment(save_frames(tf,tmp,f"expframe_{idx}"),mixed,eo,tmp,0.92); clips.append(eo)

                            # Interlude motivation/abonnement de temps en temps, sans appel Gemini.
                            if idx < total-1 and ((idx+1) % 2 == 0):
                                mot=MOTIVATION_LINES[((idx+1)//2-1) % len(MOTIVATION_LINES)]
                                ma=os.path.join(tmp,f"mot_{idx}.mp3"); synthesize_audio(mot,voice_q,ma,tts_rate); md=audio_duration(ma)
                                mmusic=make_suspense_music(md,tmp,f"mmusic_{idx}",0.055)
                                mmix=os.path.join(tmp,f"mot_mix_{idx}.m4a"); mix_background_music(ma,mmusic,mmix,music_volume=0.055)
                                mf=save_frames([(draw_motivation_scene(mot,theme_q,channel_q,bg_q,(idx+1)/total,p),max(0.04,md/7)) for p in [0.05,0.18,0.35,0.55,0.75,0.92,1.0]],tmp,f"motframe_{idx}")
                                mo=os.path.join(tmp,f"motivation_{idx}.mp4"); make_segment(mf,mmix,mo,tmp,.95); clips.append(mo)

                        # CTA final animé.
                        oa=os.path.join(tmp,"outro.mp3"); synthesize_audio(outro_q,voice_q,oa,tts_rate); od=audio_duration(oa)
                        of=save_frames([(draw_hook(outro_q,theme_q,channel_q,bg_q,p),max(0.04,od/9)) for p in [0.05,0.18,0.35,0.55,0.75,0.92,1.0]],tmp,"outro")
                        oo=os.path.join(tmp,"outro.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)

                        final=os.path.join(tmp,"quizvideo_pro.mp4"); concat_videos(clips,final,tmp)
                        with open(final,"rb") as f: data=f.read()
                        st.success("✅ Short Quiz V5 terminé.")
                        st.video(data)
                        st.download_button("⬇️ Télécharger quizvideo_pro.mp4",data=data,file_name="quizvideo_pro.mp4",mime="video/mp4",key="dq4")
            except Exception as e:
                st.error(f"Erreur pendant le montage : {e}")

with tab2:
    st.markdown('<div class="qvp-hero"><div><div class="qvp-kicker">🗣️ SHORTS 9:16</div><h1>Vocabulaire Pro</h1><p>Apprenez et faites mémoriser un mot à la fois.</p></div><div class="qvp-hero-pill">✨ Apprenez • Répétez • Partagez</div></div>',unsafe_allow_html=True)
    hook_v=st.text_input("Hook","Tu prononces mal ces 5 mots !",key="hv")
    channel_v=st.text_input("Nom de la chaîne","@LingoPulse_Daily",key="cv")
    langue_v=st.selectbox("Langue cible",list(VOICES_MAP),key="lv")
    voice_tr_name=st.selectbox("Voix traduction",list(VOICES_MAP[langue_v]),key="vtr")
    voice_tr=VOICES_MAP[langue_v][voice_tr_name]
    theme_v=st.selectbox("🎨 Style visuel",list(THEMES),key="tv")
    st.markdown("### 🖼️ Fond de la vidéo")
    bg_mode_v=st.radio(
        "Choisir le fond",
        ["✨ Généré automatiquement selon le thème","🖼️ Image personnalisée","◯ Aucun"],
        horizontal=True,key="bg_mode_v"
    )
    uploaded_bg_v=None
    if bg_mode_v=="🖼️ Image personnalisée":
        uploaded_bg_v=st.file_uploader("Télécharger une image 9:16",type=["png","jpg","jpeg"],key="bgv")
    bg_mode_clean_v=("Généré automatiquement" if bg_mode_v.startswith("✨")
                     else "Image personnalisée" if bg_mode_v.startswith("🖼️")
                     else "Aucun")
    bg_v=selected_video_background(theme_v,th_v,bg_mode_clean_v,uploaded_bg_v)
    if bg_mode_clean_v=="Généré automatiquement":
        st.caption("✨ Fond visuel créé localement selon le thème — 0 quota Gemini.")
    elif bg_mode_clean_v=="Image personnalisée" and uploaded_bg_v:
        st.success("✅ Fond personnalisé prêt.")
    outro_v=st.text_input("CTA final","Abonne-toi pour apprendre un mot par jour !",key="ov")
    nb_v=st.slider("Nombre de mots",3,10,10,key="nbv")
    th_v=st.text_input("Sujet du vocabulaire","Voyage",key="thv")
    st.caption("💡 Changer le thème visuel, la voix, le fond ou le CTA ne consomme aucun quota. Une nouvelle requête est nécessaire uniquement pour un nouveau contenu IA.")
    vg_key=_vocab_generation_key(nb_v,th_v,langue_v)
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
                                    if end>w['start']:
                                        tf.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation",entrance=1.0),end-w['start']))
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
