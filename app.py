import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import tempfile
import math
import wave
import struct
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# QUIZVIDEO PRO — V3
# ============================================================
st.set_page_config(page_title="QuizVideo Pro", page_icon="🎬", layout="wide")
st.title("🎬 QuizVideo Pro")
st.caption("Créateur de Shorts 9:16 • Quiz dynamique + Vocabulaire")

WIDTH, HEIGHT, FPS = 1080, 1920, 30

THEMES = {
    "Bleu Nuit & Or": {"bg": (10, 17, 32), "card": (27, 38, 58), "accent": (250, 204, 21), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (160, 174, 194)},
    "Chocolat Noir & Or": {"bg": (27, 17, 11), "card": (56, 38, 27), "accent": (245, 158, 11), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (190, 166, 145)},
    "Violet Neon": {"bg": (21, 12, 34), "card": (48, 28, 72), "accent": (236, 72, 153), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (190, 165, 205)},
    "Emeraude Mint": {"bg": (5, 25, 18), "card": (14, 52, 37), "accent": (52, 211, 153), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (160, 195, 180)},
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
                return ImageFont.truetype(fn, size)
        except Exception:
            pass
    return ImageFont.load_default()

def clean_text(text):
    if text is None:
        return ""
    text = str(text)
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()

def text_width(draw, text, font):
    box = draw.textbbox((0, 0), str(text), font=font)
    return box[2] - box[0]

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
    bg = fit_background(bg_file)
    if bg is not None:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 105))
        return Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    return Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])

def rounded_text(draw, xy, text, font, fill, outline=None, width=2, radius=20, pad_x=28, pad_y=16):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=width if outline else 1)
    tw = text_width(draw, text, font)
    th = font.getbbox(text)[3] - font.getbbox(text)[1]
    draw.text(((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2 - 4), text, font=font, fill="white")

def add_top_glow(img, theme):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((150, -400, 930, 450), fill=(*theme["accent"], 28))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

# ------------------------- TTS ------------------------------
async def _tts(text, voice, path, rate="+15%"):
    comm = edge_tts.Communicate(clean_text(text), voice, rate=rate, boundary="WordBoundary")
    audio = bytearray()
    words = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            word = clean_text(chunk.get("text", ""))
            if word:
                start = chunk["offset"] / 10_000_000
                dur = chunk["duration"] / 10_000_000
                words.append({"text": word, "start": start, "end": start + dur})
    with open(path, "wb") as f:
        f.write(audio)
    return words

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
    return loop.run_until_complete(coro)

def synthesize_audio(text, voice, path, rate="+15%"):
    return run_async(_tts(text, voice, path, rate))

def audio_duration(path):
    res = subprocess.run([get_ffmpeg(), "-i", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if not m:
        return 1.5
    h, mi, sec = m.groups()
    return float(h) * 3600 + float(mi) * 60 + float(sec)

# ------------------------- SFX ------------------------------
def make_sfx(tmpdir):
    tic = os.path.join(tmpdir, "tic.wav")
    ding = os.path.join(tmpdir, "ding.wav")
    with wave.open(tic, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(int(44100 * .10)):
            v = int(13000 * math.sin(2 * math.pi * 1100 * i / 44100) * math.exp(-i / 800))
            f.writeframes(struct.pack("<h", v))
    with wave.open(ding, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(int(44100 * .45)):
            v = int(11500 * (math.sin(2 * math.pi * 1318 * i / 44100) + math.sin(2 * math.pi * 1568 * i / 44100)) * math.exp(-i / 4500))
            f.writeframes(struct.pack("<h", max(-32767, min(32767, v))))
    return tic, ding

def make_sfx_countdown(tic, tmpdir):
    out = os.path.join(tmpdir, "countdown.wav")
    cmd = [get_ffmpeg(), "-y", "-i", tic, "-filter_complex", "[0:a]adelay=0|0[a0];[0:a]adelay=1000|1000[a1];[0:a]adelay=2000|2000[a2];[a0][a1][a2]amix=inputs=3:duration=longest", "-t", "3.0", out]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return out

# ---------------------- Video encoding ----------------------
def make_image_video(frames, output, fps=30):
    """frames = [(png_path, duration_seconds), ...]"""
    list_path = output + ".txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for path, duration in frames:
            f.write(f"file '{path.replace(chr(92), '/')}'\n")
            f.write(f"duration {max(0.04, float(duration))}\n")
        if frames:
            f.write(f"file '{frames[-1][0].replace(chr(92), '/')}'\n")
    cmd = [get_ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-vf", f"fps={fps},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", output]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output

def mux_audio(video, audio, output, volume=1.0):
    cmd = [get_ffmpeg(), "-y", "-i", video, "-i", audio, "-filter:a", f"volume={volume}", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", output]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output

def make_segment(frames, audio, output, tmpdir, volume=1.0):
    raw = os.path.join(tmpdir, os.path.basename(output) + ".raw.mp4")
    make_image_video(frames, raw, FPS)
    return mux_audio(raw, audio, output, volume)

def concat_videos(clips, output, tmpdir):
    lst = os.path.join(tmpdir, "concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in clips:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")
    cmd = [get_ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", output]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output

# ----------------------- Visuals -----------------------------
def draw_brand(draw, theme, channel, progress=None):
    if channel:
        f = get_font(30)
        tag = clean_text(channel)
        draw.text((55, 1800), tag, font=f, fill=theme["muted"])
    if progress is not None:
        x, y, w, h = 55, 1745, 970, 10
        draw.rounded_rectangle((x, y, x+w, y+h), radius=5, fill=(70, 75, 90))
        draw.rounded_rectangle((x, y, x+int(w*max(0,min(1,progress))), y+h), radius=5, fill=theme["accent"])

def draw_header(draw, theme, q_num, total):
    f = get_font(34)
    txt = f"QUESTION {q_num} / {total}"
    rounded_text(draw, (55, 70, 350, 132), txt, f, theme["card"], theme["accent"], 2, 26)

def draw_quiz_frame(question, options, theme_name, q_num, total, channel, bg_file=None, timer=None, correct_idx=None, anim=1.0):
    theme = THEMES[theme_name]
    img = add_top_glow(make_base(theme_name, bg_file), theme)
    draw = ImageDraw.Draw(img)
    draw_header(draw, theme, q_num, total)

    f_q = get_font(58)
    f_opt = get_font(40)
    q_lines = wrap_text(question, f_q, 900)
    q_y = 210
    for line in q_lines[:3]:
        tw = text_width(draw, line, f_q)
        draw.text(((WIDTH-tw)/2, q_y), line, font=f_q, fill="white")
        q_y += 78

    # Réponses toujours visibles ensemble.
    left, right = 55, 850
    card_h, gap = 128, 18
    start_y = max(535, q_y + 30)
    slide = int((1.0 - anim) * 70)
    for i, opt in enumerate(options[:4]):
        y = start_y + i*(card_h+gap) + slide
        correct = correct_idx is not None and i == correct_idx
        fill = theme["success"] if correct else theme["card"]
        outline = (255,255,255) if correct else theme["accent"]
        draw.rounded_rectangle((left,y,right,y+card_h), radius=28, fill=fill, outline=outline, width=4)
        label = f"{chr(65+i)}  {clean_text(opt)}"
        lines = wrap_text(label, f_opt, right-left-55)
        ty = y + 34 - (len(lines)-1)*18
        for line in lines[:2]:
            draw.text((92,ty), line, font=f_opt, fill="white")
            ty += 45
        if correct:
            draw.ellipse((right-82,y+23,right-30,y+75), fill="white")
            draw.text((right-72,y+28), "✓", font=get_font(34), fill=theme["success"])

    # Timer à droite, jamais avant l'écran question.
    if timer is not None:
        color = theme["accent"] if timer == 3 else ((249,115,22) if timer == 2 else theme["danger"])
        cx, cy, r = 935, start_y + 260, 70
        draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=theme["bg"], outline=color, width=8)
        tf = get_font(58)
        ts = str(timer)
        draw.text((cx-text_width(draw,ts,tf)/2,cy-39), ts, font=tf, fill=color)
        draw.text((cx-text_width(draw,"SEC",get_font(24))/2,cy+38), "SEC", font=get_font(24), fill=color)

    if correct_idx is not None:
        banner_y = 1415
        draw.rounded_rectangle((235,banner_y,845,banner_y+90), radius=35, fill=theme["success"])
        txt = "✓ BONNE RÉPONSE"
        f = get_font(38)
        draw.text(((WIDTH-text_width(draw,txt,f))/2,banner_y+24), txt, font=f, fill="white")

    draw_brand(draw, theme, channel, (q_num-1)/max(1,total))
    return img

def draw_text_scene(text, theme_name, channel, bg_file=None, title=None, active_word=-1, accent=None, pulse=1.0):
    theme = THEMES[theme_name]
    img = add_top_glow(make_base(theme_name, bg_file), theme)
    draw = ImageDraw.Draw(img)
    if title:
        f_title = get_font(34)
        rounded_text(draw,(55,70,1025,135),clean_text(title),f_title,theme["card"],theme["accent"],2,28)
    words = clean_text(text).split()
    f = get_font(68)
    max_w = 900
    lines=[]; cur=[]
    for w in words:
        candidate = w if not cur else " ".join(cur+[w])
        if text_width(draw,candidate,f) <= max_w:
            cur.append(w)
        else:
            if cur: lines.append(cur)
            cur=[w]
    if cur: lines.append(cur)
    lines=lines[:4]
    y=650-(len(lines)*52)
    idx=0
    for line in lines:
        widths=[text_width(draw,w,f) for w in line]
        spaces=[text_width(draw," ",f)]*(len(line)-1)
        total=sum(widths)+sum(spaces)
        x=(WIDTH-total)/2
        for w,ww in zip(line,widths):
            is_active=idx==active_word
            col=accent or theme["accent"] if is_active else "white"
            scale=pulse if is_active else 1.0
            if is_active and scale>1.0:
                draw.rounded_rectangle((x-12,y-8,x+ww+12,y+78),radius=18,fill=theme["card"],outline=col,width=3)
            draw.text((x+4,y+5),w,font=f,fill=(0,0,0))
            draw.text((x,y),w,font=f,fill=col)
            x += ww + text_width(draw," ",f)
            idx += 1
        y += 105
    draw_brand(draw, theme, channel)
    return img

def draw_hook(text, theme_name, channel, bg_file=None, pulse=1.0):
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme)
    draw=ImageDraw.Draw(img)
    badge="🎯 TESTE-TOI"
    bf=get_font(34)
    rounded_text(draw,(300,260,780,330),badge,bf,theme["accent"],None,0,30)
    f=get_font(76)
    lines=wrap_text(text,f,850)
    y=700-(len(lines)*55)
    for line in lines:
        tw=text_width(draw,line,f)
        draw.text(((WIDTH-tw)/2+6,y+6),line,font=f,fill=(0,0,0))
        draw.text(((WIDTH-tw)/2,y),line,font=f,fill="white")
        y+=110
    draw_brand(draw,theme,channel)
    return img

def draw_vocab_frame(items, idx, langue, theme_name, channel, bg_file=None, phase="mot", timer=None):
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme)
    draw=ImageDraw.Draw(img)
    header=f"VOCABULAIRE • {idx+1}/{len(items)}"
    rounded_text(draw,(55,70,430,135),header,get_font(32),theme["card"],theme["accent"],2,26)
    item=items[idx]
    fr=clean_text(item.get("fr","")); tr=clean_text(item.get("trad",""))
    fsmall=get_font(34); fbig=get_font(88)
    draw.text(((WIDTH-text_width(draw,fr,fbig))/2,520),fr,font=fbig,fill=theme["accent"])
    if phase in ("translation","reveal"):
        lines=wrap_text(tr,get_font(58),850)
        y=760
        for line in lines:
            draw.text(((WIDTH-text_width(draw,line,get_font(58)))/2,y),line,font=get_font(58),fill="white")
            y+=75
    if phase=="countdown" and timer is not None:
        color=theme["accent"] if timer==3 else ((249,115,22) if timer==2 else theme["danger"])
        draw.ellipse((405,930,675,1200),fill=theme["bg"],outline=color,width=10)
        ts=str(timer); tf=get_font(110)
        draw.text(((WIDTH-text_width(draw,ts,tf))/2,960),ts,font=tf,fill=color)
    draw_brand(draw,theme,channel,idx/max(1,len(items)))
    return img

# ---------------------- Timeline builders -------------------
def frames_for_audio(audio_path, words, frame_fn, duration=None):
    dur = duration or audio_duration(audio_path)
    frames=[]
    # keyframe every spoken word; the active word remains highlighted until the next.
    if not words:
        return [(frame_fn(-1,1.0), dur)]
    boundaries=[max(0.0,w["start"]) for w in words]
    if boundaries[0] > 0.08:
        frames.append((frame_fn(-1,1.0), min(boundaries[0],dur)))
    for i,start in enumerate(boundaries):
        end=boundaries[i+1] if i+1<len(boundaries) else dur
        if end <= start: continue
        frames.append((frame_fn(i,1.08), end-start))
    return frames

def save_frames(frames, tmpdir, prefix):
    out=[]
    for i,(img,dur) in enumerate(frames):
        p=os.path.join(tmpdir,f"{prefix}_{i:04d}.png")
        img.save(p)
        out.append((p,dur))
    return out

# ------------------------ Gemini ----------------------------
def parse_json(text):
    text=text.strip().replace("```json","").replace("```","").strip()
    m=re.search(r"\[.*\]",text,re.DOTALL)
    if not m: raise ValueError("Gemini n'a pas renvoyé un JSON valide.")
    return json.loads(m.group(0))

def normalize_questions(data):
    out=[]
    for q in data:
        opts=q.get("options",[])
        if not isinstance(opts,list) or len(opts)!=4: continue
        ans=str(q.get("reponse_correcte","A")).strip().upper()
        if ans and ans[0] in "ABCD": ans=ans[0]
        else: ans="A"
        out.append({"question":clean_text(q.get("question","")),"options":[clean_text(x) for x in opts],"reponse_correcte":ans,"explication":clean_text(q.get("explication",""))})
    return out

api_key=st.sidebar.text_input("Clé API Gemini",type="password")
if api_key:
    genai.configure(api_key=api_key)
voice_rate=st.sidebar.slider("⚡ Vitesse voix",0,30,15)
tts_rate=f"+{voice_rate}%"

MODEL_NAME="gemini-3.6-flash"

# ============================================================
# INTERFACE
# ============================================================
tab1,tab2=st.tabs(["🧠 Quizz TikTok Pro","🗣️ Vocabulaire Pro"])

with tab1:
    st.header("🧠 Quizz TikTok Pro")
    hook_q=st.text_input("Hook", "IMPOSSIBLE d'avoir 5 sur 5 !", key="hq")
    channel_q=st.text_input("Nom de la chaîne", "@QuizMaster_Pro", key="cq")
    c1,c2=st.columns(2)
    with c1:
        voice_q=VOICES_FR[st.selectbox("Voix",list(VOICES_FR),key="vq")]
        theme_q=st.selectbox("Thème",list(THEMES),key="tq")
    with c2:
        nb_q=st.slider("Nombre de questions",1,5,5,key="nbq")
        th_q=st.text_input("Sujet", "Culture Générale", key="thq")
    outro_q=st.text_input("CTA final", "Quel est ton score ? Écris-le en commentaire !", key="oq")
    bg_q=st.file_uploader("🖼️ Fond 9:16 (optionnel)",type=["png","jpg","jpeg"],key="bgq")
    mode_q=st.radio("Création",["IA Gemini","Saisie manuelle"],horizontal=True,key="mq")

    if mode_q=="IA Gemini":
        if st.button("✨ Générer les questions",key="genq"):
            if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
            else:
                with st.spinner("Gemini prépare les questions..."):
                    try:
                        prompt=f'''Génère exactement {nb_q} questions de quiz sur {th_q}. Retourne UNIQUEMENT un JSON valide sous cette forme: [{{"question":"...","options":["...","...","...","..."],"reponse_correcte":"A","explication":"..."}}]. Les 4 options doivent être crédibles et une seule correcte.'''
                        res=genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
                        st.session_state.q_data=normalize_questions(parse_json(res.text))[:nb_q]
                        st.success(f"{len(st.session_state.q_data)} questions prêtes.")
                    except Exception as e: st.error(f"Erreur Gemini : {e}")
    else:
        q_list=[]
        for i in range(nb_q):
            st.markdown(f"**Question {i+1}**")
            qt=st.text_input("Question",key=f"qt_{i}")
            opts=[st.text_input(f"Option {chr(65+j)}",key=f"o_{i}_{j}") for j in range(4)]
            rep=st.selectbox("Bonne réponse",list("ABCD"),key=f"rep_{i}")
            exp=st.text_input("Explication",key=f"exp_{i}")
            q_list.append({"question":qt,"options":opts,"reponse_correcte":rep,"explication":exp})
        if st.button("💾 Valider les questions",key="saveq"): st.session_state.q_data=normalize_questions(q_list)

    if st.session_state.get("q_data"):
        st.info(f"{len(st.session_state.q_data)} questions chargées. Le rendu V3 ajoute hook, animations, timer 3→2→1, révélation et texte synchronisé.")
        if st.button("🎬 Générer la vidéo Quiz V3",key="makeq"):
            try:
                with st.spinner("Création du Short dynamique..."):
                    with tempfile.TemporaryDirectory() as tmp:
                        tic,ding=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,tmp)
                        clips=[]; total=len(st.session_state.q_data)

                        # Hook dynamique
                        ha=os.path.join(tmp,"hook.mp3"); words=synthesize_audio(hook_q,voice_q,ha,tts_rate)
                        hframes=[]
                        hframes.append((draw_hook(hook_q,theme_q,channel_q,bg_q),0.18))
                        hframes.append((draw_hook(hook_q,theme_q,channel_q,bg_q,pulse=1.05),max(0.18,audio_duration(ha)-0.18)))
                        hf=save_frames(hframes,tmp,"hook")
                        hout=os.path.join(tmp,"hook.mp4"); make_segment(hf,ha,hout,tmp,1.0); clips.append(hout)

                        for idx,q in enumerate(st.session_state.q_data):
                            # Question: animation d'entrée, puis question + réponses fixes. Pas de timer ici.
                            qa=os.path.join(tmp,f"q_{idx}.mp3")
                            synthesize_audio(f"Question {idx+1}. {q['question']}",voice_q,qa,tts_rate)
                            qdur=audio_duration(qa)
                            qframes=save_frames([
                                (draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,anim=.0),0.12),
                                (draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,anim=.55),0.12),
                                (draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,anim=1.0),max(0.15,qdur-0.24)),
                            ],tmp,f"qf_{idx}")
                            qo=os.path.join(tmp,f"question_{idx}.mp4"); make_segment(qframes,qa,qo,tmp); clips.append(qo)

                            # Countdown: 3 -> 2 -> 1, timer visible beside answers.
                            countdown_frames=[]
                            for sec in (3,2,1):
                                countdown_frames.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,timer=sec),1.0))
                            cf=save_frames(countdown_frames,tmp,f"timer_{idx}")
                            co=os.path.join(tmp,f"countdown_{idx}.mp4"); make_segment(cf,countdown_sfx,co,tmp,0.8); clips.append(co)

                            # Reveal + explication synchronisée mot par mot.
                            corr="ABCD".index(q['reponse_correcte'])
                            exp_text=f"La bonne réponse est {q['reponse_correcte']}. {q['options'][corr]}. {q.get('explication','') or 'Bravo !'}"
                            ea=os.path.join(tmp,f"exp_{idx}.mp3"); ewords=synthesize_audio(exp_text,voice_q,ea,tts_rate)
                            edur=audio_duration(ea)
                            reveal0=draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,correct_idx=corr,anim=1.0)
                            # petit flash/zoom visuel avant la parole.
                            reveal_frames=save_frames([(reveal0,.10),(draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,correct_idx=corr,anim=1.05),max(.2,edur-.10))],tmp,f"reveal_{idx}")
                            # Remplace ensuite par frames mot par mot au-dessus de la même carte.
                            text_frames=[]
                            if ewords:
                                bounds=[max(0,w['start']) for w in ewords]
                                for wi,start in enumerate(bounds):
                                    end=bounds[wi+1] if wi+1<len(bounds) else edur
                                    if end>start:
                                        text_frames.append((draw_text_scene(exp_text,theme_q,channel_q,bg_q,title=f"✓ {q['options'][corr]}",active_word=wi,pulse=1.06),end-start))
                            if not text_frames: text_frames=[(reveal0,edur)]
                            # Force green reveal card visible for the first 0.35 sec, then synced explanation.
                            rf=save_frames([(reveal0,min(.35,edur))]+text_frames,tmp,f"expframe_{idx}")
                            eo=os.path.join(tmp,f"explanation_{idx}.mp4"); make_segment(rf,ea,eo,tmp,1.0); clips.append(eo)

                        # CTA final
                        oa=os.path.join(tmp,"outro.mp3"); synthesize_audio(outro_q,voice_q,oa,tts_rate)
                        od=audio_duration(oa)
                        of=save_frames([(draw_hook(outro_q,theme_q,channel_q,bg_q),.15),(draw_hook(outro_q,theme_q,channel_q,bg_q,pulse=1.05),max(.2,od-.15))],tmp,"outro")
                        oo=os.path.join(tmp,"outro.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)

                        final=os.path.join(tmp,"quizvideo_pro.mp4"); concat_videos(clips,final,tmp)
                        with open(final,"rb") as f: data=f.read()
                        st.success("✅ Short Quiz V3 terminé.")
                        st.video(data)
                        st.download_button("⬇️ Télécharger quizvideo_pro.mp4",data=data,file_name="quizvideo_pro.mp4",mime="video/mp4",key="dq3")
            except Exception as e:
                st.error(f"Erreur pendant le montage : {e}")

with tab2:
    st.header("🗣️ Vocabulaire Pro")
    hook_v=st.text_input("Hook", "Tu prononces mal ces 5 mots !",key="hv")
    channel_v=st.text_input("Nom de la chaîne", "@LingoPulse_Daily",key="cv")
    langue_v=st.selectbox("Langue cible",list(VOICES_MAP),key="lv")
    voice_tr_name=st.selectbox("Voix traduction",list(VOICES_MAP[langue_v]),key="vtr")
    voice_tr=VOICES_MAP[langue_v][voice_tr_name]
    theme_v=st.selectbox("Thème",list(THEMES),key="tv")
    bg_v=st.file_uploader("🖼️ Fond 9:16 (optionnel)",type=["png","jpg","jpeg"],key="bgv")
    outro_v=st.text_input("CTA final","Abonne-toi pour apprendre un mot par jour !",key="ov")
    nb_v=st.slider("Nombre de mots",3,5,5,key="nbv")
    th_v=st.text_input("Thème du vocabulaire","Voyage",key="thv")
    if st.button("✨ Générer le vocabulaire par IA",key="genv"):
        if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
        else:
            try:
                prompt=f'''Génère exactement {nb_v} mots français avec leur traduction en {langue_v} sur le thème {th_v}. Retourne UNIQUEMENT un JSON valide: [{{"fr":"...","trad":"..."}}]'''
                res=genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
                st.session_state.v_data=parse_json(res.text)[:nb_v]
                st.success("Vocabulaire prêt.")
            except Exception as e: st.error(f"Erreur Gemini : {e}")
    if st.session_state.get("v_data"):
        if st.button("🎬 Générer la vidéo Vocabulaire V3",key="makev"):
            try:
                with st.spinner("Création du Short vocabulaire..."):
                    with tempfile.TemporaryDirectory() as tmp:
                        tic,ding=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,tmp)
                        clips=[]; items=st.session_state.v_data
                        ha=os.path.join(tmp,"vh.mp3"); synthesize_audio(hook_v,VOICES_FR["Henri - Dynamique"],ha,tts_rate)
                        hf=save_frames([(draw_hook(hook_v,theme_v,channel_v,bg_v),.15),(draw_hook(hook_v,theme_v,channel_v,bg_v,pulse=1.05),max(.2,audio_duration(ha)-.15))],tmp,"vh")
                        ho=os.path.join(tmp,"vh.mp4"); make_segment(hf,ha,ho,tmp); clips.append(ho)
                        for idx,item in enumerate(items):
                            fa=os.path.join(tmp,f"fr_{idx}.mp3"); synthesize_audio(item['fr'],VOICES_FR["Henri - Dynamique"],fa,tts_rate)
                            ff=save_frames([(draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"mot"),audio_duration(fa))],tmp,f"vf_{idx}")
                            fo=os.path.join(tmp,f"fr_{idx}.mp4"); make_segment(ff,fa,fo,tmp); clips.append(fo)
                            cframes=save_frames([(draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"countdown",sec),1.0) for sec in (3,2,1)],tmp,f"vc_{idx}")
                            co=os.path.join(tmp,f"count_{idx}.mp4"); make_segment(cframes,countdown_sfx,co,tmp,.8); clips.append(co)
                            ta=os.path.join(tmp,f"tr_{idx}.mp3"); tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate); td=audio_duration(ta)
                            tf=[]
                            if tw:
                                for wi,w in enumerate(tw):
                                    end=tw[wi+1]['start'] if wi+1<len(tw) else td
                                    if end>w['start']: tf.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation"),end-w['start']))
                            if not tf: tf=[(draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation"),td)]
                            trf=save_frames(tf,tmp,f"trf_{idx}")
                            tro=os.path.join(tmp,f"tr_{idx}.mp4"); make_segment(trf,ta,tro,tmp); clips.append(tro)
                        oa=os.path.join(tmp,"vo.mp3"); synthesize_audio(outro_v,VOICES_FR["Henri - Dynamique"],oa,tts_rate)
                        of=save_frames([(draw_hook(outro_v,theme_v,channel_v,bg_v),audio_duration(oa))],tmp,"vo")
                        oo=os.path.join(tmp,"vo.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)
                        final=os.path.join(tmp,"vocabulaire_pro.mp4"); concat_videos(clips,final,tmp)
                        with open(final,"rb") as f: data=f.read()
                        st.success("✅ Short Vocabulaire V3 terminé.")
                        st.video(data)
                        st.download_button("⬇️ Télécharger vocabulaire_pro.mp4",data=data,file_name="vocabulaire_pro.mp4",mime="video/mp4",key="dv3")
            except Exception as e: st.error(f"Erreur pendant le montage : {e}")
