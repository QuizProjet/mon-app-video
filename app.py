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

st.set_page_config(page_title="Studio TikTok & Shorts Pro", layout="wide")
st.title("🚀 Studio TikTok & Shorts Pro (.MP4)")

# --- CHARGEMENT ROBUSTE DE POLICE LARGE ---
def get_font(size):
    # Chemins des polices standards pré-installées sur les serveurs Linux (Streamlit Cloud)
    system_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for font_path in system_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
    # Secours si aucune n'est disponible
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()

# --- BRUITAGES SFX ---
def ensure_sfx_files(tmpdir):
    tictac_path = os.path.join(tmpdir, "tictac.wav")
    ding_path = os.path.join(tmpdir, "ding.wav")
    
    with wave.open(tictac_path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(6615):
            val = int(14000 * math.sin(2 * math.pi * 1000 * (i/44100)) * math.exp(-i/500))
            f.writeframes(struct.pack('<h', val))
            
    with wave.open(ding_path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(17640):
            val = int(16000 * (math.sin(2 * math.pi * 1318.5 * (i/44100)) + math.sin(2 * math.pi * 1567.98 * (i/44100))) * math.exp(-i/3000))
            f.writeframes(struct.pack('<h', val))
            
    return tictac_path, ding_path

def get_audio_duration(audio_path):
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [ffmpeg_exe, "-i", audio_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if match:
            hours, minutes, seconds = match.groups()
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return 1.5
    except Exception:
        return 1.5

def create_clip_ffmpeg(img_path, audio_path, duration, output_path, volume=1.3):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y", "-loop", "1", "-i", img_path,
        "-i", audio_path,
        "-filter_complex", f"[1:a]volume={volume}[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p",
        "-t", str(duration), output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def concatenate_clips_ffmpeg(clip_paths, output_path, tmpdir):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    list_file = os.path.join(tmpdir, "files.txt")
    with open(list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p}'\n")
    cmd = [ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def remove_unsupported_emojis(text):
    emoji_map = {"🧠": "", "💡": "", "🔥": "", "⏱️": "", "⏳": "", "💬": "", "📌": "", "✨": ""}
    for em, replacement in emoji_map.items():
        text = text.replace(em, replacement)
    return text

def wrap_text(text, font, max_width):
    words = text.split()
    lines, current_line = [], []
    for word in words:
        test_line = ' '.join(current_line + [word])
        try:
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
        except AttributeError:
            w = font.getsize(test_line)[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        return asyncio.new_event_loop().run_until_complete(coro)
    return loop.run_until_complete(coro)

def clean_text_for_tts(text):
    text = re.sub(r'(\d+)/(\d+)', r'\1 sur \2', text)
    return re.sub(r'[^\w\s,.?!:\'\-]', '', text).strip()

def parse_json_response(text):
    match = re.search(r'\[.*\]|\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)

def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-3.6-flash' in m.name or 'gemini-3' in m.name:
                    return m.name
        return 'models/gemini-3.6-flash'
    except Exception:
        return 'models/gemini-3.6-flash'

THEMES = {
    "Bleu Nuit & Or (YouTube Shorts)": {"bg": (15, 23, 42), "card": (30, 41, 59), "accent": (250, 204, 21)},
    "Chocolat Noir & Or Chaud": {"bg": (28, 18, 12), "card": (54, 38, 28), "accent": (245, 158, 11)},
    "Violet Deep & Neon Pink": {"bg": (24, 15, 38), "card": (48, 30, 74), "accent": (236, 72, 153)},
    "Émeraude Deep & Mint": {"bg": (6, 28, 20), "card": (15, 52, 38), "accent": (52, 211, 153)}
}

def draw_hook_frame(hook_text, theme_name, channel_tag, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or (YouTube Shorts)"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(60)
    clean_hook = remove_unsupported_emojis(hook_text)
    lines = wrap_text(clean_hook, font_title, 850)
    
    total_height = len(lines) * 90
    y = (height - total_height) // 2
    for line in lines:
        try:
            qw = font_title.getbbox(line)[2] - font_title.getbbox(line)[0]
        except AttributeError:
            qw = font_title.getsize(line)[0]
        x = (width - qw) // 2
        draw.text((x + 4, y + 4), line, fill=(0, 0, 0), font=font_title)
        draw.text((x, y), line, fill=colors["accent"], font=font_title)
        y += 90
        
    f_tag = get_font(42)
    try:
        t_w = f_tag.getbbox(channel_tag)[2] - f_tag.getbbox(channel_tag)[0]
    except AttributeError:
        t_w = f_tag.getsize(channel_tag)[0]
    draw.text(((width - t_w)//2, 1800), channel_tag, fill=(200, 200, 200), font=f_tag)
    return img

def draw_quizz_progressive_frame(question, options, max_opt_visible, reponse_correcte, explication, q_num, total_q, channel_tag, phase="question", timer_sec=5, bg_file=None, theme_name="Bleu Nuit & Or (YouTube Shorts)"):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or (YouTube Shorts)"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_head = get_font(48)
    f_q = get_font(52)
    f_opt = get_font(44)
    
    # Header
    header_text = f"QUIZ CULTURE GENERALE {q_num} sur {total_q}"
    try:
        hw = f_head.getbbox(header_text)[2] - f_head.getbbox(header_text)[0]
    except AttributeError:
        hw = f_head.getsize(header_text)[0]
    hx = (width - hw) // 2
    draw.text((hx + 3, 113), header_text, fill=(0, 0, 0), font=f_head)
    draw.text((hx, 110), header_text, fill=colors["accent"], font=f_head)
    
    # Question Géante
    clean_q = remove_unsupported_emojis(question)
    q_lines = wrap_text(f"Q: {clean_q}", f_q, 900)
    y_q = 220
    for line in q_lines:
        try:
            qw = f_q.getbbox(line)[2] - f_q.getbbox(line)[0]
        except AttributeError:
            qw = f_q.getsize(line)[0]
        qx = (width - qw) // 2
        draw.text((qx + 3, y_q + 3), line, fill=(0, 0, 0), font=f_q)
        draw.text((qx, y_q), line, fill="white", font=f_q)
        y_q += 75
        
    # CALCUL EXACT DE L'INDEX CORRECT (A=0, B=1, C=2, D=3)
    rep_clean = str(reponse_correcte).strip().upper()
    correct_idx = -1
    if rep_clean.startswith('A') or rep_clean == 'OPTION A': correct_idx = 0
    elif rep_clean.startswith('B') or rep_clean == 'OPTION B': correct_idx = 1
    elif rep_clean.startswith('C') or rep_clean == 'OPTION C': correct_idx = 2
    elif rep_clean.startswith('D') or rep_clean == 'OPTION D': correct_idx = 3
    else:
        for idx_o, opt_val in enumerate(options):
            if opt_val.strip().lower() in rep_clean.lower():
                correct_idx = idx_o
                break

    y_opt = max(580, y_q + 30)
    for i, opt in enumerate(options):
        if i <= max_opt_visible or max_opt_visible == -1:
            is_correct = (phase == "reponse" and i == correct_idx)
            fill_col = (34, 197, 94) if is_correct else colors["card"]
            out_col = (250, 204, 21) if is_correct else (255, 255, 255)
            
            draw.rounded_rectangle([(70, y_opt), (1010, y_opt + 145)], radius=30, fill=fill_col, outline=out_col, width=4)
            clean_opt = remove_unsupported_emojis(opt)
            opt_lines = wrap_text(f"{chr(65+i)}) {clean_opt}", f_opt, 860)
            draw.text((110, y_opt + 45), opt_lines[0], fill="white", font=f_opt)
        y_opt += 175
        
    # CHRONO CENTRAL STYLE SHORTS
    if phase == "chrono":
        if timer_sec >= 4:
            timer_color = (34, 197, 94)
        elif timer_sec >= 2:
            timer_color = (245, 158, 11)
        else:
            timer_color = (239, 68, 68)

        draw.rounded_rectangle([(340, y_opt + 15), (740, y_opt + 125)], radius=50, fill=(15, 23, 42), outline=timer_color, width=5)
        f_timer = get_font(54)
        t_str = f"00:0{timer_sec}"
        try:
            tw = f_timer.getbbox(t_str)[2] - f_timer.getbbox(t_str)[0]
        except AttributeError:
            tw = f_timer.getsize(t_str)[0]
        draw.text(((width - tw)//2, y_opt + 40), t_str, fill=timer_color, font=f_timer)

    elif phase == "reponse":
        draw.rounded_rectangle([(70, y_opt + 15), (1010, y_opt + 215)], radius=25, fill=(15, 23, 42), outline=(34, 197, 94), width=4)
        clean_exp = remove_unsupported_emojis(explication)
        exp_lines = wrap_text(f"Explication : {clean_exp}", get_font(38), 880)
        y_exp = y_opt + 40
        for line in exp_lines[:3]:
            draw.text((100, y_exp), line, fill="white", font=get_font(38))
            y_exp += 52
            
    font_tag = get_font(42)
    try:
        t_w = font_tag.getbbox(channel_tag)[2] - font_tag.getbbox(channel_tag)[0]
    except AttributeError:
        t_w = font_tag.getsize(channel_tag)[0]
    draw.text(((width - t_w)//2, 1800), channel_tag, fill=(200, 200, 200), font=font_tag)
    return img

def draw_language_page_frame(mots, current_idx, phase_item, timer_sec, motiv_txt, langue, channel_tag, theme_name, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or (YouTube Shorts)"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_title, f_text, f_sub = get_font(50), get_font(42), get_font(36)
    
    title_text = f"VOCABULAIRE EN {langue.upper()}"
    try:
        tw = f_title.getbbox(title_text)[2] - f_title.getbbox(title_text)[0]
    except AttributeError:
        tw = f_title.getsize(title_text)[0]
    tx = (width - tw) // 2
    draw.text((tx + 4, 124), title_text, fill=(0, 0, 0), font=f_title)
    draw.text((tx, 120), title_text, fill=colors["accent"], font=f_title)
    
    y = 250
    for idx, item in enumerate(mots):
        clean_fr = remove_unsupported_emojis(item['fr'])
        clean_tr = remove_unsupported_emojis(item['trad'])
        if idx < current_idx:
            draw.rounded_rectangle([(70, y), (1010, y + 160)], radius=25, fill=colors["card"], outline=(255, 255, 255), width=2)
            draw.text((110, y + 30), f"FR: {clean_fr}", fill="white", font=f_text)
            draw.text((110, y + 90), f"TRAD: {clean_tr}", fill=(34, 197, 94), font=f_text)
        elif idx == current_idx:
            draw.rounded_rectangle([(70, y), (1010, y + 160)], radius=25, fill=colors["card"], outline=colors["accent"], width=4)
            draw.text((110, y + 30), f"FR: {clean_fr}", fill=colors["accent"], font=f_text)
            
            if phase_item in ["traduction", "motivation"]:
                draw.text((110, y + 90), f"TRAD: {clean_tr}", fill="white", font=f_text)
            elif phase_item == "chrono":
                draw.rounded_rectangle([(740, y + 40), (970, y + 120)], radius=25, fill=(15, 23, 42), outline=colors["accent"], width=2)
                draw.text((770, y + 55), f"00:0{timer_sec}", fill="white", font=f_sub)
        else:
            draw.rounded_rectangle([(70, y), (1010, y + 160)], radius=25, fill=(20, 24, 33), outline=(50, 55, 70), width=2)
            draw.text((110, y + 60), f"Mot #{idx+1}", fill=(100, 116, 139), font=f_sub)
        y += 190
        
    if phase_item == "motivation" and motiv_txt:
        clean_m = remove_unsupported_emojis(motiv_txt)
        draw.rounded_rectangle([(140, y + 20), (940, y + 150)], radius=25, fill=(34, 197, 94))
        try:
            mw = f_title.getbbox(clean_m)[2] - f_title.getbbox(clean_m)[0]
        except AttributeError:
            mw = f_title.getsize(clean_m)[0]
        mx = (width - mw) // 2
        draw.text((mx, y + 48), clean_m, fill="white", font=f_title)
        
    font_tag = get_font(42)
    try:
        t_w = font_tag.getbbox(channel_tag)[2] - font_tag.getbbox(channel_tag)[0]
    except AttributeError:
        t_w = font_tag.getsize(channel_tag)[0]
    draw.text(((width - t_w)//2, 1800), channel_tag, fill=(200, 200, 200), font=font_tag)
    return img

# --- INTERFACE STREAMLIT ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")
if api_key:
    genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["🧠 Quizz TikTok Pro", "🗣️ Vocabulaire Pro"])

VOICES_FR = {
    "Henri (Dynamique & Motivant)": "fr-FR-HenriNeural", 
    "Vivienne (Énergique)": "fr-FR-VivienneNeural",
    "Remy (Standard)": "fr-FR-RemyNeural"
}
VOICES_MAP = {
    "Anglais": {"Emma": "en-US-EmmaNeural", "Christopher": "en-US-ChristopherNeural"},
    "Espagnol": {"Alvaro": "es-ES-AlvaroNeural", "Elvira": "es-ES-ElviraNeural"},
    "Arabe": {"Hamed": "ar-SA-HamedNeural", "Salma": "ar-SA-SalmaNeural"},
    "Allemand": {"Killian": "de-DE-KillianNeural", "Klarissa": "de-DE-KlarissaNeural"},
    "Italien": {"Diego": "it-IT-DiegoNeural", "Elsa": "it-IT-ElsaNeural"}
}

# ==================== MODULE 1 : QUIZZ ====================
with tab1:
    st.header("1. Générateur Quizz Pro")
    hook_input = st.text_input("Accroche (Hook 3s)", "IMPOSSIBLE d'avoir 5 sur 5 sur ce test !")
    channel_q_tag = st.text_input("Signature / Nom de Chaîne Quizz", "@QuizMaster_Pro", key="tag_q")
    
    col1, col2 = st.columns(2)
    with col1:
        voice_fr_code = VOICES_FR[st.selectbox("Voix Off Motivante", list(VOICES_FR.keys()))]
    with col2:
        theme_visual_q = st.selectbox("Palette de Couleurs", list(THEMES.keys()), key="th_q")
        
    motiv_q_custom = st.text_input("Phrases de motivation (séparées par une virgule)", "Bravo !, Excellent !, Tu gères !", key="mq")
    motiv_q_list = [m.strip() for m in motiv_q_custom.split(",") if m.strip()]
    outro_q_custom = st.text_input("Phrase d'Outro / CTA Final", "Quel est ton score ? Écris-le en commentaire !", key="oq")
    
    mode_q = st.radio("Mode", ["IA Gemini", "Saisie Manuelle"], key="mode_q")
    bg_file_q = st.file_uploader("Fond 9:16 (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_q")
    
    if mode_q == "IA Gemini":
        theme_q = st.text_input("Thème", "Culture Générale", key="t_q")
        nb_q = st.slider("Questions", 1, 10, 5)
        if st.button("✨ Générer les questions"):
            if not api_key:
                st.error("Clé API requise !")
            else:
                with st.spinner("Génération IA..."):
                    try:
                        prompt = f"Génère {nb_q} questions de quizz sur '{theme_q}'. JSON strict: [{{'question': '...', 'options': ['A','B','C','D'], 'reponse_correcte': 'A', 'explication': '...'}}]"
                        res = genai.GenerativeModel(get_working_model()).generate_content(prompt)
                        st.session_state['q_data'] = parse_json_response(res.text)
                        st.success(f"{len(st.session_state['q_data'])} questions générées !")
                    except Exception as e:
                        st.error(f"Erreur IA : {e}")
    else:
        num_c = st.number_input("Nombre de questions", 1, 10, 5)
        c_list = []
        for i in range(int(num_c)):
            st.markdown(f"**Question {i+1}**")
            q_t = st.text_input(f"Question {i+1}", key=f"q_{i}")
            o_a = st.text_input(f"Option A", key=f"oa_{i}")
            o_b = st.text_input(f"Option B", key=f"ob_{i}")
            o_c = st.text_input(f"Option C", key=f"oc_{i}")
            o_d = st.text_input(f"Option D", key=f"od_{i}")
            rep = st.selectbox("Bonne réponse", ["A", "B", "C", "D"], key=f"r_{i}")
            exp = st.text_input("Explication", key=f"e_{i}")
            c_list.append({"question": q_t, "options": [o_a, o_b, o_c, o_d], "reponse_correcte": rep, "explication": exp})
        if st.button("💾 Valider les questions"):
            st.session_state['q_data'] = c_list
            st.success("Questions enregistrées !")

    if 'q_data' in st.session_state and st.session_state['q_data']:
        if st.button("🎬 Générer la vidéo Quizz MP4"):
            with st.spinner("Montage de la vidéo style YouTube Shorts..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tictac_sfx, ding_sfx = ensure_sfx_files(tmpdir)
                        clip_files = []
                        total_q = len(st.session_state['q_data'])
                        clip_counter = 0
                        
                        # Hook
                        h_aud = os.path.join(tmpdir, "h.mp3")
                        h_img = os.path.join(tmpdir, "h.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_input), voice_fr_code).save(h_aud))
                        draw_hook_frame(hook_input, theme_visual_q, channel_q_tag, bg_file_q).save(h_img)
                        h_dur = get_audio_duration(h_aud)
                        h_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(h_img, h_aud, h_dur, h_clip, volume=1.3)
                        clip_files.append(h_clip)
                        clip_counter += 1
                        
                        for idx, q in enumerate(st.session_state['q_data']):
                            q_speech_txt = clean_text_for_tts(f"Question {idx+1}. {q['question']}")
                            q_speech_aud = os.path.join(tmpdir, f"q_{idx}_speech.mp3")
                            q_speech_img = os.path.join(tmpdir, f"q_{idx}_speech.png")
                            
                            run_async(edge_tts.Communicate(q_speech_txt, voice_fr_code).save(q_speech_aud))
                            draw_quizz_progressive_frame(q['question'], q['options'], -1, q['reponse_correcte'], q['explication'], idx+1, total_q, channel_q_tag, "question", 5, bg_file_q, theme_visual_q).save(q_speech_img)
                            dur = get_audio_duration(q_speech_aud)
                            out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(q_speech_img, q_speech_aud, dur, out_clip, volume=1.3)
                            clip_files.append(out_clip)
                            clip_counter += 1
                            
                            for opt_idx in range(4):
                                opt_txt = clean_text_for_tts(f"Option {chr(65+opt_idx)}. {q['options'][opt_idx]}")
                                opt_aud = os.path.join(tmpdir, f"q_{idx}_opt_{opt_idx}.mp3")
                                opt_img = os.path.join(tmpdir, f"q_{idx}_opt_{opt_idx}.png")
                                
                                run_async(edge_tts.Communicate(opt_txt, voice_fr_code).save(opt_aud))
                                draw_quizz_progressive_frame(q['question'], q['options'], opt_idx, q['reponse_correcte'], q['explication'], idx+1, total_q, channel_q_tag, "question", 5, bg_file_q, theme_visual_q).save(opt_img)
                                dur = get_audio_duration(opt_aud)
                                out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                                create_clip_ffmpeg(opt_img, opt_aud, dur, out_clip, volume=1.3)
                                clip_files.append(out_clip)
                                clip_counter += 1
                                
                            for sec in range(5, 0, -1):
                                t_img = os.path.join(tmpdir, f"t_{idx}_{sec}.png")
                                draw_quizz_progressive_frame(q['question'], q['options'], 3, q['reponse_correcte'], q['explication'], idx+1, total_q, channel_q_tag, "chrono", sec, bg_file_q, theme_visual_q).save(t_img)
                                out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                                create_clip_ffmpeg(t_img, tictac_sfx, 1.0, out_clip, volume=1.0)
                                clip_files.append(out_clip)
                                clip_counter += 1
                                
                            m_q_txt = motiv_q_list[idx % len(motiv_q_list)] if motiv_q_list else "Bravo !"
                            r_txt = clean_text_for_tts(f"La bonne réponse est l'option {q['reponse_correcte']}. {q['explication']}. {m_q_txt}")
                            r_aud = os.path.join(tmpdir, f"r_{idx}.mp3")
                            r_img = os.path.join(tmpdir, f"r_{idx}.png")
                            
                            run_async(edge_tts.Communicate(r_txt, voice_fr_code).save(r_aud))
                            draw_quizz_progressive_frame(q['question'], q['options'], 3, q['reponse_correcte'], q['explication'], idx+1, total_q, channel_q_tag, "reponse", 0, bg_file_q, theme_visual_q).save(r_img)
                            
                            ding_dur = get_audio_duration(ding_sfx)
                            out_clip_ding = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(r_img, ding_sfx, ding_dur, out_clip_ding, volume=1.0)
                            clip_files.append(out_clip_ding)
                            clip_counter += 1
                            
                            r_dur = get_audio_duration(r_aud)
                            out_clip_r = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(r_img, r_aud, r_dur, out_clip_r, volume=1.3)
                            clip_files.append(out_clip_r)
                            clip_counter += 1
                            
                        # Outro
                        c_aud = os.path.join(tmpdir, "c.mp3")
                        c_img = os.path.join(tmpdir, "c.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(outro_q_custom), voice_fr_code).save(c_aud))
                        draw_hook_frame(outro_q_custom, theme_visual_q, channel_q_tag, bg_file_q).save(c_img)
                        c_dur = get_audio_duration(c_aud)
                        out_clip_c = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(c_img, c_aud, c_dur, out_clip_c, volume=1.3)
                        clip_files.append(out_clip_c)
                        
                        out_mp4 = os.path.join(tmpdir, "quizz_final.mp4")
                        concatenate_clips_ffmpeg(clip_files, out_mp4, tmpdir)
                        
                        st.success("✅ Vidéo Quizz générée avec succès !")
                        
                        with open(out_mp4, "rb") as f:
                            video_bytes = f.read()
                        st.video(video_bytes)
                        st.download_button("📥 Télécharger le MP4 Quizz", data=video_bytes, file_name="quizz_viral_pro.mp4", mime="video/mp4")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")

# ==================== MODULE 2 : LANGUES ====================
with tab2:
    st.header("2. Générateur Vocabulaire Pro")
    hook_l_input = st.text_input("Accroche (Hook)", "Tu prononces mal ces 5 mots ! Vérifions ensemble.", key="hl")
    channel_l_tag = st.text_input("Signature / Nom de Chaîne Vocabulaire", "@LingoPulse_Daily", key="tag_l")
    
    col1, col2 = st.columns(2)
    with col1:
        langue_c = st.selectbox("Langue cible", ["Anglais", "Espagnol", "Arabe", "Allemand", "Italien"], key="lc")
    with col2:
        voice_t_code = VOICES_MAP[langue_c][st.selectbox("Voix Traduction", list(VOICES_MAP[langue_c].keys()), key="vt")]
        
    theme_visual_l = st.selectbox("Palette de Couleurs", list(THEMES.keys()), key="th_l")
    bg_file_l = st.file_uploader("Fond 9:16 (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_l")
    
    motiv_custom = st.text_input("Mots de motivation (séparés par une virgule)", "Bravo !, Excellent !, Continue comme ça !, Super !", key="ml")
    motiv_list = [m.strip() for m in motiv_custom.split(",") if m.strip()]
    outro_custom = st.text_input("Phrase d'Outro / CTA Final", "Enregistre cette vidéo et abonne-toi pour progresser !", key="ol")
    
    mode_l = st.radio("Mode Vocabulaire", ["IA Gemini", "Saisie Manuelle"], key="mode_l")
    
    if mode_l == "IA Gemini":
        theme_l = st.text_input("Thème", "Voyage", key="t_l")
        nb_m = st.slider("Nombre de mots", 3, 6, 5)
        if st.button("✨ Générer les mots par IA"):
            if not api_key:
                st.error("Clé API requise !")
            else:
                with st.spinner("Génération des mots..."):
                    try:
                        prompt = f"Génère {nb_m} mots avec traduction en {langue_c}. JSON strict: [{{'fr': 'Bonjour', 'trad': 'Hello'}}, ...]"
                        res = genai.GenerativeModel(get_working_model()).generate_content(prompt)
                        st.session_state['l_data'] = parse_json_response(res.text)
                        st.success(f"{len(st.session_state['l_data'])} mots générés !")
                    except Exception as e:
                        st.error(f"Erreur IA : {e}")
    else:
        num_m = st.number_input("Nombre de mots à saisir", 1, 6, 5)
        c_m = []
        for i in range(int(num_m)):
            ca, cb = st.columns(2)
            with ca:
                fr_t = st.text_input(f"Français #{i+1}", key=f"fr_{i}")
            with cb:
                tr_t = st.text_input(f"Traduction #{i+1}", key=f"tr_{i}")
            c_m.append({"fr": fr_t, "trad": tr_t})
        if st.button("💾 Valider les mots"):
            st.session_state['l_data'] = c_m
            st.success("Mots enregistrés !")

    if 'l_data' in st.session_state and st.session_state['l_data']:
        if st.button("🎬 Générer le MP4 Vocabulaire"):
            with st.spinner("Montage de la séquence..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tictac_sfx, ding_sfx = ensure_sfx_files(tmpdir)
                        clip_files = []
                        mots_l = st.session_state['l_data']
                        clip_counter = 0
                        
                        in_aud = os.path.join(tmpdir, "in.mp3")
                        in_img = os.path.join(tmpdir, "in.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_l_input), "fr-FR-HenriNeural").save(in_aud))
                        draw_hook_frame(hook_l_input, theme_visual_l, channel_l_tag, bg_file_l).save(in_img)
                        dur = get_audio_duration(in_aud)
                        out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(in_img, in_aud, dur, out_clip, volume=1.3)
                        clip_files.append(out_clip)
                        clip_counter += 1
                        
                        for idx, item in enumerate(mots_l):
                            t_fr = clean_text_for_tts(item['fr'])
                            t_tr = item['trad'].strip() if langue_c == "Arabe" else clean_text_for_tts(item['trad'])
                            m_txt = motiv_list[idx % len(motiv_list)] if motiv_list else "Bravo !"
                            
                            p_fr = os.path.join(tmpdir, f"fr_{idx}.mp3")
                            p_tr = os.path.join(tmpdir, f"tr_{idx}.mp3")
                            p_mo = os.path.join(tmpdir, f"mo_{idx}.mp3")
                            
                            run_async(edge_tts.Communicate(t_fr, "fr-FR-HenriNeural").save(p_fr))
                            run_async(edge_tts.Communicate(t_tr, voice_t_code).save(p_tr))
                            run_async(edge_tts.Communicate(m_txt, "fr-FR-HenriNeural").save(p_mo))
                            
                            img_s1 = os.path.join(tmpdir, f"s1_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "mot", 0, "", langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_s1)
                            dur = get_audio_duration(p_fr)
                            out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(img_s1, p_fr, dur, out_clip, volume=1.3)
                            clip_files.append(out_clip)
                            clip_counter += 1
                            
                            for sec in range(3, 0, -1):
                                img_sc = os.path.join(tmpdir, f"sc_{idx}_{sec}.png")
                                draw_language_page_frame(mots_l, idx, "chrono", sec, "", langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_sc)
                                out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                                create_clip_ffmpeg(img_sc, tictac_sfx, 1.0, out_clip, volume=1.0)
                                clip_files.append(out_clip)
                                clip_counter += 1
                                
                            img_s3 = os.path.join(tmpdir, f"s3_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "traduction", 0, "", langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_s3)
                            
                            ding_dur = get_audio_duration(ding_sfx)
                            out_clip_ding = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(img_s3, ding_sfx, ding_dur, out_clip_ding, volume=1.0)
                            clip_files.append(out_clip_ding)
                            clip_counter += 1
                            
                            tr_dur = get_audio_duration(p_tr)
                            out_clip_tr = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(img_s3, p_tr, tr_dur, out_clip_tr, volume=1.3)
                            clip_files.append(out_clip_tr)
                            clip_counter += 1
                            
                            img_s4 = os.path.join(tmpdir, f"s4_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "motivation", 0, m_txt, langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_s4)
                            mo_dur = get_audio_duration(p_mo)
                            out_clip_mo = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(img_s4, p_mo, mo_dur, out_clip_mo, volume=1.3)
                            clip_files.append(out_clip_mo)
                            clip_counter += 1
                            
                        out_aud = os.path.join(tmpdir, "out.mp3")
                        out_img = os.path.join(tmpdir, "out.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(outro_custom), "fr-FR-HenriNeural").save(out_aud))
                        draw_hook_frame(outro_custom, theme_visual_l, channel_l_tag, bg_file_l).save(out_img)
                        out_dur = get_audio_duration(out_aud)
                        out_clip_o = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(out_img, out_aud, out_dur, out_clip_o, volume=1.3)
                        clip_files.append(out_clip_o)
                        
                        out_mp4 = os.path.join(tmpdir, "vocabulaire_final.mp4")
                        concatenate_clips_ffmpeg(clip_files, out_mp4, tmpdir)
                        
                        st.success("✅ Vidéo Vocabulaire générée avec succès !")
                        
                        with open(out_mp4, "rb") as f:
                            video_bytes = f.read()
                        st.video(video_bytes)
                        st.download_button("📥 Télécharger le MP4 Vocabulaire", data=video_bytes, file_name="vocabulaire_viral_pro.mp4", mime="video/mp4")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")
