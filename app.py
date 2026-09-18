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
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Studio TikTok Pro - Quizz & Vocabulaire", layout="wide")
st.title("🚀 Studio TikTok Pro (.MP4)")

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

# --- THEMES CLASSE & NUANCE ---
THEMES = {
    "Néon Doré & Noir Premium": {"bg": (15, 17, 23), "card": (28, 31, 42), "accent": (245, 158, 11), "text_accent": (0, 0, 0), "glow": (251, 191, 36)},
    "Bleu Nuit & Violet Royal": {"bg": (11, 15, 25), "card": (23, 30, 50), "accent": (139, 92, 246), "text_accent": (255, 255, 255), "glow": (167, 139, 250)},
    "Émeraude & Or": {"bg": (6, 24, 18), "card": (15, 45, 35), "accent": (16, 185, 129), "text_accent": (0, 0, 0), "glow": (52, 211, 153)},
    "Rose Cyberpunk": {"bg": (18, 12, 24), "card": (38, 24, 50), "accent": (236, 72, 153), "text_accent": (255, 255, 255), "glow": (244, 114, 182)}
}

# --- FONCTIONS DESSIN QUIZZ ---
def draw_hook_frame(hook_text, theme_name, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon Doré & Noir Premium"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(56)
    draw.rectangle([(60, 600), (1020, 1100)], fill=colors["accent"], outline=colors["glow"], width=6)
    draw.text((100, 750), hook_text, fill=colors["text_accent"], font=font_title)
    return img

def draw_quizz_frame(question, options, reponse_correcte, explication, q_num, total_q, phase="question", timer_sec=5, bg_file=None, theme_name="Néon Doré & Noir Premium"):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon Doré & Noir Premium"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_head, f_q, f_opt = get_font(42), get_font(46), get_font(40)
    
    draw.rectangle([(60, 100), (1020, 220)], fill=colors["accent"])
    draw.text((90, 140), f"🔥 QUESTION {q_num}/{total_q}", fill=colors["text_accent"], font=f_head)
    
    draw.text((90, 280), f"Q: {question}", fill="white", font=f_q)
    
    correct_letter = str(reponse_correcte).strip().upper()[0] if reponse_correcte else 'A'
    correct_idx = ord(correct_letter) - 65 if correct_letter in ['A', 'B', 'C', 'D'] else 0
    
    y = 520
    for i, opt in enumerate(options):
        is_correct = (phase == "reponse" and i == correct_idx)
        fill_col = (34, 197, 94) if is_correct else colors["card"]
        out_col = (250, 204, 21) if is_correct else colors["accent"]
        
        draw.rectangle([(90, y), (990, y + 140)], fill=fill_col, outline=out_col, width=4)
        draw.text((120, y + 45), f"{chr(65+i)}) {opt}", fill="white", font=f_opt)
        y += 180
        
    if phase == "reponse":
        draw.rectangle([(80, y + 20), (1000, y + 240)], fill=(15, 23, 42), outline=(34, 197, 94), width=3)
        draw.text((100, y + 50), f"💡 Explication :\n{explication}", fill="white", font=get_font(34))
    else:
        draw.rectangle([(380, y + 20), (700, y + 120)], fill=(225, 29, 72), outline=(255, 255, 255), width=3)
        draw.text((430, y + 50), f"⏱️ 00:0{timer_sec}", fill="white", font=f_head)
        
    return img

# --- FONCTIONS DESSIN VOCABULAIRE ---
def draw_lang_step_frame(mot_fr, mot_trad, step, timer_sec, motiv_txt, langue, theme_name, bg_file=None):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon Doré & Noir Premium"])
    img = Image.open(bg_file).convert('RGB').resize((width, height)) if bg_file else Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    f_title, f_big, f_sub = get_font(48), get_font(54), get_font(40)
    
    # En-tête
    draw.rectangle([(60, 120), (1020, 240)], fill=colors["accent"])
    draw.text((100, 160), f"💡 VOCABULAIRE ({langue.upper()})", fill=colors["text_accent"], font=f_title)
    
    # Cartouche Mot Français
    draw.rectangle([(90, 450), (990, 650)], fill=colors["card"], outline=colors["accent"], width=4)
    draw.text((130, 490), "FRANÇAIS :", fill=colors["accent"], font=f_sub)
    draw.text((130, 550), mot_fr, fill="white", font=f_big)
    
    # Chrono / Réflexion
    if step == "chrono":
        draw.rectangle([(380, 750), (700, 860)], fill=(225, 29, 72), outline=(255, 255, 255), width=3)
        draw.text((430, 780), f"⏱️ 00:0{timer_sec}", fill="white", font=f_title)
        
        # Barre de progression
        bar_w = int(800 * (timer_sec / 3.0))
        draw.rectangle([(140, 900), (140 + bar_w, 930)], fill=colors["accent"])
        
    # Affichage Traduction
    if step in ["traduction", "motivation"]:
        draw.rectangle([(90, 750), (990, 950)], fill=(16, 185, 129), outline=(255, 255, 255), width=4)
        draw.text((130, 790), f"TRADUCTION ({langue.upper()}) :", fill=(15, 23, 42), font=f_sub)
        draw.text((130, 850), mot_trad, fill="white", font=f_big)
        
    # Mot de Motivation
    if step == "motivation" and motiv_txt:
        draw.rectangle([(150, 1100), (930, 1250)], fill=colors["accent"])
        draw.text((200, 1150), f"🔥 {motiv_txt}", fill=colors["text_accent"], font=f_title)
        
    return img

# --- INTERFACE PRINCIPALE ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")
if api_key:
    genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["🧠 Quizz TikTok Pro", "🗣️ Fiche Langue Pro"])

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
    st.header("1. Générateur Quizz Pro")
    hook_input = st.text_input("Accroche (Hook 3s)", "IMPOSSIBLE d'avoir 5/5 sur ce test !")
    
    col1, col2 = st.columns(2)
    with col1:
        voice_fr_code = VOICES_FR[st.selectbox("Voix Off", list(VOICES_FR.keys()))]
    with col2:
        theme_visual_q = st.selectbox("Thème Visuel Classieux", list(THEMES.keys()), key="th_q")
        
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
        if st.button("🎬 Générer le MP4 Quizz"):
            with st.spinner("Montage en cours..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        clips = []
                        total_q = len(st.session_state['q_data'])
                        
                        # Hook
                        h_aud = os.path.join(tmpdir, "h.mp3")
                        h_img = os.path.join(tmpdir, "h.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_input), voice_fr_code).save(h_aud))
                        draw_hook_frame(hook_input, theme_visual_q, bg_file_q).save(h_img)
                        a_h = AudioFileClip(h_aud)
                        clips.append(ImageClip(h_img).set_duration(a_h.duration).set_audio(a_h))
                        
                        motivations = ["Bravo ! On continue !", "Super effort !", "Tu gères !"]
                        for idx, q in enumerate(st.session_state['q_data']):
                            q_aud = os.path.join(tmpdir, f"q_{idx}.mp3")
                            r_aud = os.path.join(tmpdir, f"r_{idx}.mp3")
                            q_img = os.path.join(tmpdir, f"q_{idx}.png")
                            r_img = os.path.join(tmpdir, f"r_{idx}.png")
                            
                            t_q = clean_text_for_tts(f"Question {idx+1}. {q['question']}. A: {q['options'][0]}. B: {q['options'][1]}. C: {q['options'][2]}. D: {q['options'][3]}.")
                            t_r = clean_text_for_tts(f"La bonne réponse est l'option {q['reponse_correcte']}. {q['explication']}. {motivations[idx % len(motivations)]}")
                            
                            run_async(edge_tts.Communicate(t_q, voice_fr_code).save(q_aud))
                            run_async(edge_tts.Communicate(t_r, voice_fr_code).save(r_aud))
                            
                            draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], idx+1, total_q, "question", 5, bg_file_q, theme_visual_q).save(q_img)
                            draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], idx+1, total_q, "reponse", 0, bg_file_q, theme_visual_q).save(r_img)
                            
                            a_q, a_r = AudioFileClip(q_aud), AudioFileClip(r_aud)
                            clip_q = ImageClip(q_img).set_duration(a_q.duration).set_audio(a_q)
                            
                            t_clips = []
                            for sec in range(5, 0, -1):
                                t_img = os.path.join(tmpdir, f"t_{idx}_{sec}.png")
                                draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], idx+1, total_q, "question", sec, bg_file_q, theme_visual_q).save(t_img)
                                t_clips.append(ImageClip(t_img).set_duration(1))
                                
                            clip_r = ImageClip(r_img).set_duration(a_r.duration).set_audio(a_r)
                            clips.extend([clip_q] + t_clips + [clip_r])
                            
                        # Outro
                        c_aud = os.path.join(tmpdir, "c.mp3")
                        c_img = os.path.join(tmpdir, "c.png")
                        run_async(edge_tts.Communicate("Écris ton score en commentaire et abonne-toi !", voice_fr_code).save(c_aud))
                        draw_hook_frame("QUEL EST TON SCORE ?\nÉcris-le en commentaire ! 💬", theme_visual_q, bg_file_q).save(c_img)
                        a_c = AudioFileClip(c_aud)
                        clips.append(ImageClip(c_img).set_duration(a_c.duration).set_audio(a_c))
                        
                        final_v = concatenate_videoclips(clips, method="compose")
                        out_mp4 = os.path.join(tmpdir, "quizz_final.mp4")
                        final_v.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger le MP4 Quizz", data=f.read(), file_name="quizz_viral_pro.mp4", mime="video/mp4")
                        st.success("✅ Vidéo Quizz générée !")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")

# ==================== MODULE 2 : LANGUES ====================
with tab2:
    st.header("2. Générateur Vocabulaire Rythmé Pro")
    
    hook_l_input = st.text_input("Accroche (Hook)", "Tu prononces mal ces 5 mots ! Vérifions ensemble.")
    
    col1, col2 = st.columns(2)
    with col1:
        langue_c = st.selectbox("Langue cible", ["Anglais", "Espagnol", "Arabe", "Allemand", "Italien"])
    with col2:
        voice_t_code = VOICES_MAP[langue_c][st.selectbox("Voix Traduction", list(VOICES_MAP[langue_c].keys()))]
        
    theme_visual_l = st.selectbox("Thème Visuel Classieux", list(THEMES.keys()), key="th_l")
    bg_file_l = st.file_uploader("Fond 9:16 Personnalisé (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_l")
    
    motiv_custom = st.text_input("Mots de motivation entre les mots (séparés par une virgule)", "Bravo !, Excellent !, Continue comme ça !, Super !")
    motiv_list = [m.strip() for m in motiv_custom.split(",") if m.strip()]
    
    outro_custom = st.text_input("Phrase d'Outro / CTA Final", "Enregistre cette vidéo et abonne-toi pour progresser !")
    
    mode_l = st.radio("Mode Vocabulaire", ["IA Gemini", "Saisie Manuelle"], key="mode_l")
    
    if mode_l == "IA Gemini":
        theme_l = st.text_input("Thème", "Voyage", key="t_l")
        nb_m = st.slider("Nombre de mots", 3, 8, 5)
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
        num_m = st.number_input("Nombre de mots à saisir", 1, 8, 5)
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
        if st.button("🎬 Générer le MP4 Vocabulaire Rythmé"):
            with st.spinner("Montage de la séquence mot par mot..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        w_clips = []
                        mots_l = st.session_state['l_data']
                        
                        # Hook Intro
                        in_aud = os.path.join(tmpdir, "in.mp3")
                        in_img = os.path.join(tmpdir, "in.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_l_input), "fr-FR-HenriNeural").save(in_aud))
                        draw_hook_frame(hook_l_input, theme_visual_l, bg_file_l).save(in_img)
                        a_in = AudioFileClip(in_aud)
                        w_clips.append(ImageClip(in_img).set_duration(a_in.duration).set_audio(a_in))
                        
                        # Boucle Mot par Mot
                        for idx, item in enumerate(mots_l):
                            t_fr = clean_text_for_tts(item['fr'])
                            t_tr = item['trad'].strip() if langue_c == "Arabe" else clean_text_for_tts(item['trad'])
                            m_txt = motiv_list[idx % len(motiv_list)] if motiv_list else "Bravo !"
                            
                            # Audios
                            p_fr = os.path.join(tmpdir, f"fr_{idx}.mp3")
                            p_tr = os.path.join(tmpdir, f"tr_{idx}.mp3")
                            p_mo = os.path.join(tmpdir, f"mo_{idx}.mp3")
                            
                            run_async(edge_tts.Communicate(t_fr, "fr-FR-HenriNeural").save(p_fr))
                            run_async(edge_tts.Communicate(t_tr, voice_t_code).save(p_tr))
                            run_async(edge_tts.Communicate(m_txt, "fr-FR-HenriNeural").save(p_mo))
                            
                            a_fr, a_tr, a_mo = AudioFileClip(p_fr), AudioFileClip(p_tr), AudioFileClip(p_mo)
                            
                            # Étape 1 : Mot FR
                            img_step1 = os.path.join(tmpdir, f"s1_{idx}.png")
                            draw_lang_step_frame(item['fr'], item['trad'], "mot", 0, "", langue_c, theme_visual_l, bg_file_l).save(img_step1)
                            w_clips.append(ImageClip(img_step1).set_duration(a_fr.duration).set_audio(a_fr))
                            
                            # Étape 2 : Chrono 3s
                            for sec in range(3, 0, -1):
                                img_c = os.path.join(tmpdir, f"sc_{idx}_{sec}.png")
                                draw_lang_step_frame(item['fr'], item['trad'], "chrono", sec, "", langue_c, theme_visual_l, bg_file_l).save(img_c)
                                w_clips.append(ImageClip(img_c).set_duration(1))
                                
                            # Étape 3 : Traduction
                            img_step3 = os.path.join(tmpdir, f"s3_{idx}.png")
                            draw_lang_step_frame(item['fr'], item['trad'], "traduction", 0, "", langue_c, theme_visual_l, bg_file_l).save(img_step3)
                            w_clips.append(ImageClip(img_step3).set_duration(a_tr.duration).set_audio(a_tr))
                            
                            # Étape 4 : Motivation
                            img_step4 = os.path.join(tmpdir, f"s4_{idx}.png")
                            draw_lang_step_frame(item['fr'], item['trad'], "motivation", 0, m_txt, langue_c, theme_visual_l, bg_file_l).save(img_step4)
                            w_clips.append(ImageClip(img_step4).set_duration(a_mo.duration).set_audio(a_mo))
                            
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
                            st.download_button("📥 Télécharger le MP4 Vocabulaire Rythmé", data=f.read(), file_name="vocabulaire_rythme_pro.mp4", mime="video/mp4")
                        st.success("✅ Vidéo Vocabulaire générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")
