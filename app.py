import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import imageio
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Générateur TikTok Pro", layout="wide")
st.title("🎬 Générateur de Vidéos TikTok & Shorts (.MP4)")

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
    
    # Phrase de motivation / Accroche TikTok
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
        # Minuteur animé
        draw.rectangle([(380, y + 30), (700, y + 120)], fill=(225, 29, 72))
        draw.text((430, y + 60), f"⏱️ 00:0{timer_sec}", fill="white")
        
    return img

# --- GENERATEUR VISUEL LANGUES ---
def draw_language_frame(mots, langue):
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # Accroche
    draw.rectangle([(60, 100), (1020, 200)], fill=(225, 29, 72))
    draw.text((90, 130), "💡 APPRENDS CE VOCABULAIRE !", fill="white")
    
    # Titre
    draw.rectangle([(80, 230), (1000, 330)], fill=(236, 72, 153))
    draw.text((120, 260), f"6 MOTS EN {langue.upper()}", fill="white")
    
    y = 380
    for item in mots[:6]:
        draw.rectangle([(80, y), (1000, y + 200)], fill=(30, 41, 59), outline="white", width=2)
        draw.text((110, y + 40), f"FR: {item['fr']}", fill="white")
        draw.text((110, y + 110), f"TRAD: {item['en']}", fill=(244, 63, 94))
        y += 240
        
    return img

# --- FABRICATION VIDEO MP4 DYNAMIQUE ---
def make_quizz_mp4(data, bg_file=None, output_path="quizz.mp4"):
    writer = imageio.get_writer(output_path, fps=30, codec='libx264')
    
    # 1. Phase Question (3 secondes)
    img_q = draw_quizz_frame(data, phase="question", timer_sec=5, bg_file=bg_file)
    img_q.save("temp_q.png")
    q_data = imageio.v3.imread("temp_q.png")
    for _ in range(3 * 30):
        writer.append_data(q_data)
        
    # 2. Phase Minuteur (Compte à rebours 5s à 1s)
    for sec in range(5, 0, -1):
        img_t = draw_quizz_frame(data, phase="question", timer_sec=sec, bg_file=bg_file)
        img_t.save(f"temp_t_{sec}.png")
        t_data = imageio.v3.imread(f"temp_t_{sec}.png")
        for _ in range(1 * 30):  # 1 seconde par chiffre
            writer.append_data(t_data)
            
    # 3. Phase Révélation Réponse (4 secondes)
    img_r = draw_quizz_frame(data, phase="reponse", bg_file=bg_file)
    img_r.save("temp_r.png")
    r_data = imageio.v3.imread("temp_r.png")
    for _ in range(4 * 30):
        writer.append_data(r_data)
        
    writer.close()
    return output_path

def make_langue_mp4(mots, langue, output_path="langue.mp4"):
    writer = imageio.get_writer(output_path, fps=30, codec='libx264')
    img = draw_language_frame(mots, langue)
    img.save("temp_l.png")
    l_data = imageio.v3.imread("temp_l.png")
    
    # Durée de 10 secondes pour laisser le temps de tout lire
    for _ in range(10 * 30):
        writer.append_data(l_data)
        
    writer.close()
    return output_path

# --- INTERFACE PRINCIPALE ---
api_key = st.sidebar.text_input("Clé API Gemini", type="password")

if api_key:
    genai.configure(api_key=api_key)
    tab1, tab2 = st.tabs(["🧠 Quizz TikTok (.MP4)", "🗣️ Fiche 6 Mots (.MP4)"])
    
    # --- APPLICATION 1 : QUIZZ ---
    with tab1:
        st.header("Créer un Quizz TikTok Interactif")
        theme = st.text_input("Thème du Quizz", "Culture Générale")
        bg_file = st.file_uploader("Image de fond optionnelle (9:16)", type=["png", "jpg", "jpeg"])
        
        if st.button("🎬 Générer le Quizz MP4"):
            with st.spinner("Génération du script, de la voix et du rendu MP4..."):
                try:
                    prompt = f"Génère une question de quizz sur '{theme}'. Réponds au format JSON strict : {{'question': '...', 'options': ['...','...','...','...'], 'reponse_correcte': 'A', 'explication': '...'}}"
                    model = genai.GenerativeModel(get_working_model())
                    response = model.generate_content(prompt)
                    data = parse_json_response(response.text)
                    
                    # Script Audio avec accroche et pause pour minuteur
                    audio_raw = f"Auras-tu 10 sur 10 à ce test ? {data['question']}. Option A: {data['options'][0]}. Option B: {data['options'][1]}. Option C: {data['options'][2]}. Option D: {data['options'][3]}. Attention, réfléchis bien ! ... ... La bonne réponse était la réponse {data['reponse_correcte']}."
                    audio_text = clean_text_for_tts(audio_raw)
                    
                    async def gen_audio():
                        comm = edge_tts.Communicate(audio_text, "fr-FR-HenriNeural")
                        await comm.save("quizz_audio.mp3")
                    asyncio.run(gen_audio())
                    
                    mp4_path = make_quizz_mp4(data, bg_file, "quizz_tiktok.mp4")
                    
                    st.video(mp4_path)
                    st.audio("quizz_audio.mp3")
                    
                    with open(mp4_path, "rb") as f:
                        st.download_button("📥 Télécharger la vidéo Quizz MP4", data=f, file_name="quizz_tiktok.mp4", mime="video/mp4")
                    st.success("✅ Vidéo Quizz MP4 9:16 générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")

    # --- APPLICATION 2 : FICHE LANGUE (6 MOTS) ---
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
                        await comm.save("langue_audio.mp3")
                    asyncio.run(gen_lang_audio())
                    
                    mp4_path = make_langue_mp4(mots_liste, langue, "langue_tiktok.mp4")
                    
                    st.video(mp4_path)
                    st.audio("langue_audio.mp3")
                    
                    with open(mp4_path, "rb") as f:
                        st.download_button("📥 Télécharger la vidéo Langue MP4", data=f, file_name="langue_tiktok.mp4", mime="video/mp4")
                    st.success("✅ Vidéo Fiche Langue MP4 9:16 générée avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")
else:
    st.warning("Entre ta clé API Gemini dans le panneau de gauche pour commencer.")
