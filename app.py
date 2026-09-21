import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import tempfile
import math
import wave
import struct
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# QUIZVIDEO PRO — V4 DYNAMIC SHORTS ENGINE
# ============================================================
st.set_page_config(page_title="QuizVideo Pro", page_icon="🎬", layout="wide")
st.title("🎬 QuizVideo Pro")
st.caption("Créateur de Shorts 9:16 • Quiz dynamique + Vocabulaire")

WIDTH, HEIGHT, FPS = 1080, 1920, 30

THEMES = {
    "Bleu Nuit & Or": {"bg": (10, 17, 32), "card": (27, 38, 58), "accent": (250, 204, 21), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (160, 174, 194)},
    "Chocolat Noir & Or": {"bg": (27, 17, 11), "card": (56, 38, 27), "accent": (245, 158, 11), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (190, 166, 145)},
    "Violet Neon": {"bg": (21, 12, 34), "card": (48, 28, 72), "accent": (236, 72, 153), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (190, 165, 205)},
    "Emeraude Mint": {"bg": (5, 25, 18), "card": (14, 52, 37), "accent": (52, 211, 153), "success": (34, 197, 94), "danger": (239, 68, 68), "muted": (160, 195, 180)},
}

VOICES_FR = {
    "Henri - Dynamique": "fr-FR-HenriNeural",
    "Vivienne - Energique": "fr-FR-VivienneNeural",
    "Remy - Standard": "fr-FR-RemyNeural",
}
VOICES_MAP = {
    "Anglais": {"Emma": "en-US-EmmaNeural", "Christopher": "en-US-ChristopherNeural"},
    "Espagnol": {"Alvaro": "es-ES-AlvaroNeural", "Elvira": "es-ES-ElviraNeural"},
    "Arabe": {"Hamed": "ar-SA-HamedNeural", "Salma": "ar-SA-SalmaNeural"},
    "Allemand": {"Killian": "de-DE-KillianNeural", "Klarissa": "de-DE-KlarissaNeural"},
    "Italien": {"Diego": "it-IT-DiegoNeural", "Elsa": "it-IT-ElsaNeural"},
}

# ------------------------- Helpers --------------------------
def get_ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()

def get_font(size):
    candidates = ["Roboto-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"]
    for fn in candidates:
        try:
            if os.path.exists(fn) and os.path.getsize(fn) > 100:
                return ImageFont.truetype(fn, max(12, int(size)))
        except Exception:
            pass
    return ImageFont.load_default()

def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text).replace("\n", " ")).strip()

def text_width(draw, text, font):
    box = draw.textbbox((0, 0), str(text), font=font)
    return box[2] - box[0]

def text_height(font, text="Ag"):
    b = font.getbbox(text)
    return b[3] - b[1]

def wrap_text(text, font, max_width):
    words = clean_text(text).split()
    lines, cur = [], ""
    dummy = ImageDraw.Draw(Image.new("RGB", (2, 2)))
    for word in words:
        candidate = word if not cur else cur + " " + word
        if text_width(dummy, candidate, font) <= max_width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(v)))

def ease_out(v):
    v = clamp(v)
    return 1 - (1 - v) ** 3

def ease_back(v):
    v = clamp(v)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (v - 1) ** 3 + c1 * (v - 1) ** 2

def fit_background(uploaded_file):
    if not uploaded_file:
        return None
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file).convert("RGB")
        ratio = WIDTH / HEIGHT
        src_ratio = img.width / img.height
        if src_ratio > ratio:
            new_h = HEIGHT
            new_w = int(new_h * src_ratio)
        else:
            new_w = WIDTH
            new_h = int(new_w / src_ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = max(0, (new_w - WIDTH) // 2)
        top = max(0, (new_h - HEIGHT) // 2)
        return img.crop((left, top, left + WIDTH, top + HEIGHT))
    except Exception:
        return None

def make_base(theme_name, bg_file=None):
    theme = THEMES[theme_name]
    bg = fit_background(bg_file)
    if bg is not None:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 115))
        return Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    return Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])

def add_top_glow(img, theme, strength=1.0):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    a = int(34 * clamp(strength))
    gd.ellipse((110, -420, 970, 520), fill=(*theme["accent"], a))
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

def rounded_text(draw, xy, text, font, fill, outline=None, width=2, radius=20):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=width if outline else 1)
    tw = text_width(draw, text, font)
    th = text_height(font, text)
    draw.text(((x1+x2-tw)/2, (y1+y2-th)/2-4), text, font=font, fill="white")

def draw_brand(draw, theme, channel, progress=None):
    if channel:
        draw.text((55, 1810), clean_text(channel), font=get_font(28), fill=theme["muted"])
    if progress is not None:
        x, y, w, h = 55, 1745, 970, 12
        draw.rounded_rectangle((x,y,x+w,y+h), radius=6, fill=(65,70,85))
        draw.rounded_rectangle((x,y,x+int(w*clamp(progress)),y+h), radius=6, fill=theme["accent"])

def draw_header(draw, theme, q_num, total):
    rounded_text(draw, (55, 70, 360, 136), f"QUESTION {q_num} / {total}", get_font(32), theme["card"], theme["accent"], 2, 26)

def draw_timer(draw, theme, timer, fraction=1.0, pulse=0.0):
    color = theme["accent"] if timer == 3 else ((249,115,22) if timer == 2 else theme["danger"])
    cx, cy, r = 935, 825, 70
    draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=theme["bg"], outline=(65,70,85), width=7)
    # ring remaining
    box=(cx-r+5,cy-r+5,cx+r-5,cy+r-5)
    draw.arc(box, -90, -90 + int(360*clamp(fraction)), fill=color, width=10)
    if pulse > 0:
        pr = int(4 + 14*pulse)
        draw.ellipse((cx-r-pr,cy-r-pr,cx+r+pr,cy+r+pr), outline=(*color,), width=3)
    tf=get_font(58 + int(8*pulse))
    ts=str(timer)
    draw.text((cx-text_width(draw,ts,tf)/2,cy-38),ts,font=tf,fill=color)
    sf=get_font(22)
    draw.text((cx-text_width(draw,"SEC",sf)/2,cy+37),"SEC",font=sf,fill=color)

def draw_quiz_frame(question, options, theme_name, q_num, total, channel, bg_file=None, entrance=1.0, timer=None, timer_fraction=1.0, correct_idx=None, reveal_progress=0.0, pulse=0.0):
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.0+0.35*pulse)
    draw=ImageDraw.Draw(img)
    draw_header(draw,theme,q_num,total)
    f_q=get_font(58)
    q_lines=wrap_text(question,f_q,900)[:3]
    q_y=205
    q_e=ease_out(entrance)
    q_offset=int((1-q_e)*45)
    for line in q_lines:
        tw=text_width(draw,line,f_q)
        draw.text(((WIDTH-tw)/2,q_y+q_offset),line,font=f_q,fill="white")
        q_y+=78

    left,right=55,850
    card_h,gap=128,18
    start_y=max(525,q_y+25)
    for i,opt in enumerate(options[:4]):
        local=ease_out(clamp((entrance-i*0.12)/0.58))
        y=start_y+int((1-local)*95)
        correct=(correct_idx is not None and i==correct_idx)
        dim=(correct_idx is not None and not correct)
        if correct:
            # animated green reveal
            rp=ease_back(reveal_progress)
            fill=theme["success"]
            outline=(255,255,255)
            width=5
            extra=int(10*rp)
        else:
            fill=theme["card"]
            outline=theme["accent"]
            width=3
            extra=0
        if dim:
            fill=tuple(max(0,int(c*0.55)) for c in fill)
            outline=tuple(max(0,int(c*0.55)) for c in outline)
        draw.rounded_rectangle((left-extra,y-extra,right+extra,y+card_h+extra),radius=28,fill=fill,outline=outline,width=width)
        label=f"{chr(65+i)}  {clean_text(opt)}"
        f_opt=get_font(39)
        lines=wrap_text(label,f_opt,right-left-58)[:2]
        th=sum(text_height(f_opt,x) for x in lines)+max(0,len(lines)-1)*8
        ty=y+(card_h-th)/2-3
        for line in lines:
            draw.text((92,ty),line,font=f_opt,fill="white")
            ty+=text_height(f_opt,line)+8
        if correct:
            r=29
            cx=right-55; cy=y+card_h/2
            draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill="white")
            draw.text((cx-text_width(draw,"✓",get_font(34))/2,cy-21),"✓",font=get_font(34),fill=theme["success"])

    if timer is not None:
        draw_timer(draw,theme,timer,timer_fraction,pulse)

    if correct_idx is not None:
        p=ease_back(reveal_progress)
        by=1410-int(15*p)
        draw.rounded_rectangle((235,by,845,by+92),radius=35,fill=theme["success"])
        txt="✓ BONNE RÉPONSE"
        f=get_font(38+int(4*p))
        draw.text(((WIDTH-text_width(draw,txt,f))/2,by+25),txt,font=f,fill="white")

    draw_brand(draw,theme,channel,(q_num-1)/max(1,total))
    return img

def draw_hook(text,theme_name,channel,bg_file=None,progress=1.0):
    theme=THEMES[theme_name]
    p=ease_back(progress)
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.2*p)
    draw=ImageDraw.Draw(img)
    # subtle focus circle
    r=int(210*p)
    draw.ellipse((540-r,430-r,540+r,430+r),outline=(*theme["accent"],),width=4)
    badge_w=500; bx=(WIDTH-badge_w)//2; by=250-int(30*(1-p))
    rounded_text(draw,(bx,by,bx+badge_w,by+76),"🎯 TESTE-TOI",get_font(34),theme["accent"],None,0,34)
    f=get_font(76)
    lines=wrap_text(text,f,850)[:3]
    y=690-int(90*(1-p))
    for line in lines:
        tw=text_width(draw,line,f)
        draw.text(((WIDTH-tw)/2+5,y+6),line,font=f,fill=(0,0,0))
        draw.text(((WIDTH-tw)/2,y),line,font=f,fill="white")
        y+=108
    draw_brand(draw,theme,channel)
    return img

def draw_explanation_scene(question,answer,explanation,theme_name,channel,bg_file=None,active_word=-1,pulse=0.0,progress=1.0,q_num=1,total=1):
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.0+0.3*pulse)
    draw=ImageDraw.Draw(img)
    draw_header(draw,theme,q_num,total)
    # Answer ribbon
    rounded_text(draw,(55,175,1025,245),f"✓ {answer}",get_font(34),theme["success"],None,0,25)
    # short question reminder
    qf=get_font(43)
    qlines=wrap_text(question,qf,900)[:2]
    y=300
    for line in qlines:
        tw=text_width(draw,line,qf); draw.text(((WIDTH-tw)/2,y),line,font=qf,fill=(220,225,235)); y+=58

    words=clean_text(explanation or "Bravo !").split()
    f=get_font(58)
    max_w=900
    lines=[]; cur=[]
    for w in words:
        cand=w if not cur else " ".join(cur+[w])
        if text_width(draw,cand,f)<=max_w: cur.append(w)
        else:
            if cur: lines.append(cur)
            cur=[w]
    if cur: lines.append(cur)
    lines=lines[:6]
    total_h=len(lines)*78
    yy=610-total_h/2
    idx=0
    for line in lines:
        widths=[text_width(draw,w,f) for w in line]
        space=text_width(draw," ",f)
        totalw=sum(widths)+space*max(0,len(line)-1)
        x=(WIDTH-totalw)/2
        for w,ww in zip(line,widths):
            active=(idx==active_word)
            col=theme["accent"] if active else "white"
            if active:
                pad=10+int(5*pulse)
                draw.rounded_rectangle((x-pad,yy-7,x+ww+pad,yy+68),radius=16,fill=theme["card"],outline=theme["accent"],width=3)
            draw.text((x,yy),w,font=f,fill=col)
            x+=ww+space; idx+=1
        yy+=78
    # small CTA hint
    draw.text((55,1450),"À retenir",font=get_font(32),fill=theme["accent"])
    draw_brand(draw,theme,channel,progress)
    return img

def draw_vocab_frame(items,idx,langue,theme_name,channel,bg_file=None,phase="mot",timer=None,timer_fraction=1.0,entrance=1.0):
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme)
    draw=ImageDraw.Draw(img)
    rounded_text(draw,(55,70,430,135),f"VOCABULAIRE • {idx+1}/{len(items)}",get_font(32),theme["card"],theme["accent"],2,26)
    item=items[idx]; fr=clean_text(item.get("fr","")); tr=clean_text(item.get("trad",""))
    p=ease_out(entrance)
    fbig=get_font(88)
    y=500+int((1-p)*80)
    draw.text(((WIDTH-text_width(draw,fr,fbig))/2,y),fr,font=fbig,fill=theme["accent"])
    if phase in ("translation","reveal"):
        ft=get_font(58)
        lines=wrap_text(tr,ft,850); yy=760
        for line in lines:
            draw.text(((WIDTH-text_width(draw,line,ft))/2,yy),line,font=ft,fill="white"); yy+=75
    if phase=="countdown" and timer is not None:
        draw_timer(draw,theme,timer,timer_fraction,0.15)
    draw_brand(draw,theme,channel,idx/max(1,len(items)))
    return img

# ------------------------- TTS ------------------------------
async def _tts(text,voice,path,rate="+15%"):
    comm=edge_tts.Communicate(clean_text(text),voice,rate=rate,boundary="WordBoundary")
    audio=bytearray(); words=[]
    async for chunk in comm.stream():
        if chunk["type"]=="audio": audio.extend(chunk["data"])
        elif chunk["type"]=="WordBoundary":
            word=clean_text(chunk.get("text",""))
            if word:
                start=chunk["offset"]/10_000_000; dur=chunk["duration"]/10_000_000
                words.append({"text":word,"start":start,"end":start+dur})
    with open(path,"wb") as f: f.write(audio)
    return words

def run_async(coro):
    try: loop=asyncio.get_event_loop()
    except RuntimeError:
        loop=asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    if loop.is_running():
        nl=asyncio.new_event_loop()
        try: return nl.run_until_complete(coro)
        finally: nl.close()
    return loop.run_until_complete(coro)

def synthesize_audio(text,voice,path,rate="+15%"):
    return run_async(_tts(text,voice,path,rate))

def audio_duration(path):
    res=subprocess.run([get_ffmpeg(),"-i",path],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    m=re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)",res.stderr)
    if not m: return 1.5
    h,mi,sec=m.groups(); return float(h)*3600+float(mi)*60+float(sec)

# ------------------------- SFX ------------------------------
def make_sfx(tmpdir):
    tic=os.path.join(tmpdir,"tic.wav"); ding=os.path.join(tmpdir,"ding.wav")
    with wave.open(tic,"w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(int(44100*.10)):
            v=int(13000*math.sin(2*math.pi*1100*i/44100)*math.exp(-i/800)); f.writeframes(struct.pack("<h",v))
    with wave.open(ding,"w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        for i in range(int(44100*.45)):
            v=int(11500*(math.sin(2*math.pi*1318*i/44100)+math.sin(2*math.pi*1568*i/44100))*math.exp(-i/4500))
            f.writeframes(struct.pack("<h",max(-32767,min(32767,v))))
    return tic,ding

def make_sfx_countdown(tic,tmpdir):
    out=os.path.join(tmpdir,"countdown.wav")
    cmd=[get_ffmpeg(),"-y","-i",tic,"-filter_complex","[0:a]adelay=0|0[a0];[0:a]adelay=1000|1000[a1];[0:a]adelay=2000|2000[a2];[a0][a1][a2]amix=inputs=3:duration=longest","-t","3.0",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return out

def mix_voice_sfx(voice_path,sfx_path,output,delay_ms=0,sfx_volume=0.65):
    filt=f"[1:a]volume={sfx_volume},adelay={delay_ms}|{delay_ms}[s];[0:a][s]amix=inputs=2:duration=longest:dropout_transition=0"
    cmd=[get_ffmpeg(),"-y","-i",voice_path,"-i",sfx_path,"-filter_complex",filt,"-c:a","aac","-b:a","160k","-shortest",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

# ---------------------- Video encoding ----------------------
def make_image_video(frames,output,fps=30):
    list_path=output+".txt"
    with open(list_path,"w",encoding="utf-8") as f:
        for path,duration in frames:
            f.write(f"file '{path.replace(chr(92),'/')}'\n")
            f.write(f"duration {max(0.033,float(duration))}\n")
        if frames: f.write(f"file '{frames[-1][0].replace(chr(92),'/')}'\n")
    cmd=[get_ffmpeg(),"-y","-f","concat","-safe","0","-i",list_path,"-vf",f"fps={fps},format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","22",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def mux_audio(video,audio,output,volume=1.0):
    cmd=[get_ffmpeg(),"-y","-i",video,"-i",audio,"-filter:a",f"volume={volume}","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def make_segment(frames,audio,output,tmpdir,volume=1.0):
    raw=os.path.join(tmpdir,os.path.basename(output)+".raw.mp4")
    make_image_video(frames,raw,FPS); return mux_audio(raw,audio,output,volume)

def concat_videos(clips,output,tmpdir):
    lst=os.path.join(tmpdir,"concat.txt")
    with open(lst,"w",encoding="utf-8") as f:
        for p in clips: f.write(f"file '{p.replace(chr(92),'/')}'\n")
    cmd=[get_ffmpeg(),"-y","-f","concat","-safe","0","-i",lst,"-c","copy","-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def save_frames(frames,tmpdir,prefix):
    out=[]
    for i,(img,dur) in enumerate(frames):
        p=os.path.join(tmpdir,f"{prefix}_{i:04d}.png"); img.save(p); out.append((p,dur))
    return out

def frames_for_audio(audio_path,words,frame_fn,duration=None):
    dur=duration or audio_duration(audio_path)
    if not words: return [(frame_fn(-1,0.0),dur)]
    out=[]
    boundaries=[max(0.0,w["start"]) for w in words]
    if boundaries[0]>0.03: out.append((frame_fn(-1,0.0),min(boundaries[0],dur)))
    for i,start in enumerate(boundaries):
        end=boundaries[i+1] if i+1<len(boundaries) else dur
        if end>start: out.append((frame_fn(i,0.15),end-start))
    return out

# ------------------------ Gemini ----------------------------
def parse_json(text):
    text=text.strip().replace("```json","").replace("```","").strip()
    m=re.search(r"\[.*\]",text,re.DOTALL)
    if not m: raise ValueError("Gemini n'a pas renvoyé un JSON valide.")
    return json.loads(m.group(0))

def normalize_questions(data):
    out=[]
    for q in data:
        opts=q.get("options",[])
        if not isinstance(opts,list) or len(opts)!=4: continue
        ans=str(q.get("reponse_correcte","A")).strip().upper()
        ans=ans[0] if ans and ans[0] in "ABCD" else "A"
        out.append({"question":clean_text(q.get("question","")),"options":[clean_text(x) for x in opts],"reponse_correcte":ans,"explication":clean_text(q.get("explication",""))})
    return out

api_key=st.sidebar.text_input("Clé API Gemini",type="password")
if api_key: genai.configure(api_key=api_key)
voice_rate=st.sidebar.slider("⚡ Vitesse voix",0,30,15)
tts_rate=f"+{voice_rate}%"
MODEL_NAME="gemini-3.6-flash"

# ============================================================
# INTERFACE
# ============================================================
tab1,tab2=st.tabs(["🧠 Quizz TikTok Pro","🗣️ Vocabulaire Pro"])

with tab1:
    st.header("🧠 Quizz TikTok Pro")
    hook_q=st.text_input("Hook","IMPOSSIBLE d'avoir 5 sur 5 !",key="hq")
    channel_q=st.text_input("Nom de la chaîne","@QuizMaster_Pro",key="cq")
    c1,c2=st.columns(2)
    with c1:
        voice_q=VOICES_FR[st.selectbox("Voix",list(VOICES_FR),key="vq")]
        theme_q=st.selectbox("Thème",list(THEMES),key="tq")
    with c2:
        nb_q=st.slider("Nombre de questions",1,5,5,key="nbq")
        th_q=st.text_input("Sujet","Culture Générale",key="thq")
    outro_q=st.text_input("CTA final","Quel est ton score ? Écris-le en commentaire !",key="oq")
    bg_q=st.file_uploader("🖼️ Fond 9:16 (optionnel)",type=["png","jpg","jpeg"],key="bgq")
    mode_q=st.radio("Création",["IA Gemini","Saisie manuelle"],horizontal=True,key="mq")

    if mode_q=="IA Gemini":
        if st.button("✨ Générer les questions",key="genq"):
            if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
            else:
                try:
                    prompt=f'''Génère exactement {nb_q} questions de quiz en français sur {th_q}. Chaque objet doit contenir: question, options (exactement 4 réponses A/B/C/D), reponse_correcte (A/B/C/D), explication courte. Retourne UNIQUEMENT un JSON valide sous forme de tableau.'''
                    res=genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
                    st.session_state.q_data=normalize_questions(parse_json(res.text))[:nb_q]
                    st.success(f"{len(st.session_state.q_data)} questions prêtes.")
                except Exception as e: st.error(f"Erreur Gemini : {e}")
    else:
        st.info("Saisie manuelle rapide")
        qs=[]
        for i in range(5):
            q=st.text_input(f"Q{i+1}",key=f"mq{i}")
            opts=[st.text_input(f"Q{i+1} - {chr(65+j)}",key=f"mo{i}{j}") for j in range(4)]
            ans=st.selectbox(f"Bonne réponse Q{i+1}",["A","B","C","D"],key=f"ma{i}")
            exp=st.text_input(f"Explication Q{i+1}",key=f"me{i}")
            if q and all(opts): qs.append({"question":q,"options":opts,"reponse_correcte":ans,"explication":exp})
        if st.button("📌 Préparer le quiz",key="prepq"): st.session_state.q_data=qs[:nb_q]

    if st.session_state.get("q_data"):
        st.success(f"Quiz prêt : {len(st.session_state.q_data)} question(s).")
        if st.button("🎬 Générer le Short Quiz V4",key="makeq"):
            try:
                with st.spinner("Création du Short dynamique V4..."):
                    with tempfile.TemporaryDirectory() as tmp:
                        tic,ding=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,tmp)
                        clips=[]; total=len(st.session_state.q_data)

                        # Hook: animation courte au lieu d'une carte statique.
                        ha=os.path.join(tmp,"hook.mp3"); synthesize_audio(hook_q,voice_q,ha,tts_rate); hd=audio_duration(ha)
                        hf=save_frames([(draw_hook(hook_q,theme_q,channel_q,bg_q,p),max(0.04,hd/8)) for p in [0.05,0.18,0.35,0.55,0.75,0.92,1.0]],tmp,"hook")
                        hout=os.path.join(tmp,"hook.mp4"); make_segment(hf,ha,hout,tmp); clips.append(hout)

                        for idx,q in enumerate(st.session_state.q_data):
                            corr="ABCD".index(q["reponse_correcte"])
                            # 1) Question: voix + arrivée animée des cartes.
                            qa=os.path.join(tmp,f"q_{idx}.mp3")
                            synthesize_audio(f"Question {idx+1}. {q['question']}",voice_q,qa,tts_rate); qdur=audio_duration(qa)
                            qframes=[]
                            for p in [0.0,0.12,0.25,0.40,0.58,0.76,1.0]:
                                qframes.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=p),min(0.12,max(0.04,qdur/10))))
                            # Le dernier frame porte le reste de la voix.
                            used=sum(d for _,d in qframes); qframes[-1]=(qframes[-1][0],max(0.05,qdur-used+qframes[-1][1]))
                            qo=os.path.join(tmp,f"question_{idx}.mp4"); make_segment(save_frames(qframes,tmp,f"qf_{idx}"),qa,qo,tmp); clips.append(qo)

                            # 2) Réflexion: vrai timer animé 3 -> 2 -> 1, ring qui se vide.
                            countdown_frames=[]
                            for sec in (3,2,1):
                                for step in range(0,10):
                                    frac=1-step/10
                                    pulse=1-step/10
                                    countdown_frames.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=1.0,timer=sec,timer_fraction=frac,pulse=pulse),0.1))
                            co=os.path.join(tmp,f"countdown_{idx}.mp4"); make_segment(save_frames(countdown_frames,tmp,f"timer_{idx}"),countdown_sfx,co,tmp,.9); clips.append(co)

                            # 3) Révélation avec petit zoom vert + ding.
                            reveal_frames=[]
                            for p in [0.0,0.15,0.35,0.60,0.82,1.0]:
                                reveal_frames.append((draw_quiz_frame(q['question'],q['options'],theme_q,idx+1,total,channel_q,bg_q,entrance=1.0,correct_idx=corr,reveal_progress=p,pulse=0.25*(1-p)),0.12))
                            reveal_raw=os.path.join(tmp,f"reveal_voice_{idx}.mp3")
                            exp_text=f"La bonne réponse est {q['reponse_correcte']}. {q['options'][corr]}. {q.get('explication','') or 'Bravo !'}"
                            ea=os.path.join(tmp,f"exp_{idx}.mp3"); ewords=synthesize_audio(exp_text,voice_q,ea,tts_rate); edur=audio_duration(ea)
                            # Ding superposé au début de l'explication.
                            mixed=os.path.join(tmp,f"exp_mix_{idx}.m4a"); mix_voice_sfx(ea,ding,mixed,0,0.8)
                            reveal_dur=min(0.65,max(0.45,edur*0.12))
                            reveal_frames[-1]=(reveal_frames[-1][0],reveal_dur-sum(d for _,d in reveal_frames[:-1]))
                            ro=os.path.join(tmp,f"reveal_{idx}.mp4"); make_segment(save_frames(reveal_frames,tmp,f"reveal_{idx}"),mixed,ro,tmp); clips.append(ro)

                            # 4) Explication: carte verte conservée + mots surlignés au rythme de la voix.
                            tf=[]
                            if ewords:
                                for wi,w in enumerate(ewords):
                                    start=max(0,w["start"]); end=ewords[wi+1]["start"] if wi+1<len(ewords) else edur
                                    if end>start:
                                        tf.append((draw_explanation_scene(q['question'],q['options'][corr],exp_text,theme_q,channel_q,bg_q,active_word=wi,pulse=0.12,progress=(idx+1)/total,q_num=idx+1,total=total),end-start))
                            if not tf: tf=[(draw_explanation_scene(q['question'],q['options'][corr],exp_text,theme_q,channel_q,bg_q,active_word=-1,progress=(idx+1)/total,q_num=idx+1,total=total),edur)]
                            eo=os.path.join(tmp,f"explanation_{idx}.mp4"); make_segment(save_frames(tf,tmp,f"expframe_{idx}"),mixed,eo,tmp,0.92); clips.append(eo)

                        # CTA final animé.
                        oa=os.path.join(tmp,"outro.mp3"); synthesize_audio(outro_q,voice_q,oa,tts_rate); od=audio_duration(oa)
                        of=save_frames([(draw_hook(outro_q,theme_q,channel_q,bg_q,p),max(0.04,od/9)) for p in [0.05,0.18,0.35,0.55,0.75,0.92,1.0]],tmp,"outro")
                        oo=os.path.join(tmp,"outro.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)

                        final=os.path.join(tmp,"quizvideo_pro.mp4"); concat_videos(clips,final,tmp)
                        with open(final,"rb") as f: data=f.read()
                        st.success("✅ Short Quiz V4 terminé.")
                        st.video(data)
                        st.download_button("⬇️ Télécharger quizvideo_pro.mp4",data=data,file_name="quizvideo_pro.mp4",mime="video/mp4",key="dq4")
            except Exception as e:
                st.error(f"Erreur pendant le montage : {e}")

with tab2:
    st.header("🗣️ Vocabulaire Pro")
    hook_v=st.text_input("Hook","Tu prononces mal ces 5 mots !",key="hv")
    channel_v=st.text_input("Nom de la chaîne","@LingoPulse_Daily",key="cv")
    langue_v=st.selectbox("Langue cible",list(VOICES_MAP),key="lv")
    voice_tr_name=st.selectbox("Voix traduction",list(VOICES_MAP[langue_v]),key="vtr")
    voice_tr=VOICES_MAP[langue_v][voice_tr_name]
    theme_v=st.selectbox("Thème",list(THEMES),key="tv")
    bg_v=st.file_uploader("🖼️ Fond 9:16 (optionnel)",type=["png","jpg","jpeg"],key="bgv")
    outro_v=st.text_input("CTA final","Abonne-toi pour apprendre un mot par jour !",key="ov")
    nb_v=st.slider("Nombre de mots",3,5,5,key="nbv")
    th_v=st.text_input("Thème du vocabulaire","Voyage",key="thv")
    if st.button("✨ Générer le vocabulaire par IA",key="genv"):
        if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
        else:
            try:
                prompt=f'''Génère exactement {nb_v} mots français avec leur traduction en {langue_v} sur le thème {th_v}. Retourne UNIQUEMENT un JSON valide: [{{"fr":"...","trad":"..."}}]'''
                res=genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
                st.session_state.v_data=parse_json(res.text)[:nb_v]
                st.success("Vocabulaire prêt.")
            except Exception as e: st.error(f"Erreur Gemini : {e}")
    if st.session_state.get("v_data"):
        if st.button("🎬 Générer la vidéo Vocabulaire V4",key="makev"):
            try:
                with st.spinner("Création du Short vocabulaire V4..."):
                    with tempfile.TemporaryDirectory() as tmp:
                        tic,ding=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,tmp); clips=[]; items=st.session_state.v_data
                        ha=os.path.join(tmp,"vh.mp3"); synthesize_audio(hook_v,VOICES_FR["Henri - Dynamique"],ha,tts_rate); hd=audio_duration(ha)
                        hf=save_frames([(draw_hook(hook_v,theme_v,channel_v,bg_v,p),max(.04,hd/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]],tmp,"vh")
                        ho=os.path.join(tmp,"vh.mp4"); make_segment(hf,ha,ho,tmp); clips.append(ho)
                        for idx,item in enumerate(items):
                            fa=os.path.join(tmp,f"fr_{idx}.mp3"); synthesize_audio(item['fr'],VOICES_FR["Henri - Dynamique"],fa,tts_rate); fd=audio_duration(fa)
                            ff=save_frames([(draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"mot",entrance=p),max(.04,fd/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]],tmp,f"vf_{idx}")
                            fo=os.path.join(tmp,f"fr_{idx}.mp4"); make_segment(ff,fa,fo,tmp); clips.append(fo)
                            cframes=[]
                            for sec in (3,2,1):
                                for step in range(10): cframes.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"countdown",sec,1-step/10,1.0),.1))
                            co=os.path.join(tmp,f"count_{idx}.mp4"); make_segment(save_frames(cframes,tmp,f"vc_{idx}"),countdown_sfx,co,tmp,.9); clips.append(co)
                            ta=os.path.join(tmp,f"tr_{idx}.mp3"); tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate); td=audio_duration(ta)
                            tf=[]
                            if tw:
                                for wi,w in enumerate(tw):
                                    end=tw[wi+1]['start'] if wi+1<len(tw) else td
                                    if end>w['start']:
                                        tf.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation",entrance=1.0),end-w['start']))
                            if not tf: tf=[(draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation",entrance=1.0),td)]
                            tro=os.path.join(tmp,f"tr_{idx}.mp4"); make_segment(save_frames(tf,tmp,f"trf_{idx}"),ta,tro,tmp); clips.append(tro)
                        oa=os.path.join(tmp,"vo.mp3"); synthesize_audio(outro_v,VOICES_FR["Henri - Dynamique"],oa,tts_rate); od=audio_duration(oa)
                        of=save_frames([(draw_hook(outro_v,theme_v,channel_v,bg_v,p),max(.04,od/7)) for p in [.05,.18,.35,.55,.75,.92,1.0]],tmp,"vo")
                        oo=os.path.join(tmp,"vo.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)
                        final=os.path.join(tmp,"vocabulaire_pro.mp4"); concat_videos(clips,final,tmp)
                        with open(final,"rb") as f: data=f.read()
                        st.success("✅ Short Vocabulaire V4 terminé.")
                        st.video(data)
                        st.download_button("⬇️ Télécharger vocabulaire_pro.mp4",data=data,file_name="vocabulaire_pro.mp4",mime="video/mp4",key="dv4")
            except Exception as e: st.error(f"Erreur pendant le montage : {e}")
