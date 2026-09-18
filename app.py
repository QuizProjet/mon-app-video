import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import tempfile
import uuid
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Studio TikTok & Shorts Viral Pro", layout="wide")
st.title("🚀 Studio TikTok Pro : Générateur de Vidéos Virales (.MP4)")

# --- UTILITAIRES ---
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

THEMES = {
    "Néon TikTok (Jaune & Noir)": {"bg": (10, 10, 10), "card": (25, 25, 25), "accent": (250, 204, 21), "text_accent": (0, 0, 0), "header": (236, 72, 153)},
    "Cyberpunk Pink": {"bg": (15, 23, 42), "card": (30, 41, 59), "accent": (236, 72, 153), "text_accent": (255, 255, 255), "header": (139, 92, 246)},
    "Vert Fluorescent": {"bg": (6, 78, 59), "card": (4, 120, 87), "accent": (34, 197, 94), "text_accent": (0, 0, 0), "header": (16, 185, 129)}
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
    draw.text((90, 130), f"🔥 QUESTION {q_num}/{total_q}", fill=colors["text_accent"])
    
    draw.text((90, 300), f"Q: {question}", fill="white")
    
    correct_letter = str(reponse_correcte).strip().upper()[0]
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
        draw.text((430, y + 50), f"⏱️ 00:0{timer_sec}", fill="white")
        
    return img

def draw_language_progressive_frame(mots, current_index, langue, theme_name):
    width, height = 1080, 1920
    colors = THEMES.get(theme_name, THEMES["Néon TikTok (Jaune & Noir)"])
    img = Image.new('RGB', (width, height), color=colors["bg"])
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(60, 100), (1020, 200)], fill=colors["accent"])
    draw.text((90, 130), f"💡 VOCABULAIRE ({langue.upper()})", fill=colors["text_accent"])
    
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

# --- INTERFACE ---
api_key = st.sidebar.text_input("Clé API Gemini (Facultatif si saisie manuelle)", type="password")
if api_key:
    genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["🧠 Quizz TikTok Ultra-Viral MP4", "🗣️ Fiche Langue Ultra-Virale MP4"])

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
    st.header("1. Quizz TikTok Ultra-Viral")
    
    hook_input = st.text_input("Phrase d'accroche (Hook)", "IMPOSSIBLE d'avoir 5/5 sur ce test !")
    
    col_a, col_b = st.columns(2)
    with col_a:
        voice_fr_choice = st.selectbox("Voix Off", list(VOICES_FR.keys()))
        voice_fr_code = VOICES_FR[voice_fr_choice]
    with col_b:
        theme_visual_q = st.selectbox("Thème Visuel Fluo", list(THEMES.keys()), key="th_q")
        
    mode_q = st.radio("Source des questions", ["Génération automatique par IA", "Saisie Manuelle"], key="mode_q")
    bg_file = st.file_uploader("Image de fond personnalisée (9:16)", type=["png", "jpg", "jpeg"], key="bg_q")
    
    if mode_q == "Génération automatique par IA":
        theme_q = st.text_input("Thème du Quizz", "Culture Générale", key="t_q")
        nb_q = st.slider("Nombre de questions", 1, 10, 5)
        
        if st.button("✨ Générer les questions via l'IA"):
            if not api_key:
                st.error("Clé API requise pour la génération IA !")
            else:
                with st.spinner("Génération des questions..."):
                    prompt = f"Génère une liste de {nb_q} questions de quizz sur le thème '{theme_q}'. Réponds au format JSON strict : [{{'question': '...', 'options': ['A','B','C','D'], 'reponse_correcte': 'A', 'explication': '...'}}]"
                    model = genai.GenerativeModel(get_working_model())
                    res = model.generate_content(prompt)
                    st.session_state['q_data'] = parse_json_response(res.text)
                    st.success(f"{len(st.session_state['q_data'])} questions générées !")
    else:
        num_custom = st.number_input("Nombre de questions à saisir", 1, 10, 5)
        custom_list = []
        for i in range(int(num_custom)):
            st.subheader(f"Question {i+1}")
            q_txt = st.text_input(f"Question {i+1}", key=f"q_{i}")
            opt_a = st.text_input(f"Option A", key=f"opt_a_{i}")
            opt_b = st.text_input(f"Option B", key=f"opt_b_{i}")
            opt_c = st.text_input(f"Option C", key=f"opt_c_{i}")
            opt_d = st.text_input(f"Option D", key=f"opt_d_{i}")
            rep = st.selectbox(f"Bonne réponse", ["A", "B", "C", "D"], key=f"rep_{i}")
            exp = st.text_input(f"Explication", key=f"exp_{i}")
            custom_list.append({"question": q_txt, "options": [opt_a, opt_b, opt_c, opt_d], "reponse_correcte": rep, "explication": exp})
        if st.button("💾 Valider les questions"):
            st.session_state['q_data'] = custom_list
            st.success("Questions enregistrées !")

    if 'q_data' in st.session_state and st.session_state['q_data']:
        st.write(f"📋 **{len(st.session_state['q_data'])} questions prêtes.**")
        
        if st.button("🎬 Générer la Vidéo TikTok Virale (.MP4)"):
            with st.spinner("Génération de la vidéo en cours..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        all_clips = []
                        total_q = len(st.session_state['q_data'])
                        
                        # 1. Hook
                        hook_audio_p = os.path.join(tmpdir, "hook.mp3")
                        hook_img_p = os.path.join(tmpdir, "f_hook.png")
                        async def gen_hook():
                            c = edge_tts.Communicate(clean_text_for_tts(hook_input), voice_fr_code)
                            await c.save(hook_audio_p)
                        asyncio.run(gen_hook())
                        
                        draw_hook_frame(hook_input, theme_visual_q).save(hook_img_p)
                        a_hook = AudioFileClip(hook_audio_p)
                        all_clips.append(ImageClip(hook_img_p).set_duration(a_hook.duration).set_audio(a_hook))
                        
                        # 2. Questions
                        motivations = ["Bravo ! On continue !", "Super effort ! Question suivante !", "Tu gères, voici la suite !"]
                        for idx, q in enumerate(st.session_state['q_data']):
                            q_num = idx + 1
                            txt_q = clean_text_for_tts(f"Question {q_num}. {q['question']}. A: {q['options'][0]}. B: {q['options'][1]}. C: {q['options'][2]}. D: {q['options'][3]}.")
                            txt_r = clean_text_for_tts(f"La bonne réponse est l'option {q['reponse_correcte']}! {q['explication']}. {motivations[idx % len(motivations)]}")
                            
                            p_q_aud = os.path.join(tmpdir, f"q_{idx}.mp3")
                            p_r_aud = os.path.join(tmpdir, f"r_{idx}.mp3")
                            p_q_img = os.path.join(tmpdir, f"fq_{idx}.png")
                            p_r_img = os.path.join(tmpdir, f"fr_{idx}.png")
                            
                            async def gen_auds():
                                await edge_tts.Communicate(txt_q, voice_fr_code).save(p_q_aud)
                                await edge_tts.Communicate(txt_r, voice_fr_code).save(p_r_aud)
                            asyncio.run(gen_auds())
                            
                            draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], q_num, total_q, "question", 5, bg_file, theme_visual_q).save(p_q_img)
                            draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], q_num, total_q, "reponse", 0, bg_file, theme_visual_q).save(p_r_img)
                            
                            aud_q = AudioFileClip(p_q_aud)
                            aud_r = AudioFileClip(p_r_aud)
                            
                            clip_q = ImageClip(p_q_img).set_duration(aud_q.duration).set_audio(aud_q)
                            
                            timer_clips = []
                            for sec in range(5, 0, -1):
                                p_t_img = os.path.join(tmpdir, f"ft_{idx}_{sec}.png")
                                draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], q_num, total_q, "question", sec, bg_file, theme_visual_q).save(p_t_img)
                                timer_clips.append(ImageClip(p_t_img).set_duration(1))
                                
                            clip_r = ImageClip(p_r_img).set_duration(aud_r.duration).set_audio(aud_r)
                            all_clips.extend([clip_q] + timer_clips + [clip_r])
                            
                        # 3. Outro CTA
                        cta_txt = "Écris ton score sur 5 en commentaire et abonne-toi !"
                        p_cta_aud = os.path.join(tmpdir, "cta.mp3")
                        p_cta_img = os.path.join(tmpdir, "f_cta.png")
                        async def gen_cta():
                            await edge_tts.Communicate(cta_txt, voice_fr_code).save(p_cta_aud)
                        asyncio.run(gen_cta())
                        
                        draw_hook_frame("QUEL EST TON SCORE ?\nÉcris-le en commentaire ! 💬", theme_visual_q).save(p_cta_img)
                        a_cta = AudioFileClip(p_cta_aud)
                        all_clips.append(ImageClip(p_cta_img).set_duration(a_cta.duration).set_audio(a_cta))
                        
                        # Compilation finale
                        final_v = concatenate_videoclips(all_clips, method="compose")
                        out_mp4 = os.path.join(tmpdir, "quizz_final.mp4")
                        final_v.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        with open(out_mp4, "rb") as f:
                            st.download_button("📥 Télécharger la vidéo TikTok Virale MP4", data=f.read(), file_name="quizz_viral.mp4", mime="video/mp4")
                        st.success("✅ Vidéo générée avec succès !")
                except Exception as e:
                    st.error(f"Détails de l'erreur : {e}")

# ==================== MODULE 2 : LANGUES ====================
with tab2:
    st.header("2. Fiche Langue Ultra-Virale")
    
    hook_lang_input = st.text_input("Accroche Langues", "Tu prononces mal ces 6 mots ! Vérifions ensemble.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        langue_choisie = st.selectbox("Langue cible", ["Anglais", "Espagnol", "Arabe", "Allemand", "Italien"])
    with col_l2:
        voice_target_choice = st.selectbox("Voix de la traduction", list(VOICES_MAP[langue_choisie].keys()))
        voice_target_code = VOICES_MAP[langue_choisie][voice_target_choice]
        
    theme_visual_l = st.selectbox("Thème Visuel Fluo", list(THEMES.keys()), key="th_l")
    mode_l = st.radio("Source du vocabulaire", ["Génération automatique par IA", "Saisie Manuelle"], key="mode_l")
    
    if mode_l == "Génération automatique par IA":
        theme_l = st.text_input("Thème du vocabulaire", "Voyage et Restaurant", key="t_l")
        nb_mots = st.slider("Nombre de mots", 3, 8, 6)
        if st.button("✨ Générer le vocabulaire par IA"):
            if not api_key:
                st.error("Clé API requise pour l'IA !")
            else:
                with st.spinner("Génération des mots..."):
                    prompt = f"Génère {nb_mots} mots ou phrases clés sur le thème '{theme_l}' avec la traduction en {langue_choisie}. Réponds au format JSON strict : [{{'fr': 'Bonjour', 'trad': 'Hello'}}, ...]"
                    model = genai.GenerativeModel(get_working_model())
                    res = model.generate_content(prompt)
                    st.session_state['l_data'] = parse_json_response(res.text)
                    st.success(f"{len(st.session_state['l_data'])} mots générés !")
    else:
        num_m = st.number_input("Nombre de mots à saisir", 1, 8, 6)
        custom_m = []
        for i in range(int(num_m)):
            col1, col2 = st.columns(2)
            with col1:
                fr_txt = st.text_input(f"Texte Français #{i+1}", key=f"fr_{i}")
            with col2:
                tr_txt = st.text_input(f"Traduction ({langue_choisie}) #{i+1}", key=f"tr_{i}")
            custom_m.append({"fr": fr_txt, "trad": tr_txt})
        if st.button("💾 Valider la liste de mots"):
            st.session_state['l_data'] = custom_m
            st.success("Mots enregistrés !")

    if 'l_data' in st.session_state and st.session_state['l_data']:
        st.write(f"📋 **{len(st.session_state['l_data'])} mots prêts.**")
        
        if st.button("🎬 Générer la Vidéo Vocabulaire MP4"):
            with st.spinner("Génération de la vidéo en cours..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        word_clips = []
                        mots_l = st.session_state['l_data']
                        
                        # 1. Hook
                        p_intro_aud = os.path.join(tmpdir, "intro_l.mp3")
                        p_intro_img = os.path.join(tmpdir, "f_intro_l.png")
                        async def gen_lang_hook():
                            await edge_tts.Communicate(clean_text_for_tts(hook_lang_input), "fr-FR-HenriNeural").save(p_intro_aud)
                        asyncio.run(gen_lang_hook())
                        
                        draw_hook_frame(hook_lang_input, theme_visual_l).save(p_intro_img)
                        a_intro = AudioFileClip(p_intro_aud)
                        word_clips.append(ImageClip(p_intro_img).set_duration(a_intro.duration).set_audio(a_intro))
                        
                        # 2. Mots
                        for idx, item in enumerate(mots_l):
                            t_fr = clean_text_for_tts(item['fr'])
                            t_tr = item['trad'].strip() if langue_choisie == "Arabe" else clean_text_for_tts(item['trad'])
                            
                            p_fr_aud = os.path.join(tmpdir, f"l_fr_{idx}.mp3")
                            p_tr_aud = os.path.join(tmpdir, f"l_tr_{idx}.mp3")
                            p_w_img = os.path.join(tmpdir, f"fl_w_{idx}.png")
                            
                            async def gen_w_auds():
                                await edge_tts.Communicate(t_fr, "fr-FR-HenriNeural").save(p_fr_aud)
                                await edge_tts.Communicate(t_tr, voice_target_code).save(p_tr_aud)
                            asyncio.run(gen_w_auds())
                            
                            draw_language_progressive_frame(mots_l, idx, langue_choisie, theme_visual_l).save(p_w_img)
                            
                            a_fr = AudioFileClip(p_fr_aud)
                            a_tr = AudioFileClip(p_tr_aud)
                            
                            clip_fr = ImageClip(p_w_img).set_duration(a_fr.duration).set_audio(a_fr)
                            clip_tr = ImageClip(p_w_img).set_duration(a_tr.duration + 0.5).set_audio(a_tr)
                            
                            word_clips.extend([clip_fr, clip_tr])
                            
                        # 3. Outro CTA
                        cta_lang_txt = "Enregistre cette vidéo et abonne-toi !"
                        p_cta_l_aud = os.path.join(tmpdir, "cta_l.mp3")
                        p_cta_l_img = os.path.join(tmpdir, "f_cta_l.png")
                        async def gen_lang_cta():
                            await edge_tts.Communicate(cta_lang_txt, "fr-FR-HenriNeural").save(p_cta_l_aud)
                        asyncio.run(gen_lang_cta())
                        
                        draw_hook_frame("ENREGISTRE LA VIDÉO ! 📌\nEt abonne-toi pour progresser !", theme_visual_l).save(p_cta_l_img)
                        a_cta_l = AudioFileClip(p_cta_l_aud)
                        word_clips.append(ImageClip(p_cta_l_img).set_duration(a_cta_l.duration).set_audio(a_cta_l))
                        
                        final_v = concatenate_videoclips(word_clips, method="compose")
                        out_lang_mp4 = os.path.join(tmpdir, "langue_final.mp4")
                        final_v.write_videofile(out_lang_mp4, fps=24, codec="libx264", audio_codec="aac", logger=None)
                        
                        with open(out_lang_mp4, "rb") as f:
                            st.download_button("📥 Télécharger la vidéo Fiche MP4", data=f.read(), file_name="vocabulaire_viral.mp4", mime="video/mp4")
                        st.success("✅ Vidéo générée avec succès !")
                except Exception as e:
                    st.error(f"Détails de l'erreur : {e}")
