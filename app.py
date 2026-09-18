import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import tempfile
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Studio TikTok & Shorts Pro", layout="wide")
st.title("🚀 Studio TikTok Pro : Générateur de Vidéos Virales (.MP4)")

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

# Force l'utilisation du modèle Gemini 3.6 Flash recommandé
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
    "Néon TikTok (Jaune & Noir)": {"bg": (10, 10, 10), "card": (25, 25, 25), "accent": (250, 204, 21), "text_accent": (0, 0, 0)},
    "Cyberpunk Pink": {"bg": (15, 23, 42), "card": (30, 41, 59), "accent": (236, 72, 153), "text_accent": (255, 255, 255)},
    "Vert Fluorescent": {"bg": (6, 78, 59), "card": (4, 120, 87), "accent": (34, 197, 94), "text_accent": (0, 0, 0)},
    "Minimaliste Sombre": {"bg": (0, 0, 0), "card": (24, 24, 27), "accent": (255, 255, 255), "text_accent": (0, 0, 0)}
}

def draw_hook_frame(hook_text, theme_name):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon TikTok (Jaune & Noir)"])
    img = Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(60, 600), (1020, 1100)], fill=colors["accent"])
    draw.text((100, 750), hook_text, fill=colors["text_accent"])
    return img

def draw_quizz_frame(question, options, reponse_correcte, explication, q_num, total_q, phase="question", timer_sec=5, bg_file=None, theme_name="Néon TikTok (Jaune & Noir)"):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon TikTok (Jaune & Noir)"])
    
    if bg_file:
        img = Image.open(bg_file).convert('RGB').resize((width, height))
    else:
        img = Image.new('RGB', (width, height), color=colors["bg"])
        
    draw = ImageDraw.Draw(img)
    draw.rectangle([(60, 100), (1020, 200)], fill=colors["accent"])
    draw.text((90, 130), f"QUESTION {q_num}/{total_q}", fill=colors["text_accent"])
    draw.text((90, 300), f"Q: {question}", fill="white")
    
    correct_letter = str(reponse_correcte).strip().upper()[0] if reponse_correcte else 'A'
    correct_idx = ord(correct_letter) - 65 if correct_letter in ['A', 'B', 'C', 'D'] else 0
    
    y = 550
    for i, opt in enumerate(options):
        fill_color = (34, 197, 94) if (phase == "reponse" and i == correct_idx) else colors["card"]
        draw.rectangle([(90, y), (990, y + 120)], fill=fill_color, outline=colors["accent"], width=3)
        draw.text((120, y + 40), f"{chr(65+i)}) {opt}", fill="white")
        y += 160
        
    if phase == "reponse":
        draw.rectangle([(80, y + 20), (1000, y + 220)], fill=(15, 23, 42))
        draw.text((100, y + 40), f"Explication :\n{explication}", fill="white")
    else:
        draw.rectangle([(380, y + 20), (700, y + 110)], fill=(225, 29, 72))
        draw.text((430, y + 50), f"00:0{timer_sec}", fill="white")
        
    return img

def draw_language_progressive_frame(mots, current_index, langue, theme_name):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon TikTok (Jaune & Noir)"])
    img = Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(60, 100), (1020, 200)], fill=colors["accent"])
    draw.text((90, 130), f"VOCABULAIRE ({langue.upper()})", fill=colors["text_accent"])
    
    y = 280
    for idx, item in enumerate(mots):
        if idx <= current_index:
            bg_card = colors["accent"] if idx == current_index else colors["card"]
            txt_col = colors["text_accent"] if idx == current_index else "white"
            draw.rectangle([(80, y), (1000, y + 180)], fill=bg_card, outline="white", width=3)
            draw.text((110, y + 30), f"FR: {item['fr']}", fill=txt_col)
            draw.text((110, y + 90), f"TRAD: {item['trad']}", fill=txt_col)
        else:
            draw.rectangle([(80, y), (1000, y + 180)], outline=(51, 65, 85), width=2)
            draw.text((110, y + 70), f"Mot #{idx+1}", fill=(100, 116, 139))
        y += 210
        
    return img

# --- INTERFACE STREAMLIT ---
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

# --- MODULE 1 : QUIZZ ---
with tab1:
    st.header("1. Générateur Quizz Virale")
    hook_input = st.text_input("Accroche (Hook)", "IMPOSSIBLE d'avoir 5/5 sur ce test !")
    
    col1, col2 = st.columns(2)
    with col1:
        voice_fr_code = VOICES_FR[st.selectbox("Voix Off", list(VOICES_FR.keys()))]
    with col2:
        theme_visual_q = st.selectbox("Thème Visuel", list(THEMES.keys()), key="th_q")
        
    mode_q = st.radio("Mode", ["IA Gemini", "Saisie Manuelle"], key="mode_q")
    bg_file = st.file_uploader("Fond 9:16 (Optionnel)", type=["png", "jpg", "jpeg"], key="bg_q")
    
    if mode_q == "IA Gemini":
        theme_q = st.text_input("Thème", "Culture Générale", key="t_q")
        nb_q = st.slider("Questions", 1, 10, 5)
        if st.button("✨ Générer les questions"):
            if not api_key:
                st.error("Entre ta clé API Gemini !")
            else:
                with st.spinner("Génération par l'IA..."):
                    try:
                        prompt = f"Génère {nb_q} questions de quizz sur '{theme_q}'. Format JSON strict: [{{'question': '...', 'options': ['A','B','C','D'], 'reponse_correcte': 'A', 'explication': '...'}}]"
                        model = genai.GenerativeModel(get_working_model())
                        res = model.generate_content(prompt)
                        st.session_state['q_data'] = parse_json_response(res.text)
                        st.success(f"{len(st.session_state['q_data'])} questions générées avec le modèle {get_working_model()} !")
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
        if st.button("🎬 Générer le fichier MP4"):
            with st.spinner("Montage vidéo en cours..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        clips = []
                        total_q = len(st.session_state['q_data'])
                        
                        # Hook
                        h_aud = os.path.join(tmpdir, "h.mp3")
                        h_img = os.path.join(tmpdir, "h.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_input), voice_fr_code).save(h_aud))
                        draw_hook_frame(hook_input, theme_visual_q).save(h_img)
                        a_h = AudioFileClip(h_aud)
                        clips.append(ImageClip(h_img).set_duration(a_h.duration).set_audio(a_h))
                        
                        # Questions + Motivations
                        motivations = ["Bravo ! On continue !", "Super effort ! Question suivante !", "Tu gères, voici la suite !"]
                        for idx, q in enumerate(st.session_state['q_data']):
                            q_aud = os.path.join(tmpdir, f"q_{idx}.mp3")
                            r_aud = os.path.join(tmpdir, f"r_{idx}.mp3")
                            q_img = os.path.join(tmpdir, f"q_{idx}.png")
                            r_img = os.path.join(tmpdir, f"r_{idx}.png")
                            
                            t_q = clean_text_for_tts(f"Question {idx+1}. {q['question']}. A: {q['options'][0]}. B: {q['options'][1]}. C: {q['options'][2]}. D: {q['options'][3]}.")
                            t_r = clean_text_for_tts(f"La bonne réponse est l'option {q['reponse_correcte']}. {q['explication']}. {motivations[idx % len(motivations)]}")
                            
                            run_async(edge_tts.Communicate(t_q, voice_fr_code).save(q_aud))
                            run_async(edge_tts.Communicate(t_r, voice_fr_code).save(r_aud))
                            
                            draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], idx+1, total_q, "question", 5, bg_file, theme_visual_q).save(q_img)
                            draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], idx+1, total_q, "reponse", 0, bg_file, theme_visual_q).save(r_img)
                            
                            a_q = AudioFileClip(q_aud)
                            a_r = AudioFileClip(r_aud)
                            
                            clip_q = ImageClip(q_img).set_duration(a_q.duration).set_audio(a_q)
                            
                            t_clips = []
                            for sec in range(5, 0, -1):
                                t_img = os.path.join(tmpdir, f"t_{idx}_{sec}.png")
                                draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], idx+1, total_q, "question", sec, bg_file, theme_visual_q).save(t_img)
                                t_clips.append(ImageClip(t_img).set_duration(1))
                                
                            clip_r = ImageClip(r_img).set_duration(a_r.duration).set_audio(a_r)
                            clips.extend([clip_q] + t_clips + [clip_r])
                            
                        # Outro / CTA
                        c_aud = os.path.join(tmpdir, "c.mp3")
                        c_img = os.path.join(tmpdir, "c.png")
                        run_async(edge_tts.Communicate("Écris ton score en commentaire et abonne-toi !", voice_fr_code).save(c_aud))
                        draw_hook_frame("QUEL EST TON SCORE ?\nÉcris-le en commentaire ! 💬", theme_visual_q).save(c_img)
                        a_c = AudioFileClip(c_aud)
                        clips.append(ImageClip(c_img).set_duration(a_c.duration).set_audio(a_c))
                        
                        final_v = concatenate_videoclips(clips, method="compose")
                        out_mp4 = os.path.join(tmpdir, "quizz_final.mp4")
                        final_v.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger le MP4", data=f.read(), file_name="quizz_viral.mp4", mime="video/mp4")
                        st.success("✅ Vidéo Quizz générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")

# --- MODULE 2 : LANGUES ---
with tab2:
    st.header("2. Générateur Fiche Vocabulaire")
    hook_l_input = st.text_input("Accroche", "Tu prononces mal ces mots ! Vérifions ensemble.")
    
    col1, col2 = st.columns(2)
    with col1:
        langue_c = st.selectbox("Langue cible", ["Anglais", "Espagnol", "Arabe", "Allemand", "Italien"])
    with col2:
        voice_t_code = VOICES_MAP[langue_c][st.selectbox("Voix Traduction", list(VOICES_MAP[langue_c].keys()))]
        
    theme_visual_l = st.selectbox("Thème Visuel", list(THEMES.keys()), key="th_l")
    mode_l = st.radio("Mode Vocabulaire", ["IA Gemini", "Saisie Manuelle"], key="mode_l")
    
    if mode_l == "IA Gemini":
        theme_l = st.text_input("Thème", "Voyage", key="t_l")
        nb_m = st.slider("Nombre de mots", 3, 8, 6)
        if st.button("✨ Générer les mots"):
            if not api_key:
                st.error("Entre ta clé API !")
            else:
                with st.spinner("Génération des mots..."):
                    try:
                        prompt = f"Génère {nb_m} mots avec traduction en {langue_c}. Format JSON strict: [{{'fr': 'Bonjour', 'trad': 'Hello'}}, ...]"
                        model = genai.GenerativeModel(get_working_model())
                        res = model.generate_content(prompt)
                        st.session_state['l_data'] = parse_json_response(res.text)
                        st.success(f"{len(st.session_state['l_data'])} mots générés avec le modèle {get_working_model()} !")
                    except Exception as e:
                        st.error(f"Erreur IA : {e}")
    else:
        num_m = st.number_input("Nombre de mots à saisir", 1, 8, 6)
        c_m = []
        for i in range(int(num_m)):
            col_a, col_b = st.columns(2)
            with col_a:
                fr_t = st.text_input(f"Français #{i+1}", key=f"fr_{i}")
            with col_b:
                tr_t = st.text_input(f"Traduction #{i+1}", key=f"tr_{i}")
            c_m.append({"fr": fr_t, "trad": tr_t})
        if st.button("💾 Valider les mots"):
            st.session_state['l_data'] = c_m
            st.success("Mots enregistrés !")

    if 'l_data' in st.session_state and st.session_state['l_data']:
        if st.button("🎬 Générer le fichier MP4 Vocabulaire"):
            with st.spinner("Montage vidéo en cours..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        w_clips = []
                        mots_l = st.session_state['l_data']
                        
                        in_aud = os.path.join(tmpdir, "in.mp3")
                        in_img = os.path.join(tmpdir, "in.png")
                        run_async(edge_tts.Communicate(clean_text_for_tts(hook_l_input), "fr-FR-HenriNeural").save(in_aud))
                        draw_hook_frame(hook_l_input, theme_visual_l).save(in_img)
                        a_in = AudioFileClip(in_aud)
                        w_clips.append(ImageClip(in_img).set_duration(a_in.duration).set_audio(a_in))
                        
                        for idx, item in enumerate(mots_l):
                            fr_aud = os.path.join(tmpdir, f"fr_{idx}.mp3")
                            tr_aud = os.path.join(tmpdir, f"tr_{idx}.mp3")
                            w_img = os.path.join(tmpdir, f"w_{idx}.png")
                            
                            t_fr = clean_text_for_tts(item['fr'])
                            t_tr = item['trad'].strip() if langue_c == "Arabe" else clean_text_for_tts(item['trad'])
                            
                            run_async(edge_tts.Communicate(t_fr, "fr-FR-HenriNeural").save(fr_aud))
                            run_async(edge_tts.Communicate(t_tr, voice_t_code).save(tr_aud))
                            
                            draw_language_progressive_frame(mots_l, idx, langue_c, theme_visual_l).save(w_img)
                            
                            a_fr = AudioFileClip(fr_aud)
                            a_tr = AudioFileClip(tr_aud)
                            
                            c_fr = ImageClip(w_img).set_duration(a_fr.duration).set_audio(a_fr)
                            c_tr = ImageClip(w_img).set_duration(a_tr.duration + 0.5).set_audio(a_tr)
                            w_clips.extend([c_fr, c_tr])
                            
                        out_aud = os.path.join(tmpdir, "out.mp3")
                        out_img = os.path.join(tmpdir, "out.png")
                        run_async(edge_tts.Communicate("Enregistre cette vidéo et abonne-toi !", "fr-FR-HenriNeural").save(out_aud))
                        draw_hook_frame("ENREGISTRE LA VIDÉO ! 📌\nEt abonne-toi !", theme_visual_l).save(out_img)
                        a_out = AudioFileClip(out_aud)
                        w_clips.append(ImageClip(out_img).set_duration(a_out.duration).set_audio(a_out))
                        
                        final_v = concatenate_videoclips(w_clips, method="compose")
                        out_mp4 = os.path.join(tmpdir, "langue_final.mp4")
                        final_v.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger le MP4", data=f.read(), file_name="vocabulaire_viral.mp4", mime="video/mp4")
                        st.success("✅ Vidéo Vocabulaire générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur de génération : {e}")
