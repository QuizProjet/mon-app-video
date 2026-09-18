import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Générateur Short Video", layout="wide")
st.title("🎬 Générateur de Contenu Vidéo (Quizz & Langues)")

# Fonction pour créer une image 9:16 (1080x1920)
def create_video_frame(title, body_text, filename="frame.png"):
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color=(24, 28, 36))
    draw = ImageDraw.Draw(img)
    
    # Entête visuelle
    draw.rectangle([(80, 200), (1000, 360)], fill=(79, 70, 229))
    
    font_title = ImageFont.load_default()
    font_body = ImageFont.load_default()

    draw.text((120, 250), title, fill="white", font=font_title)
    
    y_position = 450
    lines = body_text.split('\n')
    for line in lines:
        draw.text((100, y_position), line, fill="white", font=font_body)
        y_position += 60

    img.save(filename)
    return filename

# Fonction de nettoyage JSON sécurisée
def parse_json_response(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)

# Fonction pour trouver automatiquement un modèle Gemini valide
def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-3.6-flash' in m.name or 'gemini-3' in m.name:
                    return m.name
        # Modèle recommandé par l'API
        return 'models/gemini-3.6-flash'
    except Exception:
        return 'models/gemini-3.6-flash'

api_key = st.sidebar.text_input("Clé API Gemini (Gratuite)", type="password")

if api_key:
    genai.configure(api_key=api_key)
    tab1, tab2 = st.tabs(["🧠 Quizz Short", "🗣️ Langue Short"])
    
    # --- MODULE 1 : QUIZZ ---
    with tab1:
        st.header("Créer un Quizz")
        theme = st.text_input("Thème du Quizz", "Culture Générale")
        
        if st.button("🎬 Générer le Quizz"):
            with st.spinner("Génération du contenu..."):
                try:
                    prompt = f"Génère une question de quizz sur le thème '{theme}'. Réponds uniquement avec un objet JSON valide ayant exactement ces clés : 'question', 'options' (liste de 4 choix), 'reponse_correcte', 'explication'."
                    
                    # Détection automatique ou modèle gemini-3.6-flash
                    model_name = get_working_model()
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    
                    data = parse_json_response(response.text)
                    
                    # Génération Audio
                    audio_text = f"{data['question']} ... Option A: {data['options'][0]}. Option B: {data['options'][1]}. Option C: {data['options'][2]}. Option D: {data['options'][3]}."
                    async def generate_audio():
                        communicate = edge_tts.Communicate(audio_text, "fr-FR-VivienneNeural")
                        await communicate.save("quizz_audio.mp3")
                    asyncio.run(generate_audio())
                    
                    # Image 9:16
                    body_text = f"Q: {data['question']}\n\n"
                    for i, opt in enumerate(data['options']):
                        body_text += f"{chr(65+i)}) {opt}\n"
                    img_path = create_video_frame("QUIZZ DU JOUR", body_text, "quizz_frame.png")
                    
                    st.image(img_path, caption="Visuel 9:16 pour TikTok/Shorts", width=300)
                    st.audio("quizz_audio.mp3")
                    st.success(f"✅ Généré avec succès (Modèle utilisé : {model_name}) !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")

    # --- MODULE 2 : LANGUES ---
    with tab2:
        st.header("Créer une Fiche Langue")
        langue = st.selectbox("Langue à apprendre", ["Anglais", "Français"])
        niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
        
        if st.button("🎬 Générer la Fiche Langue"):
            with st.spinner("Génération de la fiche..."):
                try:
                    prompt = f"Génère une fiche de vocabulaire en {langue} pour niveau {niveau}. Réponds uniquement avec un objet JSON valide ayant exactement ces clés : 'mot', 'prononciation', 'definition', 'synonymes' (liste de 3 mots), 'phrase_exemple'."
                    
                    model_name = get_working_model()
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    
                    data = parse_json_response(response.text)
                    
                    voice = "en-US-ChristopherNeural" if langue == "Anglais" else "fr-FR-RemyNeural"
                    audio_text = f"Mot du jour : {data['mot']}. Synonymes : {', '.join(data['synonymes'])}. Exemple : {data['phrase_exemple']}"
                    
                    async def generate_lang_audio():
                        communicate = edge_tts.Communicate(audio_text, voice)
                        await communicate.save("langue_audio.mp3")
                    asyncio.run(generate_lang_audio())
                    
                    body_text = f"MOT : {data['mot']}\n({data['prononciation']})\n\n"
                    body_text += f"Définition :\n{data['definition']}\n\n"
                    body_text += f"Synonymes :\n{', '.join(data['synonymes'])}\n\n"
                    body_text += f"Exemple :\n{data['phrase_exemple']}"
                    
                    img_path = create_video_frame(f"APPRENDRE LE {langue.upper()}", body_text, "langue_frame.png")
                    
                    st.image(img_path, caption="Visuel 9:16 pour TikTok/Shorts", width=300)
                    st.audio("langue_audio.mp3")
                    st.success(f"✅ Généré avec succès (Modèle utilisé : {model_name}) !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")
else:
    st.warning("Veuillez entrer votre clé API Gemini gratuite dans le panneau de gauche pour commencer.")
