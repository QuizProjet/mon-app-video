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
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# CONFIGURATION ET PAGE STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Studio TikTok & Shorts Pro V2",
    page_icon="🎬",
    layout="wide"
)
st.title("🎬 Studio TikTok & Shorts Pro V2")
st.caption("Quiz + Vocabulaire • Synchro mot par mot • Format Shorts 9:16")

WIDTH = 1080
HEIGHT = 1920

THEMES = {
    "Bleu Nuit & Or": {
        "bg": (15, 23, 42), "card": (30, 41, 59), "accent": (250, 204, 21),
        "success": (34, 197, 94), "danger": (239, 68, 68), "white": (255, 255, 255)
    },
    "Chocolat Noir & Or": {
        "bg": (28, 18, 12), "card": (54, 38, 28), "accent": (245, 158, 11),
        "success": (34, 197, 94), "danger": (239, 68, 68), "white": (255, 255, 255)
    },
    "Violet Neon": {
        "bg": (24, 15, 38), "card": (48, 30, 74), "accent": (236, 72, 153),
        "success": (34, 197, 94), "danger": (239, 68, 68), "white": (255, 255, 255)
    },
    "Emeraude Mint": {
        "bg": (6, 28, 20), "card": (15, 52, 38), "accent": (52, 211, 153),
        "success": (34, 197, 94), "danger": (239, 68, 68), "white": (255, 255, 255)
    }
}

VOICES_FR = {
    "Henri - Dynamique": "fr-FR-HenriNeural",
    "Vivienne - Energique": "fr-FR-VivienneNeural",
    "Remy - Standard": "fr-FR-RemyNeural"
}

VOICES_MAP = {
    "Anglais": {"Emma": "en-US-EmmaNeural", "Christopher": "en-US-ChristopherNeural"},
    "Espagnol": {"Alvaro": "es-ES-AlvaroNeural", "Elvira": "es-ES-ElviraNeural"},
    "Arabe": {"Hamed": "ar-SA-HamedNeural", "Salma": "ar-SA-SalmaNeural"},
    "Allemand": {"Killian": "de-DE-KillianNeural", "Klarissa": "de-DE-KlarissaNeural"},
    "Italien": {"Diego": "it-IT-DiegoNeural", "Elsa": "it-IT-ElsaNeural"}
}

def get_ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()

def get_font(size):
    for fn in ["Roboto-Bold.ttf", "DejaVuSans-Bold.ttf"]:
        if os.path.exists(fn) and os.path.getsize(fn) > 100:
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                pass
    return ImageFont.load_default()

def clean_text(text):
    if not text:
        return ""
    text = str(text)
    for em in ["🧠", "💡", "🔥", "⏱️", "⏳", "💬", "📌", "✨", "🎯", "🇫🇷", "🇬🇧"]:
        text = text.replace(em, "")
    return re.sub(r"\s+", " ", text).strip()

def text_width(draw, text, font):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    except AttributeError:
        return font.getsize(text)[0]

def wrap_text(text, font, max_width):
    words = clean_text(text).split()
    lines, current = [], ""
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for w in words:
        test = w if not current else current + " " + w
        if text_width(dummy, test, font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def fit_background(uploaded_file):
    if not uploaded_file:
        return None
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file).convert("RGB")
        src_w, src_h = img.size
        target_ratio = WIDTH / HEIGHT
        src_ratio = src_w / src_h
        if src_ratio > target_ratio:
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

def make_base_image(theme_name, bg_file=None):
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or"])
    bg_img = fit_background(bg_file)
    if bg_img:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 85))
        return Image.alpha_composite(bg_img.convert("RGBA"), overlay).convert("RGB")
    return Image.new("RGB", (WIDTH, HEIGHT), colors["bg"])

# ============================================================
# TTS AVEC RECURRENCE MOT PAR MOT (WORDBOUNDARY)
# ============================================================
async def _tts_with_boundaries(text, voice, output_path, rate="+15%"):
    communicate = edge_tts.Communicate(clean_text(text), voice, rate=rate, boundary="WordBoundary")
    audio_data = bytearray()
    words = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            word = chunk.get("text", "").strip()
            if word:
                start = chunk["offset"] / 10_000_000
                duration = chunk["duration"] / 10_000_000
                words.append({"text": word, "start": start, "end": start + duration})
    with open(output_path, "wb") as f:
        f.write(audio_data)
    return words

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def synthesize_audio(text, voice, output_path, rate="+15%"):
    return run_async(_tts_with_boundaries(text, voice, output_path, rate))

def get_audio_duration(audio_path):
    try:
        cmd = [get_ffmpeg(), "-i", audio_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if match:
            h, m, s = match.groups()
            return float(h) * 3600 + float(m) * 60 + float(s)
        return 1.5
    except Exception:
        return 1.5

def ensure_sfx(tmpdir):
    tic = os.path.join(tmpdir, "tictac.wav")
    ding = os.path.join(tmpdir, "ding.wav")
    with wave.open(tic, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(5292):
            val = int(14000 * math.sin(2 * math.pi * 1000 * (i/44100)) * math.exp(-i/1000))
            f.writeframes(struct.pack('<h', val))
    with wave.open(ding, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(22050):
            val = int(15000 * (math.sin(2 * math.pi * 1318.5 * (i/44100)) + math.sin(2 * math.pi * 1568 * (i/44100))) * math.exp(-i/5000))
            f.writeframes(struct.pack('<h', val))
    return tic, ding

def create_clip_ffmpeg(img_path, audio_path, duration, output_path, volume=1.3):
    cmd = [
        get_ffmpeg(), "-y", "-loop", "1", "-i", img_path, "-i", audio_path,
        "-filter_complex", f"[1:a]volume={volume}[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p",
        "-t", str(duration), output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def concatenate_clips(clips, output_path, tmpdir):
    list_file = os.path.join(tmpdir, "files.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for p in clips:
            f.write(f"file '{p.replace('\\', '/')}'\n")
    cmd = [get_ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

# ============================================================
# DESSIN DYNAMIQUE DES FRAMES
# ============================================================
def draw_quiz_frame(question, options, visible_options, theme_name, q_num, total_q, channel_tag, bg_file=None, correct_idx=None, timer=None):
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or"])
    img = make_base_image(theme_name, bg_file)
    draw = ImageDraw.Draw(img)
    
    f_head, f_q, f_opt = get_font(42), get_font(52), get_font(40)
    
    header = f"QUIZ • {q_num}/{total_q}"
    draw.text(((WIDTH - text_width(draw, header, f_head)) // 2, 90), header, fill=colors["accent"], font=f_head)
    
    q_lines = wrap_text(question, f_q, 880)
    y_q = 210
    for line in q_lines[:3]:
        draw.text(((WIDTH - text_width(draw, line, f_q)) // 2, y_q), line, fill="white", font=f_q)
        y_q += 75
        
    y_opt = max(550, y_q + 30)
    for i, opt in enumerate(options):
        if i >= visible_options:
            break
        is_correct = (correct_idx is not None and i == correct_idx)
        fill_col = colors["success"] if is_correct else colors["card"]
        out_col = (255, 255, 255) if is_correct else colors["accent"]
        
        draw.rounded_rectangle([(70, y_opt), (1010, y_opt + 135)], radius=25, fill=fill_col, outline=out_col, width=4)
        draw.text((110, y_opt + 40), f"{chr(65+i)}) {clean_text(opt)}", fill="white", font=f_opt)
        y_opt += 165
        
    if timer is not None:
        draw.rounded_rectangle([(400, y_opt + 10), (680, y_opt + 130)], radius=40, fill=colors["bg"], outline=colors["accent"], width=5)
        t_str = f"00:0{timer}"
        draw.text(((WIDTH - text_width(draw, t_str, get_font(52))) // 2, y_opt + 40), t_str, fill=colors["accent"], font=get_font(52))

    draw.text(((WIDTH - text_width(draw, channel_tag, get_font(36))) // 2, 1800), channel_tag, fill=(180, 180, 180), font=get_font(36))
    return img

def draw_vocab_frame(mots, current_idx, phase, langue, theme_name, channel_tag, bg_file=None, timer=None, motiv_txt=""):
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or"])
    img = make_base_image(theme_name, bg_file)
    draw = ImageDraw.Draw(img)
    
    f_head, f_text = get_font(44), get_font(40)
    header = f"VOCABULAIRE EN {langue.upper()}"
    draw.text(((WIDTH - text_width(draw, header, f_head)) // 2, 100), header, fill=colors["accent"], font=f_head)
    
    y = 250
    for idx, item in enumerate(mots):
        fr, tr = clean_text(item["fr"]), clean_text(item["trad"])
        if idx < current_idx:
            draw.rounded_rectangle([(70, y), (1010, y + 150)], radius=20, fill=colors["card"], outline=(255, 255, 255), width=2)
            draw.text((110, y + 25), f"FR: {fr}", fill="white", font=f_text)
            draw.text((110, y + 80), f"TRAD: {tr}", fill=colors["success"], font=f_text)
        elif idx == current_idx:
            draw.rounded_rectangle([(70, y), (1010, y + 150)], radius=20, fill=colors["card"], outline=colors["accent"], width=4)
            draw.text((110, y + 25), f"FR: {fr}", fill=colors["accent"], font=f_text)
            if phase in ["traduction", "motivation"]:
                draw.text((110, y + 80), f"TRAD: {tr}", fill="white", font=f_text)
            elif phase == "chrono":
                draw.text((800, y + 45), f"00:0{timer}", fill=colors["accent"], font=f_text)
        else:
            draw.rounded_rectangle([(70, y), (1010, y + 150)], radius=20, fill=(20, 24, 33), outline=(50, 55, 70), width=2)
            draw.text((110, y + 50), f"Mot #{idx+1}", fill=(100, 116, 139), font=get_font(36))
        y += 180
        
    if phase == "motivation" and motiv_txt:
        draw.rounded_rectangle([(140, y + 20), (940, y + 140)], radius=25, fill=colors["success"])
        draw.text(((WIDTH - text_width(draw, motiv_txt, f_head)) // 2, y + 50), motiv_txt, fill="white", font=f_head)

    draw.text(((WIDTH - text_width(draw, channel_tag, get_font(36))) // 2, 1800), channel_tag, fill=(180, 180, 180), font=get_font(36))
    return img

def draw_hook_frame(text, theme_name, channel_tag, bg_file=None):
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or"])
    img = make_base_image(theme_name, bg_file)
    draw = ImageDraw.Draw(img)
    f = get_font(60)
    lines = wrap_text(text, f, 850)
    y = (HEIGHT - (len(lines) * 90)) // 2
    for line in lines:
        draw.text(((WIDTH - text_width(draw, line, f)) // 2, y), line, fill=colors["accent"], font=f)
        y += 90
    draw.text(((WIDTH - text_width(draw, channel_tag, get_font(36))) // 2, 1800), channel_tag, fill=(180, 180, 180), font=get_font(36))
    return img

# ============================================================
# APPLICATION STREAMLIT ET MODEL GEMINI CORRIGE
# ============================================================
api_key = st.sidebar.text_input("Clé API Gemini", type="password")
if api_key:
    genai.configure(api_key=api_key)

voice_rate = st.sidebar.slider("⚡ Vitesse de la Voix Off", 0, 30, 15, help="15% = vitesse recommandée Shorts/TikTok")
tts_rate_str = f"+{voice_rate}%"

def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-flash' in m.name or 'gemini-2.0-flash' in m.name:
                    return m.name
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except Exception:
        pass
    return "models/gemini-1.5-flash"

def parse_json_response(text):
    match = re.search(r"\[.*\]|\{.*\}", text, re.DOTALL)
    return json.loads(match.group(0)) if match else json.loads(text)

tab1, tab2 = st.tabs(["🧠 Quizz TikTok Pro", "🗣️ Vocabulaire Pro"])

# --- MODULE 1 : QUIZZ ---
with tab1:
    st.header("1. Générateur Quizz Shorts Pro")
    hook_q = st.text_input("Accroche (Hook)", "IMPOSSIBLE d'avoir 5 sur 5 sur ce test !", key="hq")
    channel_q = st.text_input("Nom de la chaîne", "@QuizMaster_Pro", key="cq")
    col1, col2 = st.columns(2)
    with col1:
        voice_q = VOICES_FR[st.selectbox("Voix Off", list(VOICES_FR.keys()), key="vq")]
    with col2:
        theme_q = st.selectbox("Thème Visuel", list(THEMES.keys()), key="tq")
    outro_q = st.text_input("Outro / CTA", "Quel est ton score ? Écris-le en commentaire !", key="oq")
    mode_q = st.radio("Mode de création", ["IA Gemini", "Saisie Manuelle"], key="mq")
    bg_q = st.file_uploader("Fond 9:16 (Optionnel)", type=["png", "jpg"], key="bgq")

    if mode_q == "IA Gemini":
        th_q = st.text_input("Sujet du Quiz", "Culture Générale", key="thq")
        nb_q = st.slider("Nombre de questions", 1, 5, 5, key="nbq")
        if st.button("✨ Générer les questions par IA"):
            if not api_key:
                st.error("Clé API Gemini requise !")
            else:
                with st.spinner("Génération..."):
                    try:
                        prompt = f"Génère {nb_q} questions de quiz sur '{th_q}'. Format JSON strict: [{{'question':'...', 'options':['A','B','C','D'], 'reponse_correcte':'A', 'explication':'...'}}]"
                        model_name = get_working_model()
                        res = genai.GenerativeModel(model_name).generate_content(prompt)
                        st.session_state['q_data'] = parse_json_response(res.text)
                        st.success("Questions prêtes !")
                    except Exception as e:
                        st.error(f"Erreur Gemini : {e}")
    else:
        q_list = []
        for i in range(3):
            st.markdown(f"**Question {i+1}**")
            qt = st.text_input(f"Question {i+1}", key=f"qt_{i}")
            oa = st.text_input(f"Option A", key=f"oa_{i}"); ob = st.text_input(f"Option B", key=f"ob_{i}")
            oc = st.text_input(f"Option C", key=f"oc_{i}"); od = st.text_input(f"Option D", key=f"od_{i}")
            rep = st.selectbox(f"Bonne réponse {i+1}", ["A", "B", "C", "D"], key=f"rep_{i}")
            exp = st.text_input(f"Explication {i+1}", key=f"exp_{i}")
            q_list.append({"question": qt, "options": [oa, ob, oc, od], "reponse_correcte": rep, "explication": exp})
        if st.button("💾 Valider les questions"):
            st.session_state['q_data'] = q_list

    if 'q_data' in st.session_state and st.session_state['q_data']:
        if st.button("🎬 Générer le MP4 Quizz"):
            with st.spinner("Montage accéléré en cours..."):
                with tempfile.TemporaryDirectory() as tmpdir:
                    tic, ding = ensure_sfx(tmpdir)
                    clips = []
                    
                    # Hook
                    h_aud = os.path.join(tmpdir, "h.mp3"); h_img = os.path.join(tmpdir, "h.png")
                    synthesize_audio(hook_q, voice_q, h_aud, tts_rate_str)
                    draw_hook_frame(hook_q, theme_q, channel_q, bg_q).save(h_img)
                    c_out = os.path.join(tmpdir, "c_h.mp4")
                    create_clip_ffmpeg(h_img, h_aud, get_audio_duration(h_aud), c_out)
                    clips.append(c_out)
                    
                    # Loop Questions
                    for idx, q in enumerate(st.session_state['q_data']):
                        # Énoncé
                        q_aud = os.path.join(tmpdir, f"q_{idx}.mp3"); q_img = os.path.join(tmpdir, f"q_{idx}.png")
                        synthesize_audio(f"Question {idx+1}. {q['question']}", voice_q, q_aud, tts_rate_str)
                        draw_quiz_frame(q['question'], q['options'], 4, theme_q, idx+1, len(st.session_state['q_data']), channel_q, bg_q).save(q_img)
                        c_q = os.path.join(tmpdir, f"clip_q_{idx}.mp4")
                        create_clip_ffmpeg(q_img, q_aud, get_audio_duration(q_aud), c_q)
                        clips.append(c_q)
                        
                        # Chrono
                        for sec in range(3, 0, -1):
                            t_img = os.path.join(tmpdir, f"t_{idx}_{sec}.png")
                            draw_quiz_frame(q['question'], q['options'], 4, theme_q, idx+1, len(st.session_state['q_data']), channel_q, bg_q, timer=sec).save(t_img)
                            c_t = os.path.join(tmpdir, f"clip_t_{idx}_{sec}.mp4")
                            create_clip_ffmpeg(t_img, tic, 1.0, c_t, volume=1.0)
                            clips.append(c_t)
                            
                        # Réponse & Explication
                        corr_idx = "ABCD".index(q['reponse_correcte'][0].upper()) if q['reponse_correcte'][0].upper() in "ABCD" else 0
                        r_img = os.path.join(tmpdir, f"r_{idx}.png")
                        draw_quiz_frame(q['question'], q['options'], 4, theme_q, idx+1, len(st.session_state['q_data']), channel_q, bg_q, correct_idx=corr_idx).save(r_img)
                        c_ding = os.path.join(tmpdir, f"clip_d_{idx}.mp4")
                        create_clip_ffmpeg(r_img, ding, get_audio_duration(ding), c_ding, volume=1.0)
                        clips.append(c_ding)
                        
                        exp_aud = os.path.join(tmpdir, f"e_{idx}.mp3")
                        synthesize_audio(f"Réponse {q['reponse_correcte']}. {q['explication']}", voice_q, exp_aud, tts_rate_str)
                        c_exp = os.path.join(tmpdir, f"clip_e_{idx}.mp4")
                        create_clip_ffmpeg(r_img, exp_aud, get_audio_duration(exp_aud), c_exp)
                        clips.append(c_exp)
                        
                    # Outro
                    o_aud = os.path.join(tmpdir, "o.mp3"); o_img = os.path.join(tmpdir, "o.png")
                    synthesize_audio(outro_q, voice_q, o_aud, tts_rate_str)
                    draw_hook_frame(outro_q, theme_q, channel_q, bg_q).save(o_img)
                    c_o = os.path.join(tmpdir, "c_o.mp4")
                    create_clip_ffmpeg(o_img, o_aud, get_audio_duration(o_aud), c_o)
                    clips.append(c_o)
                    
                    final = os.path.join(tmpdir, "final_quiz.mp4")
                    concatenate_clips(clips, final, tmpdir)
                    st.success("✅ Vidéo Quiz V2 prête !")
                    with open(final, "rb") as f:
                        st.video(f.read())

# --- MODULE 2 : VOCABULAIRE ---
with tab2:
    st.header("2. Générateur Vocabulaire Pro")
    hook_v = st.text_input("Accroche", "Tu prononces mal ces 5 mots ! Vérifions ensemble.", key="hv")
    channel_v = st.text_input("Nom de la chaîne", "@LingoPulse_Daily", key="cv")
    col1, col2 = st.columns(2)
    with col1:
        langue_v = st.selectbox("Langue Cible", list(VOICES_MAP.keys()), key="lv")
    with col2:
        voice_tr_name = st.selectbox("Voix Traduction", list(VOICES_MAP[langue_v].keys()), key="vtr")
        voice_tr_code = VOICES_MAP[langue_v][voice_tr_name]
    theme_v = st.selectbox("Thème Visuel", list(THEMES.keys()), key="tv")
    bg_v = st.file_uploader("Fond 9:16 (Optionnel)", type=["png", "jpg"], key="bgv")
    outro_v = st.text_input("Outro / CTA", "Abonne-toi pour apprendre un mot par jour !", key="ov")
    mode_v = st.radio("Mode Vocabulaire", ["IA Gemini", "Saisie Manuelle"], key="mv")

    if mode_v == "IA Gemini":
        th_v = st.text_input("Thème du vocabulaire", "Voyage", key="thv")
        nb_v = st.slider("Nombre de mots", 3, 5, 5, key="nbv")
        if st.button("✨ Générer le vocabulaire par IA"):
            if not api_key:
                st.error("Clé API Gemini requise !")
            else:
                with st.spinner("Génération..."):
                    try:
                        prompt = f"Génère {nb_v} mots avec leur traduction en {langue_v}. Format JSON strict: [{{'fr':'Bonjour', 'trad':'Hello'}}]"
                        model_name = get_working_model()
                        res = genai.GenerativeModel(model_name).generate_content(prompt)
                        st.session_state['v_data'] = parse_json_response(res.text)
                        st.success("Mots prêts !")
                    except Exception as e:
                        st.error(f"Erreur Gemini : {e}")
    else:
        v_list = []
        for i in range(3):
            ca, cb = st.columns(2)
            with ca: fr_in = st.text_input(f"Français #{i+1}", key=f"frin_{i}")
            with cb: tr_in = st.text_input(f"Traduction #{i+1}", key=f"trin_{i}")
            v_list.append({"fr": fr_in, "trad": tr_in})
        if st.button("💾 Valider les mots"):
            st.session_state['v_data'] = v_list

    if 'v_data' in st.session_state and st.session_state['v_data']:
        if st.button("🎬 Générer le MP4 Vocabulaire"):
            with st.spinner("Montage du vocabulaire..."):
                with tempfile.TemporaryDirectory() as tmpdir:
                    tic, ding = ensure_sfx(tmpdir)
                    clips = []
                    
                    # Hook
                    h_aud = os.path.join(tmpdir, "vh.mp3"); h_img = os.path.join(tmpdir, "vh.png")
                    synthesize_audio(hook_v, VOICES_FR["Henri - Dynamique"], h_aud, tts_rate_str)
                    draw_hook_frame(hook_v, theme_v, channel_v, bg_v).save(h_img)
                    c_h = os.path.join(tmpdir, "vc_h.mp4")
                    create_clip_ffmpeg(h_img, h_aud, get_audio_duration(h_aud), c_h)
                    clips.append(c_h)
                    
                    # Loop Words
                    for idx, item in enumerate(st.session_state['v_data']):
                        # FR
                        fr_aud = os.path.join(tmpdir, f"vfr_{idx}.mp3"); fr_img = os.path.join(tmpdir, f"vfr_{idx}.png")
                        synthesize_audio(item['fr'], VOICES_FR["Henri - Dynamique"], fr_aud, tts_rate_str)
                        draw_vocab_frame(st.session_state['v_data'], idx, "mot", langue_v, theme_v, channel_v, bg_v).save(fr_img)
                        c_fr = os.path.join(tmpdir, f"vc_fr_{idx}.mp4")
                        create_clip_ffmpeg(fr_img, fr_aud, get_audio_duration(fr_aud), c_fr)
                        clips.append(c_fr)
                        
                        # Chrono
                        for sec in range(3, 0, -1):
                            t_img = os.path.join(tmpdir, f"vt_{idx}_{sec}.png")
                            draw_vocab_frame(st.session_state['v_data'], idx, "chrono", langue_v, theme_v, channel_v, bg_v, timer=sec).save(t_img)
                            c_t = os.path.join(tmpdir, f"vc_t_{idx}_{sec}.mp4")
                            create_clip_ffmpeg(t_img, tic, 1.0, c_t, volume=1.0)
                            clips.append(c_t)
                            
                        # Traduction
                        tr_aud = os.path.join(tmpdir, f"vtr_{idx}.mp3"); tr_img = os.path.join(tmpdir, f"vtr_{idx}.png")
                        synthesize_audio(item['trad'], voice_tr_code, tr_aud, tts_rate_str)
                        draw_vocab_frame(st.session_state['v_data'], idx, "traduction", langue_v, theme_v, channel_v, bg_v).save(tr_img)
                        c_tr = os.path.join(tmpdir, f"vc_tr_{idx}.mp4")
                        create_clip_ffmpeg(tr_img, tr_aud, get_audio_duration(tr_aud), c_tr)
                        clips.append(c_tr)
                        
                    # Outro
                    o_aud = os.path.join(tmpdir, "vo.mp3"); o_img = os.path.join(tmpdir, "vo.png")
                    synthesize_audio(outro_v, VOICES_FR["Henri - Dynamique"], o_aud, tts_rate_str)
                    draw_hook_frame(outro_v, theme_v, channel_v, bg_v).save(o_img)
                    c_o = os.path.join(tmpdir, "vc_o.mp4")
                    create_clip_ffmpeg(o_img, o_aud, get_audio_duration(o_aud), c_o)
                    clips.append(c_o)
                    
                    final = os.path.join(tmpdir, "final_vocab.mp4")
                    concatenate_clips(clips, final, tmpdir)
                    st.success("✅ Vidéo Vocabulaire V2 prête !")
                    with open(final, "rb") as f:
                        st.video(f.read())
