import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Générateur Short Video Pro", layout="wide")
st.title("🎬 Générateur de Contenu Vidéo Réseaux Sociaux")

def create_quizz_frames(data, theme_color=(30, 41, 59)):
    width, height = 1080, 1920
    
    # Image 1 : Question + Choix
    img1 = Image.new('RGB', (width, height), color=theme_color)
    draw1 = ImageDraw.Draw(img1)
    
    # En-tête
    draw1.rectangle([(80, 150), (1000, 280)], fill=(79, 70, 229))
    draw1.text((120, 190), "QUIZZ DU JOUR", fill="white")
    
    # Question
    draw1.text((100, 350), f"Q: {data['question']}", fill="white")
    
    # Options
    y = 600
    for i, opt in enumerate(data['options']):
        draw1.rectangle([(100, y), (980, y + 100)], outline="white", width=3)
        draw1.text((130, y + 30), f"{chr(65+i)}) {opt}", fill="white")
        y += 140
        
    img1.save("quizz_q.png")
    
    # Image 2 : Révélation de la Bonne Réponse
    img2 = img1.copy()
    draw2 = ImageDraw.Draw(img2)
    
    correct_idx = ord(data['reponse_correcte'].upper()) - 65
    y_correct = 600 + (correct_idx * 140)
    
    # Mettre la bonne réponse en vert
    draw2.rectangle([(100, y_correct), (980, y_correct + 100)], fill=(34, 197, 94))
    draw2.text((130, y_correct + 30), f"{chr(65+correct_idx)}) {data['options'][correct_idx]}", fill="white")
    
    # Explication en bas
    draw2.rectangle([(80, 1400), (1000, 1700)], fill=(15, 23, 42))
    draw2.text((110, 1430), f"Explication :\n{data['explication']}", fill="white")
    
    img2.save("quizz_r.png")
    return "quizz_q.png", "quizz_r.png"

def create_language_frame(data, langue):
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # Titre
    draw.rectangle([(80, 150), (1000, 280)], fill=(236, 72, 153))
    draw.text((120, 190), f"6 MOTS EN {langue.upper()}", fill="white")
    
    y = 380
    for item in data['mots']:
        draw.rectangle([(80, y), (1000, y + 180)], fill=(30, 41, 59))
        draw.text((110, y + 40), f"FR: {item['fr']}", fill="white")
        draw.text((110, y + 100), f"EN: {item['en']}", fill=(244, 63, 94))
        y += 220
        
    img.save("langue_frame.png")
    return "langue_frame.png"

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

api_key = st.sidebar.text_input("Clé API Gemini", type="password")

if api_key:
    genai.configure(api_key=api_key)
    tab1, tab2 = st.tabs(["🧠 Quizz Interactif", "🗣️ Fiche 6 Mots"])
    
    with tab1:
        st.header("Créer un Quizz (Question + Révélation)")
        theme = st.text_input("Thème du Quizz", "Histoire")
        
        if st.button("🎬 Générer le Quizz"):
            with st.spinner("Création du Quizz..."):
                prompt = f"Génère une question de quizz sur '{theme}'. Réponds au format JSON strict avec les clés : 'question', 'options' (liste de 4 choix), 'reponse_correcte' (lettre A, B, C ou D), 'explication'."
                model_name = get_working_model()
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                data = parse_json_response(response.text)
                
                # Audio
                audio_text = f"Question : {data['question']}. A : {data['options'][0]}. B : {data['options'][1]}. C : {data['options'][2]}. D : {data['options'][3]}. La bonne réponse est la réponse {data['reponse_correcte']}."
                async def gen_audio():
                    comm = edge_tts.Communicate(audio_text, "fr-FR-VivienneNeural")
                    await comm.save("quizz.mp3")
                asyncio.run(gen_audio())
                
                fq, fr = create_quizz_frames(data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.image(fq, caption="1. Temps de Réflexion (Question)")
                with col2:
                    st.image(fr, caption="2. Révélation (Réponse Verte)")
                
                st.audio("quizz.mp3")
                st.success("✅ Quizz interactif prêt !")

    with tab2:
        st.header("Créer une Fiche 6 Mots / Phrases")
        langue = st.selectbox("Langue cible", ["Anglais", "Espagnol"])
        
        if st.button("🎬 Générer la Fiche 6 Mots"):
            with st.spinner("Création du vocabulaire..."):
                prompt = f"Génère 6 mots ou phrases courantes du quotidien avec leur traduction en {langue}. Réponds au format JSON strict avec une clé 'mots' contenant une liste de 6 objets avec les clés 'fr' et 'en'."
                model_name = get_working_model()
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                data = parse_json_response(response.text)
                
                # Audio alterné
                audio_text = ""
                for item in data['mots']:
                    audio_text += f"{item['fr']} ... {item['en']} ... "
                
                async def gen_lang_audio():
                    comm = edge_tts.Communicate(audio_text, "fr-FR-RemyNeural")
                    await comm.save("langue.mp3")
                asyncio.run(gen_lang_audio())
                
                frame = create_language_frame(data, langue)
                st.image(frame, caption="Fiche 6 Mots (Format 9:16)", width=350)
                st.audio("langue.mp3")
                st.success("✅ Fiche de 6 mots prête !")
else:
    st.warning("Entre ta clé API Gemini à gauche pour commencer.")
