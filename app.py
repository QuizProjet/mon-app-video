import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os

st.set_page_config(page_title="Générateur Short Video", layout="wide")
st.title("🎬 Générateur de Contenu Vidéo Court (Quizz & Langues)")

# Configuration de la clé API Gemini
api_key = st.sidebar.text_input("Clé API Gemini (Gratuite)", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    tab1, tab2 = st.tabs(["🧠 Générateur de Quizz", "🗣️ Apprentissage des Langues"])
    
    # --- MODULE 1 : QUIZZ ---
    with tab1:
        st.header("Créer un Quizz TikTok / Shorts")
        theme = st.text_input("Thème du Quizz", "Culture Générale")
        
        if st.button("Générer le Quizz"):
            prompt = f"Génère une question de quizz sur le thème '{theme}' au format JSON avec les clés : 'question', 'options' (liste de 4 choix), 'reponse_correcte', 'explication'."
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            st.subheader(f"Question : {data['question']}")
            for opt in data['options']:
                st.write(f"- {opt}")
            st.success(f"Réponse correcte : {data['reponse_correcte']}")
            st.info(f"Explication : {data['explication']}")
            
            # Génération Audio
            audio_text = f"{data['question']} ... Option A: {data['options'][0]}. Option B: {data['options'][1]}. Option C: {data['options'][2]}. Option D: {data['options'][3]}."
            
            async def generate_audio():
                communicate = edge_tts.Communicate(audio_text, "fr-FR-VivienneNeural")
                await communicate.save("quizz_audio.mp3")
            
            asyncio.run(generate_audio())
            st.audio("quizz_audio.mp3")

    # --- MODULE 2 : LANGUES ---
    with tab2:
        st.header("Créer une Vidéo de Langue")
        langue = st.selectbox("Langue à apprendre", ["Anglais", "Français"])
        niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
        
        if st.button("Générer la Fiche Vocabulaire"):
            prompt = f"Génère une fiche de vocabulaire en {langue} pour niveau {niveau} au format JSON avec les clés : 'mot', 'prononciation', 'definition', 'synonymes' (liste de 3 mots), 'phrase_exemple'."
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            st.subheader(f"Mot : {data['mot']} ({data['prononciation']})")
            st.write(f"**Définition :** {data['definition']}")
            st.write(f"**Synonymes :** {', '.join(data['synonymes'])}")
            st.write(f"**Exemple :** {data['phrase_exemple']}")
            
            voice = "en-US-ChristopherNeural" if langue == "Anglais" else "fr-FR-RemyNeural"
            audio_text = f"Mot du jour : {data['mot']}. Synonymes : {', '.join(data['synonymes'])}. Exemple : {data['phrase_exemple']}"
            
            async def generate_lang_audio():
                communicate = edge_tts.Communicate(audio_text, voice)
                await communicate.save("langue_audio.mp3")
            
            asyncio.run(generate_lang_audio())
            st.audio("langue_audio.mp3")
else:
    st.warning("Veuillez entrer votre clé API Gemini gratuite dans le panneau de gauche pour commencer.")
