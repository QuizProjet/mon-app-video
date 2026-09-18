import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Studio Créateur TikTok & Shorts Pro", layout="wide")
st.title("🎬 Studio de Création de Vidéos Réseaux Sociaux (.MP4)")

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

# --- DESSIN QUIZZ ---
def draw_quizz_frame(question, options, reponse_correcte, explication, q_num, total_q, phase="question", timer_sec=5, bg_file=None):
    width, height = 1080, 1920
    if bg_file:
        img = Image.open(bg_file).convert('RGB').resize((width, height))
    else:
        img = Image.new('RGB', (width, height), color=(15, 23, 42))
        
    draw = ImageDraw.Draw(img)
    
    # Header Motivation / Progression
    draw.rectangle([(60, 100), (1020, 200)], fill=(225, 29, 72))
    draw.text((90, 130), f"🔥 QUESTION {q_num}/{total_q} - TESTE TES CONNAISSANCES !", fill="white")
    
    # Question
    draw.text((90, 320), f"Q: {question}", fill="white")
    
    correct_letter = str(reponse_correcte).strip().upper()[0]
    correct_idx = ord(correct_letter) - 65 if correct_letter in ['A', 'B', 'C', 'D'] else 0
    
    y = 550
    for i, opt in enumerate(options):
        fill_color = (34, 197, 94) if (phase == "reponse" and i == correct_idx) else (30, 41, 59)
        draw.rectangle([(90, y), (990, y + 110)], fill=fill_color, outline="white", width=3)
        draw.text((120, y + 35), f"{chr(65+i)}) {opt}", fill="white")
        y += 150
        
    if phase == "reponse":
        draw.rectangle([(80, y + 10), (1000, y + 220)], fill=(15, 23, 42))
        draw.text((100, y + 40), f"Explication :\n{explication}", fill="white")
    else:
        draw.rectangle([(380, y + 20), (700, y + 110)], fill=(225, 29, 72))
        draw.text((430, y + 50), f"⏱️ 00:0{timer_sec}", fill="white")
        
    return img

# --- DESSIN LANGUES ---
def draw_language_progressive_frame(mots, current_index, langue):
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(60, 100), (1020, 200)], fill=(225, 29, 72))
    draw.text((90, 130), f"💡 APPRENDS LE VOCABULAIRE ({langue.upper()}) !", fill="white")
    
    y = 280
    for idx, item in enumerate(mots):
        if idx <= current_index:
            bg_card = (236, 72, 153) if idx == current_index else (30, 41, 59)
            draw.rectangle([(80, y), (1000, y + 180)], fill=bg_card, outline="white", width=3)
            draw.text((110, y + 30), f"FR: {item['fr']}", fill="white")
            draw.text((110, y + 90), f"TRAD: {item['trad']}", fill="white" if idx == current_index else (244, 63, 94))
        else:
            draw.rectangle([(80, y), (1000, y + 180)], outline=(51, 65, 85), width=2)
            draw.text((110, y + 70), f"Mot #{idx+1}", fill=(100, 116, 139))
        y += 210
        
    return img

# --- INTERFACE PRINCIPALE ---
api_key = st.sidebar.text_input("Clé API Gemini (Facultatif si saisie manuelle)", type="password")
if api_key:
    genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["🧠 Quizz Multi-Questions MP4", "🗣️ Fiche Langue Multi-Mots MP4"])

# ==================== MODULE 1 : QUIZZ ====================
with tab1:
    st.header("1. Créateur de Quizz Compilations (jusqu'à 10+ questions)")
    
    mode_q = st.radio("Source des questions", ["Génération automatique par IA", "Saisie Manuelle"], key="mode_q")
    questions_data = []
    bg_file = st.file_uploader("Image de fond personnalisée (9:16)", type=["png", "jpg", "jpeg"], key="bg_q")
    
    if mode_q == "Génération automatique par IA":
        theme_q = st.text_input("Thème du Quizz", "Culture Générale", key="t_q")
        nb_q = st.slider("Nombre de questions", 1, 10, 3)
        
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
        num_custom = st.number_input("Nombre de questions à saisir", 1, 10, 2)
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
        st.write(f"📋 **{len(st.session_state['q_data'])} questions prêtes pour le montage vidéo.**")
        
        if st.button("🎬 Générer la Vidéo Quizz Compilée (.MP4)"):
            with st.spinner("Montage de la vidéo Quizz multi-questions avec phrases de motivation..."):
                try:
                    all_clips = []
                    total_q = len(st.session_state['q_data'])
                    motivations = ["Bravo ! On passe à la question suivante !", "Super effort ! Question suivante !", "Continue comme ça, voici la suite !", "Tu gères ! Question suivante !"]
                    
                    for idx, q in enumerate(st.session_state['q_data']):
                        q_num = idx + 1
                        
                        txt_q = clean_text_for_tts(f"Question {q_num} sur {total_q}. {q['question']}. Option A: {q['options'][0]}. Option B: {q['options'][1]}. Option C: {q['options'][2]}. Option D: {q['options'][3]}. Réfléchis bien !")
                        txt_r = clean_text_for_tts(f"La bonne réponse est l'option {q['reponse_correcte']}! {q['explication']}. {motivations[idx % len(motivations)]}")
                        
                        async def gen_q_audios():
                            c1 = edge_tts.Communicate(txt_q, "fr-FR-HenriNeural")
                            await c1.save(f"part_q_{idx}.mp3")
                            c2 = edge_tts.Communicate(txt_r, "fr-FR-HenriNeural")
                            await c2.save(f"part_r_{idx}.mp3")
                        asyncio.run(gen_q_audios())
                        
                        draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], q_num, total_q, "question", 5, bg_file).save(f"fq_{idx}.png")
                        draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], q_num, total_q, "reponse", 0, bg_file).save(f"fr_{idx}.png")
                        
                        aud_q = AudioFileClip(f"part_q_{idx}.mp3")
                        aud_r = AudioFileClip(f"part_r_{idx}.mp3")
                        
                        clip_q = ImageClip(f"fq_{idx}.png").set_duration(aud_q.duration).set_audio(aud_q)
                        
                        timer_clips = []
                        for sec in range(5, 0, -1):
                            draw_quizz_frame(q['question'], q['options'], q['reponse_correcte'], q['explication'], q_num, total_q, "question", sec, bg_file).save(f"ft_{idx}_{sec}.png")
                            timer_clips.append(ImageClip(f"ft_{idx}_{sec}.png").set_duration(1))
                            
                        clip_r = ImageClip(f"fr_{idx}.png").set_duration(aud_r.duration).set_audio(aud_r)
                        
                        all_clips.extend([clip_q] + timer_clips + [clip_r])
                        
                    final_v = concatenate_videoclips(all_clips, method="compose")
                    out_mp4 = "quizz_compilation.mp4"
                    final_v.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac")
                    
                    st.video(out_mp4)
                    with open(out_mp4, "rb") as f:
                        st.download_button("📥 Télécharger la compilation Quizz MP4", data=f, file_name="quizz_compilation.mp4", mime="video/mp4")
                except Exception as e:
                    st.error(f"Erreur : {e}")

# ==================== MODULE 2 : LANGUES ====================
with tab2:
    st.header("2. Créateur de Fiche Langue Multi-Mots (5 Langues au choix)")
    
    # Prise en charge des 5 langues dont l'Arabe
    langue_choisie = st.selectbox("Sélectionne la langue cible", ["Anglais", "Espagnol", "Arabe", "Allemand", "Italien"])
    voice_map = {
        "Anglais": "en-US-EmmaNeural",
        "Espagnol": "es-ES-AlvaroNeural",
        "Arabe": "ar-SA-HamedNeural",
        "Allemand": "de-DE-KillianNeural",
        "Italien": "it-IT-DiegoNeural"
    }
    
    mode_l = st.radio("Source du vocabulaire", ["Génération automatique par IA", "Saisie Manuelle de mes mots/phrases"], key="mode_l")
    
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
        num_m = st.number_input("Nombre de mots/phrases à saisir", 1, 8, 4)
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
        st.write(f"📋 **{len(st.session_state['l_data'])} mots/phrases prêts pour le montage vidéo.**")
        
        if st.button("🎬 Générer la Vidéo Vocabulaire MP4"):
            with st.spinner("Création de la séquence mot par mot..."):
                try:
                    word_clips = []
                    mots_l = st.session_state['l_data']
                    
                    # Intro
                    intro_txt = clean_text_for_tts(f"Voici le vocabulaire essentiel en {langue_choisie} ! C'est parti !")
                    async def gen_intro():
                        c = edge_tts.Communicate(intro_txt, "fr-FR-HenriNeural")
                        await c.save("intro_l.mp3")
                    asyncio.run(gen_intro())
                    
                    draw_language_progressive_frame(mots_l, -1, langue_choisie).save("f_intro_l.png")
                    aud_intro = AudioFileClip("intro_l.mp3")
                    word_clips.append(ImageClip("f_intro_l.png").set_duration(aud_intro.duration).set_audio(aud_intro))
                    
                    # Boucle mots
                    for idx, item in enumerate(mots_l):
                        t_fr = clean_text_for_tts(item['fr'])
                        
                        # Pour l'arabe, préserver la chaîne UTF-8 pour la voix off
                        t_tr = item['trad'].strip() if langue_choisie == "Arabe" else clean_text_for_tts(item['trad'])
                        
                        target_voice = voice_map[langue_choisie]
                        
                        async def gen_w_audios():
                            c_fr = edge_tts.Communicate(t_fr, "fr-FR-HenriNeural")
                            await c_fr.save(f"l_fr_{idx}.mp3")
                            c_tr = edge_tts.Communicate(t_tr, target_voice)
                            await c_tr.save(f"l_tr_{idx}.mp3")
                        asyncio.run(gen_w_audios())
                        
                        draw_language_progressive_frame(mots_l, idx, langue_choisie).save(f"fl_w_{idx}.png")
                        
                        a_fr = AudioFileClip(f"l_fr_{idx}.mp3")
                        a_tr = AudioFileClip(f"l_tr_{idx}.mp3")
                        
                        clip_fr = ImageClip(f"fl_w_{idx}.png").set_duration(a_fr.duration).set_audio(a_fr)
                        clip_tr = ImageClip(f"fl_w_{idx}.png").set_duration(a_tr.duration + 0.5).set_audio(a_tr)
                        
                        word_clips.extend([clip_fr, clip_tr])
                        
                    final_lang_v = concatenate_videoclips(word_clips, method="compose")
                    out_lang_mp4 = "vocabulaire_multi_langue.mp4"
                    final_lang_v.write_videofile(out_lang_mp4, fps=24, codec="libx264", audio_codec="aac")
                    
                    st.video(out_lang_mp4)
                    with open(out_lang_mp4, "rb") as f:
                        st.download_button("📥 Télécharger la vidéo Fiche MP4", data=f, file_name="vocabulaire_tiktok.mp4", mime="video/mp4")
                except Exception as e:
                    st.error(f"Erreur : {e}")
