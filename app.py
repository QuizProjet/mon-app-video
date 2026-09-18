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
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

st.set_page_config(page_title="Studio TikTok Pro - Quizz & Vocabulaire", layout="wide")
st.title("🚀 Studio TikTok Pro (.MP4)")

# --- BRUITAGES SFX SÉCURISÉS (TIC-TAC & DING) ---
def ensure_sfx_files(tmpdir):
    tictac_path = os.path.join(tmpdir, "tictac.wav")
    ding_path = os.path.join(tmpdir, "ding.wav")
    
    # 1. Tic-Tac de montre (0.15s)
    with wave.open(tictac_path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(6615):
            val = int(14000 * math.sin(2 * math.pi * 1000 * (i/44100)) * math.exp(-i/500))
            f.writeframes(struct.pack('<h', val))
            
    # 2. Ding validation (0.4s)
    with wave.open(ding_path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(17640):
            val = int(16000 * (math.sin(2 * math.pi * 1318.5 * (i/44100)) + math.sin(2 * math.pi * 1567.98 * (i/44100))) * math.exp(-i/3000))
            f.writeframes(struct.pack('<h', val))
            
    return tictac_path, ding_path

# --- CHARGEMENT FONTS HD ---
def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

# --- UTILITAIRES TTS & ASYNC ---
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        new_loop = asyncio.new_event_loop()
        return new_loop.run_until_complete(coro)
    else:
        return loop.run_until_complete(coro)

def clean_text_for_tts(text):
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

# --- THEMES HIGH-CONTRAST PREMIER CLASSE ---
THEMES = {
    "Néon Doré & Noir Premium": {"bg": (15, 17, 23), "card": (28, 31, 42), "accent": (245, 158, 11), "text_accent": (0, 0, 0), "glow": (251, 191, 36)},
    "Bleu Nuit & Violet Royal": {"bg": (11, 15, 25), "card": (23, 30, 50), "accent": (139, 92, 246), "text_accent": (255, 255, 255), "glow": (167, 139, 250)},
    "Émeraude & Or": {"bg": (6, 24, 18), "card": (15, 45, 35), "accent": (16, 185, 129), "text_accent": (0, 0, 0), "glow": (52, 211, 153)},
    "Rose Cyberpunk": {"bg": (18, 12, 24), "card": (38, 24, 50), "accent": (236, 72, 153), "text_accent": (255, 255, 255), "glow": (244, 114, 182)}
}

# --- RENDU VISUEL QUIZZ PROGRESSIF ---
def draw_hook_frame(hook_text, theme_name, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon Doré & Noir Premium"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(56)
    draw.rectangle([(60, 600), (1020, 1100)], fill=colors["accent"], outline=colors["glow"], width=6)
    draw.text((100, 750), hook_text, fill=colors["text_accent"], font=font_title)
    return img

def draw_quizz_progressive_frame(question, options, max_opt_visible, reponse_correcte, explication, q_num, total_q, phase="question", timer_sec=5, bg_file=None, theme_name="Néon Doré & Noir Premium"):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon Doré & Noir Premium"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_head, f_q, f_opt = get_font(42), get_font(46), get_font(40)
    
    # En-tête
    draw.rectangle([(60, 100), (1020, 220)], fill=colors["accent"])
    draw.text((90, 140), f"🔥 QUESTION {q_num}/{total_q}", fill=colors["text_accent"], font=f_head)
    
    # Question
    draw.text((90, 280), f"Q: {question}", fill="white", font=f_q)
    
    correct_letter = str(reponse_correcte).strip().upper()[0] if reponse_correcte else 'A'
    correct_idx = ord(correct_letter) - 65 if correct_letter in ['A', 'B', 'C', 'D'] else 0
    
    y = 520
    for i, opt in enumerate(options):
        if i <= max_opt_visible:
            is_correct = (phase == "reponse" and i == correct_idx)
            fill_col = (34, 197, 94) if is_correct else colors["card"]
            out_col = (250, 204, 21) if is_correct else colors["accent"]
            
            draw.rectangle([(90, y), (990, y + 140)], fill=fill_col, outline=out_col, width=4)
            draw.text((120, y + 45), f"{chr(65+i)}) {opt}", fill="white", font=f_opt)
        else:
            # Emplacement réservé/masqué
            draw.rectangle([(90, y), (990, y + 140)], fill=(20, 24, 33), outline=(40, 45, 60), width=2)
        y += 180
        
    if phase == "chrono":
        draw.rectangle([(380, y + 20), (700, y + 120)], fill=(225, 29, 72), outline=(255, 255, 255), width=3)
        draw.text((430, y + 50), f"⏱️ 00:0{timer_sec}", fill="white", font=f_head)
    elif phase == "reponse":
        draw.rectangle([(80, y + 20), (1000, y + 240)], fill=(15, 23, 42), outline=(34, 197, 94), width=3)
        draw.text((100, y + 50), f"💡 Explication :\n{explication}", fill="white", font=get_font(34))
        
    return img

# --- RENDU VISUEL VOCABULAIRE SUR UNE SEULE PAGE ---
def draw_language_page_frame(mots, current_idx, phase_item, timer_sec, motiv_txt, langue, theme_name, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon Doré & Noir Premium"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_title, f_text, f_sub = get_font(44), get_font(38), get_font(32)
    
    draw.rectangle([(60, 100), (1020, 200)], fill=colors["accent"])
    draw.text((90, 135), f"💡 VOCABULAIRE ({langue.upper()})", fill=colors["text_accent"], font=f_title)
    
    y = 250
    for idx, item in enumerate(mots):
        if idx < current_idx:
            # Mots déjà complétés
            draw.rectangle([(80, y), (1000, y + 160)], fill=colors["card"], outline=(255, 255, 255), width=2)
            draw.text((110, y + 30), f"FR: {item['fr']}", fill="white", font=f_text)
            draw.text((110, y + 90), f"TRAD: {item['trad']}", fill=(34, 197, 94), font=f_text)
        elif idx == current_idx:
            # Mot actif en cours de traitement
            draw.rectangle([(80, y), (1000, y + 160)], fill=colors["accent"], outline=colors["glow"], width=4)
            draw.text((110, y + 30), f"FR: {item['fr']}", fill=colors["text_accent"], font=f_text)
            
            if phase_item in ["traduction", "motivation"]:
                draw.text((110, y + 90), f"TRAD: {item['trad']}", fill=(15, 23, 42), font=f_text)
            elif phase_item == "chrono":
                draw.rectangle([(750, y + 40), (960, y + 120)], fill=(225, 29, 72))
                draw.text((780, y + 55), f"⏱️ 00:0{timer_sec}", fill="white", font=f_sub)
        else:
            # Mots à venir
            draw.rectangle([(80, y), (1000, y + 160)], fill=(20, 24, 33), outline=(50, 55, 70), width=2)
            draw.text((110, y + 60), f"Mot #{idx+1}", fill=(100, 116, 139), font=f_sub)
        y += 190
        
    if phase_item == "motivation" and motiv_txt:
        draw.rectangle([(150, y + 20), (930, y + 150)], fill=(34, 197, 94))
        draw.text((200, y + 50), f"🔥 {motiv_txt}", fill="white", font=f_title)
        
    return img

# --- INTERFACE PRINCIPALE ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")
if api_key:
    genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["🧠 Quizz TikTok Rythmé Pro", "🗣️ Vocabulaire Page Unique Pro"])

VOICES_FR = {"Henri (Homme Énergique)": "fr-FR-HenriNeural", "Vivienne (Femme Dynamique)": "fr-FR-VivienneNeural"}
VOICES_MAP = {
    "Anglais": {"Emma (Femme)": "en-US-EmmaNeural", "Christopher (Homme)": "en-US-ChristopherNeural"},
    "Espagnol": {"Alvaro (Homme)": "es-ES-AlvaroNeural", "Elvira (Femme)": "es-ES-ElviraNeural"},
    "Arabe": {"Hamed (Homme)": "ar-SA-HamedNeural", "Salma (Femme)": "ar-SA-SalmaNeural"},
    "Allemand": {"Killian (Homme)": "de-DE-KillianNeural", "Klarissa (Femme)": "de-DE-KlarissaNeural"},
    "Italien": {"Diego (Homme)": "it-IT-DiegoNeural", "Elsa (Femme)": "it-IT-ElsaNeural"}
}

# ==================== MODULE 1 : QUIZZ ====================
with tab1:
    st.header("1. Générateur Quizz Rythmé (A ➔ B ➔ C ➔ D)")
    hook_input = st.text_input("Accroche (Hook 3s)", "IMPOSSIBLE d'avoir 5/5 sur ce test !")
    
    col1, col2 = st.columns(2)
    with col1:
        voice_fr_code = VOICES_FR[st.selectbox("Voix Off", list(VOICES_FR.keys()))]
    with col2:
        theme_visual_q = st.selectbox("Thème Visuel Classieux", list(THEMES.keys()), key="th_q")
        
    motiv_q_custom = st.text_input("Mots de motivation Quizz (séparés par une virgule)", "Bravo !, Excellent !, Tu gères !", key="mq")
    motiv_q_list = [m.strip() for m in motiv_q_custom.split(",") if m.strip()]
    
    outro_q_custom = st.text_input("Phrase d'Outro / CTA Final Quirm", "Quel est ton score ? Écris-le en commentaire ! 💬", key="oq")
    
    mode_q = st.radio("Mode", ["IA Gemini", "Saisie Manuelle"], key="mode_q")
    bg_file_q = st.file_uploader("Fond 9:16 Personnalisé (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_q")
    
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
        if st.button("🎬 Générer le MP4 Quizz Rythmé (SFX)"):
            with st.spinner("Montage de la séquence progressive avec Tic-Tac et Ding..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tictac_sfx, ding_sfx = ensure_sfx_files(tmpdir)
                        clips = []
                        total_q = len(st.session_state['q_data'])
                        
                        # Hook Intro
                        h_aud = os.path.join(tmpdir, "h.mp3")
                        h_img = os.path.join(tmpdir, "h.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_input), voice_fr_code).save(h_aud))
                        draw_hook_frame(hook_input, theme_visual_q, bg_file_q).save(h_img)
                        a_h = AudioFileClip(h_aud)
                        clips.append(ImageClip(h_img).set_duration(a_h.duration).set_audio(a_h))
                        
                        for idx, q in enumerate(st.session_state['q_data']):
                            # 1. Énoncé + Apparition progressive A ➔ B ➔ C ➔ D
                            for opt_idx in range(4):
                                opt_txt = clean_text_for_tts(f"Option {chr(65+opt_idx)}. {q['options'][opt_idx]}")
                                opt_aud = os.path.join(tmpdir, f"q_{idx}_opt_{opt_idx}.mp3")
                                opt_img = os.path.join(tmpdir, f"q_{idx}_opt_{opt_idx}.png")
                                
                                run_async(edge_tts.Communicate(opt_txt, voice_fr_code).save(opt_aud))
                                draw_quizz_progressive_frame(q['question'], q['options'], opt_idx, q['reponse_correcte'], q['explication'], idx+1, total_q, "question", 5, bg_file_q, theme_visual_q).save(opt_img)
                                
                                a_opt = AudioFileClip(opt_aud)
                                clips.append(ImageClip(opt_img).set_duration(a_opt.duration).set_audio(a_opt))
                                
                            # 2. Chrono 5s avec Tic-Tac
                            sfx_tictac_clip = AudioFileClip(tictac_sfx)
                            for sec in range(5, 0, -1):
                                t_img = os.path.join(tmpdir, f"t_{idx}_{sec}.png")
                                draw_quizz_progressive_frame(q['question'], q['options'], 3, q['reponse_correcte'], q['explication'], idx+1, total_q, "chrono", sec, bg_file_q, theme_visual_q).save(t_img)
                                clips.append(ImageClip(t_img).set_duration(1).set_audio(sfx_tictac_clip))
                                
                            # 3. Réponse + Explication + Motivation + Ding
                            m_q_txt = motiv_q_list[idx % len(motiv_q_list)] if motiv_q_list else "Bravo !"
                            r_txt = clean_text_for_tts(f"La bonne réponse est l'option {q['reponse_correcte']}. {q['explication']}. {m_q_txt}")
                            r_aud = os.path.join(tmpdir, f"r_{idx}.mp3")
                            r_img = os.path.join(tmpdir, f"r_{idx}.png")
                            
                            run_async(edge_tts.Communicate(r_txt, voice_fr_code).save(r_aud))
                            draw_quizz_progressive_frame(q['question'], q['options'], 3, q['reponse_correcte'], q['explication'], idx+1, total_q, "reponse", 0, bg_file_q, theme_visual_q).save(r_img)
                            
                            a_r = AudioFileClip(r_aud)
                            sfx_ding_clip = AudioFileClip(ding_sfx)
                            combined_audio = CompositeAudioClip([a_r, sfx_ding_clip])
                            clips.append(ImageClip(r_img).set_duration(a_r.duration).set_audio(combined_audio))
                            
                        # Outro CTA
                        c_aud = os.path.join(tmpdir, "c.mp3")
                        c_img = os.path.join(tmpdir, "c.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(outro_q_custom), voice_fr_code).save(c_aud))
                        draw_hook_frame(outro_q_custom, theme_visual_q, bg_file_q).save(c_img)
                        a_c = AudioFileClip(c_aud)
                        clips.append(ImageClip(c_img).set_duration(a_c.duration).set_audio(a_c))
                        
                        final_v = concatenate_videoclips(clips, method="compose")
                        out_mp4 = os.path.join(tmpdir, "quizz_final.mp4")
                        final_v.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger le MP4 Quizz Rythmé", data=f.read(), file_name="quizz_rythme_pro.mp4", mime="video/mp4")
                        st.success("✅ Vidéo Quizz générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")

# ==================== MODULE 2 : LANGUES ====================
with tab2:
    st.header("2. Générateur Vocabulaire (Page Unique + SFX)")
    
    hook_l_input = st.text_input("Accroche (Hook)", "Tu prononces mal ces 5 mots ! Vérifions ensemble.", key="hl")
    
    col1, col2 = st.columns(2)
    with col1:
        langue_c = st.selectbox("Langue cible", ["Anglais", "Espagnol", "Arabe", "Allemand", "Italien"], key="lc")
    with col2:
        voice_t_code = VOICES_MAP[langue_c][st.selectbox("Voix Traduction", list(VOICES_MAP[langue_c].keys()), key="vt")]
        
    theme_visual_l = st.selectbox("Thème Visuel Classieux", list(THEMES.keys()), key="th_l")
    bg_file_l = st.file_uploader("Fond 9:16 Personnalisé (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_l")
    
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
        if st.button("🎬 Générer le MP4 Vocabulaire Page Unique"):
            with st.spinner("Montage de la séquence sur page unique avec SFX..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tictac_sfx, ding_sfx = ensure_sfx_files(tmpdir)
                        w_clips = []
                        mots_l = st.session_state['l_data']
                        
                        # Hook Intro
                        in_aud = os.path.join(tmpdir, "in.mp3")
                        in_img = os.path.join(tmpdir, "in.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_l_input), "fr-FR-HenriNeural").save(in_aud))
                        draw_hook_frame(hook_l_input, theme_visual_l, bg_file_l).save(in_img)
                        a_in = AudioFileClip(in_aud)
                        w_clips.append(ImageClip(in_img).set_duration(a_in.duration).set_audio(a_in))
                        
                        sfx_tictac_clip = AudioFileClip(tictac_sfx)
                        sfx_ding_clip = AudioFileClip(ding_sfx)
                        
                        # Traitement sur la même page
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
                            
                            a_fr, a_tr, a_mo = AudioFileClip(p_fr), AudioFileClip(p_tr), AudioFileClip(p_mo)
                            
                            # Étape 1 : Mot FR
                            img_s1 = os.path.join(tmpdir, f"s1_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "mot", 0, "", langue_c, theme_visual_l, bg_file_l).save(img_s1)
                            w_clips.append(ImageClip(img_s1).set_duration(a_fr.duration).set_audio(a_fr))
                            
                            # Étape 2 : Chrono 3s avec Tic-Tac
                            for sec in range(3, 0, -1):
                                img_sc = os.path.join(tmpdir, f"sc_{idx}_{sec}.png")
                                draw_language_page_frame(mots_l, idx, "chrono", sec, "", langue_c, theme_visual_l, bg_file_l).save(img_sc)
                                w_clips.append(ImageClip(img_sc).set_duration(1).set_audio(sfx_tictac_clip))
                                
                            # Étape 3 : Traduction + Ding
                            img_s3 = os.path.join(tmpdir, f"s3_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "traduction", 0, "", langue_c, theme_visual_l, bg_file_l).save(img_s3)
                            combined_tr_audio = CompositeAudioClip([a_tr, sfx_ding_clip])
                            w_clips.append(ImageClip(img_s3).set_duration(a_tr.duration).set_audio(combined_tr_audio))
                            
                            # Étape 4 : Motivation
                            img_s4 = os.path.join(tmpdir, f"s4_{idx}.png")
                            draw_language_page_frame(mots_l, idx, "motivation", 0, m_txt, langue_c, theme_visual_l, bg_file_l).save(img_s4)
                            w_clips.append(ImageClip(img_s4).set_duration(a_mo.duration).set_audio(a_mo))
                            
                        # Outro CTA
                        out_aud = os.path.join(tmpdir, "out.mp3")
                        out_img = os.path.join(tmpdir, "out.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(outro_custom), "fr-FR-HenriNeural").save(out_aud))
                        draw_hook_frame(outro_custom, theme_visual_l, bg_file_l).save(out_img)
                        a_out = AudioFileClip(out_aud)
                        w_clips.append(ImageClip(out_img).set_duration(a_out.duration).set_audio(a_out))
                        
                        final_v = concatenate_videoclips(w_clips, method="compose")
                        out_mp4 = os.path.join(tmpdir, "vocabulaire_final.mp4")
                        final_v.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger le MP4 Vocabulaire Page Unique", data=f.read(), file_name="vocabulaire_page_unique_pro.mp4", mime="video/mp4")
                        st.success("✅ Vidéo Vocabulaire générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")
