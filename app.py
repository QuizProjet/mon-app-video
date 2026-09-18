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

# --- FONCTIONS VISUELLES ---
def create_quizz_frames(data, background_img=None):
    width, height = 1080, 1920
    
    if background_img:
        bg = Image.open(background_img).convert('RGB').resize((width, height))
    else:
        bg = Image.new('RGB', (width, height), color=(18, 24, 38))

    # Écran 1 : Question + Réflexion (Minuteur 5s)
    img1 = bg.copy()
    draw1 = ImageDraw.Draw(img1)
    
    draw1.rectangle([(80, 150), (1000, 270)], fill=(79, 70, 229))
    draw1.text((120, 180), "QUIZZ DU JOUR", fill="white")
    draw1.text((90, 320), f"Q: {data['question']}", fill="white")
    
    y = 550
    for i, opt in enumerate(data['options']):
        draw1.rectangle([(90, y), (990, y + 110)], outline="white", width=3, fill=(30, 41, 59))
        draw1.text((120, y + 35), f"{chr(65+i)}) {opt}", fill="white")
        y += 150
        
    draw1.rectangle([(400, y + 20), (680, y + 100)], fill=(225, 29, 72))
    draw1.text((450, y + 45), "⏱️ 00:05", fill="white")
    img1.save("quizz_question.png")
    
    # Écran 2 : Révélation de la Bonne Réponse (Vert)
    img2 = bg.copy()
    draw2 = ImageDraw.Draw(img2)
    
    draw2.rectangle([(80, 150), (1000, 270)], fill=(79, 70, 229))
    draw2.text((120, 180), "QUIZZ DU JOUR", fill="white")
    draw2.text((90, 320), f"Q: {data['question']}", fill="white")
    
    correct_letter = str(data.get('reponse_correcte', 'A')).strip().upper()[0]
    correct_idx = ord(correct_letter) - 65 if correct_letter in ['A', 'B', 'C', 'D'] else 0
    
    y = 550
    for i, opt in enumerate(data['options']):
        if i == correct_idx:
            draw2.rectangle([(90, y), (990, y + 110)], fill=(34, 197, 94))
        else:
            draw2.rectangle([(90, y), (990, y + 110)], fill=(30, 41, 59))
        draw2.text((120, y + 35), f"{chr(65+i)}) {opt}", fill="white")
        y += 150

    draw2.rectangle([(80, y + 10), (1000, y + 220)], fill=(15, 23, 42))
    draw2.text((100, y + 30), f"Réponse: {data['options'][correct_idx]}\n\nExplication: {data['explication']}", fill="white")
    img2.save("quizz_reponse.png")
    
    return "quizz_question.png", "quizz_reponse.png"

def create_language_frame(mots, langue):
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(80, 150), (1000, 280)], fill=(236, 72, 153))
    draw.text((120, 190), f"6 MOTS EN {langue.upper()}", fill="white")
    
    y = 350
    for item in mots[:6]:
        draw.rectangle([(80, y), (1000, y + 200)], fill=(30, 41, 59))
        draw.text((110, y + 40), f"FR: {item['fr']}", fill="white")
        draw.text((110, y + 110), f"TRAD: {item['en']}", fill=(244, 63, 94))
        y += 240
        
    img.save("langue_frame.png")
    return "langue_frame.png"

# --- UTILITAIRES ---
def clean_text_for_tts(text):
    # Enlève les caractères non imprimables et sécurise pour TTS
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

# --- INTERFACE STREAMLIT ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")

if api_key:
    genai.configure(api_key=api_key)
    tab1, tab2 = st.tabs(["🧠 Quizz Interactif", "🗣️ Fiche 6 Mots"])
    
    # MODULE 1 : QUIZZ
    with tab1:
        st.header("Créer un Quizz Dynamique")
        theme = st.text_input("Thème du Quizz", "Culture Générale")
        bg_file = st.file_uploader("Image de fond optionnelle (9:16)", type=["png", "jpg", "jpeg"])
        
        if st.button("🎬 Générer le Quizz"):
            with st.spinner("Génération du Quizz..."):
                try:
                    prompt = f"Génère une question de quizz sur '{theme}'. Réponds au format JSON strict : {{'question': '...', 'options': ['...','...','...','...'], 'reponse_correcte': 'A', 'explication': '...'}}"
                    model = genai.GenerativeModel(get_working_model())
                    response = model.generate_content(prompt)
                    data = parse_json_response(response.text)
                    
                    audio_raw = f"{data['question']}. Option A: {data['options'][0]}. Option B: {data['options'][1]}. Option C: {data['options'][2]}. Option D: {data['options'][3]}. La bonne réponse est l'option {data['reponse_correcte']}."
                    audio_text = clean_text_for_tts(audio_raw)
                    
                    async def gen_audio():
                        comm = edge_tts.Communicate(audio_text, "fr-FR-HenriNeural")
                        await comm.save("quizz.mp3")
                    asyncio.run(gen_audio())
                    
                    fq, fr = create_quizz_frames(data, bg_file)
                    
                    st.subheader("1. Écran de réflexion (5s)")
                    st.image(fq, width=320)
                    st.subheader("2. Écran de Révélation")
                    st.image(fr, width=320)
                    
                    st.audio("quizz.mp3")
                    st.success("✅ Quizz généré avec succès !")
                except Exception as e:
                    st.error(f"Erreur Quizz : {e}")

    # MODULE 2 : LANGUES (6 MOTS)
    with tab2:
        st.header("Créer une Fiche 6 Mots")
        langue = st.selectbox("Langue cible", ["Anglais", "Espagnol"])
        
        if st.button("🎬 Générer la Fiche 6 Mots"):
            with st.spinner("Génération de la fiche..."):
                try:
                    prompt = f"Génère 6 mots ou phrases courantes avec traduction en {langue}. Réponds au format JSON strict : {{'mots': [{{'fr': 'Bonjour', 'en': 'Hello'}}, ...]}}"
                    model = genai.GenerativeModel(get_working_model())
                    response = model.generate_content(prompt)
                    data = parse_json_response(response.text)
                    
                    mots_liste = data.get('mots', [])
                    
                    audio_raw = ""
                    for item in mots_liste[:6]:
                        audio_raw += f"{item['fr']}, {item['en']}. "
                    
                    audio_text = clean_text_for_tts(audio_raw)
                    voice = "en-US-EmmaNeural" if langue == "Anglais" else "es-ES-AlvaroNeural"
                    
                    async def gen_lang_audio():
                        comm = edge_tts.Communicate(audio_text, voice)
                        await comm.save("langue.mp3")
                    asyncio.run(gen_lang_audio())
                    
                    frame = create_language_frame(mots_liste, langue)
                    st.image(frame, caption="Fiche 6 Mots (9:16)", width=350)
                    st.audio("langue.mp3")
                    st.success("✅ Fiche 6 mots générée sans erreur !")
                except Exception as e:
                    st.error(f"Erreur Fiche Langue : {e}")
else:
    st.warning("Entre ta clé API Gemini à gauche pour commencer.")
