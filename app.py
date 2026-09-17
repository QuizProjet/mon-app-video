import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

st.set_page_config(page_title="Générateur Short Video MP4", layout="wide")
st.title("🎬 Générateur de Contenu Vidéo MP4 (Quizz & Langues)")

# Fonction pour générer une image verticale 9:16 (1080x1920) avec du texte
def create_video_frame(title, body_text, filename="frame.png"):
    width, height = 1080, 1920
    # Fond dégradé sombre élégant
    img = Image.new('RGB', (width, height), color=(24, 28, 36))
    draw = ImageDraw.Draw(img)
    
    # Cartouche de titre
    draw.rectangle([(80, 200), (1000, 360)], fill=(79, 70, 229))
    
    # Texte (Utilisation des polices par défaut si pas de custom font)
    try:
        font_title = ImageFont.truetype("arial.ttf", 50)
        font_body = ImageFont.truetype("arial.ttf", 40)
    except:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((120, 250), title, fill="white", font=font_title)
    
    # Affichage du texte principal
    y_position = 450
    lines = body_text.split('\n')
    for line in lines:
        draw.text((100, y_position), line, fill="white", font=font_body)
        y_position += 60

    img.save(filename)
    return filename

# Fonction pour combiner l'image et le son en vidéo MP4
def make_mp4(image_file, audio_file, output_mp4="output.mp4"):
    audio_clip = AudioFileClip(audio_file)
    image_clip = ImageClip(image_file).set_duration(audio_clip.duration)
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_mp4, fps=24, codec="libx264", audio_codec="aac")
    return output_mp4

api_key = st.sidebar.text_input("Clé API Gemini (Gratuite)", type="password")

if api_key:
    genai.configure(api_key=api_key)
    tab1, tab2 = st.tabs(["🧠 Quizz Short", "🗣️ Langue Short"])
    
    # --- MODULE 1 : QUIZZ ---
    with tab1:
        st.header("Créer un Quizz MP4")
        theme = st.text_input("Thème du Quizz", "Culture Générale")
        
        if st.button("🎬 Générer la Vidéo Quizz MP4"):
            with st.spinner("Génération du contenu et de la vidéo en cours..."):
                prompt = f"Génère une question de quizz sur le thème '{theme}' au format JSON avec les clés : 'question', 'options' (liste de 4 choix), 'reponse_correcte', 'explication'."
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                
                # Audio
                audio_text = f"{data['question']} ... Option A: {data['options'][0]}. Option B: {data['options'][1]}. Option C: {data['options'][2]}. Option D: {data['options'][3]}."
                async def generate_audio():
                    communicate = edge_tts.Communicate(audio_text, "fr-FR-VivienneNeural")
                    await communicate.save("quizz_audio.mp3")
                asyncio.run(generate_audio())
                
                # Image 9:16
                body_text = f"Q: {data['question']}\n\n"
                for i, opt in enumerate(data['options']):
                    body_text += f"{chr(65+i)}) {opt}\n"
                create_video_frame("QUIZZ DU JOUR", body_text, "quizz_frame.png")
                
                # Assemblage MP4
                mp4_path = make_mp4("quizz_frame.png", "quizz_audio.mp3", "quizz_video.mp4")
                
                st.video(mp4_path)
                with open(mp4_path, "rb") as file:
                    st.download_button("Télécharger la vidéo MP4", data=file, file_name="quizz_short.mp4", mime="video/mp4")

    # --- MODULE 2 : LANGUES ---
    with tab2:
        st.header("Créer une Vidéo Langue MP4")
        langue = st.selectbox("Langue à apprendre", ["Anglais", "Français"])
        niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
        
        if st.button("🎬 Générer la Vidéo Langue MP4"):
            with st.spinner("Génération de la vidéo en cours..."):
                prompt = f"Génère une fiche de vocabulaire en {langue} pour niveau {niveau} au format JSON avec les clés : 'mot', 'prononciation', 'definition', 'synonymes' (liste de 3 mots), 'phrase_exemple'."
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                
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
                
                create_video_frame(f"APPRENDRE LE {langue.upper()}", body_text, "langue_frame.png")
                mp4_path = make_mp4("langue_frame.png", "langue_audio.mp3", "langue_video.mp4")
                
                st.video(mp4_path)
                with open(mp4_path, "rb") as file:
                    st.download_button("Télécharger la vidéo MP4", data=file, file_name="langue_short.mp4", mime="video/mp4")
else:
    st.warning("Veuillez entrer votre clé API Gemini gratuite dans le panneau de gauche pour commencer.")
