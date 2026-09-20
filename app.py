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

st.set_page_config(page_title="Studio TikTok Pro", layout="wide")
st.title("🚀 Studio TikTok & Shorts Pro (.MP4)")

# --- BRUITAGES SFX ---
def ensure_sfx_files(tmpdir):
    tictac_path = os.path.join(tmpdir, "tictac.wav")
    ding_path = os.path.join(tmpdir, "ding.wav")
    
    with wave.open(tictac_path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(4410):
            val = int(10000 * math.sin(2 * math.pi * 1000 * (i/44100)) * math.exp(-i/400))
            f.writeframes(struct.pack('<h', val))
            
    with wave.open(ding_path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(11025):
            val = int(12000 * (math.sin(2 * math.pi * 1318.5 * (i/44100)) + math.sin(2 * math.pi * 1567.98 * (i/44100))) * math.exp(-i/2500))
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

def create_clip_ffmpeg(img_path, audio_path, duration, output_path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y", "-loop", "1", "-i", img_path,
        "-i", audio_path, "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "96k", "-pix_fmt", "yuv420p",
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

# --- POLICES HD ET GRANDES TAILLES GARANTIES ---
def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()

def remove_unsupported_emojis(text):
    emoji_map = {"🧠": "", "💡": "", "🔥": "", "⏱️": "", "⏳": "", "💬": "", "📌": "", "✨": ""}
    for em, rep in emoji_map.items():
        text = text.replace(em, rep)
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
            if 'generateContent' in m.supported_generation_methods and ('gemini-3.6-flash' in m.name or 'gemini-3' in m.name):
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

# --- RENDU DE L'ACCROCHE (HOOK) ---
def draw_hook_frame(hook_text, theme_name, channel_tag, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or (YouTube Shorts)"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(64)
    clean_hook = remove_unsupported_emojis(hook_text)
    lines = wrap_text(clean_hook, font_title, 880)
    
    total_height = len(lines) * 85
    y = (height - total_height) // 2
    for line in lines:
        try:
            bbox = font_title.getbbox(line)
            w = bbox[2] - bbox[0]
        except AttributeError:
            w = font_title.getsize(line)[0]
        x = (width - w) // 2
        draw.text((x + 4, y + 4), line, fill=(0, 0, 0), font=font_title)
        draw.text((x, y), line, fill=colors["accent"], font=font_title)
        y += 85
        
    font_tag = get_font(40)
    try:
        t_w = font_tag.getbbox(channel_tag)[2] - font_tag.getbbox(channel_tag)[0]
    except AttributeError:
        t_w = font_tag.getsize(channel_tag)[0]
    draw.text(((width - t_w)//2, 1800), channel_tag, fill=(200, 200, 200), font=font_tag)
    return img

# --- RENDU DU QUIZZ GRAND ET CENTRÉ ---
def draw_quizz_progressive_frame(question, options, max_opt_visible, reponse_correcte, explication, q_num, total_q, channel_tag, phase="question", timer_sec=3, bg_file=None, theme_name="Bleu Nuit & Or (YouTube Shorts)"):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or (YouTube Shorts)"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_head = get_font(52)
    f_q = get_font(48)
    f_opt = get_font(42)
    f_exp = get_font(36)
    
    # Header Centré
    header_text = f"QUIZ CULTURE GÉNÉRALE {q_num} sur {total_q}"
    try:
        h_w = f_head.getbbox(header_text)[2] - f_head.getbbox(header_text)[0]
    except AttributeError:
        h_w = f_head.getsize(header_text)[0]
    h_x = (width - h_w) // 2
    draw.text((h_x + 3, 133), header_text, fill=(0, 0, 0), font=f_head)
    draw.text((h_x, 130), header_text, fill=colors["accent"], font=f_head)
    
    # Question Centrée
    clean_q = remove_unsupported_emojis(question)
    q_lines = wrap_text(f"Q: {clean_q}", f_q, 920)
    y_q = 240
    for line in q_lines:
        try:
            qw = f_q.getbbox(line)[2] - f_q.getbbox(line)[0]
        except AttributeError:
            qw = f_q.getsize(line)[0]
        qx = (width - qw) // 2
        draw.text((qx + 3, y_q + 3), line, fill=(0, 0, 0), font=f_q)
        draw.text((qx, y_q), line, fill="white", font=f_q)
        y_q += 65
        
    rep_clean = str(reponse_correcte).strip().upper()
    correct_idx = -1
    if 'A' in rep_clean: correct_idx = 0
    elif 'B' in rep_clean: correct_idx = 1
    elif 'C' in rep_clean: correct_idx = 2
    elif 'D' in rep_clean: correct_idx = 3
    else:
        for idx_o, opt_val in enumerate(options):
            if opt_val.lower() in rep_clean.lower():
                correct_idx = idx_o
                break

    y_opt = max(580, y_q + 40)
    for i, opt in enumerate(options):
        if i <= max_opt_visible or max_opt_visible == -1:
            is_correct = (phase == "reponse" and i == correct_idx)
            fill_col = (34, 197, 94) if is_correct else colors["card"]
            out_col = (250, 204, 21) if is_correct else (255, 255, 255)
            
            # Boutons imposants et bien dessinés
            draw.rounded_rectangle([(70, y_opt), (1010, y_opt + 140)], radius=25, fill=fill_col, outline=out_col, width=4)
            clean_opt = remove_unsupported_emojis(opt)
            opt_text = f"{chr(65+i)}) {clean_opt}"
            draw.text((110, y_opt + 42), opt_text, fill="white", font=f_opt)
        y_opt += 175
        
    if phase == "chrono":
        draw.rounded_rectangle([(360, y_opt + 20), (720, y_opt + 120)], radius=40, fill=(15, 23, 42), outline=colors["accent"], width=4)
        draw.text((430, y_opt + 42), f"00:0{timer_sec}", fill="white", font=f_head)
    elif phase == "reponse":
        draw.rounded_rectangle([(60, y_opt + 20), (1020, y_opt + 230)], radius=22, fill=(15, 23, 42), outline=(34, 197, 94), width=4)
        clean_exp = remove_unsupported_emojis(explication)
        exp_lines = wrap_text(f"Explication : {clean_exp}", f_exp, 900)
        y_exp = y_opt + 45
        for line in exp_lines[:3]:
            draw.text((90, y_exp), line, fill="white", font=f_exp)
            y_exp += 48
            
    # Signature
    font_tag = get_font(40)
    try:
        t_w = font_tag.getbbox(channel_tag)[2] - font_tag.getbbox(channel_tag)[0]
    except AttributeError:
        t_w = font_tag.getsize(channel_tag)[0]
    draw.text(((width - t_w)//2, 1800), channel_tag, fill=(200, 200, 200), font=font_tag)
    return img

# --- RENDU DU VOCABULAIRE GRAND ET CENTRÉ ---
def draw_language_page_frame(mots, current_idx, phase_item, timer_sec, motiv_txt, langue, channel_tag, theme_name, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Bleu Nuit & Or (YouTube Shorts)"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_title = get_font(50)
    f_text = get_font(42)
    f_sub = get_font(36)
    
    title_text = f"VOCABULAIRE EN {langue.upper()}"
    try:
        tw = f_title.getbbox(title_text)[2] - f_title.getbbox(title_text)[0]
    except AttributeError:
        tw = f_title.getsize(title_text)[0]
    tx = (width - tw) // 2
    draw.text((tx + 3, 123), title_text, fill=(0, 0, 0), font=f_title)
    draw.text((tx, 120), title_text, fill=colors["accent"], font=f_title)
    
    y = 250
    for idx, item in enumerate(mots):
        clean_fr = remove_unsupported_emojis(item['fr'])
        clean_tr = remove_unsupported_emojis(item['trad'])
        if idx < current_idx:
            draw.rounded_rectangle([(70, y), (1010, y + 160)], radius=22, fill=colors["card"], outline=(255, 255, 255), width=2)
            draw.text((110, y + 25), f"FR: {clean_fr}", fill="white", font=f_text)
            draw.text((110, y + 90), f"TRAD: {clean_tr}", fill=(34, 197, 94), font=f_text)
        elif idx == current_idx:
            draw.rounded_rectangle([(70, y), (1010, y + 160)], radius=22, fill=colors["card"], outline=colors["accent"], width=4)
            draw.text((110, y + 25), f"FR: {clean_fr}", fill=colors["accent"], font=f_text)
            if phase_item in ["traduction", "motivation"]:
                draw.text((110, y + 90), f"TRAD: {clean_tr}", fill="white", font=f_text)
            elif phase_item == "chrono":
                draw.rounded_rectangle([(740, y + 35), (970, y + 125)], radius=20, fill=(15, 23, 42), outline=colors["accent"], width=3)
                draw.text((770, y + 52), f"00:0{timer_sec}", fill="white", font=f_sub)
        else:
            draw.rounded_rectangle([(70, y), (1010, y + 160)], radius=22, fill=(20, 24, 33), outline=(50, 55, 70), width=2)
            draw.text((110, y + 55), f"Mot #{idx+1}", fill=(100, 116, 139), font=f_sub)
        y += 195
        
    if phase_item == "motivation" and motiv_txt:
        clean_m = remove_unsupported_emojis(motiv_txt)
        draw.rounded_rectangle([(120, y + 20), (960, y + 150)], radius=22, fill=(34, 197, 94))
        try:
            mw = f_title.getbbox(clean_m)[2] - f_title.getbbox(clean_m)[0]
        except AttributeError:
            mw = f_title.getsize(clean_m)[0]
        mx = (width - mw) // 2
        draw.text((mx, y + 48), clean_m, fill="white", font=f_title)
        
    font_tag = get_font(40)
    try:
        t_w = font_tag.getbbox(channel_tag)[2] - font_tag.getbbox(channel_tag)[0]
    except AttributeError:
        t_w = font_tag.getsize(channel_tag)[0]
    draw.text(((width - t_w)//2, 1800), channel_tag, fill=(200, 200, 200), font=font_tag)
    return img

# --- INTERFACE STREAMLIT ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")
if api_key: genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["🧠 Quizz TikTok Pro", "🗣️ Vocabulaire Pro"])

VOICES_FR = {"Henri (Dynamique)": "fr-FR-HenriNeural", "Vivienne (Énergique)": "fr-FR-VivienneNeural", "Remy (Standard)": "fr-FR-RemyNeural"}
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
    hook_input = st.text_input("Accroche (Hook 3s)", "IMPOSSIBLE d'avoir 5/5 sur ce test !")
    channel_q_tag = st.text_input("Signature (Nom Chaîne)", "@QuizMaster_Pro", key="tag_q")
    
    col1, col2 = st.columns(2)
    with col1: voice_fr_code = VOICES_FR[st.selectbox("Voix Off (Forte)", list(VOICES_FR.keys()))]
    with col2: theme_visual_q = st.selectbox("Palette de Couleurs", list(THEMES.keys()), key="th_q")
        
    motiv_q_custom = st.text_input("Phrases motivation (séparées par virgule)", "Bravo !, Excellent !, Tu gères !", key="mq")
    motiv_q_list = [m.strip() for m in motiv_q_custom.split(",") if m.strip()]
    outro_q_custom = st.text_input("Outro / CTA Final", "Quel est ton score ? Écris-le en commentaire !", key="oq")
    
    mode_q = st.radio("Mode", ["IA Gemini", "Saisie Manuelle"], key="mode_q")
    bg_file_q = st.file_uploader("Fond 9:16 (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_q")
    
    if mode_q == "IA Gemini":
        theme_q = st.text_input("Thème", "Culture Générale", key="t_q")
        nb_q = st.slider("Questions", 1, 5, 3)
        if st.button("✨ Générer les questions"):
            if not api_key: st.error("Clé API requise !")
            else:
                with st.spinner("Génération..."):
                    try:
                        prompt = f"Génère {nb_q} questions quizz '{theme_q}'. JSON strict: [{{'question': '...', 'options': ['A','B','C','D'], 'reponse_correcte': 'A', 'explication': '...'}}]"
                        res = genai.GenerativeModel(get_working_model()).generate_content(prompt)
                        st.session_state['q_data'] = parse_json_response(res.text)
                        st.success("Généré !")
                    except Exception as e: st.error(f"Erreur : {e}")
    else:
        num_c = st.number_input("Nombre de questions", 1, 5, 3)
        c_list = []
        for i in range(int(num_c)):
            st.markdown(f"**Question {i+1}**")
            c_list.append({
                "question": st.text_input(f"Question {i+1}", key=f"q_{i}"),
                "options": [st.text_input("A", key=f"oa_{i}"), st.text_input("B", key=f"ob_{i}"), st.text_input("C", key=f"oc_{i}"), st.text_input("D", key=f"od_{i}")],
                "reponse_correcte": st.selectbox("Bonne réponse", ["A", "B", "C", "D"], key=f"r_{i}"),
                "explication": st.text_input("Explication", key=f"e_{i}")
            })
        if st.button("💾 Valider"): st.session_state['q_data'] = c_list

    if 'q_data' in st.session_state and st.session_state['q_data']:
        if st.button("🎬 Générer Vidéo Quizz"):
            with st.spinner("Montage sécurisé avec grande typographie..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tictac_sfx, ding_sfx = ensure_sfx_files(tmpdir)
                        clip_files = []
                        total_q = len(st.session_state['q_data'])
                        clip_counter = 0
                        
                        h_aud = os.path.join(tmpdir, "h.mp3")
                        h_img = os.path.join(tmpdir, "h.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_input), voice_fr_code, volume="+30%").save(h_aud))
                        draw_hook_frame(hook_input, theme_visual_q, channel_q_tag, bg_file_q).save(h_img)
                        h_dur = get_audio_duration(h_aud)
                        h_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(h_img, h_aud, h_dur, h_clip)
                        clip_files.append(h_clip)
                        clip_counter += 1
                        
                        for idx, q in enumerate(st.session_state['q_data']):
                            q_speech_txt = clean_text_for_tts(f"Question {idx+1}. {q['question']}")
                            q_speech_aud = os.path.join(tmpdir, f"q_{idx}_speech.mp3")
                            q_speech_img = os.path.join(tmpdir, f"q_{idx}_speech.png")
                            run_async(edge_tts.Communicate(q_speech_txt, voice_fr_code, volume="+30%").save(q_speech_aud))
                            draw_quizz_progressive_frame(q['question'], q['options'], -1, q['reponse_correcte'], q['explication'], idx+1, total_q, channel_q_tag, "question", 3, bg_file_q, theme_visual_q).save(q_speech_img)
                            dur = get_audio_duration(q_speech_aud)
                            out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(q_speech_img, q_speech_aud, dur, out_clip)
                            clip_files.append(out_clip)
                            clip_counter += 1
                            
                            for sec in range(3, 0, -1):
                                t_img = os.path.join(tmpdir, f"t_{idx}_{sec}.png")
                                draw_quizz_progressive_frame(q['question'], q['options'], 3, q['reponse_correcte'], q['explication'], idx+1, total_q, channel_q_tag, "chrono", sec, bg_file_q, theme_visual_q).save(t_img)
                                out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                                create_clip_ffmpeg(t_img, tictac_sfx, 1.0, out_clip)
                                clip_files.append(out_clip)
                                clip_counter += 1
                                
                            m_q_txt = motiv_q_list[idx % len(motiv_q_list)] if motiv_q_list else "Bravo !"
                            r_txt = clean_text_for_tts(f"La bonne réponse est {q['reponse_correcte']}. {q['explication']}. {m_q_txt}")
                            r_aud = os.path.join(tmpdir, f"r_{idx}.mp3")
                            r_img = os.path.join(tmpdir, f"r_{idx}.png")
                            run_async(edge_tts.Communicate(r_txt, voice_fr_code, volume="+30%").save(r_aud))
                            draw_quizz_progressive_frame(q['question'], q['options'], 3, q['reponse_correcte'], q['explication'], idx+1, total_q, channel_q_tag, "reponse", 0, bg_file_q, theme_visual_q).save(r_img)
                            
                            r_dur = get_audio_duration(r_aud)
                            out_clip_r = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(r_img, r_aud, r_dur, out_clip_r)
                            clip_files.append(out_clip_r)
                            clip_counter += 1
                            
                        c_aud = os.path.join(tmpdir, "c.mp3")
                        c_img = os.path.join(tmpdir, "c.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(outro_q_custom), voice_fr_code, volume="+30%").save(c_aud))
                        draw_hook_frame(outro_q_custom, theme_visual_q, channel_q_tag, bg_file_q).save(c_img)
                        c_dur = get_audio_duration(c_aud)
                        out_clip_c = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(c_img, c_aud, c_dur, out_clip_c)
                        clip_files.append(out_clip_c)
                        
                        out_mp4 = os.path.join(tmpdir, "quizz_final.mp4")
                        concatenate_clips_ffmpeg(clip_files, out_mp4, tmpdir)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger MP4 Quizz", data=f.read(), file_name="quizz_viral.mp4", mime="video/mp4")
                        st.success("✅ Vidéo générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur : {e}")

# ==================== MODULE 2 : LANGUES ====================
with tab2:
    st.header("2. Générateur Vocabulaire Pro")
    hook_l_input = st.text_input("Accroche (Hook)", "Tu prononces mal ces 5 mots !", key="hl")
    channel_l_tag = st.text_input("Signature (Nom Chaîne)", "@LingoPulse_Daily", key="tag_l")
    
    col1, col2 = st.columns(2)
    with col1: langue_c = st.selectbox("Langue cible", ["Anglais", "Espagnol", "Arabe", "Allemand", "Italien"], key="lc")
    with col2: voice_t_code = VOICES_MAP[langue_c][st.selectbox("Voix Traduction", list(VOICES_MAP[langue_c].keys()), key="vt")]
        
    theme_visual_l = st.selectbox("Palette de Couleurs", list(THEMES.keys()), key="th_l")
    bg_file_l = st.file_uploader("Fond 9:16 (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_l")
    
    motiv_custom = st.text_input("Mots motivation (séparés par virgule)", "Bravo !, Super !", key="ml")
    motiv_list = [m.strip() for m in motiv_custom.split(",") if m.strip()]
    outro_custom = st.text_input("Outro / CTA Final", "Abonne-toi !", key="ol")
    
    mode_l = st.radio("Mode Vocabulaire", ["IA Gemini", "Saisie Manuelle"], key="mode_l")
    
    if mode_l == "IA Gemini":
        theme_l = st.text_input("Thème", "Voyage", key="t_l")
        nb_m = st.slider("Mots", 3, 5, 3)
        if st.button("✨ Générer les mots"):
            if not api_key: st.error("Clé API !")
            else:
                with st.spinner("Génération..."):
                    try:
                        prompt = f"Génère {nb_m} mots avec traduction en {langue_c}. JSON strict: [{{'fr': 'Bonjour', 'trad': 'Hello'}}, ...]"
                        res = genai.GenerativeModel(get_working_model()).generate_content(prompt)
                        st.session_state['l_data'] = parse_json_response(res.text)
                        st.success("Généré !")
                    except Exception as e: st.error(f"Erreur : {e}")
    else:
        num_m = st.number_input("Mots à saisir", 1, 5, 3)
        c_m = []
        for i in range(int(num_m)):
            ca, cb = st.columns(2)
            with ca: c_m.append({"fr": st.text_input(f"FR #{i+1}", key=f"fr_{i}"), "trad": st.text_input(f"Trad #{i+1}", key=f"tr_{i}")})
        if st.button("💾 Valider"): st.session_state['l_data'] = c_m

    if 'l_data' in st.session_state and st.session_state['l_data']:
        if st.button("🎬 Générer Vidéo Vocabulaire"):
            with st.spinner("Montage sécurisé avec grande typographie..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tictac_sfx, ding_sfx = ensure_sfx_files(tmpdir)
                        clip_files = []
                        mots_l = st.session_state['l_data']
                        clip_counter = 0
                        
                        in_aud = os.path.join(tmpdir, "in.mp3")
                        in_img = os.path.join(tmpdir, "in.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_l_input), "fr-FR-HenriNeural", volume="+30%").save(in_aud))
                        draw_hook_frame(hook_l_input, theme_visual_l, channel_l_tag, bg_file_l).save(in_img)
                        dur = get_audio_duration(in_aud)
                        out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(in_img, in_aud, dur, out_clip)
                        clip_files.append(out_clip)
                        clip_counter += 1
                        
                        for idx, item in enumerate(mots_l):
                            t_fr = clean_text_for_tts(item['fr'])
                            t_tr = item['trad'].strip() if langue_c == "Arabe" else clean_text_for_tts(item['trad'])
                            m_txt = motiv_list[idx % len(motiv_list)] if motiv_list else "Bravo !"
                            
                            p_fr = os.path.join(tmpdir, f"fr_{idx}.mp3")
                            p_tr = os.path.join(tmpdir, f"tr_{idx}.mp3")
                            p_mo = os.path.join(tmpdir, f"mo_{idx}.mp3")
                            
                            run_async(edge_tts.Communicate(t_fr, "fr-FR-HenriNeural", volume="+30%").save(p_fr))
                            run_async(edge_tts.Communicate(t_tr, voice_t_code, volume="+30%").save(p_tr))
                            run_async(edge_tts.Communicate(m_txt, "fr-FR-HenriNeural", volume="+30%").save(p_mo))
                            
                            img_s1 = os.path.join(tmpdir, f"s1_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "mot", 0, "", langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_s1)
                            dur = get_audio_duration(p_fr)
                            out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(img_s1, p_fr, dur, out_clip)
                            clip_files.append(out_clip)
                            clip_counter += 1
                            
                            for sec in range(2, 0, -1):
                                img_sc = os.path.join(tmpdir, f"sc_{idx}_{sec}.png")
                                draw_language_page_frame(mots_l, idx, "chrono", sec, "", langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_sc)
                                out_clip = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                                create_clip_ffmpeg(img_sc, tictac_sfx, 1.0, out_clip)
                                clip_files.append(out_clip)
                                clip_counter += 1
                                
                            img_s3 = os.path.join(tmpdir, f"s3_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "traduction", 0, "", langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_s3)
                            tr_dur = get_audio_duration(p_tr)
                            out_clip_tr = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(img_s3, p_tr, tr_dur, out_clip_tr)
                            clip_files.append(out_clip_tr)
                            clip_counter += 1
                            
                            img_s4 = os.path.join(tmpdir, f"s4_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "motivation", 0, m_txt, langue_c, channel_l_tag, theme_visual_l, bg_file_l).save(img_s4)
                            mo_dur = get_audio_duration(p_mo)
                            out_clip_mo = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                            create_clip_ffmpeg(img_s4, p_mo, mo_dur, out_clip_mo)
                            clip_files.append(out_clip_mo)
                            clip_counter += 1
                            
                        out_aud = os.path.join(tmpdir, "out.mp3")
                        out_img = os.path.join(tmpdir, "out.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(outro_custom), "fr-FR-HenriNeural", volume="+30%").save(out_aud))
                        draw_hook_frame(outro_custom, theme_visual_l, channel_l_tag, bg_file_l).save(out_img)
                        out_dur = get_audio_duration(out_aud)
                        out_clip_o = os.path.join(tmpdir, f"clip_{clip_counter}.mp4")
                        create_clip_ffmpeg(out_img, out_aud, out_dur, out_clip_o)
                        clip_files.append(out_clip_o)
                        
                        out_mp4 = os.path.join(tmpdir, "vocabulaire_final.mp4")
                        concatenate_clips_ffmpeg(clip_files, out_mp4, tmpdir)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger MP4 Vocabulaire", data=f.read(), file_name="vocabulaire_viral.mp4", mime="video/mp4")
                        st.success("✅ Vidéo générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur : {e}")
