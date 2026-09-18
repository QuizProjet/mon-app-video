import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Générateur TikTok Pro", layout="wide")
st.title("🎬 Générateur de Vidéos TikTok & Shorts Synchronisées (.MP4)")

# --- UTILITAIRES TTS & JSON ---
def clean_text_for_tts(text):
    return re.sub(r'[^\w\s,.?!:\'\-]', '', text).strip()

def parse_json_response(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
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

# --- GENERATEUR VISUEL QUIZZ ---
def draw_quizz_frame(data, phase="question", timer_sec=5, bg_file=None):
    width, height = 1080, 1920
    if bg_file:
        img = Image.open(bg_file).convert('RGB').resize((width, height))
    else:
        img = Image.new('RGB', (width, height), color=(15, 23, 42))
        
    draw = ImageDraw.Draw(img)
    
    # Accroche
    draw.rectangle([(60, 100), (1020, 200)], fill=(225, 29, 72))
    draw.text((90, 130), "🔥 TESTE TES CONNAISSANCES !", fill="white")
    
    # En-tête Thème
    draw.rectangle([(80, 230), (1000, 330)], fill=(79, 70, 229))
    draw.text((120, 260), "QUIZZ DU JOUR", fill="white")
    
    # Question
    draw.text((90, 380), f"Q: {data['question']}", fill="white")
    
    # Options
    correct_letter = str(data.get('reponse_correcte', 'A')).strip().upper()[0]
    correct_idx = ord(correct_letter) - 65 if correct_letter in ['A', 'B', 'C', 'D'] else 0
    
    y = 600
    for i, opt in enumerate(data['options']):
        fill_color = (34, 197, 94) if (phase == "reponse" and i == correct_idx) else (30, 41, 59)
        draw.rectangle([(90, y), (990, y + 120)], fill=fill_color, outline="white", width=3)
        draw.text((120, y + 40), f"{chr(65+i)}) {opt}", fill="white")
        y += 160
        
    if phase == "reponse":
        draw.rectangle([(80, y + 20), (1000, y + 220)], fill=(15, 23, 42))
        draw.text((100, y + 50), f"Explication :\n{data['explication']}", fill="white")
    else:
        draw.rectangle([(380, y + 30), (700, y + 120)], fill=(225, 29, 72))
        draw.text((430, y + 60), f"⏱️ 00:0{timer_sec}", fill="white")
        
    return img

# --- GENERATEUR VISUEL LANGUES ---
def draw_language_frame(mots, langue):
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(60, 100), (1020, 200)], fill=(225, 29, 72))
    draw.text((90, 130), "💡 APPRENDS CE VOCABULAIRE !", fill="white")
    
    draw.rectangle([(80, 230), (1000, 330)], fill=(236, 72, 153))
    draw.text((120, 260), f"6 MOTS EN {langue.upper()}", fill="white")
    
    y = 380
    for item in mots[:6]:
        draw.rectangle([(80, y), (1000, y + 200)], fill=(30, 41, 59), outline="white", width=2)
        draw.text((110, y + 40), f"FR: {item['fr']}", fill="white")
        draw.text((110, y + 110), f"TRAD: {item['en']}", fill=(244, 63, 94))
        y += 240
        
    return img

# --- INTERFACE PRINCIPALE ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")

if api_key:
    genai.configure(api_key=api_key)
    tab1, tab2 = st.tabs(["🧠 Quizz TikTok (.MP4)", "🗣️ Fiche 6 Mots (.MP4)"])
    
    # --- MODULE 1 : QUIZZ ---
    with tab1:
        st.header("Créer un Quizz TikTok Interactif")
        theme = st.text_input("Thème du Quizz", "Culture Générale")
        bg_file = st.file_uploader("Image de fond optionnelle (9:16)", type=["png", "jpg", "jpeg"])
        
        if st.button("🎬 Générer le Quizz MP4"):
            with st.spinner("Génération du Quizz et montage MP4 en cours..."):
                try:
                    prompt = f"Génère une question de quizz sur '{theme}'. Réponds au format JSON strict : {{'question': '...', 'options': ['...','...','...','...'], 'reponse_correcte': 'A', 'explication': '...'}}"
                    model = genai.GenerativeModel(get_working_model())
                    response = model.generate_content(prompt)
                    data = parse_json_response(response.text)
                    
                    # 1. Audios séparés pour caler la vidéo
                    txt_q = clean_text_for_tts(f"Auras-tu 10 sur 10 ? {data['question']}. Option A: {data['options'][0]}. Option B: {data['options'][1]}. Option C: {data['options'][2]}. Option D: {data['options'][3]}. Réfléchis bien !")
                    txt_r = clean_text_for_tts(f"La bonne réponse est l'option {data['reponse_correcte']}! {data['explication']}")
                    
                    async def gen_audios():
                        c1 = edge_tts.Communicate(txt_q, "fr-FR-HenriNeural")
                        await c1.save("part_q.mp3")
                        c2 = edge_tts.Communicate(txt_r, "fr-FR-HenriNeural")
                        await c2.save("part_r.mp3")
                    asyncio.run(gen_audios())
                    
                    # 2. Création des visuels
                    img_q = draw_quizz_frame(data, phase="question", timer_sec=5, bg_file=bg_file)
                    img_q.save("frame_q.png")
                    
                    img_r = draw_quizz_frame(data, phase="reponse", bg_file=bg_file)
                    img_r.save("frame_r.png")
                    
                    # 3. Assemblage des séquences vidéo
                    audio_q = AudioFileClip("part_q.mp3")
                    audio_r = AudioFileClip("part_r.mp3")
                    
                    # Clip Question (Durée de la voix off)
                    clip_q = ImageClip("frame_q.png").set_duration(audio_q.duration).set_audio(audio_q)
                    
                    # Clips Minuteur (5 secondes de silence avec décompte visuel)
                    timer_clips = []
                    for sec in range(5, 0, -1):
                        t_img = draw_quizz_frame(data, phase="question", timer_sec=sec, bg_file=bg_file)
                        t_img.save(f"frame_t_{sec}.png")
                        timer_clips.append(ImageClip(f"frame_t_{sec}.png").set_duration(1))
                    
                    # Clip Réponse (Durée de la voix off)
                    clip_r = ImageClip("frame_r.png").set_duration(audio_r.duration).set_audio(audio_r)
                    
                    # 4. Concaténation finale
                    final_video = concatenate_videoclips([clip_q] + timer_clips + [clip_r], method="compose")
                    output_mp4 = "quizz_final.mp4"
                    final_video.write_videofile(output_mp4, fps=24, codec="libx264", audio_codec="aac")
                    
                    st.video(output_mp4)
                    with open(output_mp4, "rb") as f:
                        st.download_button("📥 Télécharger la vidéo Quizz MP4", data=f, file_name="quizz_tiktok.mp4", mime="video/mp4")
                        
                    st.success("✅ Vidéo Quizz synchronisée et générée !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")

    # --- MODULE 2 : FICHE LANGUE (6 MOTS) ---
    with tab2:
        st.header("Créer une Fiche 6 Mots TikTok")
        langue = st.selectbox("Langue cible", ["Anglais", "Espagnol"])
        
        if st.button("🎬 Générer la Fiche 6 Mots MP4"):
            with st.spinner("Génération du vocabulaire et de la vidéo MP4..."):
                try:
                    prompt = f"Génère 6 mots ou phrases courantes avec traduction en {langue}. Réponds au format JSON strict : {{'mots': [{{'fr': 'Bonjour', 'en': 'Hello'}}, ...]}}"
                    model = genai.GenerativeModel(get_working_model())
                    response = model.generate_content(prompt)
                    data = parse_json_response(response.text)
                    mots_liste = data.get('mots', [])
                    
                    audio_raw = f"Voici 6 mots essentiels à retenir en {langue} ! "
                    for item in mots_liste[:6]:
                        audio_raw += f"{item['fr']} ... {item['en']}. "
                    
                    audio_text = clean_text_for_tts(audio_raw)
                    voice = "en-US-EmmaNeural" if langue == "Anglais" else "es-ES-AlvaroNeural"
                    
                    async def gen_lang_audio():
                        comm = edge_tts.Communicate(audio_text, voice)
                        await comm.save("langue.mp3")
                    asyncio.run(gen_lang_audio())
                    
                    img_l = draw_language_frame(mots_liste, langue)
                    img_l.save("frame_l.png")
                    
                    audio_l = AudioFileClip("langue.mp3")
                    clip_l = ImageClip("frame_l.png").set_duration(audio_l.duration).set_audio(audio_l)
                    
                    output_langue_mp4 = "langue_final.mp4"
                    clip_l.write_videofile(output_langue_mp4, fps=24, codec="libx264", audio_codec="aac")
                    
                    st.video(output_langue_mp4)
                    with open(output_langue_mp4, "rb") as f:
                        st.download_button("📥 Télécharger la vidéo Fiche MP4", data=f, file_name="langue_tiktok.mp4", mime="video/mp4")
                        
                    st.success("✅ Vidéo Fiche Langue synchronisée et générée !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")
else:
    st.warning("Entre ta clé API Gemini dans le panneau de gauche pour commencer.")
