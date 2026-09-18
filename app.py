import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import imageio
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Générateur TikTok/Shorts MP4", layout="wide")
st.title("🎬 Générateur de Vidéos TikTok & Shorts (.MP4)")

# --- FONCTION DE CREATION DE CARTE 9:16 ---
def draw_quizz_frame(data, show_answer=False, bg_file=None):
    width, height = 1080, 1920
    if bg_file:
        img = Image.open(bg_file).convert('RGB').resize((width, height))
    else:
        img = Image.new('RGB', (width, height), color=(15, 23, 42))
        
    draw = ImageDraw.Draw(img)
    
    # En-tête
    draw.rectangle([(80, 140), (1000, 260)], fill=(79, 70, 229))
    draw.text((120, 175), "QUIZZ DU JOUR", fill="white")
    
    # Question
    draw.text((90, 320), f"Q: {data['question']}", fill="white")
    
    # Options
    correct_letter = str(data.get('reponse_correcte', 'A')).strip().upper()[0]
    correct_idx = ord(correct_letter) - 65 if correct_letter in ['A', 'B', 'C', 'D'] else 0
    
    y = 550
    for i, opt in enumerate(data['options']):
        fill_color = (34, 197, 94) if (show_answer and i == correct_idx) else (30, 41, 59)
        draw.rectangle([(90, y), (990, y + 110)], fill=fill_color, outline="white", width=2)
        draw.text((120, y + 35), f"{chr(65+i)}) {opt}", fill="white")
        y += 150
        
    if show_answer:
        draw.rectangle([(80, y + 10), (1000, y + 220)], fill=(15, 23, 42))
        draw.text((100, y + 30), f"Explication:\n{data['explication']}", fill="white")
    else:
        draw.rectangle([(400, y + 20), (680, y + 100)], fill=(225, 29, 72))
        draw.text((450, y + 45), "⏱️ 00:05", fill="white")
        
    return img

# --- ASSEMBLAGE VIDEO MP4 ---
def generate_mp4_video(data, output_path="video.mp4", bg_file=None):
    frame_q = draw_quizz_frame(data, show_answer=False, bg_file=bg_file)
    frame_r = draw_quizz_frame(data, show_answer=True, bg_file=bg_file)
    
    # Sauvegarde temporaire des images
    frame_q.save("f_q.png")
    frame_r.save("f_r.png")
    
    img_q = imageio.v3.imread("f_q.png")
    img_r = imageio.v3.imread("f_r.png")
    
    fps = 30
    duration_q_sec = 5  # 5 secondes de réflexion
    duration_r_sec = 4  # 4 secondes d'affichage de la réponse
    
    writer = imageio.get_writer(output_path, fps=fps, codec='libx264')
    
    # Frames Question
    for _ in range(duration_q_sec * fps):
        writer.append_data(img_q)
        
    # Frames Réponse
    for _ in range(duration_r_sec * fps):
        writer.append_data(img_r)
        
    writer.close()
    return output_path

# --- UTILITAIRES ---
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

# --- INTERFACE ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")

if api_key:
    genai.configure(api_key=api_key)
    st.header("🧠 Générateur de Quizz Vidéo (.MP4)")
    
    theme = st.text_input("Thème du Quizz", "Culture Générale")
    bg_file = st.file_uploader("Image de fond optionnelle (9:16)", type=["png", "jpg", "jpeg"])
    
    if st.button("🎬 Générer la Vidéo MP4"):
        with st.spinner("Création du contenu et rendu de la vidéo MP4..."):
            try:
                prompt = f"Génère une question de quizz sur '{theme}'. Réponds au format JSON strict : {{'question': '...', 'options': ['...','...','...','...'], 'reponse_correcte': 'A', 'explication': '...'}}"
                model = genai.GenerativeModel(get_working_model())
                response = model.generate_content(prompt)
                data = parse_json_response(response.text)
                
                # Génération Audio
                audio_raw = f"{data['question']}. Option A: {data['options'][0]}. Option B: {data['options'][1]}. Option C: {data['options'][2]}. Option D: {data['options'][3]}. La bonne réponse est l'option {data['reponse_correcte']}."
                audio_text = clean_text_for_tts(audio_raw)
                
                async def gen_audio():
                    comm = edge_tts.Communicate(audio_text, "fr-FR-HenriNeural")
                    await comm.save("quizz_audio.mp3")
                asyncio.run(gen_audio())
                
                # Génération Vidéo MP4
                mp4_file = generate_mp4_video(data, "quizz_tiktok.mp4", bg_file)
                
                st.video(mp4_file)
                st.audio("quizz_audio.mp3")
                
                with open(mp4_file, "rb") as file:
                    st.download_button("Télécharger la vidéo MP4", data=file, file_name="quizz_tiktok.mp4", mime="video/mp4")
                    
                st.success("✅ Vidéo MP4 9:16 générée et prête à télécharger !")
            except Exception as e:
                st.error(f"Erreur lors de la génération vidéo : {e}")
else:
    st.warning("Entre ta clé API Gemini à gauche pour commencer.")
