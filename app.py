import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import tempfile
import math
import time
import random
import csv
import io
import zipfile
import hashlib
import gc
import wave
import struct
import subprocess
import base64
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# SUSPENSELINGO — STUDIO
# V32.3.4 — palettes lumineuses, aperçu/éditeur mis à jour; moteur vidéo conservé.
# V19 — Motivation milieu supprimée; TTS nettoyé; accroches localisées; suspense audio renforcé
# V23 — Stabilisation interface : colonne droite sticky, aperçu live, génération pro. Aucune fonctionnalité vidéo supprimée.
# ============================================================
st.set_page_config(page_title="SuspenseLingo Studio", page_icon="🎬", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg,#f8fbff 0%,#eef3fa 55%,#f7f4ff 100%); color:#172033; }
[data-testid="stMain"] { background: transparent; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0b1630 0%,#101d3d 58%,#111a33 100%); border-right: 1px solid #1f3159; }
[data-testid="stSidebar"] * { color:#eef4ff !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:#dbe7ff !important; }
[data-testid="stSidebar"] .stRadio label { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10); border-radius:14px; padding:8px 10px; margin:4px 0; }
label, [data-testid="stMarkdownContainer"] { color:#253047; }
[data-testid="stHeader"] { background: rgba(255,255,255,.78); }
.block-container { max-width: 1220px; padding-top: .55rem; padding-bottom: 1rem; }
h1, h2, h3 { letter-spacing: -0.02em; color:#111827; }
[data-testid="stTabs"] button { font-weight: 800; font-size: 1.02rem; color:#334155; padding:10px 18px; }
[data-testid="stTabs"] [aria-selected="true"] { color:#6d4aff !important; border-bottom-color:#6d4aff !important; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea { border-radius: 14px !important; background:#ffffff !important; color:#172033 !important; border-color:#cbd5e1 !important; }
[data-baseweb="select"] > div { background:#ffffff !important; border-color:#cbd5e1 !important; color:#172033 !important; border-radius:14px !important; }
[data-testid="stButton"] button { border-radius: 14px; min-height: 2.8rem; font-weight: 700; border: 1px solid #cbd5e1; background: linear-gradient(135deg,#ffffff,#f3f6fa); color:#172033; box-shadow:0 4px 12px rgba(15,23,42,.06); }
[data-testid="stButton"] button:hover { border-color:#7c8cff; transform: translateY(-1px); box-shadow:0 8px 18px rgba(15,23,42,.10); }
[data-testid="stFileUploaderDropzone"] { border: 1px dashed #b9c5d6; border-radius: 16px; background: #ffffff; }
.qvp-card { padding: 9px 12px; border: 1px solid #dbe2ec; border-radius: 18px; background: #ffffff; box-shadow: 0 10px 28px rgba(15,23,42,.07); margin: 4px 0 8px; }
.qvp-small { color:#64748b; font-size:.9rem; }
.qvp-side-brand { display:flex; gap:12px; align-items:center; padding:8px 2px 18px; }
.qvp-logo { width:42px; height:42px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:25px; font-weight:900; background:linear-gradient(135deg,#7b4dff,#36b8e8); color:white !important; box-shadow:0 8px 24px rgba(83,67,180,.35); }
.qvp-side-title { font-size:1.18rem; font-weight:800; color:#fff !important; }
.qvp-side-sub { font-size:.72rem; color:#b9c8e8 !important; margin-top:2px; }
.qvp-side-note { margin-top:18px; padding:14px; border:1px solid rgba(255,255,255,.13); border-radius:16px; background:linear-gradient(135deg,rgba(124,77,255,.18),rgba(42,180,216,.10)); font-size:.78rem; line-height:1.45; }
.qvp-hero { display:flex; justify-content:space-between; align-items:center; gap:14px; padding:12px 16px; border:1px solid #dbe4f0; border-radius:24px; background:rgba(255,255,255,.84); box-shadow:0 14px 36px rgba(31,48,82,.08); margin-bottom:18px; }
.qvp-hero h1 { margin:2px 0 3px; font-size:1.55rem; }
.qvp-hero p { margin:0; color:#66748c; }
.qvp-kicker { color:#6751e8; font-size:.78rem; font-weight:800; letter-spacing:.12em; }
.qvp-hero-pill { padding:11px 16px; border-radius:999px; background:#f0edff; color:#5c45d5; font-weight:800; white-space:nowrap; }
.qvp-flow { display:flex; align-items:center; justify-content:center; gap:14px; flex-wrap:wrap; padding:13px 18px; border:1px solid #e1e7f0; border-radius:18px; background:#fff; color:#334155; margin:0 0 20px; box-shadow:0 7px 20px rgba(15,23,42,.04); }
.qvp-flow b { color:#8b78ee; }
.qvp-mini-card { min-height:94px; padding:18px; border:1px solid #ddd7ff; border-radius:17px; background:linear-gradient(135deg,#faf9ff,#f2f8ff); color:#334155; }
.qvp-mini-card span { color:#64748b; font-size:.88rem; }
.qvp-preview-placeholder { height:250px; border:1px dashed #cbd5e1; border-radius:18px; display:flex; align-items:center; justify-content:center; text-align:center; color:#64748b; background:#f8fafc; }
.qvp-economy { padding:13px 16px; border-radius:15px; border:1px solid #d6e7f7; background:#eef8ff; color:#28506d; margin:10px 0 16px; }
.qvp-preview-sticky { z-index:20; }
[data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) > [data-testid="column"]:last-child { position:sticky; top:72px; align-self:flex-start; z-index:30; }
.qvp-preview-panel { padding:14px; border:1px solid #dbe4f0; border-radius:20px; background:rgba(255,255,255,.96); box-shadow:0 14px 34px rgba(15,23,42,.10); }
.qvp-preview-title { font-weight:800; color:#172033; font-size:1.05rem; margin-bottom:8px; }
.qvp-preview-note { color:#64748b; font-size:.82rem; margin-bottom:10px; }
.qvp-editor-tabs [data-testid="stTabs"] button { font-size:.86rem !important; padding:7px 10px !important; }
.qvp-editor-tabs { margin-bottom:8px; }


/* V8.1 — éditeur compact + aperçu plus proche */
.qvp-editor-tabs [data-testid="stVerticalBlock"] { gap: 0.28rem; }
.qvp-editor-tabs [data-testid="stHorizontalBlock"] { gap: 0.45rem; }
.qvp-editor-tabs .stSlider { margin-bottom: -0.15rem; }
.qvp-editor-tabs .stCheckbox { margin-bottom: -0.25rem; }
.qvp-editor-tabs .stCaption { margin-top: -0.2rem; }
.qvp-preview-sticky { top: 1rem !important; }
.qvp-preview-panel { margin-bottom: 0.35rem; }

/* V8.3 — studio compact / navigation always visible */
/* Main module switcher: make the first tab bar look like a real app navigation. */
[data-testid="stMain"] [data-testid="stTabs"]:not(.qvp-editor-tabs [data-testid="stTabs"]) > div:first-child {background:rgba(255,255,255,.97);border:1px solid #d9e2ef;border-radius:16px;padding:6px 8px;box-shadow:0 8px 24px rgba(15,23,42,.08);position:sticky;top:4px;z-index:100;}
[data-testid="stMain"] [data-testid="stTabs"]:not(.qvp-editor-tabs [data-testid="stTabs"]) button {font-weight:850 !important;font-size:1rem !important;padding:10px 14px !important;border-radius:11px !important;}

[data-testid="stAppViewContainer"] .main .block-container {max-width:1500px !important; padding-top:0.55rem !important; padding-bottom:0.7rem !important;}
[data-testid="stHeader"] {background:transparent !important;}
.qvp-studio-nav {position:sticky;top:0;z-index:100;background:rgba(255,255,255,.96);backdrop-filter:blur(12px);border:1px solid #d9e2ef;border-radius:16px;padding:6px 8px;margin:0 0 10px;box-shadow:0 8px 24px rgba(15,23,42,.08);}
.qvp-studio-nav [data-testid="stTabs"] {margin:0 !important;}
.qvp-studio-nav [data-testid="stTabs"] [role="tablist"] {gap:6px;border-bottom:0 !important;}
.qvp-studio-nav [data-testid="stTabs"] button {flex:1;font-weight:800;font-size:1rem !important;padding:10px 12px !important;border-radius:11px !important;border:1px solid transparent !important;}
.qvp-studio-nav [data-testid="stTabs"] button[aria-selected="true"] {background:#172033 !important;color:#fff !important;border-color:#172033 !important;}
.qvp-studio-nav [data-testid="stTabs"] button[aria-selected="false"] {background:#f3f6fb !important;color:#334155 !important;}
.qvp-studio-nav [data-testid="stTabs"] > div:last-child {display:none !important;}
.qvp-hero {padding:10px 14px !important;margin:0 0 8px !important;min-height:0 !important;}
.qvp-card {padding:8px 12px !important;margin:5px 0 !important;}
.qvp-editor-tabs {border:1px solid #dbe4f0;border-radius:16px;padding:8px;background:#fff;}
.qvp-editor-tabs [data-testid="stTabs"] [role="tablist"] {gap:4px;overflow-x:auto;white-space:nowrap;border-bottom:1px solid #e2e8f0;}
.qvp-editor-tabs [data-testid="stTabs"] button {font-weight:750 !important;font-size:.78rem !important;padding:7px 8px !important;border-radius:9px !important;}
.qvp-editor-tabs [data-testid="stTabs"] button[aria-selected="true"] {background:#eef3fa !important;}
.qvp-preview-panel {padding:9px 12px !important;}
.qvp-preview-note {margin-bottom:5px !important;}
.qvp-actionbar {position:sticky;bottom:8px;z-index:90;background:rgba(255,255,255,.97);backdrop-filter:blur(10px);border:1px solid #d9e2ef;border-radius:14px;padding:7px;margin-top:10px;box-shadow:0 8px 22px rgba(15,23,42,.10);}
 .qvp-fast-note{color:#52637a;font-size:.72rem;margin:2px 0 5px;}

/* V8.5 Studio : interface compacte, pensée pour 100% de zoom. */
.qvp-studio-header{display:flex;align-items:center;gap:12px;padding:6px 10px;margin:0 0 6px;border-bottom:1px solid #dbe4f0;font-size:.92rem;color:#172033}
.qvp-studio-header span{padding:4px 9px;border-radius:999px;background:#172033;color:#fff;font-weight:800;font-size:.75rem}
.qvp-studio-header small{margin-left:auto;color:#64748b;font-size:.72rem}
.qvp-hero{display:none !important}
[data-testid="stMain"] .stCaption{font-size:.72rem !important;margin-top:2px !important;margin-bottom:4px !important}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]{gap:.38rem !important}
.qvp-preview-panel{padding:8px 10px !important;border-radius:12px !important}
.qvp-preview-title{font-size:.88rem !important;margin-bottom:3px !important}
.qvp-preview-note{font-size:.68rem !important;margin-bottom:4px !important}
.qvp-actionbar{padding:5px 8px !important;margin-top:5px !important}


/* ===== QuizVideo Pro Studio V14 — refonte visuelle complète ===== */
.qvp-studio-header{padding:10px 14px!important;margin:0 0 8px!important;border:1px solid #d8e2ef!important;border-radius:14px!important;background:linear-gradient(90deg,#fff,#f6f9fd)!important;box-shadow:0 5px 18px rgba(15,23,42,.06)!important;font-size:1rem!important}
.qvp-studio-header b{font-size:1.02rem!important}
.qvp-studio-header span{padding:5px 11px!important;font-size:.76rem!important;letter-spacing:.02em}
.qvp-studio-header small{font-size:.72rem!important}
/* Champs principaux plus lisibles */
[data-testid="stMain"] label{font-weight:650!important;color:#334155!important}
[data-testid="stMain"] input,[data-testid="stMain"] textarea,[data-testid="stMain"] [data-baseweb="select"]>div{border-radius:10px!important}
/* Editeur : contraste, espacement et onglets */
.qvp-editor-title{font-size:1rem!important;font-weight:850!important;color:#172033!important;margin:2px 0 8px!important}
[data-testid="stVerticalBlock"]:has(.qvp-editor-title){background:#fff!important}
[data-testid="stTabs"] [role="tablist"]{scrollbar-width:thin!important}
[data-testid="stTabs"] button{transition:all .15s ease!important}
/* Aperçu plus présent */
.qvp-preview-panel{border:1px solid #cfdbea!important;background:linear-gradient(180deg,#ffffff,#f8fbff)!important;box-shadow:0 10px 28px rgba(15,23,42,.09)!important}
.qvp-preview-title{font-size:.98rem!important;color:#172033!important}
.qvp-preview-note{font-size:.72rem!important;color:#64748b!important}
/* Image de preview : bordure premium */
[data-testid="stImage"] img{border-radius:12px!important;border:1px solid #cbd5e1!important;box-shadow:0 12px 30px rgba(15,23,42,.13)!important}
/* Actions */
.qvp-actionbar{box-shadow:0 10px 25px rgba(15,23,42,.12)!important}
/* Les zones principales doivent rester compactes à 100% de zoom */
[data-testid="stMain"] [data-testid="stHorizontalBlock"]{align-items:flex-start!important}
/* Slider plus lisible */
[data-testid="stSlider"] [role="slider"]{transform:scale(1.05)!important}
/* Bouton principal de génération */
button[kind="primary"]{font-weight:850!important}


/* V14 : interface Studio plus lisible et hiérarchisée */
.qvp-studio-shell{max-width:1500px;margin:0 auto;}
.qvp-studio-header{padding:11px 16px!important;margin:0 0 10px!important;border:1px solid #d5dfeb!important;border-radius:16px!important;background:linear-gradient(100deg,#ffffff,#f5f8fc)!important;box-shadow:0 7px 22px rgba(15,23,42,.07)!important;font-size:1.02rem!important;}
.qvp-studio-header b{font-size:1.08rem!important;color:#0f172a!important;}
.qvp-studio-header span{padding:6px 12px!important;font-size:.78rem!important;}
.qvp-studio-header small{font-size:.74rem!important;}
.qvp-section-card{border:1px solid #d9e3ef;border-radius:14px;padding:10px 12px;background:linear-gradient(180deg,#ffffff,#f8fbff);box-shadow:0 4px 16px rgba(15,23,42,.045);}
.qvp-section-title{font-size:.75rem;letter-spacing:.06em;font-weight:850;color:#64748b;margin-bottom:7px;}
.qvp-editor-wrap{border:1px solid #d4deea;border-radius:16px;background:#fff;padding:8px 10px;box-shadow:0 7px 24px rgba(15,23,42,.06);}
.qvp-editor-title{font-size:1.04rem!important;font-weight:900!important;color:#111827!important;margin:2px 0 8px!important;}
.qvp-editor-subtitle{font-size:.72rem;color:#64748b;margin:-4px 0 8px;}
.qvp-editor-wrap [data-testid="stTabs"] [role="tablist"]{gap:4px!important;overflow-x:auto!important;padding-bottom:2px;}
.qvp-editor-wrap [data-testid="stTabs"] button{font-size:.76rem!important;font-weight:750!important;min-height:34px!important;padding:5px 9px!important;border-radius:9px 9px 0 0!important;}
.qvp-editor-wrap [data-testid="stTabs"] [aria-selected="true"]{background:#eef4fb!important;color:#0f172a!important;}
.qvp-editor-wrap label{font-size:.78rem!important;font-weight:700!important;color:#334155!important;}
.qvp-editor-wrap [data-testid="stSlider"]{padding-top:1px!important;padding-bottom:1px!important;}
.qvp-editor-wrap [data-testid="stHorizontalBlock"]{gap:.55rem!important;}
.qvp-preview-sticky{position:sticky;top:10px;z-index:25;}
.qvp-preview-panel{border:1px solid #c9d6e6!important;background:linear-gradient(180deg,#ffffff,#f5f9fd)!important;box-shadow:0 12px 30px rgba(15,23,42,.10)!important;border-radius:16px!important;padding:10px 12px!important;}
.qvp-preview-title{font-size:1rem!important;font-weight:850!important;color:#0f172a!important;margin-bottom:2px!important;}
.qvp-preview-note{font-size:.72rem!important;color:#64748b!important;margin-bottom:4px!important;}
.qvp-preview-stage{display:flex;justify-content:center;align-items:flex-start;padding:6px 0 2px;}
.qvp-preview-stage [data-testid="stImage"]{width:min(100%,520px)!important;margin:0 auto!important;}
.qvp-preview-stage img{border-radius:16px!important;border:1px solid #cbd5e1!important;box-shadow:0 16px 36px rgba(15,23,42,.15)!important;}
.qvp-preview-stage{margin-bottom:6px!important;}

.qvp-actionbar-v11{position:sticky;bottom:10px;z-index:60;margin-top:12px;padding:8px;background:rgba(248,250,252,.94);backdrop-filter:blur(12px);border:1px solid #cdd8e5;border-radius:16px;box-shadow:0 14px 30px rgba(15,23,42,.14);}
.qvp-actionbar-v11 .qvp-action-label{font-size:.68rem;color:#64748b;font-weight:750;text-align:center;margin:0 0 4px;}
.qvp-actionbar-v11 button{min-height:42px!important;font-weight:820!important;}
.qvp-content-box{border:1px solid #d9e3ef;border-radius:14px;padding:4px 10px;background:#fff;}
.qvp-content-box summary{font-weight:850!important;color:#0f172a!important;}
@media (min-width: 1100px){
  .qvp-main-layout{display:block;}
}

/* V12 — aperçu réduit + édition directe par clic */
.qvp-main-layout{gap:18px!important}
.qvp-preview-stage{display:flex!important;justify-content:center!important;}
.qvp-preview-stage [data-testid="stImage"]{width:100%!important;max-width:360px!important;}
.qvp-preview-stage img{max-width:360px!important;height:auto!important;}
.qvp-click-preview{position:relative;background-size:100% 100%;background-repeat:no-repeat;border-radius:16px;box-shadow:0 18px 38px rgba(15,23,42,.18);border:1px solid #cbd5e1;overflow:hidden;margin:8px auto 10px;}
.qvp-hotspot{position:absolute;display:flex;align-items:flex-start;justify-content:flex-start;text-decoration:none!important;border:1px dashed rgba(255,255,255,.25);background:rgba(0,0,0,.02);border-radius:7px;transition:.15s ease;}
.qvp-hotspot span{font-size:8px;line-height:1;padding:3px 5px;border-radius:0 0 5px 0;background:rgba(15,23,42,.76);color:white;opacity:.55;font-weight:750;}
.qvp-hotspot:hover,.qvp-hotspot.selected{border:2px solid #ffcd40;background:rgba(255,205,64,.08);box-shadow:0 0 0 2px rgba(255,205,64,.18) inset;z-index:4;}
.qvp-hotspot.selected span{opacity:1;background:#ffcd40;color:#111827;}
.qvp-interactive-note{font-size:.72rem;color:#64748b;text-align:center;margin:-2px auto 7px;}
.qvp-selected-card{border:1px solid #d8e2ee;border-radius:12px;padding:8px 10px;background:#f8fbff;margin:5px 0 8px;}
.qvp-selected-title{font-size:.74rem;font-weight:850;color:#334155;margin-bottom:6px;text-align:center;}
.qvp-movegrid [data-testid="stButton"] button{min-height:32px!important;padding:3px 5px!important;font-size:.78rem!important;border-radius:9px!important;}
.qvp-anim-caption{text-align:center;font-size:.7rem;color:#64748b;margin:3px 0 5px;}


/* V21 — interface compacte et workflow linéaire */
.qvp-studio-header{margin-top:2px!important;margin-bottom:8px!important;}
.qvp-section-card{padding:9px 12px!important;}
.qvp-section-title{margin-bottom:6px!important;}
.qvp-actionbar-v11{margin-top:4px!important;margin-bottom:6px!important;}
.qvp-preview-sticky{top:8px!important;}

/* V27 — vrai poste de travail Studio : éditeur et aperçu côte à côte */
.qvp-studio-workspace-title{margin:22px 0 10px;font-size:1.05rem;font-weight:800;color:#0f172a;}
.qvp-studio-workspace-note{margin:0 0 12px;color:#64748b;font-size:.88rem;}
.qvp-studio-workspace-anchor{height:1px;}
[data-testid="stHorizontalBlock"]:has(.qvp-studio-workspace-anchor) > [data-testid="column"]:last-child{position:sticky!important;top:82px!important;align-self:flex-start!important;z-index:35!important;}
@media (max-width:1050px){[data-testid="stHorizontalBlock"]:has(.qvp-studio-workspace-anchor) > [data-testid="column"]:last-child{position:static!important;}}

/* V22 — Studio 60/40 : réglages à gauche, aperçu sticky à droite */
.block-container{max-width:1700px!important;padding-left:1.2rem!important;padding-right:1.2rem!important;}
.qvp-studio-shell{max-width:none!important;width:100%!important;}
.qvp-two-col{width:100%;}
.qvp-settings-card{border:1px solid #d8e2ee;border-radius:16px;padding:14px 15px;background:linear-gradient(180deg,#ffffff,#f7faff);box-shadow:0 6px 20px rgba(15,23,42,.055);margin:0 0 12px;}
.qvp-settings-card .qvp-card-heading{font-size:.84rem;font-weight:900;letter-spacing:.035em;color:#172033;margin:0 0 9px;display:flex;align-items:center;gap:7px;}
.qvp-settings-card .qvp-card-sub{font-size:.72rem;color:#64748b;margin:-5px 0 9px;}
.qvp-settings-card .qvp-section-title{margin-bottom:8px!important;}
.qvp-settings-card .qvp-content-box{margin-top:0!important;}
.qvp-preview-column{position:sticky;top:1rem;align-self:flex-start;z-index:30;}
/* V25 — aperçu permanent en face de l’éditeur, sans scroll interne. */
[data-testid="column"]:has(.qvp-preview-anchor){position:sticky!important;top:1rem!important;align-self:flex-start!important;z-index:40!important;min-width:0!important;}

.qvp-preview-column > div{width:100%;}
/* V23 — la colonne entière de droite reste visible pendant le défilement. */
[data-testid="column"]:has(.qvp-preview-anchor){
  position:sticky!important;
  top:1rem!important;
  align-self:flex-start!important;
  z-index:40!important;
}
.qvp-preview-column .qvp-preview-panel{margin-bottom:8px!important;}
.qvp-preview-column .qvp-preview-stage{padding-top:4px!important;}
.qvp-preview-column .qvp-selected-card{margin-top:6px!important;}
.qvp-preview-column .qvp-actionbar-v11{position:static!important;margin-top:9px!important;}
.qvp-preview-column .qvp-secondary-actions{margin-top:7px;}
.qvp-preview-column button[kind="primary"]{min-height:48px!important;font-size:.96rem!important;box-shadow:0 10px 24px rgba(91,73,190,.18)!important;}
/* V23 — le bouton principal reste clairement identifiable. */
.qvp-preview-column button[kind="primary"]{background:linear-gradient(135deg,#6d4aff,#3b82f6)!important;color:#fff!important;border-color:#5b45d6!important;}
.qvp-main-grid [data-testid="stHorizontalBlock"]{align-items:flex-start!important;}
.qvp-main-grid{margin-top:4px!important;}
.qvp-main-grid .qvp-editor-wrap{margin-bottom:0!important;}
.qvp-main-grid .qvp-settings-card:last-child{margin-bottom:0!important;}

/* V25 — contraste + hiérarchie + aperçu permanent en face de l’éditeur */
.qvp-studio-header{
  background:linear-gradient(135deg,#0b1220,#111c31)!important;
  border:1px solid #33445f!important;
  color:#f8fafc!important;
  box-shadow:0 10px 26px rgba(2,6,23,.20)!important;
}
.qvp-studio-header b{color:#ffffff!important;font-weight:900!important;letter-spacing:.02em!important;}
.qvp-studio-header span{background:#1b2b46!important;border:1px solid #4b6282!important;color:#f8fafc!important;font-weight:850!important;}
.qvp-studio-header small{color:#b9c7da!important;}
.qvp-settings-card{border-color:#b8c8dc!important;background:linear-gradient(180deg,#ffffff,#f4f7fb)!important;box-shadow:0 7px 22px rgba(15,23,42,.075)!important;}
.qvp-settings-card .qvp-card-heading{color:#0b1220!important;}
.qvp-settings-card .qvp-card-sub{color:#475569!important;}
.qvp-editor-wrap{border:1px solid #aebfd5!important;background:#fbfdff!important;box-shadow:0 8px 24px rgba(15,23,42,.08)!important;}
.qvp-editor-title{color:#08111f!important;font-size:1.12rem!important;font-weight:950!important;letter-spacing:.02em!important;}
.qvp-editor-subtitle{color:#475569!important;}
.qvp-editor-wrap [data-testid="stTabs"] button{color:#25364d!important;border:1px solid transparent!important;font-weight:800!important;}
.qvp-editor-wrap [data-testid="stTabs"] [aria-selected="true"]{background:#17263d!important;color:#ffffff!important;border-color:#3f5878!important;}
.qvp-editor-wrap [data-testid="stTabs"] button:hover{background:#e6edf6!important;color:#0b1220!important;}
.qvp-editor-wrap label{color:#17263d!important;}
.qvp-preview-panel{border:1px solid #aebfd5!important;background:linear-gradient(180deg,#f8fbff,#eef3f9)!important;}
.qvp-preview-title{color:#08111f!important;font-weight:950!important;}
.qvp-preview-note{color:#475569!important;}
.qvp-preview-column{min-width:0!important;}
[data-testid="column"]:has(.qvp-preview-anchor) .qvp-preview-panel{position:relative!important;}
[data-testid="column"]:has(.qvp-preview-anchor) .qvp-click-preview{border:2px solid #8da2bd!important;box-shadow:0 18px 38px rgba(2,6,23,.22)!important;}
[data-testid="column"]:has(.qvp-preview-anchor) button[kind="primary"]{background:linear-gradient(135deg,#4f46e5,#2563eb)!important;border-color:#3730a3!important;box-shadow:0 12px 28px rgba(37,99,235,.28)!important;}
[data-testid="column"]:has(.qvp-preview-anchor) button[kind="primary"]:hover{filter:brightness(1.08)!important;}

@media (max-width: 900px){
  .block-container{padding-left:.65rem!important;padding-right:.65rem!important;}
  .qvp-preview-column{position:static!important;}
  [data-testid="column"]:has(.qvp-preview-anchor){position:static!important;height:auto!important;max-height:none!important;overflow:visible!important;}
}


/* V24.6 — UX cible : l’aperçu reste à l’écran pendant l’édition à gauche.
   Le scroll appartient au st.container(height fixe supprimée) ; ne pas le transformer en
   scroll de colonne, afin que le panneau puisse aller jusqu’au dernier bouton. */
[data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) > [data-testid="column"]:last-child {
  position:sticky !important;
  top:1rem !important;
  align-self:flex-start !important;
  z-index:40 !important;
  min-width:0 !important;
}
@media (max-width: 900px) {
  [data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) > [data-testid="column"]:last-child {
    position:static !important;
  }
}

/* V26 — vrai mode édition : l'aperçu reste devant l'Éditeur Studio.
   Aucun conteneur à hauteur fixe et aucun scroll interne. */
[data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) {
  align-items:flex-start !important;
}
[data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) > [data-testid="column"]:last-child {
  position:sticky !important;
  top:1rem !important;
  align-self:flex-start !important;
  height:auto !important;
  max-height:none !important;
  overflow:visible !important;
  z-index:80 !important;
}
[data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) > [data-testid="column"]:last-child .qvp-preview-column {
  position:static !important;
}
.qvp-preview-anchor {height:1px !important; margin:0 !important; padding:0 !important;}
@media (max-width: 900px) {
  [data-testid="stHorizontalBlock"]:has(.qvp-preview-anchor) > [data-testid="column"]:last-child {
    position:static !important;
  }
}
</style>
""", unsafe_allow_html=True)

WIDTH, HEIGHT, FPS = 1080, 1920, 24
COUNTDOWN_STEPS = 24
REVEAL_MAX_STEPS = 12
VIDEO_PRESET = "superfast"
VIDEO_CRF = 21
_BASE_CACHE = {}

THEMES = {
    "Bleu Nuit & Or": {"bg": (24, 45, 82), "bg2": (48, 88, 145), "card": (29, 58, 101), "card2": (42, 79, 132), "accent": (255, 194, 52), "success": (20, 205, 132), "danger": (255, 83, 99), "muted": (241, 247, 255)},
    "Chocolat Noir & Or": {"bg": (69, 39, 29), "bg2": (143, 83, 47), "card": (91, 52, 35), "card2": (125, 72, 43), "accent": (255, 205, 92), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (255, 232, 203)},
    "Violet Neon": {"bg": (49, 25, 82), "bg2": (111, 53, 153), "card": (65, 36, 105), "card2": (94, 51, 137), "accent": (255, 133, 255), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (245, 220, 255)},
    "Emeraude Mint": {"bg": (15, 61, 49), "bg2": (30, 127, 95), "card": (23, 78, 63), "card2": (35, 105, 81), "accent": (102, 255, 199), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (211, 255, 238)},
    "Noir Carbone": {"bg": (33, 47, 65), "bg2": (73, 99, 128), "card": (40, 61, 82), "card2": (55, 79, 103), "accent": (130, 211, 255), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (225, 241, 255)},
}

# V29 — nouvelles palettes premium, sans modifier les thèmes existants.
THEMES.update({
    "Midnight Sapphire": {"bg": (21, 43, 88), "bg2": (38, 91, 165), "card": (28, 61, 112), "card2": (43, 83, 142), "accent": (94, 211, 255), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (213, 238, 255)},
    "Crimson Noir": {"bg": (72, 19, 39), "bg2": (143, 37, 68), "card": (87, 27, 48), "card2": (123, 35, 61), "accent": (255, 119, 145), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (255, 220, 230)},
    "Royal Violet": {"bg": (44, 24, 81), "bg2": (93, 48, 145), "card": (58, 35, 99), "card2": (82, 48, 128), "accent": (203, 157, 255), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (241, 224, 255)},
    "Black Gold": {"bg": (54, 42, 21), "bg2": (113, 83, 32), "card": (69, 53, 26), "card2": (98, 73, 34), "accent": (255, 220, 105), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (255, 242, 201)},
    "Arctic Cyan": {"bg": (19, 55, 77), "bg2": (30, 111, 143), "card": (25, 72, 95), "card2": (34, 95, 121), "accent": (102, 239, 255), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (219, 251, 255)},
    "Cyber Pink": {"bg": (68, 20, 71), "bg2": (139, 39, 127), "card": (83, 28, 81), "card2": (119, 40, 111), "accent": (255, 139, 229), "success": (46, 218, 123), "danger": (255, 83, 99), "muted": (255, 224, 248)},
})

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
# Option 1 — Bleu Nuit & Or : spécification CSS exacte pour le preview HTML/Tailwind.
# Le rendu vidéo actuel reste PIL/Pillow ; cette classe sert de contrat visuel commun
# pour les wrappers Streamlit/HTML sans remplacer le moteur vidéo existant.
BLUE_GOLD_PREVIEW_CSS = r"""
/* Bleu Nuit & Or — preview 9:16, largeur fluide et safe-zone haute */
.video-canvas, .quiz-preview {
    width: 100%;
    max-width: 1080px;
    aspect-ratio: 9 / 16;
    box-sizing: border-box;
    background: #0B1021;
    color: #FFFFFF;
    padding: 170px 40px 200px 40px;
    overflow: hidden;
}
.quiz-header {
    width: 100%;
    box-sizing: border-box;
    margin-top: 0;
    background:#151D33; border:2px solid #2B3960; border-radius:20px;
    display:flex; align-items:center; justify-content:space-between;
}
.quiz-header .brand { color:#F59E0B; font-weight:700; }
.quiz-header .title { color:#FFFFFF; font-weight:700; text-align:center; }
.quiz-header .counter { background:#F59E0B; color:#000000; border-radius:9999px; font-weight:800; }
.question-card {
    width:100%; box-sizing:border-box; max-width:100%;
    background:#151C33; border:2px solid #334155; border-radius:24px;
    padding:20px; color:#FFFFFF; font-weight:700; text-align:center;
    font-size:clamp(1rem, 2.5vw, 1.3rem);
    overflow-wrap:anywhere; word-break:normal;
}
.options-list { width:100%; box-sizing:border-box; max-width:100%; display:flex; flex-direction:column; }
.option-item {
    width:100%; box-sizing:border-box; max-width:100%;
    background:#1E293B; border:2px solid #334155; border-radius:20px; color:#E2E8F0;
    overflow-wrap:anywhere; word-break:normal;
}
.option-item .letter { background:#F59E0B; color:#000000; border-radius:9999px; font-weight:800; }
.option-correct { background:#10B981; border-color:#34D399; color:#FFFFFF; }
.option-correct .letter { background:#FFFFFF; color:#059669; }
.option-correct .checkmark { color:#FFFFFF; }
.timer-badge { background:#1E293B; border:4px solid #F59E0B; color:#F59E0B; border-radius:9999px; text-align:center; }
.explanation-card { width:100%; box-sizing:border-box; max-width:100%; background:#0F172A; border:2px solid #F59E0B; border-radius:20px; color:#F8FAFC; text-align:center; }
.explanation-card .title { color:#F59E0B; font-weight:800; }
"""

def get_blue_gold_preview_css():
    return BLUE_GOLD_PREVIEW_CSS

QUIZ_LANGUAGES = {
    "Français": VOICES_FR,
    **VOICES_MAP,
}
QUIZ_LANGUAGE_LABELS = {"Français":"français","Anglais":"anglais","Espagnol":"espagnol","Arabe":"arabe","Allemand":"allemand","Italien":"italien"}

# V29 — profils de narration. Ils utilisent les voix déjà disponibles et ajoutent une intention claire.
VOICE_PROFILES = {
    "🎙️ Suspense — tension progressive": {"rate": "+2%", "prefer": 0},
    "🔥 Énergique — rythme rapide": {"rate": "+10%", "prefer": 1},
    "😈 Défi — ton provocateur": {"rate": "+6%", "prefer": 0},
    "🎯 Animateur Quiz — naturel": {"rate": "+4%", "prefer": 1},
    "⚡ Intense — pression maximale": {"rate": "+15%", "prefer": 1},
}

QUIZ_MOTIVATION_DEFAULTS = {
    "Français": {"start":"Prêt ? C'est parti !", "end":"Bravo ! À bientôt pour un nouveau quiz !", "start_label":"PRÊT ?", "mid_label":"CONTINUE !", "end_label":"QUIZ TERMINÉ", "start_sub":"Teste tes connaissances !", "end_sub":"À bientôt pour un nouveau défi."},
    "Anglais": {"start":"Ready? Let's go!", "end":"Great job! See you in the next quiz!", "start_label":"READY?", "mid_label":"KEEP GOING", "end_label":"QUIZ COMPLETE", "start_sub":"Test your knowledge!", "end_sub":"See you in the next challenge."},
    "Espagnol": {"start":"¿Listo? ¡Empezamos!", "end":"¡Bravo! ¡Hasta el próximo quiz!", "start_label":"¿LISTO?", "mid_label":"¡SIGUE!", "end_label":"QUIZ TERMINADO", "start_sub":"¡Pon a prueba tus conocimientos!", "end_sub":"Hasta el próximo desafío."},
    "Arabe": {"start":"هل أنت مستعد؟ لنبدأ!", "end":"أحسنت! نلتقي في الاختبار القادم!", "start_label":"مستعد؟", "mid_label":"تابع!", "end_label":"انتهى الاختبار", "start_sub":"اختبر معلوماتك!", "end_sub":"إلى التحدي القادم."},
    "Allemand": {"start":"Bereit? Los geht's!", "end":"Super! Bis zum nächsten Quiz!", "start_label":"BEREIT?", "mid_label":"WEITER!", "end_label":"QUIZ FERTIG", "start_sub":"Teste dein Wissen!", "end_sub":"Bis zur nächsten Herausforderung."},
    "Italien": {"start":"Pronto? Si parte!", "end":"Bravo! Ci vediamo al prossimo quiz!", "start_label":"PRONTO?", "mid_label":"CONTINUA!", "end_label":"QUIZ COMPLETATO", "start_sub":"Metti alla prova le tue conoscenze!", "end_sub":"Alla prossima sfida."},
}

# ------------------------- Helpers --------------------------
def get_ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()

FONT_PATHS = {
    "DejaVu Sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "DejaVu Serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "Lato": "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
    "Liberation Sans": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "Liberation Serif": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "Gillius": "/usr/share/fonts/truetype/adf/GilliusADF-Bold.otf",
    "Universalis": "/usr/share/fonts/truetype/adf/UniversalisADFStd-Bold.otf",
}
FONT_CHOICES = list(FONT_PATHS.keys())

def get_font(size, family=None):
    family = family or "DejaVu Sans"
    candidates = [FONT_PATHS.get(family), "Roboto-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"]
    for fn in candidates:
        if not fn: continue
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
    """Fond vidéo moderne mis en cache pour garder le rendu rapide."""
    theme = THEMES[theme_name]
    if isinstance(bg_file, Image.Image):
        bg = bg_file
        key = None
    elif bg_file is not None:
        bg = fit_background(bg_file)
        key = None
    else:
        bg = None
        key = ("theme_v2_bright", theme_name)

    if bg is not None:
        base = bg.convert("RGBA")
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 55))
        shade = Image.new("L", (WIDTH, HEIGHT), 0)
        sd = ImageDraw.Draw(shade)
        sd.rectangle((70, 120, WIDTH-70, HEIGHT-100), fill=115)
        shade = shade.filter(ImageFilter.GaussianBlur(90))
        overlay.putalpha(shade)
        return Image.alpha_composite(base, overlay).convert("RGB")

    if key in _BASE_CACHE:
        return _BASE_CACHE[key].copy()
    # V32.3.4 — toutes les palettes utilisent désormais un dégradé plus lumineux
    # et des halos visibles. Le cache est versionné pour ne pas garder l'ancien fond sombre.
    c1, c2 = theme["bg"], theme["bg2"]
    img = Image.new("RGB", (WIDTH, HEIGHT))
    px = img.load()
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        t2 = 0.5 - 0.5 * math.cos(math.pi * t)
        row = tuple(int(c1[i] * (1-t2) + c2[i] * t2) for i in range(3))
        for x in range(WIDTH):
            px[x, y] = row
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-260, -260, 650, 600), fill=(*theme["accent"], 54))
    gd.ellipse((520, 1180, 1380, 2050), fill=(*theme["accent"], 42))
    gd.ellipse((130, 680, 920, 1320), fill=(*theme["accent"], 18))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    result = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    _BASE_CACHE[key] = result
    return result.copy()

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

def draw_thinking_icon(draw, theme, phase=0.0, cx=935, cy=1250, size=44):
    """Icône de réflexion dessinée en formes : aucun emoji/font externe nécessaire."""
    phase=float(phase or 0.0)
    accent=theme.get("accent",(255,205,64))
    pulse=0.5+0.5*math.sin(phase*math.pi*2)
    r=int(size+4*pulse)
    draw.ellipse((cx-r-8,cy-r-8,cx+r+8,cy+r+8), outline=(*accent,90), width=3)
    draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(8,13,27), outline="white", width=4)
    er=max(3,int(r*.10))
    draw.ellipse((cx-int(r*.32)-er,cy-int(r*.18)-er,cx-int(r*.32)+er,cy-int(r*.18)+er), fill="white")
    draw.ellipse((cx+int(r*.32)-er,cy-int(r*.18)-er,cx+int(r*.32)+er,cy-int(r*.18)+er), fill="white")
    draw.line((cx-int(r*.46),cy-int(r*.43),cx-int(r*.16),cy-int(r*.50)), fill=accent, width=4)
    draw.line((cx+int(r*.16),cy-int(r*.50),cx+int(r*.46),cy-int(r*.43)), fill=accent, width=4)
    draw.arc((cx-int(r*.28),cy-int(r*.02),cx+int(r*.30),cy+int(r*.40)),190,340,fill=accent,width=4)
    draw.line((cx+int(r*.15),cy+int(r*.55),cx+int(r*.42),cy+int(r*.82)),fill="white",width=5)
    draw.line((cx+int(r*.42),cy+int(r*.82),cx+int(r*.60),cy+int(r*.65)),fill="white",width=5)


def draw_thinking_face(draw, theme, cx, cy, size=30, phase=0.0, style="Réflexion", color=None):
    """Visage personnalisable : Réflexion, Sourire, Surpris, Clin d'œil ou Simple."""
    a=color or theme["accent"]
    pulse=1.0+0.08*math.sin(float(phase)*math.pi*2)
    r=int(size*pulse)
    # bulle
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(8,14,30,235),outline="white",width=max(2,int(size/8)))
    # yeux
    er=max(2,int(r*0.10))
    for ex in (-int(r*.30), int(r*.30)):
        draw.ellipse((cx+ex-er,cy-int(r*.18)-er,cx+ex+er,cy-int(r*.18)+er),fill="white")
    style=str(style or "Réflexion")
    if style=="Surpris":
        draw.ellipse((cx-int(r*.28),cy-int(r*.05),cx+int(r*.28),cy+int(r*.48)),outline=a,width=max(2,int(size/9)))
    elif style=="Sourire":
        draw.arc((cx-int(r*.34),cy-int(r*.05),cx+int(r*.34),cy+int(r*.45)),10,170,fill=a,width=max(2,int(size/9)))
    elif style=="Clin d'œil":
        draw.line((cx-int(r*.48),cy-int(r*.18),cx-int(r*.12),cy-int(r*.18)),fill=a,width=max(2,int(size/9)))
        draw.arc((cx-int(r*.30),cy-int(r*.02),cx+int(r*.30),cy+int(r*.38)),190,335,fill=a,width=max(2,int(size/9)))
    elif style=="Simple":
        draw.line((cx-int(r*.25),cy+int(r*.22),cx+int(r*.25),cy+int(r*.22)),fill=a,width=max(2,int(size/9)))
    else:
        draw.line((cx-int(r*.48),cy-int(r*.47),cx-int(r*.12),cy-int(r*.55)),fill=a,width=max(2,int(size/8)))
        draw.line((cx+int(r*.12),cy-int(r*.55),cx+int(r*.48),cy-int(r*.47)),fill=a,width=max(2,int(size/8)))
        draw.arc((cx-int(r*.30),cy-int(r*.02),cx+int(r*.30),cy+int(r*.38)),190,335,fill=a,width=max(2,int(size/9)))
    if style in ("Réflexion","Surpris"):
        br=max(4,int(size*.18))
        draw.ellipse((cx+int(r*.65),cy-int(r*.85),cx+int(r*.65)+br,cy-int(r*.85)+br),fill=a)
        draw.ellipse((cx+int(r*.95),cy-int(r*1.15),cx+int(r*.95)+br//2,cy-int(r*1.15)+br//2),fill=a)

def draw_lightning_icon(draw, theme, cx, cy, size=28):
    """Éclair vectoriel pour remplacer ⚡ dans les scènes vidéo."""
    a=theme["accent"]; r=size
    pts=[(cx+int(.15*r),cy-r),(cx-int(.55*r),cy+int(.05*r)),
         (cx-int(.08*r),cy+int(.05*r)),(cx-int(.28*r),cy+r),
         (cx+int(.60*r),cy-int(.18*r)),(cx+int(.05*r),cy-int(.18*r))]
    draw.polygon(pts,fill=a)

def draw_brand(draw, theme, channel, progress=None):
    cfg=_layout("quiz", "1")
    if channel and bool(cfg.get("brand_show",True)):
        text=clean_text(channel) or "SuspenseLingo"
        f=get_font(int(cfg.get("brand_size",28)),cfg.get("font_family","DejaVu Sans"))
        x=int(cfg.get("brand_x",55)); y=int(cfg.get("brand_y",34))
        if cfg.get("brand_bg_enabled",False):
            tw=text_width(draw,text,f); th=text_height(f,text)
            pad=10; bg=_hex_rgb(cfg.get("brand_bg"),(7,13,28))
            draw.rounded_rectangle((x-pad,y-pad,x+tw+pad,y+th+pad),radius=12,fill=bg)
        draw.text((x,y),text,font=f,fill=_hex_rgb(cfg.get("brand_color"),(255,255,255)))
    # Progress bar remains at the bottom, separate from the brand.
    if progress is not None:
        cfg=_layout("quiz", "1")
        safe_y=int(cfg.get("social_progress_y",1695))
        safe_auto=bool(cfg.get("social_auto_layout",False))
        x=32 if safe_auto else 55
        w=(874-32) if safe_auto else 970
        y=safe_y
        h=12
        draw.rounded_rectangle((x,y,x+w,y+h), radius=6, fill=(65,70,85))
        draw.rounded_rectangle((x,y,x+int(w*clamp(progress)),y+h), radius=6, fill=theme["accent"])

def _highlight_words(question):
    words=clean_text(question).split()
    stop={"quel","quelle","quels","quelles","est","sont","le","la","les","un","une","des","du","de","dans","sur","au","aux","en","à","a","et","ou","pour","par","avec","qui","que","se","ce","cette","cet","d","l","comment","combien","où","on"}
    candidates=[w.strip(".,?!:;()[]«»\"'") for w in words if len(w.strip(".,?!:;()[]«»\"'"))>=5 and w.lower().strip(".,?!:;()[]«»\"'") not in stop]
    return set(c.lower() for c in candidates[:max(2,min(4,len(candidates)))]) if candidates else set()

def draw_unified_header(draw, cfg, q_num, total, title="Culture Générale"):
    """V31.30 — en-tête commun aux 4 styles : LOGO | TITRE | COMPTEUR.
    Les trois zones ont la même largeur et restent dans la zone sûre.
    """
    ff=cfg.get("font_family","Lato")
    gold=(250,184,60); navy=(25,45,78); border=(76,105,150); white=(255,255,255); black=(15,23,42)
    left=int(cfg.get("social_safe_left",40)); right=int(cfg.get("social_safe_right",WIDTH-40))
    top=int(cfg.get("header_y", int(cfg.get("social_safe_top",120))))
    safe_top=int(cfg.get("social_safe_top",120)); safe_bottom=int(cfg.get("social_safe_bottom",HEIGHT-220))
    # V31.32 — l'en-tête doit rester entièrement dans la zone sûre, avec
    # une marge interne supplémentaire pour ne jamais toucher le masque.
    safe_margin_top=24; safe_margin_bottom=24
    top=max(safe_top+safe_margin_top,top)
    header_h=max(58,min(78,int(cfg.get("header_h",72))))
    bottom=min(safe_bottom-safe_margin_bottom,top+header_h)
    if bottom-top < 52:
        top=max(safe_top+10, safe_bottom-62)
        bottom=min(safe_bottom-10,top+52)
    left=max(32,min(left,WIDTH-120)); right=max(left+120,min(right,WIDTH-32))
    draw.rounded_rectangle((left,top,right,bottom),radius=20,fill=navy,outline=border,width=2)
    third=(right-left)/3.0
    # Zone 1 : logo
    if cfg.get("brand_show",True):
        brand=clean_text(cfg.get("brand_text") or "SuspenseLingo") or "SuspenseLingo"
        bf=get_font(int(cfg.get("brand_size",31)),ff); bh=text_height(bf,brand)
        bx=left+18; by=top+(bottom-top-bh)//2
        # Badge de marque : petit monogramme + capsule pour donner plus de
        # présence à SuspenseLingo sans modifier la mécanique du quiz.
        icon_r=max(12,min(18,(bottom-top)//4))
        icx=bx+icon_r; icy=top+(bottom-top)//2
        draw.ellipse((icx-icon_r,icy-icon_r,icx+icon_r,icy+icon_r),fill=gold)
        sf=get_font(max(14,int(icon_r*1.25)),ff)
        stxt="S"; ssw=text_width(draw,stxt,sf); ssh=text_height(sf,stxt)
        draw.text((icx-ssw/2,icy-ssh/2-1),stxt,font=sf,fill=black)
        text_x=bx+icon_r*2+10
        if cfg.get("brand_bg_enabled",True):
            tw=text_width(draw,brand,bf); pad_x=10; pad_y=7
            draw.rounded_rectangle((text_x-pad_x,by-pad_y,text_x+tw+pad_x,by+bh+pad_y),radius=12,fill=_hex_rgb(cfg.get("brand_bg"),(32,56,94)),outline=border,width=1)
        draw.text((text_x,by),brand,font=bf,fill=_hex_rgb(cfg.get("brand_color"),gold))
    # Zone 2 : titre
    title=clean_text(title) or "Culture Générale"
    if title.lower().startswith("quiz "): title=title[5:].strip()
    if len(title)>22: title=title[:22].rstrip()+"…"
    tf=get_font(int(cfg.get("title_size",32)),ff); th=text_height(tf,title)
    center_x=left+third*1.5; max_tw=int(third-24)
    while text_width(draw,title,tf)>max_tw and tf.size>24:
        tf=get_font(tf.size-1,ff); th=text_height(tf,title)
    tw=text_width(draw,title,tf); tx=center_x-tw/2; ty=top+(bottom-top-th)//2
    draw.text((tx+2,ty+2),title,font=tf,fill=black); draw.text((tx,ty),title,font=tf,fill=white)
    # Zone 3 : compteur
    score=f"{q_num}/{total}"; sf=get_font(int(cfg.get("score_size",28)),ff); sw=text_width(draw,score,sf); sh=text_height(sf,score)
    # Le badge reste intégralement dans le troisième tiers et dans le masque sûr.
    third_left=left+2*third; third_right=right
    pill_w=min(max(78,sw+24),max(78,int(third-18)))
    pill_h=min(max(40,sh+10),max(40,header_h-10))
    cx=(third_left+third_right)/2
    px=max(third_left+9,min(cx-pill_w/2,third_right-9-pill_w))
    py=top+(bottom-top-pill_h)/2
    draw.rounded_rectangle((px,py,px+pill_w,py+pill_h),radius=min(16,pill_h//2),fill=gold)
    draw.text((px+(pill_w-sw)/2,py+(pill_h-sh)/2-1),score,font=sf,fill=black)
    return top, bottom

def draw_header(draw, theme, q_num, total, title="Culture Générale", phase=0.0):
    cfg=_layout("quiz", "1")
    return draw_unified_header(draw,cfg,q_num,total,title)

def _draw_timer_visual(draw, color, cx, cy, r, timer, fraction, style, text_size, label=None, label_size=23, label_color=None, pulse=0.0):
    """Chronomètres Studio Pro. Option 1 utilise un cercle Bleu Nuit + bordure Or."""
    frac=clamp(fraction); style=str(style or "Double cercle")
    if color == (245,158,11):
        # Option 1 : badge circulaire fixe, exactement comme la spécification CSS.
        bg=(30,41,59)
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=bg,outline=(245,158,11),width=4)
        tf=get_font(text_size); ts=str(timer if timer is not None else ""); th=text_height(tf,ts)
        draw.text((cx-text_width(draw,ts,tf)/2,cy-th/2-3),ts,font=tf,fill=(245,158,11))
        if label:
            lf=get_font(label_size); lw=text_width(draw,label,lf); draw.text(((WIDTH-lw)/2,cy+r+16),label,font=lf,fill=label_color or (245,158,11))
        return
    frac=clamp(fraction); style=str(style or "Double cercle")
    bg=(7,12,26)
    white=(245,248,252)
    if style=="Double cercle":
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline=color,width=max(3,int(r*.07)))
        r2=max(8,int(r*.72)); draw.ellipse((cx-r2,cy-r2,cx+r2,cy+r2),fill=bg,outline=white,width=max(2,int(r*.045)))
        draw.arc((cx-r+5,cy-r+5,cx+r-5,cy+r-5),-90,-90+int(360*frac),fill=color,width=max(4,int(r*.09)))
    elif style=="Montre":
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=bg,outline=white,width=max(2,int(r*.045)))
        draw.arc((cx-r+5,cy-r+5,cx+r-5,cy+r-5),-90,-90+int(360*frac),fill=color,width=max(4,int(r*.08)))
        # aiguilles
        angle=math.radians(-90+360*(1-frac)); hx=cx+int(math.cos(angle)*r*.48); hy=cy+int(math.sin(angle)*r*.48)
        draw.line((cx,cy,hx,hy),fill=color,width=max(3,int(r*.06)))
        draw.line((cx,cy,cx-int(r*.28),cy-int(r*.18)),fill=white,width=max(2,int(r*.045)))
        draw.ellipse((cx-5,cy-5,cx+5,cy+5),fill=color)
        for a in range(0,360,45):
            rr=math.radians(a); x1=cx+int(math.cos(rr)*r*.84); y1=cy+int(math.sin(rr)*r*.84)
            x2=cx+int(math.cos(rr)*r*.93); y2=cy+int(math.sin(rr)*r*.93)
            draw.line((x1,y1,x2,y2),fill=white,width=2)
    elif style=="Gouttes d’eau":
        # anneau + petites gouttes qui se remplissent autour du cercle
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(100,120,145),width=3)
        n=10
        active=int(math.ceil(frac*n))
        for i in range(n):
            a=math.radians(-90+i*(360/n)); gx=cx+int(math.cos(a)*r*.83); gy=cy+int(math.sin(a)*r*.83); rr=max(5,int(r*.08))
            fill=color if i<active else (75,86,105)
            draw.ellipse((gx-rr,gy-rr,gx+rr,gy+rr),fill=fill)
    elif style=="Sablier":
        w=max(28,int(r*.75)); h=max(42,int(r*1.35)); x0=cx-w; x1=cx+w; y0=cy-h; y1=cy+h
        draw.line((x0,y0,x1,y0),fill=white,width=4); draw.line((x0,y1,x1,y1),fill=white,width=4)
        draw.line((x0,y0,x1,y1),fill=white,width=3); draw.line((x1,y0,x0,y1),fill=white,width=3)
        sand_h=int((y1-y0)*.36*frac)
        if sand_h>0:
            draw.polygon([(cx-10,y1-8),(cx+10,y1-8),(cx+int(18*frac),y1-sand_h),(cx-int(18*frac),y1-sand_h)],fill=color)
        draw.line((cx,cy-int(h*.1),cx,cy+int(h*.1)),fill=color,width=3)
    elif style=="Anneau progressif":
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=bg,outline=(255,255,255),width=3)
        draw.arc((cx-r+6,cy-r+6,cx+r-6,cy+r-6),-90,-90+int(360*frac),fill=color,width=max(5,int(r*.14)))
    elif style=="Numérique":
        w=max(130,int(r*3.1)); h=max(62,int(r*1.05));
        draw.rounded_rectangle((cx-w//2,cy-h//2,cx+w//2,cy+h//2),radius=int(h*.28),fill=bg,outline=color,width=max(3,int(r*.06)))
        draw.rounded_rectangle((cx-w//2+8,cy-h//2+8,cx-w//2+8+int((w-16)*frac),cy-h//2+13),radius=3,fill=color)
    else:
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=bg,outline=color,width=3)
    tf=get_font(text_size)
    ts=str(timer if timer is not None else "")
    th=text_height(tf,ts)
    draw.text((cx-text_width(draw,ts,tf)/2,cy-th/2-3),ts,font=tf,fill=color)
    if label:
        lf=get_font(label_size); lw=text_width(draw,label,lf); draw.text(((WIDTH-lw)/2,cy+r+16),label,font=lf,fill=label_color or color)

def draw_timer(draw, theme, timer, fraction=1.0, pulse=0.0):
    cfg=_layout("quiz", "1"); color=_hex_rgb(cfg.get("timer_color"),theme["accent"])
    if timer is not None and timer<=1: color=_hex_rgb(cfg.get("timer_color"),theme["danger"])
    timer_size=max(24,int(cfg.get("timer_size",58)))
    if cfg.get("timer_auto_below_answers", True):
        answer_bottom=int(cfg.get("answer_y",630))+4*int(cfg.get("answer_h",82))+3*int(cfg.get("answer_gap",12))
        timer_y=min(1500, answer_bottom + timer_size + 22)
    else:
        timer_y=int(cfg.get("timer_y",1045))
    _draw_timer_visual(draw,color,int(cfg.get("timer_x",540)),timer_y,timer_size,timer,fraction,cfg.get("timer_style"),max(20,int(cfg.get("timer_text_size",55))),clean_text(cfg.get("timer_label")) if cfg.get("timer_show_label",True) else None,int(cfg.get("timer_label_size",23)),_hex_rgb(cfg.get("timer_label_color"),color),pulse)


def _hex_rgb(value, fallback=(255,255,255)):
    try:
        h=str(value).strip().lstrip("#")
        if len(h)==6:
            return tuple(int(h[i:i+2],16) for i in (0,2,4))
    except Exception:
        pass
    return fallback

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qvp_settings.json")

def _load_saved_settings():
    # Les widgets qui ne sont pas affichés pendant le passage Quiz ↔ Vocabulaire
    # peuvent être retirés par Streamlit. On recharge donc les réglages sauvegardés
    # à chaque rerun, mais uniquement pour les clés absentes afin de ne jamais
    # écraser une modification en cours.
    sources=[]
    snap=st.session_state.get("_qvp_saved_settings")
    if isinstance(snap,dict): sources.append(snap)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved=json.load(f)
        if isinstance(saved,dict): sources.append(saved)
    except Exception:
        pass
    for saved in sources:
        for k,v in saved.items():
            if k.startswith(("q1_","q2_","v1_","v2_")) and k not in st.session_state:
                st.session_state[k]=v
    st.session_state["_qvp_settings_loaded"]=True

def _save_settings():
    keys=[]
    for k in st.session_state.keys():
        if k.startswith(("q_","v_","q1_","q2_","v1_","v2_")):
            keys.append(k)
    data={}
    for k in keys:
        v=st.session_state.get(k)
        if isinstance(v,(str,int,float,bool)):
            data[k]=v
    # Snapshot en session : protège les réglages même si les widgets disparaissent
    # temporairement lors du passage d’un module à l’autre.
    st.session_state["_qvp_saved_settings"] = dict(data)
    try:
        tmp=SETTINGS_FILE+".tmp"
        with open(tmp,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
        os.replace(tmp,SETTINGS_FILE)
    except Exception:
        pass

_load_saved_settings()

# V31.13 — mise en page automatique réseaux sociaux + zones sûres.
# V31.12 — visuel Bleu Nuit & Or appliqué directement au moteur Pillow/MoviePy.
# V31.11 — mise en page Bleu Nuit & Or alignée sur la maquette approuvée et la spécification CSS utilisateur.
# V31.10 — preset géométrique du visuel approuvé « Bleu Nuit & Or ».
# Appliqué une seule fois pour ne pas écraser ensuite les réglages manuels de l’Éditeur Studio.
if not st.session_state.get("_blue_gold_layout_v31_10_applied"):
    _blue_gold_preset = {
        "q1_question_x": 540, "q1_question_y": 315, "q1_question_size": 47, "q1_question_width": 940,
        "q1_answer_x": 70, "q1_answer_y": 600, "q1_answer_width": 940, "q1_answer_h": 90, "q1_answer_gap": 16,
        "q1_answer_size": 31, "q1_answer_badge_size": 54, "q1_answer_text_padding": 24,
        "q1_timer_x": 540, "q1_timer_y": 1110, "q1_timer_size": 64, "q1_timer_text_size": 55,
        "q1_timer_auto_below_answers": False, "q1_explanation_auto_below_timer": False,
        "q1_explanation_x": 540, "q1_explanation_y": 1375, "q1_explanation_width": 940, "q1_explanation_h": 250,
        "q1_explanation_size": 30,
        "q1_primary": "#F59E0B", "q1_answer": "#1E293B", "q1_answer2": "#1E293B",
        "q1_correct": "#10B981", "q1_text": "#FFFFFF", "q1_muted": "#E2E8F0",
        "q1_border_color": "#334155", "q1_border_width": 2, "q1_border_radius": 20,
        "q1_question_frame_enabled": True, "q1_question_frame_bg_enabled": True, "q1_question_border_enabled": True,
        "q1_answer_cards_enabled": True, "q1_answer_badges_enabled": True,
        "q1_answer_frame_bg_enabled": True, "q1_answer_border_enabled": True,
        "q1_explanation_frame_enabled": True, "q1_explanation_frame_bg_enabled": True, "q1_explanation_border_enabled": True,
        "q1_header_y": 120, "q1_header_h": 74, "q1_score_x": 965, "q1_score_y": 130, "q1_score_size": 31,
        "q1_brand_x": 70, "q1_brand_y": 139, "q1_brand_size": 28, "q1_brand_color": "#F59E0B", "q1_brand_show": True,
        "q1_social_auto_layout": True, "q1_social_platform": "Universel",
    }
    for _k, _v in _blue_gold_preset.items():
        st.session_state[_k] = _v
    st.session_state["_blue_gold_layout_v31_10_applied"] = True

def _migrate_stock_visual_defaults():
    """Éclaircit les réglages hérités seulement lorsqu'ils correspondent encore aux anciens défauts stock."""
    prefixes = ("q1_", "q2_", "v1_", "v2_")
    old_to_new = {
        "bg_opacity": (10, 0),
        "brand_size": (28, 38),
        "brand_color": ("#F59E0B", "#FFD166"),
        "brand_bg_enabled": (False, True),
        "brand_bg": ("#151D33", "#244D7C"),
        "primary": ("#F59E0B", "#FFD166"),
        "answer": ("#1E293B", "#23466F"),
        "answer2": ("#1E293B", "#2E5B8D"),
        "border_color": ("#334155", "#8CCBFF"),
        "border_width": (2, 3),
        "timer_style": ("Double cercle", "Anneau progressif"),
        "timer_text_size": (55, 68),
    }
    for prefix in prefixes:
        for name, (old, new) in old_to_new.items():
            key = prefix + name
            if key in st.session_state and st.session_state.get(key) == old:
                st.session_state[key] = new
        q = prefix.startswith("q")
        key = prefix + "question_size"
        if key in st.session_state and st.session_state.get(key) in (47, 50):
            st.session_state[key] = 58 if q else 62
        key = prefix + "answer_size"
        if key in st.session_state and st.session_state.get(key) in (31, 33, 42):
            st.session_state[key] = 39 if q else 46
        key = prefix + "timer_size"
        if key in st.session_state and st.session_state.get(key) in (52, 62):
            st.session_state[key] = 72 if q else 68

_migrate_stock_visual_defaults()

def _layout(module="quiz", style=None):
    """Réglages visuels persistants, séparés par éditeur/style."""
    if module == "vocab":
        prefix = "v2_" if str(style or "1").lower() in ("2", "style2", "cumulative") else "v1_"
        legacy_prefix = "v_"
    else:
        prefix = "q2_" if str(style or "1").lower() in ("2", "style2", "cumulative") else "q1_"
        legacy_prefix = "q_"
    defaults={
        "font_family":"Lato",
        "show_title":True,"header_y":120,"header_h":74,"title_x":540,"title_y":139,"title_size":38,
        "question_x":540,"question_y":315,"question_size":56,"question_width":940,"question_box_radius":24,
        "answer_y":600,"answer_x":80,"answer_width":920,"answer_h":96,"answer_gap":16,"answer_size":38,"answer_radius":20,"answer_badge_size":54,"answer_text_padding":24,"answer_auto_height":False,
        "history_x":80,"history_y":650,"history_width":920,"history_row_h":78,"history_gap":12,"history_text_x":540,"history_size":30,
        "timer_y":1110,"timer_x":540,"timer_size":76,"timer_style":"Anneau progressif","timer_color":"#FFC94A","timer_text_size":68,"timer_label_y":1175,"timer_label_size":23,"timer_show_label":False,"timer_label":"RÉFLÉCHIS","timer_label_color":"#F59E0B",
        "timer_auto_below_answers":False,"explanation_auto_below_timer":False,"explanation_auto_height":False,
        "face_size":30,"face_x":0,"face_y":0,"face_style":"Aucun","face_color":"#FFCD40","face_show":False,
        "score_x":965,"score_y":130,"score_size":31,"score_color":"#000000","score_bg":"#F59E0B","score_radius":22,"score_border":0,
        "brand_x":70,"brand_y":139,"brand_size":38,"brand_show":True,"brand_bg_enabled":True,"brand_bg":"#244D7C","brand_color":"#FFD166",
        "explanation_x":540,"explanation_y":1375,"explanation_width":940,"explanation_h":250,"explanation_size":30,
        "explanation_radius":24,"show_explanation":True,"show_timer":True,
        "social_auto_layout":True,"social_platform":"Universel","social_progress_y":1530,
        "question_frame_enabled":True,"question_frame_bg_enabled":True,"question_border_enabled":True,
        "answer_cards_enabled":True,"answer_badges_enabled":True,"answer_frame_bg_enabled":True,"answer_border_enabled":True,
        "explanation_frame_enabled":True,"explanation_frame_bg_enabled":True,"explanation_border_enabled":True,
        "animation":"Glissement","animation_speed":1.0,"animation_strength":1.0,
        "bg_opacity":0,"motion_strength":1.0,"bg_zoom":1.02,"bg_x":0,"bg_y":0,
        "primary":"#FFD166","answer":"#23466F","answer2":"#2E5B8D",
        "correct":"#10B981","text":"#FFFFFF","muted":"#E2E8F0",
        "border_color":"#8CCBFF","border_width":3,"border_radius":22,
    }
    if module=="vocab":
        defaults.update({
            "title_y":70,"title_size":34,"question_y":500,"question_size":58,
            "answer_y":760,"answer_size":42,"timer_y":760,"timer_x":810,"timer_size":48,
            "animation":"Glissement vertical","primary":"#FFCD40",
            "translation_x":540,"translation_y":760,"translation_width":850,
            "table_x":70,"table_y":430,"table_width":940,"table_row_h":82,"table_gap":8,
            "table_split":540,"table_radius":16,"vocab_fr_size":42,"vocab_tr_size":38,
            "vocab_timer_size":44,"vocab_header_size":28,"vocab_history_dim":0.62,
        })
    out={}
    for k,v in defaults.items():
        key=prefix+k
        if key not in st.session_state and legacy_prefix+k in st.session_state:
            st.session_state[key]=st.session_state[legacy_prefix+k]
        out[k]=st.session_state.get(key,v)
    return out

def _draw_question_rich(draw, question, theme, y=205, phase=0.0, active_word=-1):
    cfg=_layout("quiz", "1")
    ff=cfg.get("font_family","DejaVu Sans")
    base_size=int(cfg["question_size"]); maxw=int(cfg.get("question_width",900))
    # Priorité à la lisibilité : on essaie d'abord 2 lignes, puis 3 lignes avant de réduire
    # excessivement la police. La question reste toujours dans son cadre.
    size=base_size; f=get_font(size,ff); lines=wrap_text(question,f,maxw)
    while len(lines)>3 and size>32:
        size-=2; f=get_font(size,ff); lines=wrap_text(question,f,maxw)
    lines=lines[:3]
    hi=_highlight_words(question); yy=int(cfg["question_y"]);
    line_h=int(size*1.18)
    box_top=yy-18; box_bottom=yy+len(lines)*line_h+22
    radius=int(cfg["question_box_radius"])
    box_w=int(cfg.get("question_width",964)); center_x=int(cfg.get("question_x",540)); left=max(20,center_x-box_w//2); right=min(WIDTH-20,center_x+box_w//2)
    if cfg.get("question_frame_enabled", True):
        is_blue_gold = theme.get("accent") == (245,158,11) and theme.get("bg") == (11,16,33)
        fill=(21,28,51) if is_blue_gold and cfg.get("question_frame_bg_enabled",True) else ((6,12,28,218) if cfg.get("question_frame_bg_enabled",True) else None)
        outline=(51,65,85) if is_blue_gold and cfg.get("question_border_enabled",True) else (_hex_rgb(cfg.get("border_color"),_hex_rgb(cfg["primary"],theme["accent"])) if cfg.get("question_border_enabled",True) else None)
        draw.rounded_rectangle((left,box_top,right,box_bottom),radius=int(cfg.get("border_radius",radius)),fill=fill,outline=outline,width=2 if is_blue_gold else max(1,int(cfg.get("border_width",2))))
    global_word=0
    for line in lines:
        words=line.split(); widths=[text_width(draw,w,f) for w in words]; space=text_width(draw," ",f)
        totalw=sum(widths)+space*max(0,len(words)-1)
        x=center_x-totalw/2+int(5*math.sin(phase*math.pi*2*cfg["motion_strength"]))
        for w,ww in zip(words,widths):
            current=(active_word >= 0 and global_word == int(active_word))
            fill=_hex_rgb(cfg["primary"],theme["accent"]) if current else _hex_rgb(cfg["text"],(255,255,255))
            draw.text((x+2,yy+3),w,font=f,fill=(0,0,0)); draw.text((x,yy),w,font=f,fill=fill)
            x+=ww+space; global_word+=1
        yy+=line_h
    return box_bottom

def _draw_answers(draw, options, theme, entrance=1.0, correct_idx=None, reveal_progress=0.0, phase=0.0):
    cfg=_layout("quiz", "1"); ff=cfg.get("font_family","DejaVu Sans")
    left=int(cfg.get("answer_x",80)); right=min(WIDTH-20,left+int(cfg.get("answer_width",920)))
    configured_h=int(cfg.get("answer_h",92)); gap=int(cfg.get("answer_gap",14)); start_y=int(cfg.get("answer_y",690))
    base_size=int(cfg.get("answer_size",31)); padding=int(cfg.get("answer_text_padding",24))
    anim=str(cfg["animation"]); speed=max(0.25,float(cfg["animation_speed"])); strength=max(0.0,float(cfg["animation_strength"]))
    badge_size=max(36,min(72,int(cfg.get("answer_badge_size",54))))
    for i,opt in enumerate(options[:4]):
        opt_clean=clean_text(opt)
        # La carte reste indépendante de la taille du texte. Si nécessaire, seul le texte
        # se réduit légèrement pour tenir dans la hauteur choisie.
        f_opt=get_font(base_size,ff)
        max_text_w=max(180,right-(left+badge_size+70)-padding)
        lines=wrap_text(opt_clean,f_opt,max_text_w)[:2]
        if not lines: lines=[""]
        if not bool(cfg.get("answer_auto_height",False)):
            fit_size=base_size
            while fit_size>20:
                f_try=get_font(fit_size,ff)
                lines_try=wrap_text(opt_clean,f_try,max_text_w)[:2]
                text_h_try=sum(text_height(f_try,z) for z in lines_try)+max(0,len(lines_try)-1)*4
                if text_h_try <= configured_h-2*padding: break
                fit_size-=1
            f_opt=get_font(fit_size,ff); lines=wrap_text(opt_clean,f_opt,max_text_w)[:2]
        text_h=sum(text_height(f_opt,z) for z in lines)+max(0,len(lines)-1)*4
        card_h=(max(configured_h,badge_size+16,text_h+padding*2) if bool(cfg.get("answer_auto_height",False)) else configured_h)
        if anim=="Aucune": local=1.0
        else: local=ease_out(clamp((entrance-i*0.07*speed)/(0.48/max(.25,speed))))
        offset=int((1-local)*52*strength) if anim in ("Glissement","Glissement vertical") else 0
        extra=int(7*ease_back(clamp(reveal_progress))) if correct_idx is not None and i==correct_idx else 0
        xpad=int((1-local)*40*strength) if anim in ("Glissement","Glissement vertical") else (int((1-local)*10*strength) if anim=="Pop" else 0)
        y=start_y+i*(card_h+gap)+offset+int(2*math.sin((phase+i*.13)*math.pi*2*cfg["motion_strength"]))
        correct=(correct_idx is not None and i==correct_idx)
        is_blue_gold = theme.get("accent") == (245,158,11) and theme.get("bg") == (11,16,33)
        if correct:
            fill=(16,185,129) if is_blue_gold else _hex_rgb(cfg["correct"],theme["success"]); outline=(52,211,153) if is_blue_gold else _hex_rgb(cfg.get("correct"),theme["success"]); width=2 if is_blue_gold else max(2,int(cfg.get("border_width",2))+1)
        else:
            fill=(30,41,59) if is_blue_gold else (_hex_rgb(cfg["answer"],(17,48,91)) if i%2==0 else _hex_rgb(cfg["answer2"],(20,55,101))); outline=(51,65,85) if is_blue_gold else _hex_rgb(cfg.get("border_color"),(210,225,250)); width=2 if is_blue_gold else max(1,int(cfg.get("border_width",2)))
            if correct_idx is not None:
                fill=tuple(int(c*.55) for c in fill); outline=tuple(int(c*.55) for c in outline)
        if cfg.get("answer_cards_enabled",True):
            card_fill=fill if cfg.get("answer_frame_bg_enabled",True) else None
            card_outline=outline if cfg.get("answer_border_enabled",True) else None
            draw.rounded_rectangle((left-extra+xpad,y-extra,right+extra+xpad,y+card_h+extra),radius=int(cfg.get("border_radius",cfg["answer_radius"])),fill=card_fill,outline=card_outline,width=width)
        badge_x=left+10+xpad; badge_y=int(y+(card_h-badge_size)/2)
        badge_fill=(245,158,11) if (is_blue_gold and not correct) else (_hex_rgb(cfg["primary"],theme["accent"]) if not correct else "white")
        if cfg.get("answer_badges_enabled",True):
            draw.rounded_rectangle((badge_x,badge_y,badge_x+badge_size,badge_y+badge_size),radius=min(int(badge_size*.28),int(cfg["answer_radius"]*.8)),fill=badge_fill)
        lf=get_font(max(18,min(42,int(base_size*1.02))),ff); letter=chr(65+i); lc=(0,0,0) if (is_blue_gold and not correct) else (theme["card"] if not correct else ((5,150,105) if is_blue_gold else _hex_rgb(cfg["correct"],theme["success"])))
        lh=text_height(lf,letter); draw.text((badge_x+(badge_size-text_width(draw,letter,lf))/2,badge_y+(badge_size-lh)/2-2),letter,font=lf,fill=lc)
        text_x=badge_x+badge_size+padding; maxw=right-text_x-padding; ty=y+(card_h-text_h)/2-2
        for line in lines:
            draw.text((text_x+2,ty+3),line,font=f_opt,fill=(0,0,0)); draw.text((text_x,ty),line,font=f_opt,fill=_hex_rgb(cfg["text"],(255,255,255))); ty+=text_height(f_opt,line)+4
        if correct:
            cx=right-38+xpad; cy=y+card_h/2
            if is_blue_gold:
                draw.line((cx-10,cy,cx-3,cy+8),fill="white",width=5)
                draw.line((cx-3,cy+8,cx+11,cy-10),fill="white",width=5)
            else:
                rr=19
                draw.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill="white")
                draw.line((cx-8,cy,cx-2,cy+7),fill=_hex_rgb(cfg["correct"],theme["success"]),width=4)
                draw.line((cx-2,cy+7,cx+10,cy-9),fill=_hex_rgb(cfg["correct"],theme["success"]),width=4)

def draw_explanation_panel(draw, theme, explanation, progress=1.0, active_word=-1):
    cfg=_layout("quiz", "1")
    if cfg.get("explanation_auto_below_timer", False):
        timer_size=max(24,int(cfg.get("timer_size",58)))
        if cfg.get("timer_auto_below_answers",True):
            answer_bottom=int(cfg.get("answer_y",630))+4*int(cfg.get("answer_h",82))+3*int(cfg.get("answer_gap",12))
            timer_cy=min(1500, answer_bottom + timer_size + 22)
        else:
            timer_cy=int(cfg.get("timer_y",1045))
        timer_r=timer_size
        y1=min(1450, timer_cy + timer_r + 10)
    else:
        y1=int(cfg["explanation_y"])
    p=ease_out(progress)
    primary=_hex_rgb(cfg["primary"],theme["accent"])
    box_w=max(420,min(1020,int(cfg.get("explanation_width",964))))
    center_x=max(box_w//2,min(WIDTH-box_w//2,int(cfg.get("explanation_x",540))))
    left=max(30,center_x-box_w//2); right=min(WIDTH-30,center_x+box_w//2)
    # Maquette Bleu Nuit & Or : aucun pictogramme dans la carte d'explication.
    # Titre doré centré, description blanche centrée, comme le visuel approuvé.
    title_font=get_font(min(36,int(cfg["explanation_size"]*.95)),cfg.get("font_family","DejaVu Sans"))
    title_text="EXPLICATION :"
    tw=text_width(draw,title_text,title_font)
    draw.text(((left+right-tw)/2,y1+26),title_text,font=title_font,fill=primary)
    f=get_font(int(cfg["explanation_size"])); lines=wrap_text(explanation or "Bravo !",f,max(300,box_w-100))[:5]
    if cfg.get("explanation_auto_height", False):
        needed_h=int(118 + max(1,len(lines))*int(cfg["explanation_size"]*1.32))
        box_h=max(205,min(int(cfg.get("explanation_h",320)),needed_h))
    else:
        box_h=int(cfg.get("explanation_h",320))
    y2=min(1645,y1+box_h)
    is_blue_gold = theme.get("accent") == (245,158,11) and theme.get("bg") == (11,16,33)
    if cfg.get("explanation_frame_enabled", True):
        fill=(15,23,42) if is_blue_gold and cfg.get("explanation_frame_bg_enabled",True) else ((6,13,28) if cfg.get("explanation_frame_bg_enabled",True) else None)
        outline=(245,158,11) if is_blue_gold and cfg.get("explanation_border_enabled",True) else (_hex_rgb(cfg.get("border_color"),primary) if cfg.get("explanation_border_enabled",True) else None)
        draw.rounded_rectangle((left,y1,right,y2),radius=20 if is_blue_gold else int(cfg.get("border_radius",cfg["explanation_radius"])),fill=fill,outline=outline,width=2 if is_blue_gold else max(1,int(cfg.get("border_width",2))))
        if cfg.get("explanation_border_enabled",True) or cfg.get("explanation_frame_bg_enabled",True):
            draw.rounded_rectangle((left,y1,left+int((right-left)*p),y1+6),radius=3,fill=primary)
    yy=y1+82; global_word=0
    for line in lines:
        words=line.split(); widths=[text_width(draw,w,f) for w in words]; space=text_width(draw," ",f); totalw=sum(widths)+space*max(0,len(words)-1); x=(left+right-totalw)/2
        for w,ww in zip(words,widths):
            current=(active_word>=0 and global_word==int(active_word))
            # Karaoké explication : changement de couleur uniquement, sans cadre
            # ni fond autour du mot actif pour éviter tout scintillement visuel.
            draw.text((x,yy),w,font=f,fill=_hex_rgb(cfg["primary"],theme["accent"]) if current else _hex_rgb(cfg["text"],(255,255,255)))
            x+=ww+space; global_word+=1
        yy+=int(cfg["explanation_size"]*1.35)

def draw_inline_timer(draw, theme, cx, cy, timer, fraction=1.0, module="quiz", style="1"):
    cfg=_layout(module, style); color=_hex_rgb(cfg.get("timer_color"),theme["accent"])
    if timer is not None and timer<=1: color=_hex_rgb(cfg.get("timer_color"),theme["danger"])
    _draw_timer_visual(draw,color,int(cx),int(cy),max(22,int(cfg.get("timer_size",58))),timer,fraction,cfg.get("timer_style"),max(20,int(cfg.get("timer_text_size",55))),None,23,color,0.1)


def _animated_progress(value, style):
    v=clamp(value); style=str(style or "Fondu")
    if style=="Rebond léger": return ease_back(v)
    if style=="Zoom doux": return 0.92+0.08*ease_out(v)
    return ease_out(v)

def draw_vocab_cumulative_frame(items, active_idx, theme_name, channel, bg_file=None, timer=None, timer_fraction=1.0, reveal=False, motion=0.0, video_title="Voyage", translation_active_word=-1, source_active_word=-1):
    """Vocabulaire Style 2 uniquement.
    Tableau cumulatif : les anciennes lignes restent toujours visibles.
    Sur la ligne active, les mots apparaissent au rythme des WordBoundaries TTS.
    """
    cfg=_layout("vocab", "2"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    alpha=int(clamp(cfg.get("bg_opacity",18),0,90))
    if alpha:
        base=Image.alpha_composite(
            base.convert("RGBA"),
            Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha))
        ).convert("RGB")
    img=add_top_glow(base,theme,1.0+0.08*math.sin(float(motion)*math.pi*2))
    draw=ImageDraw.Draw(img)

    total=max(1,len(items))
    active_idx=max(0,min(int(active_idx),total-1))
    ff=cfg.get("font_family","DejaVu Sans")
    table_ff=cfg.get("table_font_family",ff)

    # V31.27 — Vocabulaire Style 2 : mise en page visuelle validée
    # (header SuspenseLingo + titre + compteur), puis tableau cumulatif.
    # Cette couche ne change PAS la mécanique cumulative : elle ne fait qu'habiller
    # le rendu final et reste entièrement à l'intérieur de la zone sûre.
    safe_left=int(cfg.get("social_safe_left",40)); safe_top=int(cfg.get("social_safe_top",120))
    safe_right=int(cfg.get("social_safe_right",WIDTH-40)); safe_bottom=int(cfg.get("social_safe_bottom",HEIGHT-220))
    header_y,header_bottom=draw_unified_header(draw,cfg,active_idx+1,total,video_title or "Vocabulaire")
    # Pour 15 lignes, on réduit automatiquement la hauteur si nécessaire afin
    # que le tableau reste entièrement visible et ne touche jamais le footer.
    x=int(cfg.get("table_x",70))
    w=min(int(cfg.get("table_width",940)),safe_right-safe_left)
    x=max(safe_left,min(x,safe_right-w))
    y0=int(cfg.get("table_y",350))
    y0=max(y0,header_bottom+28)
    configured_rh=int(cfg.get("table_row_h",82))
    gap=int(cfg.get("table_gap",6))
    split=int(cfg.get("table_split",540))
    radius=int(cfg.get("table_radius",16))

    bottom_limit=max(y0+100,safe_bottom-24)
    max_rh=(bottom_limit-y0-gap*(total-1))//total
    effective_rh=max(58,min(configured_rh,int(max_rh))) if total>=12 else configured_rh

    # Taille adaptée automatiquement quand 12–15 lignes sont affichées.
    base_fr_size=int(cfg.get("vocab_fr_size",44))
    base_tr_size=int(cfg.get("vocab_tr_size",40))
    if total>=12:
        fr_size=min(base_fr_size,max(30,int(effective_rh*0.47)))
        tr_size=min(base_tr_size,max(28,int(effective_rh*0.42)))
    else:
        fr_size=base_fr_size
        tr_size=base_tr_size

    visible=active_idx+1

    for i in range(visible):
        item=items[i]
        ry=y0+i*(effective_rh+gap)
        active_row=(i==active_idx)
        history_row=(i<active_idx)

        fill=_hex_rgb(cfg.get("answer2" if active_row else "answer"),theme["card"])
        outline=_hex_rgb(
            cfg.get("border_color"),
            theme["accent"] if active_row else theme["muted"]
        )

        if active_row:
            shadow=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0))
            sd=ImageDraw.Draw(shadow)
            sd.rounded_rectangle(
                (x+4,ry+5,x+w+4,ry+effective_rh+5),
                radius=int(cfg.get("border_radius",radius)),
                fill=(0,0,0,70)
            )
            shadow=shadow.filter(ImageFilter.GaussianBlur(8))
            img=Image.alpha_composite(img.convert("RGBA"),shadow).convert("RGB")
            draw=ImageDraw.Draw(img)

        draw.rounded_rectangle(
            (x,ry,x+w,ry+effective_rh),
            radius=int(cfg.get("border_radius",radius)),
            fill=fill,
            outline=outline,
            width=max(1,int(cfg.get("border_width",2))+(1 if active_row else 0))
        )
        draw.line(
            (x+split,ry+10,x+split,ry+effective_rh-10),
            fill=outline,width=2
        )

        fr=clean_text(item.get("fr",""))
        if fr:
            fr=fr[:1].upper()+fr[1:]
        tr=clean_text(item.get("trad",""))

        fs=get_font(fr_size,table_ff)
        ts=get_font(tr_size,table_ff)

        # HISTORIQUE : français ET traduction restent définitivement affichés.
        # L'ancienne version envoyait -1 pour ces lignes, ce qui les effaçait.
        if history_row:
            source_limit=10**9
            translation_limit=10**9
        elif active_row:
            source_limit=int(source_active_word) if int(source_active_word)>=0 else -1
            translation_limit=int(translation_active_word) if int(translation_active_word)>=0 else -1
        else:
            source_limit=-1
            translation_limit=-1

        # Hiérarchie visuelle : la ligne active domine, l'historique reste lisible
        # mais plus discret. Cela évite l'effet "mur vert" à 10–15 lignes.
        if history_row:
            dim=float(cfg.get("vocab_history_dim",0.62))
            muted_rgb=_hex_rgb(cfg.get("muted"), theme["muted"])
            card_rgb=_hex_rgb(cfg.get("answer"), theme["card"])
            # Mélange avec la carte pour obtenir une vraie discrétion visuelle
            # sans utiliser de transparence (le rendu final est en RGB).
            history_fr_fill=tuple(int(card_rgb[k]*(1-dim)+muted_rgb[k]*dim) for k in range(3))
            history_tr_fill=history_fr_fill
        else:
            history_fr_fill = _hex_rgb(cfg.get("text"), (255,255,255))
            history_tr_fill = _hex_rgb(cfg.get("correct"), theme["success"])

        # ----- Français -----
        lines=wrap_text(fr,fs,max(80,split-45))[:2]
        ty=ry+(effective_rh-len(lines)*text_height(fs))/2-2
        global_source_word=0

        for line in lines:
            words_line=line.split()
            widths=[text_width(draw,z,fs) for z in words_line]
            space=text_width(draw," ",fs)
            indexed=[
                (global_source_word+j,word,ww)
                for j,(word,ww) in enumerate(zip(words_line,widths))
            ]
            visible_words=[
                (gidx,word,ww)
                for gidx,word,ww in indexed
                if gidx<=source_limit
            ]

            if visible_words:
                totalw=sum(ww for _,_,ww in visible_words)+space*max(0,len(visible_words)-1)
                xx=x+20
                if totalw < split-45:
                    xx=x+(split-totalw)/2

                for gidx,word,ww in visible_words:
                    current=(active_row and gidx==int(source_active_word))
                    # Le mot français actif reste mis en valeur par sa couleur,
                    # sans petit cadre supplémentaire autour du mot.
                    draw.text(
                        (xx,ty),word,font=fs,
                        fill=_hex_rgb(cfg.get("correct"),theme["success"]) if current
                        else history_fr_fill
                    )
                    xx+=ww+space

            global_source_word+=len(words_line)
            ty+=text_height(fs,line)+2

        # ----- Traduction -----
        # Elle n'apparaît que sur l'historique ou après le ding, puis se construit
        # mot par mot au rythme de la voix de traduction.
        show_translation=history_row or (active_row and reveal)

        if show_translation:
            lines2=wrap_text(tr,ts,max(80,w-split-45))[:2]
            ty2=ry+(effective_rh-len(lines2)*text_height(ts))/2-2
            global_idx=0

            for line in lines2:
                words_line=line.split()
                widths=[text_width(draw,z,ts) for z in words_line]
                space=text_width(draw," ",ts)
                indexed=[
                    (global_idx+j,word,ww)
                    for j,(word,ww) in enumerate(zip(words_line,widths))
                ]
                visible_words=[
                    (gidx,word,ww)
                    for gidx,word,ww in indexed
                    if gidx<=translation_limit
                ]

                if visible_words:
                    totalw=sum(ww for _,_,ww in visible_words)+space*max(0,len(visible_words)-1)
                    xx=x+split+20
                    if totalw < w-split-45:
                        xx=x+split+(w-split-totalw)/2

                    for gidx,word,ww in visible_words:
                        active_word=(active_row and gidx==int(translation_active_word))

                        if active_word:
                            pad=5
                            draw.rounded_rectangle(
                                (xx-pad,ty2-3,xx+ww+pad,ty2+text_height(ts,word)+4),
                                radius=8,
                                fill=_hex_rgb(cfg.get("answer2"),theme["card2"]),
                                outline=_hex_rgb(cfg.get("correct"),theme["success"]),
                                width=2
                            )

                        draw.text(
                            (xx,ty2),word,font=ts,
                            fill=_hex_rgb(cfg.get("correct"),theme["success"]) if active_word else history_tr_fill
                        )
                        xx+=ww+space

                global_idx+=len(words_line)
                ty2+=text_height(ts,line)+2

        # ----- Minuteur : uniquement pendant la réflexion de la ligne active -----
        elif active_row and timer is not None and cfg.get("show_timer",True):
            cell_cx=(
                x+split+(w-split)//2+
                int(cfg.get("vocab_timer_offset_x",0))
            )
            cell_cy=(
                ry+effective_rh//2+
                int(cfg.get("vocab_timer_offset_y",0))
            )
            r=max(22,min(int(cfg.get("vocab_timer_size",44)),int(effective_rh*.36)))
            timer_text_size=max(
                22,min(int(cfg.get("timer_text_size",38)),int(r*.95))
            )
            tc=_hex_rgb(cfg.get("timer_color"),theme["accent"])
            if timer is not None and timer<=1:
                tc=_hex_rgb(cfg.get("timer_color"),theme["danger"])

            _draw_timer_visual(
                draw,tc,int(cell_cx),int(cell_cy),r,timer,timer_fraction,
                cfg.get("timer_style","Double cercle"),
                timer_text_size,None,20,tc,0.12
            )

    # V31.28: un seul branding dans l'entête. Ne pas rappeler draw_brand() ici
    # (sinon un second logo apparaît sous le tableau).
    return img


def draw_style2_frame(items, active_idx, theme_name, channel, bg_file=None, timer=None, timer_fraction=1.0, answer_reveal=False, motion=0.0, video_title="Culture Générale", question_active_word=-1):
    """Quiz Style 2 : même écran 9:16, titre fixe, une seule question active.
    Séquence : Q1 + minuteur → Q2 + R1 → Q3 + R1/R2.
    Les réponses précédentes restent dans l'historique et la question active
    reprend toujours exactement la même zone.
    """
    cfg=_layout("quiz", "2"); theme=THEMES[theme_name]; white=_hex_rgb(cfg.get("text"),(255,255,255))
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    alpha=int(clamp(cfg.get("bg_opacity",16),0,90))
    if alpha:
        base=Image.alpha_composite(base.convert("RGBA"),Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha))).convert("RGB")
    img=add_top_glow(base,theme,1.0+0.10*math.sin(float(motion)*math.pi*2)); draw=ImageDraw.Draw(img)
    total=max(1,len(items)); active_idx=max(0,min(int(active_idx),total-1)); active=items[active_idx]; ff=cfg.get("font_family","Lato")

    safe_left=int(cfg.get("social_safe_left",40)); safe_top=int(cfg.get("social_safe_top",120))
    safe_right=int(cfg.get("social_safe_right",WIDTH-40)); safe_bottom=int(cfg.get("social_safe_bottom",HEIGHT-220))
    auto=bool(cfg.get("social_auto_layout",False))
    header_y,header_bottom=draw_unified_header(draw,cfg,active_idx+1,total,video_title or "Culture Générale")
    # Question active : toujours dans la même zone, largeur entièrement sûre.
    q=clean_text(active.get("question",""))
    if cfg.get("animation")=="Machine à écrire":
        reveal_chars=max(3,int(len(q)*clamp(motion))); q=q[:min(len(q),reveal_chars)]
    qf=get_font(int(cfg.get("question_size",50)),ff)
    qx=int(cfg.get("question_x",(safe_left+safe_right)//2)); qy=int(cfg.get("question_y",header_bottom+28))
    maxw=min(int(cfg.get("question_width",safe_right-safe_left)),safe_right-safe_left-20)
    if auto: qx=(safe_left+safe_right)//2; qy=max(header_bottom+28,qy)
    prog=_animated_progress(motion,cfg.get("animation")); dx=int((1-prog)*70) if cfg.get("animation") in ("Glissement vertical","Glissement") else 0
    lines=wrap_text(q,qf,maxw)[:3]
    line_h=max(42,int(qf.size*1.10)); box_h=max(112,len(lines)*line_h+54); box_w=min(safe_right-safe_left,max(620,maxw+40))
    bx1=max(safe_left,qx-box_w//2); bx2=min(safe_right,qx+box_w//2); by1=max(header_bottom+16,qy-28); by2=min(760,by1+box_h)
    if cfg.get("question_frame_enabled",True):
        qfill=(5,14,31) if cfg.get("question_frame_bg_enabled",True) else None
        qoutline=_hex_rgb(cfg.get("border_color"),_hex_rgb(cfg.get("primary"),theme["accent"])) if cfg.get("question_border_enabled",True) else None
        draw.rounded_rectangle((bx1,by1,bx2,by2),radius=int(cfg.get("border_radius",22)),fill=qfill,outline=qoutline,width=max(1,int(cfg.get("border_width",2))) if qoutline else 1)
    q_draw_y=by1+20; global_q_word=0
    for line in lines:
        words=line.split(); widths=[text_width(draw,w,qf) for w in words]; space=text_width(draw," ",qf); totalw=sum(widths)+space*max(0,len(words)-1); xx=qx-totalw/2+dx
        for word,ww in zip(words,widths):
            current=(question_active_word>=0 and global_q_word==int(question_active_word))
            draw.text((xx+2,q_draw_y+3),word,font=qf,fill=(0,0,0)); draw.text((xx,q_draw_y),word,font=qf,fill=_hex_rgb(cfg.get("primary"),theme["accent"]) if current else _hex_rgb(cfg.get("text"),white))
            xx+=ww+space; global_q_word+=1
        q_draw_y+=line_h

    hist=[(i,items[i]) for i in range(active_idx)]
    if answer_reveal: hist.append((active_idx,active))
    timer_cy=None

    if hist and cfg.get("answer_cards_enabled",True):
        hx=int(cfg.get("history_x",safe_left)); hw=min(int(cfg.get("history_width",safe_right-safe_left)),safe_right-safe_left)
        hx=max(safe_left,min(hx,safe_right-hw))
        hy_base=int(cfg.get("history_y",690)); hy=max(hy_base,(timer_cy+105 if timer_cy is not None else by2+42))
        available=max(260,safe_bottom-30-hy); shown=hist[-15:]
        hg=max(5,int(cfg.get("history_gap",8))); rh_cfg=max(46,int(cfg.get("history_row_h",74)))
        rh=max(40,min(rh_cfg,int((available-max(25,len(shown)-1)*hg)/max(1,len(shown)))))
        hsize_cfg=max(20,int(cfg.get("history_size",29))); hsize=max(20,min(hsize_cfg,int(34*74/max(46,rh))))
        hfs=get_font(hsize,ff); label_f=get_font(max(18,int(hsize*.68)),ff)
        draw.text((hx,hy-32),"HISTORIQUE DES RÉPONSES",font=label_f,fill=_hex_rgb(cfg.get("muted"),theme["muted"]))
        row_bg=_hex_rgb(cfg.get("answer"),theme["card2"])
        for pos,(i,item) in enumerate(shown):
            ry=hy+pos*(rh+hg); muted=tuple(int(c*.72) for c in row_bg)
            draw.rounded_rectangle((hx,ry,hx+hw,ry+rh),radius=min(int(cfg.get("border_radius",18)),max(8,rh//4)),fill=muted,outline=tuple(int(c*.72) for c in _hex_rgb(cfg.get("border_color"),(140,155,180))),width=max(1,int(cfg.get("border_width",2))))
            opts=item.get("options",[]); rc=clean_text(item.get("reponse_correcte","A")).upper()[:1]
            try: ans=clean_text(opts["ABCD".index(rc)])
            except Exception: ans=""
            rf=get_font(max(18,int(hsize*.70)),ff)
            draw.text((hx+18,ry+(rh-text_height(rf,"R1"))/2-2),f"R{i+1}",font=rf,fill=_hex_rgb(cfg.get("primary"),theme["accent"]))
            lines2=wrap_text("✓ "+ans,hfs,hw-120)[:2]; ty=ry+(rh-len(lines2)*text_height(hfs))/2-2
            for line in lines2:
                tw=text_width(draw,line,hfs); draw.text((hx+hw/2-tw/2,ty),line,font=hfs,fill=_hex_rgb(cfg.get("correct"),theme["success"])); ty+=text_height(hfs,line)+2

    # V31.27 : le minuteur vient après les réponses cumulatives.
    if timer is not None and cfg.get("show_timer",True):
        if hist and cfg.get("answer_cards_enabled",True):
            last_bottom=hy+len(shown)*rh+(len(shown)-1)*hg
            timer_cy=max(by2+90,last_bottom+28+int(cfg.get("timer_size",52)))
        else:
            timer_cy=max(by2+90,int(cfg.get("timer_y",by2+100)))
        timer_cy=min(safe_bottom-40,timer_cy)
        draw_inline_timer(draw,theme,int(cfg.get("timer_x",(safe_left+safe_right)//2)),int(timer_cy),timer,timer_fraction,"quiz","2")
    return img

def draw_quiz_frame(question, options, theme_name, q_num, total, channel, bg_file=None, entrance=1.0, timer=None, timer_fraction=1.0, correct_idx=None, reveal_progress=0.0, pulse=0.0, motion=0.0, video_title="Culture Générale", explanation=None, explanation_progress=0.0, question_active_word=-1, explanation_active_word=-1):
    # V31.18: le rendu ne modifie plus les clés de widgets Streamlit.
    # L’auto-layout est appliqué en amont de la création des widgets dans render_layout_editor().
    cfg=_layout("quiz", "1")
    ff=cfg.get("font_family","DejaVu Sans"); theme=THEMES[theme_name]
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    # Assombrissement réglable : le fond reste visible mais le texte reste lisible.
    alpha=int(clamp(cfg["bg_opacity"],0,90))
    if alpha:
        ov=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha)); base=Image.alpha_composite(base.convert("RGBA"),ov).convert("RGB")
    phase=float(motion or 0.0)*max(.25,float(cfg["motion_strength"]))
    scale=float(cfg.get("bg_zoom",1.02))+0.008*math.sin(phase*math.pi*2)
    nw,nh=int(WIDTH*scale),int(HEIGHT*scale); z=base.resize((nw,nh),Image.Resampling.LANCZOS)
    sx=max(0,min(nw-WIDTH,int((nw-WIDTH)*(0.5+0.12*math.sin(phase*math.pi*2)))+int(cfg.get("bg_x",0))))
    sy=max(0,min(nh-HEIGHT,int((nh-HEIGHT)*(0.5+0.10*math.cos(phase*math.pi*2)))+int(cfg.get("bg_y",0))))
    img=z.crop((sx,sy,sx+WIDTH,sy+HEIGHT)); img=add_top_glow(img,theme,1.0+0.55*pulse)
    # Pas de grand panneau décoratif fixe : les cadres de chaque élément sont contrôlés séparément dans le Studio.
    draw=ImageDraw.Draw(img)
    for k in range(9):
        px=int((90+k*121+(phase*34*(1+k%3)))%1000)+40; py=int(250+((k*177+phase*55)%1420)); rr=2+(k%3); draw.ellipse((px-rr,py-rr,px+rr,py+rr),fill=_hex_rgb(cfg["primary"],theme["accent"]))
    if cfg["show_title"]:
        draw_header(draw,theme,q_num,total,video_title,phase)
    # Halo doré discret derrière la question pour renforcer la hiérarchie visuelle.
    qcx=int(cfg.get("question_x",540)); qcy=int(cfg.get("question_y",250))+55
    glow=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gr=max(120,min(360,int(cfg.get("question_width",900)*0.28)))
    gd.ellipse((qcx-gr,qcy-gr//2,qcx+gr,qcy+gr//2),fill=(*_hex_rgb(cfg.get("primary"),theme["accent"]),38))
    glow=glow.filter(ImageFilter.GaussianBlur(55)); img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB"); draw=ImageDraw.Draw(img)
    _draw_question_rich(draw,question,theme,y=int(cfg["question_y"]),phase=phase,active_word=question_active_word)
    _draw_answers(draw,options,theme,entrance,correct_idx,reveal_progress,phase)
    if timer is not None and cfg["show_timer"]:
        draw_timer(draw,theme,timer,timer_fraction,pulse)
    if correct_idx is not None and reveal_progress>0:
        rp=clamp(reveal_progress)
        if rp<0.45:
            alpha=int(95*(1-rp/0.45)); glow=Image.new("RGBA",(WIDTH,HEIGHT),(255,255,255,0)); gd=ImageDraw.Draw(glow); gd.rectangle((42,360,1038,870),outline=(255,255,255,alpha),width=8); glow=glow.filter(ImageFilter.GaussianBlur(12)); img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB"); draw=ImageDraw.Draw(img)
    if correct_idx is not None and explanation and explanation_progress>0 and cfg["show_explanation"]:
        draw_explanation_panel(draw,theme,explanation,explanation_progress,active_word=explanation_active_word)
    # Le nom SuspenseLingo est rendu une seule fois dans le header; ici on garde uniquement la barre de progression.
    return img

def draw_vocab_style2_outro(message, subtitle, theme_name, channel, bg_file=None, progress=1.0):
    """Écran final dédié au Vocabulaire Style 2. Le texte principal est celui
    choisi par l'utilisateur dans "Message de fin"; aucun libellé fixe de quiz.
    """
    theme=THEMES[theme_name]
    cfg=_layout("vocab","2")
    ff=cfg.get("font_family","DejaVu Sans")
    p=ease_back(progress)
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.15*p)
    draw=ImageDraw.Draw(img)
    # Cercle central discret, sans badge "TESTE-TOI".
    r=int(190*p)
    draw.ellipse((540-r,500-r,540+r,500+r),outline=(*theme["accent"],),width=4)
    title=clean_text(message or "Bravo !")
    f=get_font(72,ff)
    lines=wrap_text(title,f,860)[:3]
    y=560-int(60*(1-p))
    for line in lines:
        tw=text_width(draw,line,f)
        draw.text(((WIDTH-tw)/2+4,y+6),line,font=f,fill=(0,0,0))
        draw.text(((WIDTH-tw)/2,y),line,font=f,fill="white")
        y+=100
    sub=clean_text(subtitle or "")
    if sub:
        sf=get_font(34,ff)
        slines=wrap_text(sub,sf,800)[:2]
        sy=y+28
        for line in slines:
            tw=text_width(draw,line,sf)
            draw.text(((WIDTH-tw)/2,sy),line,font=sf,fill=theme["accent"])
            sy+=52
    draw_brand(draw,theme,channel)
    return img

def draw_page_template(text, theme_name, channel, bg_file=None, progress=1.0, kind="intro", variant="Premium lumineux", module="quiz", style="1", language="Français"):
    """Pages intro/outro premium. Toutes les variantes restent lumineuses, lisibles et cohérentes avec SuspenseLingo."""
    variant = clean_text(variant or "Premium lumineux")
    theme = THEMES[theme_name]
    cfg = _layout(module, style)
    ff = cfg.get("font_family", "DejaVu Sans")
    p = ease_out(progress)
    title = clean_text(text or ("Prêt ? C'est parti !" if kind == "intro" else "Merci d'avoir joué !"))
    brand = clean_text(channel or "SuspenseLingo") or "SuspenseLingo"

    # Base volontairement plus lumineuse : aucun écran de fin presque noir.
    img = add_top_glow(make_base(theme_name, bg_file), theme, 1.12 + 0.08*p)
    draw = ImageDraw.Draw(img)

    # Variante 1 — Premium lumineux : référence principale.
    if variant == "Premium lumineux":
        # Voile clair et carte premium pour détacher le message du fond.
        panel = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
        pd = ImageDraw.Draw(panel)
        pd.rounded_rectangle((72, 300, 1008, 1515), radius=48,
                             fill=(9,24,52,218), outline=(*theme["accent"],190), width=3)
        pd.rounded_rectangle((92, 320, 988, 1495), radius=40,
                             outline=(255,255,255,38), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), panel).convert("RGB")
        draw = ImageDraw.Draw(img)
        lf=get_font(26,ff); lw=text_width(draw,brand,lf)
        draw.text(((WIDTH-lw)/2,390),brand,font=lf,fill=theme["accent"])
        draw.line((270,455,810,455),fill=(255,255,255,65),width=2)
        _motivation_icon(draw,theme,"start" if kind=="intro" else "end",540,610,86,p)
        f=get_font(66,ff); lines=wrap_text(title,f,800)[:3]
        y=790-int(30*(1-p))
        for line in lines:
            tw=text_width(draw,line,f)
            draw.text(((WIDTH-tw)/2+4,y+6),line,font=f,fill=(0,0,0))
            draw.text(((WIDTH-tw)/2,y),line,font=f,fill=(255,255,255))
            y+=92
        sub="C'est parti !" if kind=="intro" else "À très bientôt !"
        sf=get_font(29,ff); sw=text_width(draw,sub,sf)
        draw.text(((WIDTH-sw)/2,1165),sub,font=sf,fill=(225,232,244))
        draw.rounded_rectangle((220,1300,860,1314),radius=7,fill=(255,255,255,35))
        draw.rounded_rectangle((220,1300,220+int(640*p),1314),radius=7,fill=theme["accent"])
        draw.text(((WIDTH-text_width(draw,brand,get_font(20,ff)))/2,1415),brand,font=get_font(20,ff),fill=(190,201,220))
        return img

    # Variante 2 — Éclat néon premium : moderne mais toujours claire et élégante.
    if variant == "Néon élégant":
        # Deux halos décoratifs et une carte translucide; pas de gros cadre sombre.
        draw.ellipse((80,250,420,590),fill=(*theme["accent"],28))
        draw.ellipse((690,1120,1030,1460),fill=(*theme["accent"],22))
        panel=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0)); pd=ImageDraw.Draw(panel)
        pd.rounded_rectangle((78,410,1002,1390),radius=54,fill=(12,32,65,205),outline=(*theme["accent"],220),width=4)
        pd.rounded_rectangle((98,430,982,1370),radius=44,outline=(255,255,255,42),width=2)
        img=Image.alpha_composite(img.convert("RGBA"),panel).convert("RGB"); draw=ImageDraw.Draw(img)
        lf=get_font(25,ff); lw=text_width(draw,brand.upper(),lf)
        draw.text(((WIDTH-lw)/2,500),brand.upper(),font=lf,fill=theme["accent"])
        _motivation_icon(draw,theme,"start" if kind=="intro" else "end",540,650,92,p)
        f=get_font(64,ff); lines=wrap_text(title,f,790)[:3]
        y=820-int(28*(1-p))
        for line in lines:
            tw=text_width(draw,line,f)
            draw.text(((WIDTH-tw)/2+4,y+6),line,font=f,fill=(0,0,0))
            draw.text(((WIDTH-tw)/2,y),line,font=f,fill=(255,255,255))
            y+=90
        draw.line((250,1150,830,1150),fill=theme["accent"],width=3)
        sf=get_font(28,ff); sub="Ton défi commence maintenant" if kind=="intro" else "Merci pour ta participation !"
        sw=text_width(draw,sub,sf); draw.text(((WIDTH-sw)/2,1200),sub,font=sf,fill=(220,230,245))
        draw_brand(draw,theme,brand,None)
        return img

    # Variante 3 — Élégance éditoriale : sobre, luxueuse et lumineuse.
    # Elle évite l'ancien écran minimal trop vide.
    panel=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0)); pd=ImageDraw.Draw(panel)
    pd.rounded_rectangle((110,350,970,1450),radius=36,fill=(245,248,252,235),outline=(*theme["accent"],220),width=3)
    pd.rounded_rectangle((128,368,952,1432),radius=28,outline=(255,255,255,210),width=2)
    img=Image.alpha_composite(img.convert("RGBA"),panel).convert("RGB"); draw=ImageDraw.Draw(img)
    # Bandeau supérieur coloré et marque.
    draw.rounded_rectangle((170,455,910,535),radius=20,fill=theme["accent"])
    lf=get_font(24,ff); lw=text_width(draw,brand,lf)
    draw.text(((WIDTH-lw)/2,480),brand,font=lf,fill=(10,18,35))
    _motivation_icon(draw,theme,"start" if kind=="intro" else "end",540,680,86,p)
    f=get_font(62,ff); lines=wrap_text(title,f,730)[:3]
    y=820-int(25*(1-p))
    for line in lines:
        tw=text_width(draw,line,f)
        draw.text(((WIDTH-tw)/2,y),line,font=f,fill=(18,31,55))
        y+=88
    sub="PRÊT POUR LE DÉFI" if kind=="intro" else "À BIENTÔT"
    sf=get_font(24,ff); sw=text_width(draw,sub,sf)
    draw.text(((WIDTH-sw)/2,1190),sub,font=sf,fill=theme["accent"])
    draw.line((245,1260,835,1260),fill=(18,31,55,55),width=2)
    draw.text(((WIDTH-text_width(draw,"SuspenseLingo",get_font(19,ff)))/2,1320),"SuspenseLingo",font=get_font(19,ff),fill=(90,105,125))
    return img


def draw_hook(text,theme_name,channel,bg_file=None,progress=1.0,module="quiz",style="1",language="Français"):
    theme=THEMES[theme_name]
    ff=_layout(module, style).get("font_family","DejaVu Sans")
    p=ease_back(progress)
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.25*p)
    draw=ImageDraw.Draw(img)
    brand=clean_text(channel or "SuspenseLingo")
    bf=get_font(34,ff); bw=text_width(draw,brand,bf)
    draw.text(((WIDTH-bw)/2,300),brand,font=bf,fill=theme["accent"])
    _motivation_icon(draw,theme,"end",540,485,78,p)
    lf=get_font(32,ff); label="NEXT CHALLENGE"; lw=text_width(draw,label,lf)
    draw.text(((WIDTH-lw)/2,610),label,font=lf,fill=theme["accent"])
    visible=_motivation_text_clean(text)
    f=get_font(64,ff); lines=wrap_text(visible,f,850)[:3] or ["See you next time!"]
    y=735-int(45*(1-ease_out(p)))
    for line in lines:
        tw=text_width(draw,line,f)
        draw.text(((WIDTH-tw)/2+4,y+6),line,font=f,fill=(0,0,0))
        draw.text(((WIDTH-tw)/2,y),line,font=f,fill="white")
        y+=88
    cta_subs={"Français":"Abonne-toi à SuspenseLingo !","Anglais":"Follow SuspenseLingo for the next quiz!","Espagnol":"¡Suscríbete a SuspenseLingo!","Arabe":"اشترك في SuspenseLingo!","Allemand":"Abonniere SuspenseLingo!","Italien":"Iscriviti a SuspenseLingo!"}
    sub=cta_subs.get(str(language),cta_subs["Français"])
    sf=get_font(29,ff); sw=text_width(draw,sub,sf)
    draw.text(((WIDTH-sw)/2,1115),sub,font=sf,fill=(220,228,242))
    draw.rounded_rectangle((180,1270,900,1284),radius=7,fill=(55,62,78))
    draw.rounded_rectangle((180,1270,180+int(720*clamp(p)),1284),radius=7,fill=theme["accent"])
    sf2=get_font(21,ff); sw2=text_width(draw,brand,sf2)
    draw.text(((WIDTH-sw2)/2,1450),brand,font=sf2,fill=theme["muted"])
    return img

def draw_explanation_scene(question,answer,explanation,theme_name,channel,bg_file=None,active_word=-1,pulse=0.0,progress=1.0,q_num=1,total=1,video_title="Culture Générale"):
    theme=THEMES[theme_name]
    ff=_layout("quiz", "1").get("font_family","DejaVu Sans")
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.0+0.3*pulse)
    draw=ImageDraw.Draw(img)
    draw_header(draw,theme,q_num,total,video_title)
    # Keep the quiz visible during the explanation, with the correct answer highlighted.
    rounded_text(draw,(60,620,1020,738),f"✓ {answer}",get_font(42,ff),theme["success"],None,0,30)
    words=clean_text(explanation or "Bravo !").split()
    f=get_font(45,ff)
    max_w=900
    lines=[]; cur=[]
    for w in words:
        cand=w if not cur else " ".join(cur+[w])
        if text_width(draw,cand,f)<=max_w: cur.append(w)
        else:
            if cur: lines.append(cur)
            cur=[w]
    if cur: lines.append(cur)
    lines=lines[:5]
    # Explanation deliberately sits low in the frame, like a compact knowledge card.
    box_y1,box_y2=790,1175
    draw.rounded_rectangle((60,box_y1,1020,box_y2),radius=30,fill=theme["card"],outline=theme["accent"],width=3)
    draw.text((145,820),"EXPLICATION",font=get_font(32),fill=theme["accent"])
    # ampoule vectorielle
    draw.ellipse((100,812,128,844),outline=theme["accent"],width=3)
    draw.line((106,850,122,850),fill=theme["accent"],width=3)
    draw.line((110,856,118,856),fill=theme["accent"],width=3)
    yy=885
    idx=0
    for line in lines:
        widths=[text_width(draw,w,f) for w in line]
        space=text_width(draw," ",f); totalw=sum(widths)+space*max(0,len(line)-1)
        x=(WIDTH-totalw)/2
        for w,ww in zip(line,widths):
            active=(idx==active_word)
            col=theme["accent"] if active else "white"
            # Karaoké propre : aucune boîte autour du mot actif.
            # Seule la couleur du texte change pendant la prononciation.
            draw.text((x,yy),w,font=f,fill=col)
            x+=ww+space; idx+=1
        yy+=58
    draw_brand(draw,theme,channel,progress)
    sf=get_font(23)
    return img


def draw_vocab_frame(items,idx,langue,theme_name,channel,bg_file=None,phase="mot",timer=None,timer_fraction=1.0,entrance=1.0,translation_active_word=-1,source_active_word=-1):
    cfg=_layout("vocab", "1"); theme=THEMES[theme_name]; ff=cfg.get("font_family","DejaVu Sans")
    base=bg_file.copy() if isinstance(bg_file,Image.Image) else make_base(theme_name,bg_file)
    alpha=int(clamp(cfg.get("bg_opacity",18),0,90))
    if alpha: base=Image.alpha_composite(base.convert("RGBA"),Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,alpha))).convert("RGB")
    img=add_top_glow(base,theme); draw=ImageDraw.Draw(img)
    draw_unified_header(draw,cfg,idx+1,len(items),"Vocabulaire")
    item=items[idx]; fr=clean_text(item.get("fr","")); tr=clean_text(item.get("trad","")); p=ease_out(entrance)
    if cfg.get("animation")=="Machine à écrire": fr=fr[:max(1,int(len(fr)*p))]
    elif cfg.get("animation")=="Glissement vertical": fr=" "*0+fr
    fbig=get_font(int(cfg.get("question_size",58)),ff); qx=int(cfg.get("question_x",540)); y=int(cfg.get("question_y",500))
    # Mot/phrase source : mot actuellement prononcé mis en évidence sans masquer le reste.
    words_src=fr.split()
    if len(words_src)>1 and source_active_word>=0:
        widths=[text_width(draw,w,fbig) for w in words_src]; space=text_width(draw," ",fbig); totalw=sum(widths)+space*(len(words_src)-1); sx=qx-totalw/2
        for wi,(word,ww) in enumerate(zip(words_src,widths)):
            current=wi==int(source_active_word)
            if current:
                pad=7; draw.rounded_rectangle((sx-pad,y-6,sx+ww+pad,y+text_height(fbig,word)+6),radius=12,fill=_hex_rgb(cfg.get("answer2"),theme["card2"]),outline=_hex_rgb(cfg.get("correct"),theme["success"]),width=2)
            draw.text((sx,y),word,font=fbig,fill=_hex_rgb(cfg.get("primary"),theme["accent"]) if not current else _hex_rgb(cfg.get("correct"),theme["success"]))
            sx+=ww+space
    else:
        tw=text_width(draw,fr,fbig); draw.text((qx-tw/2,y),fr,font=fbig,fill=_hex_rgb(cfg.get("primary"),theme["accent"]))
    if phase in ("translation","reveal"):
        ft=get_font(int(cfg.get("answer_size",42)),ff); lines=wrap_text(tr,ft,int(cfg.get("translation_width",850))); yy=int(cfg.get("translation_y",760)); tx=int(cfg.get("translation_x",540))
        global_idx=0
        for line in lines:
            words_line=line.split(); widths=[text_width(draw,z,ft) for z in words_line]; space=text_width(draw," ",ft)
            totalw=sum(widths)+space*max(0,len(words_line)-1); xx=tx-totalw/2
            for wi,(word,ww) in enumerate(zip(words_line,widths)):
                active_word=(global_idx==int(translation_active_word))
                if active_word:
                    pad=6
                    draw.rounded_rectangle((xx-pad,yy-4,xx+ww+pad,yy+text_height(ft,word)+5),radius=10,fill=_hex_rgb(cfg.get("answer2"),theme["card2"]),outline=_hex_rgb(cfg.get("correct"),theme["success"]),width=2)
                draw.text((xx,yy),word,font=ft,fill=_hex_rgb(cfg.get("correct"),theme["success"]))
                xx+=ww+space; global_idx+=1
            yy+=text_height(ft,line)+8
    if phase=="countdown" and timer is not None and cfg.get("show_timer"): draw_inline_timer(draw,theme,int(cfg.get("timer_x",540)),int(cfg.get("timer_y",760)),timer,timer_fraction,"vocab","1")
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
def _write_wav_mono(path, samples, rate=44100):
    with wave.open(path,"w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        for v in samples: f.writeframes(struct.pack("<h",max(-32767,min(32767,int(v)))))
    return path

def make_sfx(tmpdir):
    """Pack d'effets sonores courts, générés localement (0 quota) : tic, ding, pop, whoosh."""
    rate=44100
    tic=os.path.join(tmpdir,"tic.wav")
    ding=os.path.join(tmpdir,"ding.wav")
    pop=os.path.join(tmpdir,"pop.wav")
    whoosh=os.path.join(tmpdir,"whoosh.wav")
    # Tic net mais court.
    n=int(rate*.10); _write_wav_mono(tic,[13000*math.sin(2*math.pi*1100*i/rate)*math.exp(-i/800) for i in range(n)],rate)
    # Ding double-ton, réservé à la fin du chrono / bonne réponse.
    n=int(rate*.45); _write_wav_mono(ding,[11500*(math.sin(2*math.pi*1318*i/rate)+math.sin(2*math.pi*1568*i/rate))*math.exp(-i/4500) for i in range(n)],rate)
    # Pop discret pour l'apparition d'un mot / d'une réponse.
    n=int(rate*.14); _write_wav_mono(pop,[10500*(math.sin(2*math.pi*(420+900*i/max(1,n-1))*i/rate))*math.exp(-i/2600) for i in range(n)],rate)
    # Whoosh synthétique très court pour l'entrée d'une question.
    n=int(rate*.20); _write_wav_mono(whoosh,[6500*math.sin(2*math.pi*(260+1450*(i/max(1,n-1))) * i/rate)*(math.sin(math.pi*i/max(1,n-1))**1.7) for i in range(n)],rate)
    return tic,ding,pop,whoosh

def make_sfx_countdown(tic,ding,tmpdir):
    # 3 -> 2 -> 1 avec tic/tac plus présent + pulsation légère, puis ding net.
    # Le dernier son reste réservé à la révélation / fin du chrono.
    out=os.path.join(tmpdir,"countdown.wav")
    rate=44100
    pulse=os.path.join(tmpdir,"countdown_pulse.wav")
    n=int(rate*3.12)
    samples=[]
    for i in range(n):
        t=i/rate
        # Trois battements courts, légèrement plus intenses à l'approche de la fin.
        beat=min([abs(t-x) for x in (0.48,1.48,2.48)])
        env=math.exp(-beat/0.055)
        value=(6500+2500*(t/3.12))*math.sin(2*math.pi*72*t)*env
        samples.append(value)
    _write_wav_mono(pulse,samples,rate)
    cmd=[get_ffmpeg(),"-y","-i",tic,"-i",ding,"-i",pulse,
         "-filter_complex",
         "[0:a]adelay=0|0,volume=1.15[a0];[0:a]adelay=1000|1000,volume=1.22[a1];[0:a]adelay=2000|2000,volume=1.30[a2];[1:a]adelay=3000|3000,volume=0.82[ad];[2:a]volume=0.55[p];[a0][a1][a2][ad][p]amix=inputs=5:duration=longest,apad=pad_dur=0.12,atrim=duration=3.12",
         "-c:a","pcm_s16le",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return out

def make_vocab_style2_countdown_sfx(tic,ding,tmpdir):
    """Style 2 Vocabulaire uniquement.
    Réflexion type montre : tic/tac audibles pendant 3 secondes, puis ding net.
    La traduction commence seulement après ce son de fin.
    """
    out=os.path.join(tmpdir,"vocab_style2_countdown.wav")
    tock=os.path.join(tmpdir,"vocab_style2_tock.wav")

    # Tock légèrement plus grave pour obtenir une vraie sensation tic/tac.
    rate=44100
    n=int(rate*0.085)
    _write_wav_mono(
        tock,
        [
            11500*math.sin(2*math.pi*820*i/rate)*math.exp(-i/700)
            for i in range(n)
        ],
        rate
    )

    cmd=[get_ffmpeg(),"-y","-i",tic,"-i",tock,"-i",ding,
         "-filter_complex",
         "[0:a]volume=1.20,adelay=120|120[t1];"
         "[1:a]volume=1.05,adelay=620|620[t2];"
         "[0:a]volume=1.20,adelay=1120|1120[t3];"
         "[1:a]volume=1.05,adelay=1620|1620[t4];"
         "[0:a]volume=1.20,adelay=2120|2120[t5];"
         "[1:a]volume=1.05,adelay=2620|2620[t6];"
         "[2:a]volume=1.15,adelay=3120|3120[ding];"
         "[t1][t2][t3][t4][t5][t6][ding]"
         "amix=inputs=7:duration=longest:dropout_transition=0,"
         "apad=pad_dur=0.08,atrim=duration=3.55,asetpts=PTS-STARTPTS",
         "-c:a","pcm_s16le",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return out


def make_end_tick(tic,ding,tmpdir):
    out=os.path.join(tmpdir,"reflection_end.wav")
    cmd=[get_ffmpeg(),"-y","-i",ding,"-filter_complex","[0:a]volume=0.75[a]","-map","[a]","-t","0.45",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return out

def make_suspense_music(duration,tmpdir,name,volume=0.08):
    """Petite nappe de suspense générée localement : aucun fichier musical externe."""
    duration=max(0.2,float(duration))
    out=os.path.join(tmpdir,f"{name}.wav")
    vol=max(0.0,min(0.25,float(volume)))
    fade_out=max(0.05,min(0.35,duration*0.18))
    fade_start=max(0.0,duration-fade_out)
    filt=(
        f"[0:a]volume={vol:.3f},lowpass=f=900,afade=t=in:st=0:d=0.12,afade=t=out:st={fade_start:.3f}:d={fade_out:.3f}[a];"
        f"[1:a]volume={vol*0.42:.3f},lowpass=f=1200,afade=t=in:st=0:d=0.12,afade=t=out:st={fade_start:.3f}:d={fade_out:.3f}[b];"
        "[a][b]amix=inputs=2:duration=longest:dropout_transition=0"
    )
    cmd=[get_ffmpeg(),"-y",
         "-f","lavfi","-i",f"sine=frequency=92:sample_rate=44100:duration={duration:.3f}",
         "-f","lavfi","-i",f"sine=frequency=138:sample_rate=44100:duration={duration:.3f}",
         "-filter_complex",filt,"-c:a","pcm_s16le",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return out

def make_quiz_background_music(duration,tmpdir,name,volume=1.0,style="Suspense léger",countdown_start=None,countdown_duration=3.12):
    """Fond musical local audible : harmonie + petite mélodie + pulsation douce."""
    duration=max(0.4,float(duration)); out=os.path.join(tmpdir,f"{name}.wav")
    gain=max(0.0,min(1.0,float(volume))); style=str(style or "Suspense léger"); rate=44100
    presets={"Suspense sombre":([55,73,92,110],[110,92,73,110],1.7),"Mystère":([73,92,110,146],[146,110,92,73],1.9),"Tension":([82,110,138,165],[165,138,110,82],2.3),"Défi intense":([92,123,155,196],[196,155,123,92],3.0),"Quiz futuriste":([98,147,196,247],[247,196,147,98],2.7),"Cinématique":([65,87,116,174],[174,116,87,65],2.0),"Suspense léger":([110,146,174,220],[220,174,146,220],2.2),"Chill":([98,123,147,196],[196,147,123,196],1.8),"Pop légère":([110,138,165,220],[220,165,138,220],2.8)}
    chords,melody,beat_speed=presets.get(style,presets["Suspense léger"]); n=int(duration*rate); samples=[]
    fi=int(min(0.35,duration*0.12)*rate); fo=int(min(0.50,duration*0.16)*rate)
    for i in range(n):
        t=i/rate; beat=t*beat_speed; step=int(beat)%4; phase=beat-step
        root=chords[step]; third=chords[(step+1)%4]; fifth=chords[(step+2)%4]
        harmonic=0.44*math.sin(2*math.pi*root*t)+0.25*math.sin(2*math.pi*third*t)+0.16*math.sin(2*math.pi*fifth*t)+0.07*math.sin(2*math.pi*root*2*t)
        melodic=0.24*math.exp(-3.0*phase)*math.sin(2*math.pi*melody[step]*t)
        pulse=0.80+0.20*math.sin(2*math.pi*beat_speed*t)
        tension=1.0
        if countdown_start is not None and float(countdown_start) <= t <= float(countdown_start)+float(countdown_duration):
            cp=(t-float(countdown_start))/max(0.1,float(countdown_duration))
            tension=1.0+0.28*cp+0.10*math.sin(2*math.pi*3*cp)
        value=(harmonic*pulse+melodic)*0.22*gain*tension
        if i<fi: value*=i/max(1,fi)
        if i>=n-fo: value*=max(0,(n-i)/max(1,fo))
        samples.append(int(max(-32767,min(32767,value*32767))))
    _write_wav_mono(out,samples,rate); return out


def prepare_custom_background_music(uploaded,duration,tmpdir,name):
    if uploaded is None: return None
    src=os.path.join(tmpdir,f"{name}_source")
    data=uploaded.getvalue() if hasattr(uploaded,"getvalue") else uploaded
    with open(src,"wb") as f: f.write(data)
    out=os.path.join(tmpdir,f"{name}.wav")
    cmd=[get_ffmpeg(),"-y","-stream_loop","-1","-i",src,"-t",f"{max(0.4,float(duration)):.3f}","-ac","2","-ar","44100","-c:a","pcm_s16le",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return out

def mix_background_music(voice_path,music_path,output,voice_volume=1.0,music_volume=0.10):
    """Mixage robuste. 0.10≈-6 dB et 0.15≈-3 dB pour que la musique reste audible."""
    user=max(0.0,min(0.30,float(music_volume))); music_db=-12.0+(user/0.30)*18.0; music_db=max(-18.0,min(4.0,music_db))
    filt=(f"[0:a]volume={float(voice_volume):.3f}[v];" f"[1:a]highpass=f=55,lowpass=f=7000,volume={music_db:.2f}dB[m];" "[v][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.94")
    cmd=[get_ffmpeg(),"-y","-i",voice_path,"-i",music_path,"-filter_complex",filt,"-c:a","aac","-b:a","256k","-ar","44100","-ac","2","-shortest",output]
    res=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if res.returncode!=0: raise RuntimeError("Impossible de mixer la musique de fond : "+res.stderr[-1200:])
    return output


def mix_voice_sfx(voice_path,sfx_path,output,delay_ms=0,sfx_volume=0.65):
    filt=f"[1:a]volume={sfx_volume},adelay={delay_ms}|{delay_ms}[s];[0:a][s]amix=inputs=2:duration=longest:dropout_transition=0"
    cmd=[get_ffmpeg(),"-y","-i",voice_path,"-i",sfx_path,"-filter_complex",filt,"-c:a","aac","-b:a","160k","-shortest",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def concat_audio_files(audio_files, output):
    """Concatène les segments audio dans l'ordre et réencode en AAC/M4A."""
    inputs=[]
    for p in audio_files: inputs += ["-i",p]
    labels="".join(f"[{i}:a]" for i in range(len(audio_files)))
    filt=f"{labels}concat=n={len(audio_files)}:v=0:a=1[a]"
    cmd=[get_ffmpeg(),"-y",*inputs,"-filter_complex",filt,"-map","[a]","-c:a","aac","-b:a","160k","-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return output


# ---------------------- Video encoding ----------------------
def make_image_video(frames,output,fps=30):
    list_path=output+".txt"
    with open(list_path,"w",encoding="utf-8") as f:
        for path,duration in frames:
            f.write(f"file '{path.replace(chr(92),'/')}'\n")
            f.write(f"duration {max(0.033,float(duration))}\n")
        if frames: f.write(f"file '{frames[-1][0].replace(chr(92),'/')}'\n")
    cmd=[get_ffmpeg(),"-y","-f","concat","-safe","0","-i",list_path,"-vf",f"fps={fps},format=yuv420p","-c:v","libx264","-preset",VIDEO_PRESET,"-crf",str(VIDEO_CRF),"-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def mux_audio(video,audio,output,volume=1.0):
    cmd=[get_ffmpeg(),"-y","-i",video,"-i",audio,"-filter:a",f"volume={volume}","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True); return output

def video_duration(path):
    """Durée fiable d'une vidéo, utilisée pour verrouiller vidéo et voix sur la même durée."""
    res=subprocess.run([get_ffmpeg(),"-i",path],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    m=re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)",res.stderr)
    if not m: return 0.0
    h,mi,sec=m.groups()
    return float(h)*3600+float(mi)*60+float(sec)

def _normalize_video_to_audio(raw_video,audio_path,output_path):
    """Force chaque segment vidéo à avoir exactement la durée de son audio.
    Si la vidéo est trop courte, la dernière image est gelée; si elle est trop longue,
    elle est coupée. Cela évite les fins de vidéo avant la voix, surtout en vocabulaire.
    """
    target=max(0.05,audio_duration(audio_path))
    current=video_duration(raw_video)
    if current <= 0:
        raise ValueError("La vidéo intermédiaire n'a pas de durée valide.")
    if current < target-0.03:
        extra=target-current
        vf=f"tpad=stop_mode=clone:stop_duration={extra:.3f},fps={FPS},format=yuv420p"
    else:
        vf=f"trim=duration={target:.3f},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p"
    cmd=[get_ffmpeg(),"-y","-i",raw_video,"-an","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","22","-movflags","+faststart",output_path]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return output_path

def make_segment(frames,audio,output,tmpdir,volume=1.0):
    """Encode directement les images + la voix en un seul passage FFmpeg.
    La durée cible vient de l'audio; une petite réserve de tpad évite toute coupure
    si le dernier intervalle d'image est légèrement plus court. Cela supprime les
    deux encodages intermédiaires de l'ancienne version et accélère fortement le rendu.
    """
    if not frames:
        raise ValueError("Aucune image à encoder pour le segment.")
    target=max(0.05,audio_duration(audio))
    list_path=os.path.join(tmpdir,os.path.basename(output)+".frames.txt")
    with open(list_path,"w",encoding="utf-8") as f:
        for path,duration in frames:
            f.write(f"file '{path.replace(chr(92),'/')}'\n")
            f.write(f"duration {max(0.033,float(duration)):.6f}\n")
        # Le concat demuxer utilise la dernière durée comme intervalle final.
        f.write(f"file '{frames[-1][0].replace(chr(92),'/')}'\n")

    af=[]
    if abs(float(volume)-1.0)>1e-6:
        af=["-af",f"volume={float(volume):.3f}"]
    vf=f"fps={FPS},tpad=stop_mode=clone:stop_duration=3,format=yuv420p"
    cmd=[get_ffmpeg(),"-y",
         "-f","concat","-safe","0","-i",list_path,
         "-i",audio,
         "-map","0:v:0","-map","1:a:0",
         "-vf",vf,
         "-t",f"{target:.3f}",
         "-c:v","libx264","-preset",VIDEO_PRESET,"-crf",str(VIDEO_CRF),
         "-c:a","aac","-b:a","160k",*af,
         "-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return output

def make_vocab_style2_segment(frames,audio,output,tmpdir,volume=1.0):
    """Encodeur robuste réservé au Vocabulaire Style 2.
    1) construit la vidéo à partir des durées d'images,
    2) force sa durée à celle de la voix,
    3) remuxe ensuite la voix.
    Cette méthode évite les décalages de timebase observés sur 15 lignes.
    """
    if not frames:
        raise ValueError("Aucune image à encoder pour le segment Vocabulaire Style 2.")

    raw=os.path.join(tmpdir,os.path.basename(output)+".raw.mp4")
    normalized=os.path.join(tmpdir,os.path.basename(output)+".norm.mp4")

    make_image_video(frames,raw,fps=FPS)
    _normalize_video_to_audio(raw,audio,normalized)

    if abs(float(volume)-1.0)>1e-6:
        mux_audio(normalized,audio,output,volume=float(volume))
    else:
        mux_audio(normalized,audio,output,volume=1.0)

    target=audio_duration(audio)
    actual=video_duration(output)
    if actual>0 and abs(actual-target)>0.04:
        # Dernier verrou du segment.
        _normalize_video_to_audio(output,audio,normalized)
        mux_audio(normalized,audio,output,volume=float(volume))

    return output


def word_timed_frames(audio_path, words, frame_fn, duration=None):
    """Construit des images dont les intervalles suivent les WordBoundaries TTS.
    Le premier intervalle commence toujours à 0 et le dernier va jusqu'à la fin
    de l'audio, afin de ne jamais perdre le début ou la fin de la voix.
    """
    dur=max(0.05,float(duration or audio_duration(audio_path)))
    clean_words=[]
    for w in (words or []):
        try:
            start=max(0.0,min(dur,float(w.get("start",0.0))))
            end=max(start,min(dur,float(w.get("end",start))))
            if end>start+0.005:
                clean_words.append((start,end))
        except Exception:
            pass
    clean_words.sort(key=lambda x:x[0])
    if not clean_words:
        return [(frame_fn(-1,0.0),dur)]
    out=[]; cursor=0.0
    for i,(start,end) in enumerate(clean_words):
        if start>cursor+0.005:
            out.append((frame_fn(max(-1,i-1),cursor),start-cursor))
        out.append((frame_fn(i,start),end-start))
        cursor=end
    if cursor<dur-0.005:
        out.append((frame_fn(len(clean_words)-1,cursor),dur-cursor))
    return out

def word_timed_frames_vocab_style2(audio_path, words, frame_fn, duration=None):
    """Timing dédié au Vocabulaire Style 2.
    Chaque mot devient visible à son WordBoundary START et reste visible
    jusqu'au début du mot suivant. C'est volontairement différent du découpage
    par END : cela évite que l'écriture paraisse plus rapide que la voix.
    """
    dur=max(0.05,float(duration or audio_duration(audio_path)))
    starts=[]

    for w in (words or []):
        try:
            st=max(0.0,min(dur,float(w.get("start",0.0))))
            if not starts or st>starts[-1]+0.005:
                starts.append(st)
        except Exception:
            pass

    if not starts:
        return [(frame_fn(-1,0.0),dur)]

    out=[]
    cursor=0.0

    # Petit silence initial éventuel : aucun mot n'est encore affiché.
    if starts[0]>0.02:
        out.append((frame_fn(-1,0.0),starts[0]))
        cursor=starts[0]

    for i,st in enumerate(starts):
        st=max(cursor,st)
        next_st=starts[i+1] if i+1<len(starts) else dur
        end=max(st,min(dur,next_st))

        if end>st+0.005:
            # motion est seulement utilisé pour les animations légères; la
            # visibilité des mots est pilotée par i, donc par la voix.
            out.append((frame_fn(i,0.0),end-st))
            cursor=end

    if not out:
        return [(frame_fn(-1,0.0),dur)]

    total=sum(float(d) for _,d in out)
    if abs(total-dur)>0.002:
        img,last=out[-1]
        out[-1]=(img,max(0.033,float(last)+(dur-total)))

    return out


def _repair_final_av_sync(path, tmpdir):
    """Dernier verrou : durée vidéo exactement égale à la durée audio finale."""
    target=max(0.05,audio_duration(path)); current=max(0.0,video_duration(path))
    repaired=os.path.join(tmpdir,os.path.basename(path)+".avfix.mp4")
    if current < target-0.03:
        vf=f"tpad=stop_mode=clone:stop_duration={target-current:.3f},fps={FPS},format=yuv420p"
    else:
        vf=f"trim=duration={target:.3f},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p"
    cmd=[get_ffmpeg(),"-y","-i",path,"-map","0:v","-map","0:a","-vf",vf,"-t",f"{target:.3f}","-c:v","libx264","-preset","veryfast","-crf","22","-c:a","aac","-b:a","160k","-movflags","+faststart",repaired]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    os.replace(repaired,path)
    return path

def concat_videos(clips,output,tmpdir):
    """Assemble les segments sans réencoder dans le cas normal.
    Tous les segments sortent avec le même codec, fps et résolution; on évite donc
    le gros réencodage final. Une réparation complète ne se déclenche qu'en cas de
    décalage mesurable entre la durée audio et vidéo finales.
    """
    clips=[p for p in clips if p and os.path.exists(p)]
    if not clips: raise ValueError("Aucun segment à concaténer.")
    lst=os.path.join(tmpdir,"concat.txt")
    with open(lst,"w",encoding="utf-8") as f:
        for p in clips: f.write(f"file '{p.replace(chr(92),'/')}'\n")
    try:
        cmd=[get_ffmpeg(),"-y","-f","concat","-safe","0","-i",lst,
             "-map","0:v:0","-map","0:a:0","-c","copy","-avoid_negative_ts","make_zero",output]
        subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    except subprocess.CalledProcessError:
        # Fallback exceptionnel si FFmpeg refuse le stream-copy (timebase/metadata).
        raw=os.path.join(tmpdir,"concat_reencoded.mp4")
        cmd=[get_ffmpeg(),"-y","-fflags","+genpts","-f","concat","-safe","0","-i",lst,
             "-map","0:v:0","-map","0:a:0","-vf",f"fps={FPS},format=yuv420p","-r",str(FPS),
             "-c:v","libx264","-preset",VIDEO_PRESET,"-crf",str(VIDEO_CRF),
             "-c:a","aac","-b:a","160k","-movflags","+faststart",raw]
        subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        os.replace(raw,output)

    # Contrôle léger: pas de seconde passe si tout est déjà aligné.
    vd=video_duration(output); ad=audio_duration(output)
    if vd>0 and abs(vd-ad)>0.08:
        _repair_final_av_sync(output,tmpdir)
    return output

def concat_videos_precise(clips, output, tmpdir):
    """Concaténation réencodée précise, réservée au Vocabulaire Style 2.
    Elle évite que de petites différences de timebase/PTS s'accumulent sur 15 questions.
    """
    clips=[p for p in clips if p and os.path.exists(p)]
    if not clips:
        raise ValueError("Aucun segment à concaténer.")
    lst=os.path.join(tmpdir,"concat_precise.txt")
    with open(lst,"w",encoding="utf-8") as f:
        for p in clips:
            f.write(f"file '{p.replace(chr(92),'/')}'\n")
    cmd=[get_ffmpeg(),"-y","-fflags","+genpts",
         "-f","concat","-safe","0","-i",lst,
         "-map","0:v:0","-map","0:a:0",
         "-vf",f"fps={FPS},format=yuv420p",
         "-c:v","libx264","-preset",VIDEO_PRESET,"-crf",str(VIDEO_CRF),
         "-c:a","aac","-b:a","160k",
         "-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    vd=video_duration(output); ad=audio_duration(output)
    if vd>0 and abs(vd-ad)>0.08:
        _repair_final_av_sync(output,tmpdir)
    return output

def _concat_videos_style2_chunk(clips, output, tmpdir):
    """Concatène un petit groupe avec le même moteur PTS/audio que V6.
    On limite volontairement le nombre d'entrées FFmpeg pour éviter le pic RAM
    de V6, tout en conservant le réencodage qui faisait fonctionner le chrono,
    le tic/tac et le ding correctement.
    """
    clips=[p for p in clips if p and os.path.exists(p)]
    if not clips:
        raise ValueError("Aucun segment à concaténer.")
    if len(clips)==1:
        import shutil
        if os.path.abspath(clips[0]) != os.path.abspath(output):
            shutil.copyfile(clips[0], output)
        return output

    inputs=[]; graph=[]; pairs=[]
    for i,p in enumerate(clips):
        inputs += ["-i",p]
        graph.append(f"[{i}:v:0]fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[v{i}];")
        graph.append(f"[{i}:a:0]aresample=async=1:first_pts=0[a{i}];")
        pairs.append(f"[v{i}][a{i}]")
    graph.append("".join(pairs)+f"concat=n={len(clips)}:v=1:a=1[outv][outa]")

    cmd=[get_ffmpeg(),"-y",*inputs,
         "-filter_complex","".join(graph),
         "-map","[outv]","-map","[outa]",
         "-c:v","libx264","-preset",VIDEO_PRESET,"-crf",str(VIDEO_CRF),
         "-c:a","aac","-b:a","160k",
         "-movflags","+faststart",output]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return output


def concat_videos_style2(clips,output,tmpdir):
    """V8 : même mécanique audio/vidéo fiable que V6, mais par petits groupes.

    V6 envoyait jusqu'à 16 entrées dans un seul filter_complex, ce qui pouvait
    faire tomber Streamlit avec 15 mots. V7 a réduit la RAM avec du stream-copy,
    mais cette approche pouvait casser les PTS et faire disparaître ou désynchroniser
    le compte à rebours et ses effets sonores. V8 garde donc le réencodage précis de
    V6, en limitant simplement chaque opération à 4 clips maximum.
    """
    clips=[p for p in clips if p and os.path.exists(p)]
    if not clips:
        raise ValueError("Aucun segment à concaténer.")
    if len(clips)==1:
        import shutil
        if os.path.abspath(clips[0]) != os.path.abspath(output):
            shutil.copyfile(clips[0], output)
        return output

    # Petits groupes : 4 entrées max par passe. Cela réduit fortement le pic mémoire
    # sans changer le moteur de concaténation qui garantit les PTS et l'audio.
    current=list(clips)
    level=0
    while len(current)>1:
        nxt=[]
        for gi in range(0,len(current),4):
            group=current[gi:gi+4]
            if len(group)==1:
                nxt.append(group[0])
                continue
            is_final=(len(current)<=4 and gi==0)
            group_out=output if is_final else os.path.join(tmpdir,f"__v2_chunk_{level:02d}_{gi//4:02d}.mp4")
            _concat_videos_style2_chunk(group,group_out,tmpdir)
            nxt.append(group_out)
        # Supprimer seulement les intermédiaires devenus inutiles.
        old=set(current)
        keep=set(nxt)
        for p in old:
            if p in clips or p in keep:
                continue
            try: os.remove(p)
            except OSError: pass
        current=nxt
        level+=1

    final=current[0]
    if os.path.abspath(final)!=os.path.abspath(output):
        import shutil
        shutil.copyfile(final,output)
        try: os.remove(final)
        except OSError: pass

    vd=video_duration(output)
    ad=audio_duration(output)
    if vd>0 and abs(vd-ad)>0.06:
        _repair_final_av_sync(output,tmpdir)
    return output

def save_frames(frames,tmpdir,prefix):
    out=[]
    for i,(img,dur) in enumerate(frames):
        p=os.path.join(tmpdir,f"{prefix}_{i:04d}.png"); img.save(p,compress_level=1); out.append((p,dur))
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
    text = (text or "").strip().replace("```json", "").replace("```", "").strip()
    # Gemini peut parfois ajouter une courte phrase avant/après le JSON.
    # On récupère le premier tableau JSON complet.
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end <= start:
        raise ValueError("Gemini n'a pas renvoyé un JSON valide.")
    return json.loads(text[start:end + 1])

def _gemini_wait_seconds(error_text, default=5.0):
    """Extrait 'retry in XXs' du message Gemini quand il est présent."""
    text = str(error_text or "")
    patterns = [
        r"retry in\s*([0-9]+(?:\.[0-9]+)?)s",
        r"retry_delay.*?([0-9]+(?:\.[0-9]+)?)s",
        r"([0-9]+(?:\.[0-9]+)?)\s*seconds",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            try:
                return max(1.0, min(60.0, float(m.group(1)) + 0.5))
            except Exception:
                pass
    return max(1.0, min(60.0, float(default)))

def _is_gemini_quota_error(error_text):
    text = str(error_text or "").upper()
    return any(token in text for token in [
        "429", "RESOURCE_EXHAUSTED", "QUOTA EXCEEDED", "RATE LIMIT", "TOO MANY REQUESTS"
    ])

def gemini_generate_text(prompt):
    """Un seul appel Gemini par clic, sans retry automatique.

    Les erreurs 429 sont volontairement remontées immédiatement : refaire
    plusieurs appels automatiquement consomme le quota et peut aggraver
    le problème. Un cooldown global de 13 s aide aussi à rester sous une
    limite de 5 requêtes/minute.
    """
    now = time.time()
    cooldown = 13.0
    last_attempt = float(st.session_state.get("_gemini_last_attempt", 0) or 0)
    remaining = cooldown - (now - last_attempt)
    if remaining > 0:
        raise RuntimeError(
            f"Patiente encore environ {int(math.ceil(remaining))} s avant une nouvelle génération. "
            "Une seule requête Gemini est envoyée par clic."
        )

    # Marqué AVANT l'appel : même si Gemini renvoie 429, un double-clic
    # ou plusieurs reruns ne déclencheront pas immédiatement d'autres appels.
    st.session_state._gemini_last_attempt = now

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = getattr(response, "text", None)
        if not text:
            raise ValueError("Gemini a renvoyé une réponse vide.")
        return text, False
    except Exception as e:
        if _is_gemini_quota_error(e):
            raw=str(e)
            lower=raw.lower()
            # Une limite quotidienne ne se résout pas avec un simple cooldown.
            if any(token in lower for token in ["per day", "per_day", "daily", "requestsperday", "generate_requests_per_day"]):
                msg=(
                    "⏳ Limite quotidienne Gemini atteinte. Il ne faut pas relancer plusieurs fois : "
                    "attends le prochain renouvellement du quota, puis fais un seul clic. "
                    "Cette version ne fait aucun retry automatique."
                )
            else:
                wait=_gemini_wait_seconds(e, default=13.0)
                msg=(
                    f"⏳ Limite Gemini de fréquence atteinte. Attends environ {int(math.ceil(wait))} s avant un seul nouveau clic. "
                    "Cette version ne fait aucun retry automatique."
                )
            raise RuntimeError(msg + f" Détail : {e}") from e
        raise

def parse_quiz_csv(uploaded_file):
    """Lit un CSV manuel avec colonnes question,A,B,C,D,reponse_correcte,explication."""
    raw = uploaded_file.getvalue().decode("utf-8-sig", errors="replace")
    try: dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
    except csv.Error: dialect = csv.excel
    reader = csv.DictReader(io.StringIO(raw), dialect=dialect)
    if not reader.fieldnames: raise ValueError("Le CSV ne contient pas de ligne d'en-tête.")
    fields = {f.strip().lower(): f for f in reader.fieldnames if f}
    required = ["question", "a", "b", "c", "d", "reponse_correcte"]
    missing = [f for f in required if f not in fields]
    if missing: raise ValueError("Colonnes manquantes : " + ", ".join(missing) + ".")
    data=[]
    for row in reader:
        q=clean_text(row.get(fields["question"],"")); opts=[clean_text(row.get(fields[k],"")) for k in ["a","b","c","d"]]
        ans=clean_text(row.get(fields["reponse_correcte"],"A")).upper()[:1]
        exp=clean_text(row.get(fields["explication"],"")) if "explication" in fields else ""
        if q and all(opts) and ans in "ABCD": data.append({"question":q,"options":opts,"reponse_correcte":ans,"explication":exp})
    if not data: raise ValueError("Aucune question valide trouvée dans le CSV.")
    return data[:10]

def csv_template():
    return "question,A,B,C,D,reponse_correcte,explication\nQuelle est la capitale de la France ?,Paris,Londres,Rome,Berlin,A,Paris est la capitale de la France.\n"

def normalize_questions(data):
    """Normalise plusieurs formats Gemini sans jeter les questions valides.

    Gemini peut renvoyer les 4 réponses soit dans ``options`` (liste), soit
    sous forme de clés A/B/C/D. La bonne réponse peut également être renvoyée
    comme lettre, ``A - texte`` ou comme texte de la réponse.
    """
    out=[]
    if not isinstance(data, list):
        return out

    for q in data:
        if not isinstance(q, dict):
            continue

        question = clean_text(q.get("question", q.get("question_text", "")))

        # Format principal : options = [A, B, C, D]
        raw_opts = q.get("options")
        if isinstance(raw_opts, dict):
            opts = [raw_opts.get(k, "") for k in "ABCD"]
        elif isinstance(raw_opts, (list, tuple)):
            opts = list(raw_opts)
        else:
            # Format alternatif : A/B/C/D directement dans l'objet.
            opts = [q.get(k, q.get(k.lower(), "")) for k in "ABCD"]

        opts = [clean_text(x) for x in opts]
        if len(opts) != 4 or not question or not all(opts):
            continue

        raw_ans = q.get("reponse_correcte", q.get("correct_answer", q.get("answer", "A")))
        raw_ans_text = clean_text(raw_ans)
        upper_ans = raw_ans_text.upper()

        # Lettre seule ou forme ``A - ...`` / ``A) ...``.
        m = re.match(r"^\s*([ABCD])(?:\s*[-:.)]\s*.*)?$", upper_ans)
        if m:
            ans = m.group(1)
        else:
            # Si Gemini renvoie directement le texte de la bonne option,
            # on retrouve son index dans les 4 réponses.
            ans = "A"
            for i, opt in enumerate(opts):
                if upper_ans == opt.upper():
                    ans = "ABCD"[i]
                    break

        exp = clean_text(q.get("explication", q.get("explanation", "")))
        out.append({
            "question": question,
            "options": opts,
            "reponse_correcte": ans,
            "explication": exp,
        })

    return out

# ------------------- Cache / édition sans quota -------------------
def _stable_hash(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

def _quiz_generation_key(nb, subject, language="Français"):
    return _stable_hash({"type":"quiz","model":MODEL_NAME,"nb":int(nb),"subject":clean_text(subject).lower(),"language":language})

def _vocab_generation_key(nb, subject, language):
    return _stable_hash({"type": "vocab", "model": MODEL_NAME, "nb": int(nb), "subject": clean_text(subject).lower(), "language": language})

def _save_quiz_editor(rows):
    cleaned=[]
    for row in rows:
        q=clean_text(row.get("Question", ""))
        opts=[clean_text(row.get(k, "")) for k in ["A","B","C","D"]]
        ans=clean_text(row.get("Bonne", "A")).upper()[:1]
        exp=clean_text(row.get("Explication", ""))
        if q and all(opts) and ans in "ABCD":
            cleaned.append({"question":q,"options":opts,"reponse_correcte":ans,"explication":exp})
    return cleaned[:15]

def _save_vocab_editor(rows):
    cleaned=[]
    for row in rows:
        fr=clean_text(row.get("Français", ""))
        tr=clean_text(row.get("Traduction", ""))
        if fr and tr:
            cleaned.append({"fr":fr,"trad":tr})
    return cleaned[:15]

api_key=st.sidebar.text_input("Clé API Gemini",type="password")
if api_key: genai.configure(api_key=api_key)
voice_rate=st.sidebar.slider("⚡ Vitesse voix",-10,25,0,format="%+d%%")
tts_rate=f"{voice_rate:+d}%"
st.sidebar.caption(f"Vitesse sélectionnée : {1.0 + voice_rate/100:.2f}×")
MODEL_NAME="gemini-3.6-flash"

MOTIVATION_LINES=[
    "🔥 Encore une ! Ne lâche rien.",
    "⚡ Plus vite ! La prochaine est difficile.",
    "🧠 Concentre-toi… tu peux faire mieux !",
    "🎯 Ton score monte… continue !",
    "💬 Abonne-toi pour le prochain quiz !",
]

def _motivation_text_clean(text):
    """Retire les emojis du texte PIL : ils ne sont pas fiables avec les polices vidéo."""
    t=clean_text(text or "")
    t=re.sub(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002300-\U000023FF\U00002B00-\U00002BFF]", "", t)
    t=re.sub(r"\s{2,}", " ", t).strip()
    return t

def _motivation_icon(draw, theme, kind="start", cx=540, cy=455, size=78, phase=0.0):
    """Icône vectorielle fiable, sans dépendre d'une police emoji."""
    a=theme["accent"]
    pulse=1.0+0.06*math.sin(float(phase)*math.pi*2)
    r=int(size*pulse)
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(8,13,28),outline=a,width=4)
    kind=str(kind or "mid")
    if kind=="start":
        # éclair + petite étincelle = énergie immédiate
        draw_lightning_icon(draw,theme,cx,cy,size//2)
        draw.ellipse((cx+r+12,cy-r//2,cx+r+28,cy-r//2+16),fill=a)
        draw.ellipse((cx-r-28,cy-r//3,cx-r-12,cy-r//3+16),fill=a)
    elif kind=="end":
        # trophée stylisé
        cup=(cx-30,cy-34,cx+30,cy+16)
        draw.rounded_rectangle(cup,radius=8,fill=a)
        draw.arc((cx-52,cy-28,cx-12,cy+10),70,290,fill=a,width=7)
        draw.arc((cx+12,cy-28,cx+52,cy+10),250,110,fill=a,width=7)
        draw.rectangle((cx-6,cy+16,cx+6,cy+35),fill=a)
        draw.rounded_rectangle((cx-34,cy+35,cx+34,cy+45),radius=5,fill=a)
    else:
        # sourire + étoiles pour le message du milieu
        er=7
        draw.ellipse((cx-28-er,cy-18-er,cx-28+er,cy-18+er),fill="white")
        draw.ellipse((cx+28-er,cy-18-er,cx+28+er,cy-18+er),fill="white")
        draw.arc((cx-35,cy-5,cx+35,cy+48),10,170,fill=a,width=6)
        for sx,sy in ((cx-r-18,cy-25),(cx+r+18,cy+5)):
            draw.line((sx-10,sy,sx+10,sy),fill=a,width=4)
            draw.line((sx,sy-10,sx,sy+10),fill=a,width=4)

def draw_motivation_scene(text,theme_name,channel,bg_file=None,progress=1.0,phase=0.0,kind="mid",language="Français"):
    """Écran motivation professionnel : intro forte, pause milieu ou fin."""
    theme=THEMES[theme_name]
    img=add_top_glow(make_base(theme_name,bg_file),theme,1.25+0.08*math.sin(float(phase)*math.pi*2))
    draw=ImageDraw.Draw(img)
    p=ease_out(progress)
    kind=str(kind or "mid")

    # Assombrissement central pour un rendu plus premium et lisible.
    panel=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0))
    pd=ImageDraw.Draw(panel)
    pd.rounded_rectangle((55,250,1025,1510),radius=46,fill=(4,9,22,205),outline=(*theme["accent"],95),width=2)
    panel=panel.filter(ImageFilter.GaussianBlur(0.2))
    img=Image.alpha_composite(img.convert("RGBA"),panel).convert("RGB")
    draw=ImageDraw.Draw(img)

    # Marque toujours visible dès la première seconde.
    brand=clean_text(channel or "SuspenseLingo")
    bf=get_font(30)
    bw=text_width(draw,brand,bf)
    draw.text(((WIDTH-bw)/2,292),brand,font=bf,fill=theme["accent"])
    draw.line((330,340,750,340),fill=(255,255,255,55),width=2)

    icon_kind="start" if kind=="start" else "end" if kind=="end" else "mid"
    _motivation_icon(draw,theme,icon_kind,540,485,78,phase)

    lang_defaults=QUIZ_MOTIVATION_DEFAULTS.get(str(language),QUIZ_MOTIVATION_DEFAULTS["Français"])
    labels={"start":lang_defaults["start_label"],"mid":lang_defaults["mid_label"],"end":lang_defaults["end_label"]}
    label=labels.get(kind,lang_defaults["mid_label"])
    lf=get_font(34)
    lw=text_width(draw,label,lf)
    draw.text(((WIDTH-lw)/2,610),label,font=lf,fill=theme["accent"])

    visible=_motivation_text_clean(text)
    f=get_font(68)
    lines=wrap_text(visible,f,850)[:3] or ["Keep going!"]
    y=760-int(45*(1-p))
    for i,line in enumerate(lines):
        tw=text_width(draw,line,f)
        x=(WIDTH-tw)/2+int(12*math.sin((phase+i*.15)*math.pi*2))
        draw.text((x+4,y+6),line,font=f,fill=(0,0,0))
        draw.text((x,y),line,font=f,fill="white")
        y+=92

    if kind=="start":
        sub=lang_defaults["start_sub"]
    elif kind=="end":
        sub=lang_defaults["end_sub"]
    else:
        sub=lang_defaults["start_sub"]
    sf=get_font(29)
    sw=text_width(draw,sub,sf)
    draw.text(((WIDTH-sw)/2,1110),sub,font=sf,fill=(220,228,242))

    # Barre de progression discrète : 0→100 selon l'étape de la scène.
    draw.rounded_rectangle((180,1270,900,1284),radius=7,fill=(55,62,78))
    draw.rounded_rectangle((180,1270,180+int(720*p),1284),radius=7,fill=theme["accent"])
    draw_brand(draw,theme,brand,None)
    sf2=get_font(21)
    sig="SuspenseLingo  •  Quiz"
    sw2=text_width(draw,sig,sf2)
    draw.text(((WIDTH-sw2)/2,1450),sig,font=sf2,fill=theme["muted"])
    return img


# ============================================================
# FONDS THÉMATIQUES AUTOMATIQUES — 0 QUOTA GEMINI
# ============================================================
def _theme_keywords(topic):
    t=clean_text(topic).lower()
    groups={
        "espace":["espace","astronomie","planète","planetes","galaxie","univers","nasa","étoile","etoile"],
        "histoire":["histoire","antiquité","antiquite","moyen âge","moyen age","guerre","empire","roi","reine","pétra","petra","jordanie","monument","civilisation","temple"],
        "geographie":["géographie","geographie","pays","capitale","monde","continent","ville","voyage","aéroport","aeroport","avion","passager","frontière","frontiere","territoire","outre-mer","île","ile","archipel"],
        "science":["science","physique","chimie","biologie","atome","scientifique","corps humain","anatomie"],
        "animaux":["animal","animaux","faune","océan","ocean","insecte","mammifère","mammifere"],
        "sport":["sport","football","soccer","tennis","basket","olympique","olympiques"],
        "art":["art","peinture","musique","cinéma","cinema","littérature","litterature"],
        "food":["cuisine","gastronomie","aliment","aliments","nourriture","recette"],
    }
    for key,words in groups.items():
        if any(w in t for w in words): return key
    return "general"

def generate_theme_background(theme_name,topic):
    """Fond local réellement illustratif selon le sujet. Aucun appel Gemini."""
    key=("auto_bg_v6_bright",theme_name,clean_text(topic).lower())
    if key in _BASE_CACHE: return _BASE_CACHE[key].copy()
    theme=THEMES[theme_name]; kind=_theme_keywords(topic)
    seed=int(hashlib.md5((theme_name+"|"+clean_text(topic)).encode()).hexdigest()[:8],16); rng=random.Random(seed)
    img=Image.new("RGB",(WIDTH,HEIGHT),theme["bg"]); px=img.load(); c1,c2=theme["bg"],theme["bg2"]
    for y in range(HEIGHT):
        t=y/(HEIGHT-1); t2=0.5-0.5*math.cos(math.pi*t)
        row=tuple(int(c1[k]*(1-t2)+c2[k]*t2) for k in range(3))
        for x in range(WIDTH): px[x,y]=row
    art=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0)); d=ImageDraw.Draw(art); accent=theme["accent"]; sec=theme["muted"]
    # profondeur lumineuse
    for (cx,cy,rx,ry,a) in [(160,250,360,300,28),(900,1180,500,520,20),(540,1750,650,260,18)]:
        d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(*accent,a))
    # motif discret commun
    for band in range(7):
        pts=[]; basey=300+band*210
        for x in range(-80,1160,35): pts.append((x,basey+50*math.sin(x/115+band)))
        d.line(pts,fill=(*accent,18),width=10)

    if kind=="geographie":
        # globe reconnaissable + route aérienne
        cx,cy,r=540,1390,285
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(8,20,42,90),outline=(*accent,115),width=7)
        d.ellipse((cx-r+35,cy-r,cx+r-35,cy+r),outline=(*sec,70),width=4)
        d.ellipse((cx-r,cy-r+70,cx+r,cy+r-70),outline=(*sec,65),width=4)
        for off in (-100,0,100): d.arc((cx-r,cy-r+off,cx+r,cy+r+off),205,335,fill=(*accent,45),width=3)
        # continents stylisés
        d.polygon([(380,1250),(450,1205),(515,1240),(495,1305),(430,1325),(395,1290)],fill=(*accent,55))
        d.polygon([(620,1280),(700,1250),(755,1315),(720,1380),(650,1370),(615,1320)],fill=(*sec,45))
        d.polygon([(500,1450),(565,1460),(600,1570),(555,1640),(505,1560)],fill=(*accent,45))
        # trajectoire + avion stylisé
        route=[(180,1530),(330,1390),(470,1430),(640,1280),(835,1190)]
        d.line(route,fill=(*accent,150),width=6)
        for x,y in route: d.ellipse((x-7,y-7,x+7,y+7),fill=(*accent,190))
        ax,ay=820,1195
        d.polygon([(ax,ay),(ax+70,ay-20),(ax+42,ay+3),(ax+78,ay+25),(ax+20,ay+12),(ax-15,ay+45),(ax-2,ay+8)],fill=(*accent,210))
        # petites cartes/repères en haut
        for x,y in [(130,500),(930,420),(180,760),(900,780)]:
            d.rounded_rectangle((x,y,x+90,y+58),radius=12,outline=(*sec,45),width=3)
            d.ellipse((x+35,y+17,x+55,y+37),fill=(*accent,100))
    elif kind=="espace":
        for _ in range(7):
            x=rng.randint(100,980); y=rng.randint(400,1550); r=rng.randint(120,300)
            d.ellipse((x-r,y-r,x+r,y+r),outline=(*accent,48),width=5)
        for _ in range(140):
            x=rng.randint(0,WIDTH); y=rng.randint(120,1800); rr=rng.randint(1,4); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(255,255,255,rng.randint(80,190)))
        cx,cy=540,1300
        d.ellipse((cx-150,cy-150,cx+150,cy+150),fill=(60,100,170,55),outline=(*accent,100),width=6)
        d.arc((cx-230,cy-80,cx+230,cy+80),0,360,fill=(*sec,75),width=5)
    elif kind=="histoire":
        for x in (150,370,590,810):
            d.rectangle((x,820,x+80,1430),fill=(*accent,20),outline=(*accent,60),width=4)
            d.polygon([(x-18,820),(x+40,750),(x+98,820)],fill=(*accent,28),outline=(*accent,60))
        d.rectangle((100,1430,980,1490),fill=(*accent,35))
        d.ellipse((260,440,820,1000),outline=(*sec,40),width=6)
    elif kind=="science":
        cx,cy=540,1370
        for r in (120,230,340): d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*accent,55),width=4)
        for ang in (0,60,120):
            rad=math.radians(ang); d.line((cx+math.cos(rad)*340,cy+math.sin(rad)*340,cx-math.cos(rad)*340,cy-math.sin(rad)*340),fill=(*sec,45),width=4)
        d.ellipse((cx-42,cy-42,cx+42,cy+42),fill=(*accent,130))
    elif kind=="animaux":
        # silhouettes de collines + empreintes stylisées
        for j in range(6):
            pts=[(x,900+j*120+int(35*math.sin(x/100+j))) for x in range(-30,1120,30)]; d.line(pts,fill=(*accent,45),width=9)
        for x,y in [(300,1400),(540,1280),(780,1450)]:
            d.ellipse((x-22,y-38,x+22,y+18),fill=(*sec,55)); d.ellipse((x-65,y-65,x-30,y-25),fill=(*sec,50)); d.ellipse((x+30,y-65,x+65,y-25),fill=(*sec,50))
    elif kind=="sport":
        d.ellipse((540-300,1300-300,540+300,1300+300),outline=(*accent,55),width=8)
        d.line((150,1300,930,1300),fill=(*sec,55),width=6); d.line((540,1000,540,1600),fill=(*sec,45),width=4)
        d.ellipse((495,1255,585,1345),outline=(*accent,100),width=5)
    elif kind=="art":
        for _ in range(10):
            x=rng.randint(100,760); y=rng.randint(900,1500); w=rng.randint(120,280); h=rng.randint(80,180)
            d.rounded_rectangle((x,y,x+w,y+h),radius=30,fill=(*accent,16),outline=(*accent,50),width=4)
    elif kind=="food":
        for x,y,r in [(250,1350,95),(540,1240,120),(800,1400,80),(400,1540,70),(720,1560,100)]:
            d.ellipse((x-r,y-r,x+r,y+r),fill=(*accent,20),outline=(*accent,60),width=4)
            d.ellipse((x-r//3,y-r//3,x+r//3,y+r//3),outline=(*sec,45),width=3)
    else:
        # culture générale : globe + cartes de connaissance
        cx,cy,r=540,1360,275
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*accent,80),width=6)
        d.ellipse((cx-r+35,cy-r,cx+r-35,cy+r),outline=(*sec,45),width=3)
        d.arc((cx-r,cy-120,cx+r,cy+120),0,360,fill=(*sec,45),width=3)
        for x,y in [(120,1050),(840,980),(120,1510),(850,1530)]:
            d.rounded_rectangle((x,y,x+110,y+75),radius=14,fill=(*accent,18),outline=(*accent,45),width=3)
    result=Image.alpha_composite(img.convert("RGBA"),art.filter(ImageFilter.GaussianBlur(0.25))).convert("RGB")
    _BASE_CACHE[key]=result.copy(); return result


def selected_video_background(theme_name,topic,mode,uploaded=None):
    if mode=="Image personnalisée" and uploaded is not None: return fit_background(uploaded)
    if mode=="Généré automatiquement":
        # Une variation change réellement le fond local sans toucher au quota Gemini.
        seed=st.session_state.get("q_variation_seed") or st.session_state.get("v_variation_seed") or 0
        variant_topic=f"{topic} • variation {seed}" if seed else topic
        return generate_theme_background(theme_name,variant_topic)
    return None


# ============================================================
# APERÇU INTERACTIF — V12
# ============================================================
def _qvp_prefix(module, style):
    if module == "vocab":
        return "v2_" if str(style) == "2" else "v1_"
    return "q2_" if str(style) == "2" else "q1_"


def _qvp_selected_element(module, style):
    allowed = {
        ("quiz", "1"): {"title","question","answers","timer","score","explanation"},
        ("quiz", "2"): {"title","question","timer","history"},
        ("vocab", "1"): {"title","word","translation","timer"},
        ("vocab", "2"): {"title","table","timer"},
    }.get((module, str(style)), {"question"})
    try:
        value = str(st.query_params.get("qvp_element", ""))
    except Exception:
        value = ""
    return value if value in allowed else ("question" if module == "quiz" else "word")


def _qvp_set_selected(element):
    try:
        st.query_params["qvp_element"] = element
    except Exception:
        pass


def _qvp_clear_selected():
    try:
        st.query_params.clear()
    except Exception:
        pass


def _qvp_adjust(module, style, element, dx=0, dy=0, dsize=0):
    """Déplace directement l'élément sélectionné. Les valeurs modifiées sont celles du rendu réel."""
    p = _qvp_prefix(module, style)
    ss = st.session_state
    def add(key, delta, lo=None, hi=None):
        val = float(ss.get(p+key, 0)) + float(delta)
        if lo is not None: val = max(lo, val)
        if hi is not None: val = min(hi, val)
        if isinstance(ss.get(p+key, 0), int): val = int(round(val))
        ss[p+key] = val
    if element == "title":
        add("title_x", dx, 0, 1080); add("title_y", dy, 20, 320); add("title_size", dsize, 20, 90)
    elif element == "score":
        add("score_x", dx, 0, 1080); add("score_y", dy, 40, 300); add("score_size", dsize, 20, 72)
    elif element in ("question","word"):
        add("question_x", dx, 0, 1080); add("question_y", dy, 60, 1050); add("question_size", dsize, 20, 110)
    elif element == "answers":
        add("answer_x", dx, 20, 220); add("answer_y", dy, 280, 1100); add("answer_size", dsize, 18, 66)
    elif element == "timer":
        if module=="vocab" and str(style)=="2":
            add("vocab_timer_offset_x", dx, -220, 220); add("vocab_timer_offset_y", dy, -80, 80); add("vocab_timer_size", dsize, 22, 70)
        else:
            add("timer_x", dx, 0, 1080); add("timer_y", dy, 200, 1500); add("timer_size", dsize, 24, 150)
    elif element == "explanation":
        add("explanation_x", dx, 0, 1080); add("explanation_y", dy, 700, 1600); add("explanation_size", dsize, 22, 60)
    elif element == "history":
        add("history_x", dx, 0, 250); add("history_y", dy, 350, 1350); add("history_size", dsize, 18, 54)
    elif element == "translation":
        add("translation_x", dx, 150, 930); add("translation_y", dy, 500, 1300); add("answer_size", dsize, 18, 66)
    elif element == "table":
        add("table_x", dx, 10, 180); add("table_y", dy, 250, 750); add("vocab_fr_size", dsize, 22, 64); add("vocab_tr_size", dsize, 20, 60)
    _save_settings()


def _qvp_element_boxes(module, style, cfg):
    """Zones cliquables approximatives en coordonnées vidéo 1080x1920."""
    boxes=[]
    def add(name,label,x,y,w,h): boxes.append((name,label,float(x),float(y),float(w),float(h)))
    add("title","Titre",cfg.get("title_x",540),cfg.get("title_y",70),900,105)
    if module=="quiz" and str(style)=="1":
        add("score","Compteur",cfg.get("score_x",540),cfg.get("score_y",150),180,70)
        add("question","Question",cfg.get("question_x",540),cfg.get("question_y",250),cfg.get("question_width",900),210)
        add("answers","Réponses",cfg.get("answer_x",80)+cfg.get("answer_width",920)/2,cfg.get("answer_y",650)+180,cfg.get("answer_width",920),4*(cfg.get("answer_h",78)+cfg.get("answer_gap",12)))
        auto_timer_y = (int(cfg.get("answer_y",630))+4*int(cfg.get("answer_h",82))+3*int(cfg.get("answer_gap",12))+max(24,int(cfg.get("timer_size",58)))+22) if cfg.get("timer_auto_below_answers",True) else int(cfg.get("timer_y",1015))
        add("timer","Minuteur",cfg.get("timer_x",540),auto_timer_y,220,220)
        add("explanation","Explication",540,cfg.get("explanation_y",1135)+cfg.get("explanation_h",380)/2,964,cfg.get("explanation_h",380))
    elif module=="quiz" and str(style)=="2":
        add("question","Question active",cfg.get("question_x",540),cfg.get("question_y",150),cfg.get("question_width",920),230)
        add("timer","Minuteur",cfg.get("timer_x",540),cfg.get("timer_y",430),220,180)
        add("history","Historique",cfg.get("history_x",80)+cfg.get("history_width",920)/2,cfg.get("history_y",690)+280,cfg.get("history_width",920),600)
    elif module=="vocab" and str(style)=="1":
        add("word","Mot / phrase",cfg.get("question_x",540),cfg.get("question_y",500),850,150)
        add("timer","Minuteur",cfg.get("timer_x",810),cfg.get("timer_y",760),200,170)
        add("translation","Traduction",cfg.get("translation_x",540),cfg.get("translation_y",760),cfg.get("translation_width",850),190)
    elif module=="vocab" and str(style)=="2":
        add("table","Tableau cumulatif",cfg.get("table_x",70)+cfg.get("table_width",940)/2,cfg.get("table_y",430)+430,cfg.get("table_width",940),850)
        add("timer","Minuteur",cfg.get("table_x",70)+cfg.get("table_split",540)+(cfg.get("table_width",940)-cfg.get("table_split",540))/2+cfg.get("vocab_timer_offset_x",0),cfg.get("table_y",430)+cfg.get("table_row_h",82)/2+cfg.get("vocab_timer_offset_y",0),200,150)
    return boxes


def _qvp_image_data_uri(image):
    buf=io.BytesIO()
    image.save(buf,format="JPEG",quality=84,optimize=True)
    return "data:image/jpeg;base64,"+base64.b64encode(buf.getvalue()).decode("ascii")


def render_clickable_preview(image, module, style, cfg, selected):
    """Aperçu 9:16 compact. La sélection et les commandes sont gérées par Streamlit sous l'aperçu."""
    max_w=360
    max_h=int(max_w*16/9)
    thumb=image.copy().resize((max_w,max_h),Image.Resampling.LANCZOS)
    # L'ancienne couche de hotspots HTML est volontairement supprimée : elle était lourde
    # et ses liens query-string ne déclenchaient pas toujours correctement Streamlit.
    st.markdown('<div class="quiz-preview qvp-preview-stage" data-theme="bleu-nuit-or">', unsafe_allow_html=True)
    st.image(thumb, use_container_width=False, width=max_w)
    st.markdown('</div>', unsafe_allow_html=True)




# V31.25 — Style 2 Quiz : structure cumulative exacte Q1 → Q2+R1 → Q3+R1/R2.
# V31.18 — correction définitive Streamlit : le moteur de rendu ne modifie plus les clés des widgets.
# V31.16 — zones sûres strictes : cadres complets + header/logo/compteur contenus.
# Marges recommandées/indicatives : elles servent à garder les éléments
# importants loin des zones d'interface susceptibles de recouvrir la vidéo.
SOCIAL_SAFE_PROFILES = {
    "TikTok": {"top":0.10,"bottom":0.19,"left":0.03,"right":0.19},
    "Instagram Reels": {"top":0.09,"bottom":0.18,"left":0.03,"right":0.16},
    "YouTube Shorts": {"top":0.08,"bottom":0.14,"left":0.03,"right":0.12},
    "Facebook Reels": {"top":0.09,"bottom":0.17,"left":0.03,"right":0.15},
}
SOCIAL_SAFE_PROFILES["Universel"] = {
    k:max(v[k] for v in SOCIAL_SAFE_PROFILES.values()) for k in ("top","bottom","left","right")
}

def apply_social_auto_layout(module="quiz", style="1"):
    """Mise en page sociale réelle. Style 1 Quiz reste son preset validé.
    Les autres styles conservent leur identité visuelle et sont seulement
    compactés/repositionnés lorsque leurs BORDS dépassent la zone sûre.
    """
    p = ("q1_" if module == "quiz" and str(style) == "1" else
         "q2_" if module == "quiz" else
         "v1_" if str(style) == "1" else "v2_")
    if not st.session_state.get(p+"social_auto_layout", False):
        return
    platform = st.session_state.get(p+"social_platform", "Universel")
    prof = SOCIAL_SAFE_PROFILES.get(platform, SOCIAL_SAFE_PROFILES["Universel"])
    safe_top = int(HEIGHT*prof["top"]); safe_bottom = int(HEIGHT*(1-prof["bottom"]))
    safe_left = int(WIDTH*prof["left"]); safe_right = int(WIDTH*(1-prof["right"]))
    safe_w = safe_right-safe_left; center = (safe_left+safe_right)//2

    # ================================================================
    # QUIZ STYLE 1 — NE PAS MODIFIER LE PRESET VALIDÉ.
    # ================================================================
    if module == "quiz" and str(style) == "1":
        # Gabarit PRO 9:16 : question plus présente, cartes de réponses plus
        # grandes et moins d'espace perdu sous le quiz, tout en restant dans
        # la zone sûre de la plateforme sélectionnée.
        header_h=72; header_y=safe_top; header_bottom=header_y+header_h
        question_y=header_bottom+38; question_reserved_h=205; question_bottom=question_y+question_reserved_h
        answer_h=88; answer_gap=14; answer_y=question_bottom+20
        answers_bottom=answer_y+4*answer_h+3*answer_gap
        timer_size=60; timer_y=answers_bottom+42; explanation_h=220
        explanation_y=timer_y+timer_size+24; progress_y=safe_bottom-18
        available=progress_y-explanation_h-18
        if explanation_y>available:
            explanation_y=available; timer_y=explanation_y-timer_size-34
        if timer_y < answers_bottom+40:
            timer_y=answers_bottom+40; explanation_y=timer_y+timer_size+24
        if explanation_y+explanation_h > progress_y-12:
            explanation_y=progress_y-12-explanation_h
        vals={
            p+"header_y":header_y,p+"header_h":header_h,p+"brand_x":safe_left+16,p+"brand_y":header_y+20,p+"brand_size":28,
            p+"title_x":center,p+"title_y":header_y+18,p+"title_size":32,p+"score_x":safe_right-50,p+"score_y":header_y+10,p+"score_size":29,
            p+"question_x":center,p+"question_y":question_y,p+"question_width":safe_w,
            p+"answer_x":safe_left,p+"answer_width":safe_w,p+"answer_y":answer_y,p+"answer_h":answer_h,p+"answer_gap":answer_gap,
            p+"timer_x":center,p+"timer_y":timer_y,p+"timer_size":timer_size,p+"timer_auto_below_answers":False,
            p+"explanation_x":center,p+"explanation_y":explanation_y,p+"explanation_width":safe_w,p+"explanation_h":explanation_h,
            p+"explanation_auto_below_timer":False,p+"explanation_auto_height":False,p+"social_progress_y":progress_y,
        }
        for k,v in vals.items(): st.session_state[k]=v
        st.session_state[p+"social_safe_left"]=safe_left; st.session_state[p+"social_safe_right"]=safe_right
        st.session_state[p+"social_safe_top"]=safe_top; st.session_state[p+"social_safe_bottom"]=safe_bottom
        return

    # ================================================================
    # QUIZ STYLE 2 — question fixe + historique cumulatif.
    # Aucun nouvel écran ni changement de mécanique.
    # ================================================================
    if module == "quiz" and str(style) == "2":
        p="q2_"
        header_h=64; header_y=safe_top; header_bottom=header_y+header_h
        qy=max(header_bottom+28, min(int(st.session_state.get(p+"question_y",315)), header_bottom+500))
        qw=min(int(st.session_state.get(p+"question_width",920)), safe_w); qx=center
        # Réponses cumulatives : on réserve l'espace avant le minuteur.
        hist_y=max(qy+250, int(st.session_state.get(p+"history_y",690)))
        hist_gap=min(int(st.session_state.get(p+"history_gap",10)),10)
        max_rows=15
        available=max(180,safe_bottom-105-hist_y)
        hist_row_h=max(42,min(int(st.session_state.get(p+"history_row_h",68)), int((available-hist_gap*(max_rows-1))/max_rows)))
        visible_rows=max(1,min(max_rows,int((available+hist_gap)/(hist_row_h+hist_gap))))
        hist_bottom=hist_y+visible_rows*hist_row_h+(visible_rows-1)*hist_gap
        timer_size=min(int(st.session_state.get(p+"timer_size",52)),58)
        timer_y=min(safe_bottom-timer_size-22, hist_bottom+24)
        if timer_y+timer_size>safe_bottom:
            timer_y=max(hist_bottom+12,safe_bottom-timer_size)
        # Un même gabarit d'en-tête pour tous les styles.
        st.session_state[p+"header_y"]=header_y; st.session_state[p+"header_h"]=header_h
        st.session_state[p+"brand_x"]=safe_left+16; st.session_state[p+"brand_y"]=header_y+17; st.session_state[p+"brand_size"]=24
        st.session_state[p+"title_x"]=center; st.session_state[p+"title_y"]=header_y+16; st.session_state[p+"title_size"]=30
        st.session_state[p+"score_x"]=safe_right-50; st.session_state[p+"score_y"]=header_y+9; st.session_state[p+"score_size"]=27
        st.session_state[p+"question_x"]=qx; st.session_state[p+"question_y"]=qy; st.session_state[p+"question_width"]=qw
        st.session_state[p+"history_x"]=safe_left; st.session_state[p+"history_width"]=safe_w; st.session_state[p+"history_y"]=hist_y
        st.session_state[p+"history_row_h"]=hist_row_h; st.session_state[p+"history_gap"]=hist_gap
        st.session_state[p+"timer_x"]=center; st.session_state[p+"timer_y"]=timer_y; st.session_state[p+"timer_size"]=timer_size
        st.session_state[p+"social_safe_left"]=safe_left; st.session_state[p+"social_safe_right"]=safe_right; st.session_state[p+"social_safe_top"]=safe_top; st.session_state[p+"social_safe_bottom"]=safe_bottom
        return

    # ================================================================
    # VOCABULAIRE STYLE 1 — mise en page dédiée, sobre et sûre.
    # ================================================================
    if module == "vocab" and str(style) == "1":
        p="v1_"
        header_h=64; header_y=safe_top; header_bottom=header_y+header_h
        st.session_state[p+"header_y"]=header_y; st.session_state[p+"header_h"]=header_h
        st.session_state[p+"brand_x"]=safe_left+16; st.session_state[p+"brand_y"]=header_y+17; st.session_state[p+"brand_size"]=24
        st.session_state[p+"title_x"]=center; st.session_state[p+"title_y"]=header_y+16; st.session_state[p+"title_size"]=30
        st.session_state[p+"score_x"]=safe_right-50; st.session_state[p+"score_y"]=header_y+9; st.session_state[p+"score_size"]=27
        qy=max(header_bottom+150, min(int(st.session_state.get(p+"question_y",500)), safe_top+620))
        qw=min(int(st.session_state.get(p+"question_width",920)),safe_w)
        ty=max(qy+170, min(int(st.session_state.get(p+"translation_y",760)), safe_bottom-360))
        tw=min(int(st.session_state.get(p+"translation_width",850)),safe_w)
        timer_size=min(int(st.session_state.get(p+"timer_size",62)),70)
        timer_y=max(ty+120, min(int(st.session_state.get(p+"timer_y",760)), safe_bottom-160))
        st.session_state[p+"question_x"]=center; st.session_state[p+"question_y"]=qy; st.session_state[p+"question_width"]=qw
        st.session_state[p+"translation_x"]=center; st.session_state[p+"translation_y"]=ty; st.session_state[p+"translation_width"]=tw
        st.session_state[p+"timer_x"]=center; st.session_state[p+"timer_y"]=timer_y; st.session_state[p+"timer_size"]=timer_size
        st.session_state[p+"social_safe_left"]=safe_left; st.session_state[p+"social_safe_right"]=safe_right; st.session_state[p+"social_safe_top"]=safe_top; st.session_state[p+"social_safe_bottom"]=safe_bottom
        return

    # ================================================================
    # VOCABULAIRE STYLE 2 — ON CONSERVE LE VISUEL CUMULATIF APPROUVÉ.
    # On adapte uniquement la largeur/position/hauteur pour la zone sûre.
    # ================================================================
    if module == "vocab" and str(style) == "2":
        p="v2_"
        header_h=64; header_y=safe_top; header_bottom=header_y+header_h
        st.session_state[p+"header_y"]=header_y; st.session_state[p+"header_h"]=header_h
        st.session_state[p+"brand_x"]=safe_left+16; st.session_state[p+"brand_y"]=header_y+17; st.session_state[p+"brand_size"]=24
        st.session_state[p+"title_x"]=center; st.session_state[p+"title_y"]=header_y+16; st.session_state[p+"title_size"]=30
        st.session_state[p+"score_x"]=safe_right-50; st.session_state[p+"score_y"]=header_y+9; st.session_state[p+"score_size"]=27
        tw=min(int(st.session_state.get(p+"table_width",940)),safe_w)
        tx=max(safe_left,min(center-tw//2,safe_right-tw))
        gap=min(int(st.session_state.get(p+"table_gap",6)),8)
        total=max(1,len(st.session_state.get("v_data") or st.session_state.get("vocab_data") or [])); total=min(total,15)
        min_table_y=header_bottom+28
        ty=max(min_table_y,int(st.session_state.get(p+"table_y",350)))
        available=max(180,safe_bottom-24-ty-gap*max(0,total-1))
        row_h=max(42,min(int(st.session_state.get(p+"table_row_h",82)),int(available/max(1,total))))
        if ty+total*row_h+gap*max(0,total-1)>safe_bottom-24:
            ty=max(min_table_y,safe_bottom-24-total*row_h-gap*max(0,total-1))
        split=max(300,min(int(st.session_state.get(p+"table_split",540)),tw-260))
        st.session_state[p+"table_x"]=tx; st.session_state[p+"table_width"]=tw; st.session_state[p+"table_y"]=ty
        st.session_state[p+"table_row_h"]=row_h; st.session_state[p+"table_gap"]=gap; st.session_state[p+"table_split"]=split
        st.session_state[p+"social_safe_left"]=safe_left; st.session_state[p+"social_safe_right"]=safe_right; st.session_state[p+"social_safe_top"]=safe_top; st.session_state[p+"social_safe_bottom"]=safe_bottom
        return


def render_platform_safe_preview(image, key_prefix="platform_preview", module="quiz", style="1"):
    """Aperçu vertical 9:16 à l'échelle de travail, avec zones de sécurité par plateforme."""
    profiles={
        "TikTok":{"top":0.10,"bottom":0.19,"left":0.03,"right":0.19,"label":"TikTok"},
        "Instagram Reels":{"top":0.09,"bottom":0.18,"left":0.03,"right":0.16,"label":"Instagram Reels"},
        "YouTube Shorts":{"top":0.08,"bottom":0.14,"left":0.03,"right":0.12,"label":"YouTube Shorts"},
        "Facebook Reels":{"top":0.09,"bottom":0.17,"left":0.03,"right":0.15,"label":"Facebook Reels"},
        "Universel":{"top":0.10,"bottom":0.19,"left":0.03,"right":0.19,"label":"Universel"},
    }
    c1,c2=st.columns([1.35,0.9],gap="small")
    with c1:
        platform=st.selectbox("📱 Plateforme à prévisualiser",list(profiles),key=f"{key_prefix}_platform")
    with c2:
        show=st.checkbox("Afficher les zones",value=True,key=f"{key_prefix}_show")
    profile=profiles[platform]
    prefix=("q2_" if module=="quiz" and str(style)=="2" else "q1_" if module=="quiz" else "v2_" if str(style)=="2" else "v1_")
    auto_on=bool(st.session_state.get(prefix+"social_auto_layout",False))
    if auto_on:
        st.success(f"🛡️ Mise en page automatique active — contenu placé dans la zone sûre ({platform}).")
    else:
        st.warning("⚠️ Mise en page automatique désactivée : l'aperçu montre les zones interdites, mais ne déplace pas les éléments.")
    st.caption("Les zones rouges indiquent les zones d'interface à éviter. Avec la mise en page automatique, les cadres complets — en-tête, question, réponses, minuteur, explication et progression — restent à l'intérieur de la zone sûre.")
    canvas=image.convert("RGBA").resize((432,768),Image.Resampling.LANCZOS)
    if show:
        ov=Image.new("RGBA",canvas.size,(0,0,0,0)); d=ImageDraw.Draw(ov); W,H=canvas.size
        zones=[
            (0,0,W,int(H*profile["top"]),"ZONE À ÉVITER • HAUT"),
            (0,int(H*(1-profile["bottom"])),W,H,"ZONE À ÉVITER • BAS"),
            (0,int(H*profile["top"]),int(W*profile["left"]),int(H*(1-profile["bottom"])),""),
            (int(W*(1-profile["right"])),int(H*profile["top"]),W,int(H*(1-profile["bottom"])),"ZONE UI"),
        ]
        for x1,y1,x2,y2,label in zones:
            d.rectangle((x1,y1,x2,y2),fill=(220,45,65,72),outline=(255,110,125,180),width=2)
            if label:
                try:
                    tw=max(150, min(250, int(d.textlength(label))+18))
                    d.rounded_rectangle((x1+8,y1+8,x1+tw,y1+31),radius=7,fill=(25,25,30,205))
                    d.text((x1+14,y1+13),label,fill=(255,255,255,235))
                except Exception:
                    pass
        d.rectangle((int(W*profile["left"]),int(H*profile["top"]),int(W*(1-profile["right"])),int(H*(1-profile["bottom"]))),outline=(255,255,255,115),width=2)
        canvas=Image.alpha_composite(canvas,ov).convert("RGB")
    st.image(canvas,width=432)
    st.caption(f"🛡️ Zone de contenu recommandée pour {profile['label']} : garde la question et les réponses dans le cadre central.")

def _qvp_quick_controls(module, style, selected, theme_name, channel, bg, state, title, language="Anglais", prefix_key="qvp"):
    """Barre compacte d'édition rapide sous l'aperçu. Ne remplace pas l'Éditeur Studio."""
    allowed = list(_qvp_element_boxes(module, style, _layout(module, style)))
    labels = {name: label for name, label, *_ in allowed}
    names = [name for name, *_ in allowed]
    if not names:
        return selected
    current = selected if selected in names else names[0]
    current = st.selectbox(
        "Élément à modifier",
        names,
        index=names.index(current),
        format_func=lambda x: labels.get(x, x),
        key=f"{prefix_key}_element_select_{module}_{style}"
    )
    _qvp_set_selected(current)

    c1,c2,c3,c4,c5,c6=st.columns([.75,.75,.9,.75,.75,1.25],gap="small")
    with c1:
        if st.button("←",key=f"{prefix_key}_l_{module}_{style}",use_container_width=True):
            _qvp_adjust(module,style,current,dx=-20); st.rerun()
    with c2:
        if st.button("↑",key=f"{prefix_key}_u_{module}_{style}",use_container_width=True):
            _qvp_adjust(module,style,current,dy=-20); st.rerun()
    with c3:
        if st.button("● Centrer",key=f"{prefix_key}_c_{module}_{style}",use_container_width=True):
            p=_qvp_prefix(module,style)
            center={"title":"title_x","question":"question_x","word":"question_x","answers":"answer_x","timer":"timer_x","translation":"translation_x","history":"history_x","table":"table_x"}.get(current)
            if center:
                st.session_state[p+center] = 540 if current not in ("answers","history","table") else (80 if current in ("answers","history") else 70)
            if current=="explanation": st.session_state[p+"explanation_y"]=1135
            if current=="timer" and module=="vocab": st.session_state[p+"timer_x"]=810
            _save_settings(); st.rerun()
    with c4:
        if st.button("↓",key=f"{prefix_key}_d_{module}_{style}",use_container_width=True):
            _qvp_adjust(module,style,current,dy=20); st.rerun()
    with c5:
        if st.button("→",key=f"{prefix_key}_r_{module}_{style}",use_container_width=True):
            _qvp_adjust(module,style,current,dx=20); st.rerun()
    with c6:
        z1,z2=st.columns(2,gap="small")
        with z1:
            if st.button("A −",key=f"{prefix_key}_sm_{module}_{style}",use_container_width=True):
                _qvp_adjust(module,style,current,dsize=-2); st.rerun()
        with z2:
            if st.button("A +",key=f"{prefix_key}_sp_{module}_{style}",use_container_width=True):
                _qvp_adjust(module,style,current,dsize=2); st.rerun()

    a1,a2,a3=st.columns([1,1,1],gap="small")
    with a1:
        if st.button("▶️ Animation",key=f"{prefix_key}_anim_{module}_{style}",use_container_width=True):
            play_preview_animation(module,style,theme_name,channel,bg,state,title,language)
    with a2:
        if st.button("✕ Désélectionner",key=f"{prefix_key}_clear_{module}_{style}",use_container_width=True):
            _qvp_clear_selected(); st.rerun()
    with a3:
        st.caption(f"🎯 {labels.get(current,current)}")
    return current

def _qvp_animation_frames(module, style, theme_name, channel, bg, state, title, language="Anglais"):
    """Petite animation de démonstration, volontairement courte pour rester fluide."""
    frames=[]
    if module=="quiz":
        demo=[{"question":"Quelle est la capitale de la France ?","options":["Paris","Londres","Rome","Berlin"],"reponse_correcte":"A"},{"question":"Quelle est la capitale de l'Espagne ?","options":["Paris","Madrid","Rome","Lisbonne"],"reponse_correcte":"B"},{"question":"Quelle est la capitale de l'Italie ?","options":["Milan","Paris","Rome","Madrid"],"reponse_correcte":"C"}]
        if str(style)=="2":
            for i in range(12):
                t=i/11
                frames.append(draw_style2_frame(demo,1 if state=="Q2 + R1" else 0,theme_name,channel,bg,timer=max(1,3-int(t*3)),timer_fraction=1-t,answer_reveal=(state=="Q2 + R1" and t>.72),motion=t,video_title=title))
        else:
            for i in range(12):
                t=i/11
                frames.append(draw_quiz_frame("Quelle est la capitale de la France ?",["Paris","Londres","Rome","Berlin"],theme_name,1,15,channel,bg,entrance=t,timer=3 if t<.9 else None,timer_fraction=max(.0,1-t),pulse=.45+.45*math.sin(t*math.pi*4),motion=t,video_title=title))
            frames.extend([draw_quiz_frame("Quelle est la capitale de la France ?",["Paris","Londres","Rome","Berlin"],theme_name,1,15,channel,bg,entrance=1.0,correct_idx=0,reveal_progress=t,motion=1+t,video_title=title,explanation="Paris est la capitale de la France.",explanation_progress=t) for t in (.15,.35,.55,.75,1.0)])
    else:
        demo=[{"fr":"Bonjour","trad":"Hello"},{"fr":"Merci","trad":"Thank you"},{"fr":"Voyage","trad":"Travel"}]
        if str(style)=="2":
            for i in range(12):
                t=i/11
                frames.append(draw_vocab_cumulative_frame(demo,2 if "Ligne 3" in state else 1 if "Ligne 2" in state else 0,theme_name,channel,bg,timer=3 if t<.78 else None,timer_fraction=1-t,reveal=(t>.72 and "réflexion" not in state),motion=t,video_title=title))
        else:
            for i in range(12):
                t=i/11
                phase="countdown" if t<.78 else "translation"
                frames.append(draw_vocab_frame(demo,0,language,theme_name,channel,bg,phase,3,max(0,1-t),1.0 if t>.15 else t))
    return frames


def play_preview_animation(module, style, theme_name, channel, bg, state, title, language="Anglais"):
    placeholder=st.empty()
    frames=_qvp_animation_frames(module,style,theme_name,channel,bg,state,title,language)
    total=len(frames)
    for i,frame in enumerate(frames):
        placeholder.image(frame.resize((300,533),Image.Resampling.LANCZOS),width=300)
        time.sleep(0.08)
    placeholder.empty()

# ============================================================
# INTERFACE — DESIGN PREMIUM / STUDIO V12 INTERACTIF
# ============================================================
st.sidebar.markdown("""
<div class="qvp-side-brand">
  <div class="qvp-logo">▶</div>
  <div>
    <div class="qvp-side-title">SuspenseLingo</div>
    <div class="qvp-side-sub">Studio de création de quiz vidéo</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.caption("🧠 SuspenseLingo Studio V32  •  🗣️ Vocabulaire Pro")
st.sidebar.markdown("""
<div class="qvp-side-note"><b>✨ Mode économique actif</b><br>
Gemini est utilisé uniquement lorsque vous demandez du nouveau contenu IA.</div>
""", unsafe_allow_html=True)


def _ss_default(key, value):
    """Initialise sans écraser une valeur sauvegardée quand un module revient à l’écran."""
    if key in st.session_state:
        return
    snap=st.session_state.get("_qvp_saved_settings", {})
    if isinstance(snap,dict) and key in snap:
        st.session_state[key]=snap[key]
        return
    st.session_state[key]=value

def export_platform_video(video_data, platform, quality, tmpdir):
    """Crée une copie prête pour la plateforme sans modifier le rendu master."""
    src=os.path.join(tmpdir, f"export_master_{platform}.mp4")
    with open(src,"wb") as f: f.write(video_data)
    if quality == "1080p":
        width,height,crf=1080,1920,"20"
    else:
        width,height,crf=720,1280,"22"
    out=os.path.join(tmpdir, f"{platform}_{quality}.mp4")
    vf=f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
    cmd=[get_ffmpeg(),"-y","-i",src,"-vf",vf,"-c:v","libx264","-preset","medium","-crf",crf,"-c:a","aac","-b:a","192k","-movflags","+faststart",out]
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    with open(out,"rb") as f: return f.read()

def render_export_panel(video_data, base_name, key_prefix):
    """Export robuste : préparation une seule fois, puis boutons persistants.
    Les téléchargements ne relancent pas la préparation ni le rendu vidéo.
    """
    st.markdown("### 📥 EXPORTER LA VIDÉO")
    st.caption("Votre rendu master reste inchangé. Sélectionnez une ou plusieurs plateformes, puis préparez les fichiers.")
    platform_options=["Toutes les plateformes","TikTok","YouTube Shorts","Instagram Reels","Facebook Reels"]
    selected=st.multiselect("Plateformes",platform_options,default=["Toutes les plateformes"],key=f"{key_prefix}_platforms")
    if "Toutes les plateformes" in selected:
        platforms=["TikTok","YouTube Shorts","Instagram Reels","Facebook Reels"]
    else:
        platforms=selected
    quality=st.radio("Qualité",["720p","1080p"],index=1,horizontal=True,key=f"{key_prefix}_quality")

    export_state_key=f"{key_prefix}_prepared_exports"
    signature=(base_name,quality,tuple(platforms),hash(video_data)) if platforms else None
    if st.button("📦 Préparer les téléchargements",key=f"{key_prefix}_prepare",type="primary",disabled=not platforms):
        with st.spinner("Préparation des fichiers…"):
            prepared={}
            # Une seule conversion par qualité : les 4 plateformes partagent le même master 9:16.
            safe0=platforms[0].replace(" ","").replace("Shorts","Short").replace("Reels","Reel")
            with tempfile.TemporaryDirectory(prefix="sl_export_") as export_tmp:
                exported=export_platform_video(video_data,safe0,quality,export_tmp)
            for platform in platforms:
                safe=platform.replace(" ","").replace("Shorts","Short").replace("Reels","Reel")
                prepared[platform]={
                    "data":exported,
                    "filename":f"{base_name}_{safe}_{quality}.mp4"
                }
            st.session_state[export_state_key]={"signature":signature,"files":prepared}
        st.success(f"✅ Export prêt : {len(platforms)} fichier(s) disponible(s) ci-dessous.")

    prepared_state=st.session_state.get(export_state_key)
    if prepared_state and prepared_state.get("signature")==signature:
        st.markdown("#### ⬇️ Téléchargements prêts")
        files_to_download=prepared_state["files"]
        if len(platforms) > 1:
            zip_buf=io.BytesIO()
            with zipfile.ZipFile(zip_buf,mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
                for platform in platforms:
                    item=files_to_download.get(platform)
                    if item:
                        zf.writestr(item["filename"],item["data"])
            st.download_button("📦 Télécharger toutes les plateformes (ZIP)",data=zip_buf.getvalue(),file_name=f"{base_name}_Toutes_les_plateformes.zip",mime="application/zip",key=f"{key_prefix}_dl_all_zip",use_container_width=True)
        for platform in platforms:
            item=files_to_download.get(platform)
            if item:
                st.download_button(f"⬇️ {platform} — {quality}",data=item["data"],file_name=item["filename"],mime="video/mp4",key=f"{key_prefix}_dl_{platform.replace(' ','_')}_{quality}",use_container_width=True)

    # En 1080p, le master est déjà le fichier vertical final : téléchargement direct.
    elif platforms and quality=="1080p" and video_data:
        st.markdown("#### ⚡ Téléchargement direct")
        direct_files={}
        for platform in platforms:
            safe=platform.replace(" ","").replace("Shorts","Short").replace("Reels","Reel")
            direct_files[platform]={"data":video_data,"filename":f"{base_name}_{safe}_1080p.mp4"}
        if len(platforms)>1:
            zip_buf=io.BytesIO()
            with zipfile.ZipFile(zip_buf,mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
                for item in direct_files.values():
                    zf.writestr(item["filename"],item["data"])
            st.download_button("📦 Télécharger toutes les plateformes (ZIP)",data=zip_buf.getvalue(),file_name=f"{base_name}_Toutes_les_plateformes.zip",mime="application/zip",key=f"{key_prefix}_dl_all_direct",use_container_width=True)
        for platform,item in direct_files.items():
            st.download_button(f"⬇️ {platform} — 1080p",data=item["data"],file_name=item["filename"],mime="video/mp4",key=f"{key_prefix}_dl_direct_{platform.replace(' ','_')}",use_container_width=True)

def render_layout_editor(module, style="1"):
    """Éditeur Studio V14 : indépendant pour chacun des 4 styles."""
    is_quiz = module == "quiz"
    style = str(style)
    p = ("q2_" if is_quiz and style=="2" else "q1_" if is_quiz else "v2_" if style=="2" else "v1_")
    defaults = {
        "font_family":"Lato", "show_title":True, "title_x":540, "title_y":139, "title_size":38,
        "question_x":540, "question_y":250 if is_quiz else 500, "question_size":58 if is_quiz else 62, "question_width":920,
        "answer_y":550 if is_quiz else 760, "answer_x":70, "answer_width":940, "answer_h":82, "answer_gap":14, "answer_size":33 if is_quiz else 42, "answer_radius":22,
        "history_x":80, "history_y":690, "history_width":920, "history_row_h":74, "history_gap":10, "history_size":29,
        "show_explanation":True, "explanation_x":540, "explanation_y":1160, "explanation_width":964, "explanation_h":320, "explanation_size":31,
        "question_frame_enabled":True, "question_frame_bg_enabled":True, "question_border_enabled":True,
        "answer_cards_enabled":True, "answer_badges_enabled":True, "answer_frame_bg_enabled":True, "answer_border_enabled":True,
        "explanation_frame_enabled":True, "explanation_frame_bg_enabled":True, "explanation_border_enabled":True,
        "score_x":965, "score_y":130, "score_size":32, "score_radius":22, "score_color":"#FFCD40", "score_bg":"#070D1C",
        "intro_page_variant":"Premium lumineux", "outro_page_variant":"Premium lumineux",
        "brand_x":70, "brand_y":139, "brand_size":31, "brand_show":True, "brand_bg_enabled":True, "brand_bg":"#20385E", "brand_color":"#F59E0B",
        "animation":"Glissement", "animation_speed":1.0, "animation_strength":1.0, "motion_strength":1.0,
        "show_timer":True, "timer_y":1075 if is_quiz else 760, "timer_x":540 if is_quiz else 810, "timer_size":72 if is_quiz else 68, "timer_text_size":68 if is_quiz else 64, "timer_style":"Anneau progressif",
        "timer_auto_below_answers":True, "explanation_auto_below_timer":False, "explanation_auto_height":False,
        "timer_show_label":False, "timer_label":"RÉFLÉCHIS", "timer_label_size":23, "timer_color":"#FFD166", "timer_label_color":"#FFD166",
        "primary":"#FFD166", "answer":"#23466F", "answer2":"#2E5B8D", "correct":"#2EDA7B", "text":"#FFFFFF", "muted":"#E5F1FF",
        "border_color":"#D2DFF5", "border_width":2, "border_radius":20,
        "bg_opacity":0, "bg_zoom":1.02, "bg_x":0, "bg_y":0, "bg_mode":"✨ Automatique",
        "translation_x":540, "translation_y":760, "translation_width":850,
        "table_x":70, "table_y":350, "table_width":940, "table_row_h":82, "table_gap":6, "table_split":540, "table_radius":18,
        "vocab_fr_size":42, "vocab_tr_size":38, "vocab_header_size":29, "vocab_timer_offset_x":0, "vocab_timer_offset_y":0, "vocab_timer_size":44,
        "table_header_font":"DejaVu Serif", "table_header_h":58, "sfx_enabled":True, "sfx_volume":0.30,
    }
    for k,v in defaults.items(): _ss_default(p+k,v)

    # Migration : l’ancien défaut Style 1 (150 px) est remplacé par 270 px.
    if is_quiz and style == "1" and st.session_state.get(p+"question_y") == 150:
        st.session_state[p+"question_y"] = 270
    if is_quiz and style == "1":
        _ss_default(p+"bg_music_enabled", True)
        _ss_default(p+"bg_music_volume", 0.15)
        _ss_default(p+"bg_music_style", "Suspense léger")
        _ss_default(p+"bg_music_source", "Musique générée par SuspenseLingo")

    # V31.25 — calcul avant création des widgets.
    # Style 1 Quiz reste strictement sur son preset validé V31.18/V31.19.
    # Les trois autres styles utilisent une protection additive qui conserve
    # leur géométrie et ne corrige que les débordements.
    if p+"social_auto_layout" not in st.session_state:
        st.session_state[p+"social_auto_layout"] = True
    if p+"social_platform" not in st.session_state:
        st.session_state[p+"social_platform"] = "Universel"
    # V31.25 : activation initiale des 4 protections. Une seule fois pour
    # ne pas réactiver le mode automatique après que l'utilisateur l'a désactivé.
    if not st.session_state.get("_social_auto_layout_v31_24_migrated", False):
        for _mod,_style in (("quiz","1"),("quiz","2"),("vocab","1"),("vocab","2")):
            _pp=("q1_" if _mod=="quiz" and _style=="1" else "q2_" if _mod=="quiz" else "v1_" if _style=="1" else "v2_")
            # Ne jamais écraser un réglage déjà chargé depuis qvp_settings.json.
            if _pp+"social_auto_layout" not in st.session_state:
                st.session_state[_pp+"social_auto_layout"] = True
        st.session_state["_social_auto_layout_v31_24_migrated"] = True
    # V32 MISE EN PAGE PRO — l'automatique ne doit plus écraser les réglages
    # manuels à chaque rerun Streamlit. Il s'applique au premier chargement
    # et uniquement lorsqu'on change de plateforme ou réactive l'automatique.
    _auto_on = bool(st.session_state.get(p+"social_auto_layout", False))
    _auto_sig = f"{module}|{style}|{st.session_state.get(p+"social_platform", "Universel")}"
    if _auto_on:
        # V32 : la mise en page automatique ne doit plus réinitialiser les
        # réglages enregistrés à chaque nouvelle visite. La signature est
        # elle-même persistée dans qvp_settings.json. Elle ne change que
        # lorsque la plateforme cible change.
        if st.session_state.get(p+"_social_auto_applied_sig") != _auto_sig:
            apply_social_auto_layout(module, style)
            st.session_state[p+"_social_auto_applied_sig"] = _auto_sig
    else:
        st.session_state.pop(p+"_social_auto_applied_sig", None)

    st.markdown('<div class="qvp-editor-title">🎨 ÉDITEUR STUDIO • PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="qvp-editor-subtitle">Chaque élément possède ses propres positions, tailles, couleurs et cadres. X = horizontal • Y = vertical • les réglages sont indépendants par style.</div>', unsafe_allow_html=True)
    st.info("🧭 **Comment lire X/Y :** X déplace de gauche à droite (0 → 1080). Y déplace de haut en bas (0 → 1920). Les coordonnées concernent la vidéo 1080×1920, pas la taille du téléphone affiché.")
    tabs = st.tabs(["🧩 Structure","🖼️ État","📐 Position","📏 Taille","🎨 Couleurs","🎞️ Animation","⏱️ Minuteur","🔤 Police","🌄 Fond","🎵 Musique"])

    with tabs[1]:
        st.markdown("### 🖼️ Première page et dernière page")
        st.caption("Choisis le style de l'écran d'ouverture et de l'écran final. Les choix sont conservés avec les autres réglages et n'altèrent ni les questions, ni la voix, ni la synchronisation.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**▶️ PREMIÈRE PAGE**")
            st.selectbox("Style de la première page", ["Premium lumineux", "Néon élégant", "Minimal premium"], key=p+"intro_page_variant")
            intro_txt = "Prêt ? C'est parti !" if is_quiz else "Apprends ces nouveaux mots !"
            st.caption("Aperçu")
            intro_preview = draw_page_template(intro_txt, list(THEMES.keys())[0], "SuspenseLingo", None, 1.0, "intro", st.session_state.get(p+"intro_page_variant", "Premium lumineux"), module, style)
            st.image(intro_preview.resize((216,384), Image.Resampling.LANCZOS), width=216)
        with c2:
            st.markdown("**🏁 DERNIÈRE PAGE**")
            st.selectbox("Style de la dernière page", ["Premium lumineux", "Néon élégant", "Minimal premium"], key=p+"outro_page_variant")
            outro_txt = "Merci d'avoir joué !" if is_quiz else "Abonne-toi pour un nouveau mot !"
            st.caption("Aperçu")
            outro_preview = draw_page_template(outro_txt, list(THEMES.keys())[0], "SuspenseLingo", None, 1.0, "outro", st.session_state.get(p+"outro_page_variant", "Premium lumineux"), module, style)
            st.image(outro_preview.resize((216,384), Image.Resampling.LANCZOS), width=216)
        st.info("💡 Les aperçus utilisent le fond et le thème actifs au moment du rendu vidéo. Les trois propositions sont disponibles pour chaque style.")

    with tabs[0]:
        if is_quiz:
            if style=="1":
                st.info("**Style 1 Pro** : question + 4 réponses → minuteur compact sous les réponses → révélation verte + carte d'explication adaptative. Le fond décoratif est volontairement plus discret pour garder le quiz au premier plan.")
            else:
                st.info("**Style 1** : question + 4 réponses → réflexion → révélation verte + explication.\n\n**Style 2** : titre fixe + une seule question active → réflexion → réponse ajoutée à l'historique → question suivante au même emplacement.")
        else:
            st.info("**Style 1** : mot/phrase → réflexion → traduction.\n\n**Style 2** : tableau cumulatif : français à gauche → minuteur dans la cellule traduction → traduction → nouvelle ligne sous la précédente, jusqu'à 15 lignes.")
        st.checkbox("Afficher le titre", key=p+"show_title")
        if is_quiz:
            st.checkbox("Afficher l'explication", key=p+"show_explanation")
        st.markdown("**🧱 Visibilité des éléments et cadres**")
        vc1,vc2=st.columns(2)
        with vc1:
            st.checkbox("Afficher le cadre de la question",key=p+"question_frame_enabled")
            st.checkbox("Afficher le fond du cadre question",key=p+"question_frame_bg_enabled")
            st.checkbox("Afficher la bordure question",key=p+"question_border_enabled")
            st.checkbox("Afficher les cartes des réponses",key=p+"answer_cards_enabled")
            st.checkbox("Afficher les badges A/B/C/D",key=p+"answer_badges_enabled")
        with vc2:
            st.checkbox("Afficher le fond des cartes réponses",key=p+"answer_frame_bg_enabled")
            st.checkbox("Afficher la bordure des cartes réponses",key=p+"answer_border_enabled")
            st.checkbox("Afficher le cadre de l'explication",key=p+"explanation_frame_enabled")
            st.checkbox("Afficher le fond de l'explication",key=p+"explanation_frame_bg_enabled")
            st.checkbox("Afficher la bordure de l'explication",key=p+"explanation_border_enabled")
        st.markdown("**🏷️ Logo / nom de chaîne**")
        st.checkbox("Afficher SuspenseLingo en haut à gauche",key=p+"brand_show")
        st.checkbox("Fond derrière le logo",key=p+"brand_bg_enabled")
        c_brand1,c_brand2=st.columns(2)
        with c_brand1:
            st.slider("Logo X — gauche ↔ droite",0,1080,key=p+"brand_x")
            st.slider("Logo Y — haut ↕ bas",80,500,key=p+"brand_y")
        with c_brand2:
            st.slider("Taille du logo / nom",16,60,key=p+"brand_size")
            st.color_picker("Couleur du logo",key=p+"brand_color")
        c_auto1,c_auto2=st.columns(2)
        with c_auto1: st.checkbox("Position automatique sous le minuteur",key=p+"explanation_auto_below_timer")
        with c_auto2: st.checkbox("Hauteur automatique de l’explication",key=p+"explanation_auto_height")

    with tabs[2]:
        st.markdown("### 📱 Mise en page automatique — Réseaux sociaux")
        if is_quiz and style=="1":
            st.caption("🎯 Style 1 Pro : le mode automatique positionne la composition dans la zone sûre au premier chargement. Ensuite, tu peux déplacer librement la question, les réponses, le minuteur et l'explication depuis Position/Taille.")
        elif is_quiz and style=="2":
            st.caption("🎯 Style 2 : Q1 → Q2 + R1 → Q3 + R1/R2. L'automatique protège la question active et l'historique sans transformer la mise en page.")
        elif (not is_quiz) and style=="2":
            st.caption("🧩 Style 2 Vocabulaire : tableau cumulatif conservé. L'automatique ne fait que borner le tableau s'il dépasse la zone sûre.")
        else:
            st.caption("🗣️ Style 1 Vocabulaire : la mise en page existante est conservée ; seuls les débordements hors zone sûre sont corrigés.")
        ac1,ac2=st.columns(2)
        with ac1:
            st.checkbox("Activer la mise en page automatique",key=p+"social_auto_layout")
        with ac2:
            st.selectbox("Plateforme cible",["Universel","TikTok","Instagram Reels","YouTube Shorts","Facebook Reels"],key=p+"social_platform")
        if st.session_state.get(p+"social_auto_layout",False):
            st.success(f"✓ Protection active : {st.session_state.get(p+"social_platform","Universel")}")
        else:
            st.info("🔓 Mode manuel : la mise en page actuelle est conservée.")
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Position de l’élément principal**")
            st.slider("↔ X — gauche 0 • centre 540 • droite 1080",0,1080,key=p+"question_x")
            st.slider("↕ Y — haut 0 • bas 1920",60,1500,key=p+"question_y")
            if is_quiz and style=="2":
                st.markdown("**Historique — Style 2**")
                st.slider("Historique — X",0,220,key=p+"history_x")
                st.slider("Historique — Y",450,1300,key=p+"history_y")
            if not is_quiz and style=="2":
                st.markdown("**📋 Mise en page — Style 2**")
                st.caption("Réglages essentiels, regroupés ici pour garder la page courte.")
                st.slider("Tableau — X",20,160,key=p+"table_x",step=5)
                st.slider("Tableau — Y",280,700,key=p+"table_y",step=5)
                st.slider("Largeur du tableau",700,1000,key=p+"table_width",step=10)
                st.slider("Séparation français / traduction",400,650,key=p+"table_split",step=10)
                st.slider("Hauteur d’une ligne",60,115,key=p+"table_row_h",step=5)
                st.slider("Espace entre lignes",0,24,key=p+"table_gap",step=2)
        with c2:
            st.markdown("**🧭 En-tête — position dans la zone sûre**")
            if is_quiz and style=="1":
                st.slider("↕ En-tête Y — haut 0 • bas 1920",80,500,key=p+"header_y")
                st.slider("Hauteur de l’en-tête",60,110,key=p+"header_h")
            st.markdown("**Titre**")
            st.slider("↔ Titre X — gauche 0 • centre 540 • droite 1080",0,1080,key=p+"title_x")
            st.slider("↕ Titre Y — haut 0 • bas 1920",20,320,key=p+"title_y")
            if is_quiz and style=="1":
                st.markdown("**Réponses — Style 1**")
                st.slider("↔ Réponses X — bord gauche du bloc",20,180,key=p+"answer_x")
                st.slider("↕ Réponses Y — haut du bloc",300,1050,key=p+"answer_y")
            if is_quiz and style=="1":
                st.markdown("**💡 Explication — position libre**")
                st.slider("↔ X — gauche 0 • centre 540 • droite 1080",0,1080,key=p+"explanation_x")
            st.caption("📐 Repère vidéo : X = horizontal (0→1080) • Y = vertical (0→1920). Ces valeurs sont des coordonnées vidéo, pas des pixels d’écran.")
            st.slider("↕ Explication Y — haut 0 • bas 1920",120,1750,key=p+"explanation_y")
            if not is_quiz and style=="2":
                st.markdown("**⏱️ Minuteur — Style 2**")
                st.slider("Décalage X", -180, 180, key=p+"vocab_timer_offset_x", step=5)
                st.slider("Décalage Y", -50, 50, key=p+"vocab_timer_offset_y", step=5)
                st.slider("Taille du minuteur",24,70,key=p+"vocab_timer_size")

    with tabs[3]:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Élément actif**")
            st.slider("Taille du texte",22,110,key=p+"question_size")
            st.slider("Largeur",500,1020,key=p+"question_width")
            if is_quiz and style=="1":
                st.slider("Arrondi du cadre question",0,48,key=p+"question_box_radius")
            if is_quiz and style=="1":
                st.markdown("**Réponses**")
                st.slider("Largeur des cartes",700,1000,key=p+"answer_width")
                st.slider("Hauteur des cartes",55,140,key=p+"answer_h")
        with c2:
            st.markdown("**Titre**")
            st.slider("Taille du titre",22,86,key=p+"title_size")
            if is_quiz and style=="1":
                st.slider("Taille du texte des réponses",20,62,key=p+"answer_size")
                st.slider("Espacement des réponses",4,32,key=p+"answer_gap")
                st.slider("Arrondi des réponses",0,48,key=p+"answer_radius")
                st.slider("Taille indépendante du badge A/B/C/D",36,72,key=p+"answer_badge_size")
                st.checkbox("Hauteur automatique des cartes",key=p+"answer_auto_height")
                st.slider("Marge du texte dans les cartes",12,40,key=p+"answer_text_padding")
                st.slider("Taille du compteur",20,72,key=p+"score_size")
                st.markdown("**Compteur 1/15 — position indépendante**")
                st.slider("↔ Compteur X — gauche 0 • centre 540 • droite 1080",0,1080,key=p+"score_x")
                st.slider("↕ Compteur Y — haut 0 • bas 1920",40,600,key=p+"score_y")
                st.markdown("**Explication**")
                st.slider("Taille du texte de l'explication",20,62,key=p+"explanation_size")
                st.slider("Largeur de l'explication",500,1020,key=p+"explanation_width",step=10)
                st.slider("Hauteur de l'explication",180,520,key=p+"explanation_h",step=10)
                st.caption("💡 X = gauche ↔ droite • Y = haut ↕ bas. Désactive l’automatique pour placer l’explication librement.")
            elif is_quiz and style=="2":
                st.slider("Largeur de l'historique",600,1000,key=p+"history_width")
                # V31.28 — migration sûre : une ancienne valeur < 55 faisait
                # planter Streamlit avec StreamlitValueBelowMinError.
                _history_row_key = p + "history_row_h"
                try:
                    _history_row_value = int(st.session_state.get(_history_row_key, 78))
                except (TypeError, ValueError):
                    _history_row_value = 78
                st.session_state[_history_row_key] = max(55, min(110, _history_row_value))
                st.slider("Hauteur d'une ligne",55,110,key=_history_row_key)
                st.slider("Taille du texte historique",20,52,key=p+"history_size")
            elif not is_quiz and style=="2":
                st.caption("Tableau cumulatif optimisé pour 1 à 15 lignes. À partir de 12 lignes, la hauteur et la taille du texte s'adaptent automatiquement.")
                st.slider("Discrétion des anciennes lignes",0.55,1.0,key=p+"vocab_history_dim",step=0.05)
                st.caption("La ligne active reste dominante ; les lignes déjà apprises restent visibles mais plus discrètes.")
            else:
                st.slider("X traduction — Style 1",200,880,key=p+"translation_x")
                st.slider("Y traduction — Style 1",650,1200,key=p+"translation_y")
                st.slider("Largeur traduction",400,1000,key=p+"translation_width")

    with tabs[4]:
        c1,c2 = st.columns(2)
        with c1:
            st.color_picker("Accent / titre",key=p+"primary")
            st.color_picker("Cartes principales",key=p+"answer")
            st.color_picker("Cartes secondaires",key=p+"answer2")
        with c2:
            st.color_picker("Bonne réponse / traduction",key=p+"correct")
            st.color_picker("Texte principal",key=p+"text")
            st.color_picker("Texte secondaire",key=p+"muted")
        st.markdown("**Visibilité des cadres**")
        st.caption("Les interrupteurs de visibilité, fonds et bordures se trouvent dans l’onglet 🧩 Structure pour éviter les doublons et piloter directement le rendu live.")
        st.markdown("**Bordures**")
        bc1,bc2,bc3=st.columns(3)
        with bc1: st.color_picker("Couleur",key=p+"border_color")
        with bc2: st.slider("Épaisseur",1,8,key=p+"border_width")
        with bc3: st.slider("Arrondi",0,48,key=p+"border_radius")

    with tabs[5]:
        st.selectbox("Animation principale",["Glissement","Glissement vertical","Fondu","Zoom doux","Rebond léger","Machine à écrire","Pop","Aucune"],key=p+"animation")
        c1,c2=st.columns(2)
        with c1: st.slider("Vitesse",0.5,2.0,key=p+"animation_speed")
        with c2: st.slider("Amplitude",0.0,2.0,key=p+"animation_strength")
        st.slider("Mouvement du fond",0.0,2.0,key=p+"motion_strength")
        st.caption("Les animations de la vidéo suivent la durée réelle de la voix.")

    with tabs[6]:
        # Quiz Style 1 : le compte à rebours est une fonctionnalité fondamentale.
        # IMPORTANT : sa valeur doit être fixée AVANT la création du widget Streamlit,
        # sinon Streamlit lève StreamlitWidgetAlreadyInstantiatedError.
        if is_quiz and style=="1":
            st.session_state[p+"show_timer"] = True
        st.checkbox("Afficher le compte à rebours",key=p+"show_timer",disabled=(is_quiz and style=="1"))
        if is_quiz and style=="1":
            st.checkbox("Position automatique sous les 4 réponses",key=p+"timer_auto_below_answers")
        c1,c2=st.columns(2)
        with c1:
            if (not is_quiz) and style=="2":
                st.info("Le minuteur du Style 2 est positionné dans la cellule de traduction. Utilise les réglages X/Y juste au-dessus pour l’ajuster.")
            else:
                st.slider("Position X",0,1080,key=p+"timer_x")
                # V31.30: normaliser toute ancienne valeur avant le slider pour éviter ValueAboveMax/BelowMin.
                timer_y_key=p+"timer_y"
                if timer_y_key not in st.session_state:
                    st.session_state[timer_y_key]=1110
                else:
                    try: st.session_state[timer_y_key]=max(250,min(1450,int(st.session_state[timer_y_key])))
                    except Exception: st.session_state[timer_y_key]=1110
                st.slider("Position Y",250,1450,key=timer_y_key)
                st.slider("Taille",28,140,key=p+"timer_size")
        with c2:
            st.selectbox("Style",["Double cercle","Montre","Gouttes d’eau","Sablier","Anneau progressif","Numérique"],key=p+"timer_style")
            st.slider("Taille du chiffre",20,112,key=p+"timer_text_size")
            st.checkbox("Afficher le libellé",key=p+"timer_show_label")
            st.text_input("Libellé",key=p+"timer_label")
            st.color_picker("Couleur du minuteur",key=p+"timer_color")
        st.markdown("**Effets sonores**")
        st.checkbox("Activer les effets sonores",key=p+"sfx_enabled")
        st.slider("Volume des effets",0.05,0.60,key=p+"sfx_volume",step=0.01)
        if (not is_quiz) and style=="2":
            st.caption("Style 2 : pop à l’apparition du mot • 3 tics pendant 3 → 2 → 1 • ding à la fin de la réflexion • pop discret au démarrage de la traduction.")
        else:
            st.caption("Tic du chrono • entrée de question/mot • pop de révélation • ding de fin.")

    with tabs[7]:
        st.selectbox("Police du style",FONT_CHOICES,key=p+"font_family")
        if (not is_quiz) and style=="2":
            st.selectbox("Police des en-têtes du tableau",FONT_CHOICES,key=p+"table_header_font")
            st.slider("Hauteur de l’en-tête",46,78,key=p+"table_header_h")
        st.caption("✅ Cette police est utilisée par l’aperçu et le rendu vidéo de CE style uniquement.")
        st.info("Choisis une police une seule fois pour ce style. Les réglages des autres styles restent indépendants.")

    with tabs[8]:
        st.radio("Source du fond",["✨ Automatique","🖼️ Personnalisé","◯ Aucun"],horizontal=True,key=p+"bg_mode")
        if st.session_state.get(p+"bg_mode")=="🖼️ Personnalisé":
            st.file_uploader("Image de fond",type=["png","jpg","jpeg"],key=p+"bg_upload")
        c1,c2=st.columns(2)
        with c1:
            st.slider("Assombrissement",0,80,key=p+"bg_opacity")
            st.slider("Zoom",1.00,1.25,key=p+"bg_zoom",step=.01)
        with c2:
            st.slider("Déplacement X",-120,120,key=p+"bg_x")
            st.slider("Déplacement Y",-120,120,key=p+"bg_y")
        st.caption("Le fond automatique est généré localement et ne consomme pas de quota Gemini.")

    if is_quiz and style == "1":
        with tabs[9]:
            st.markdown("**🎵 Musique de fond du Quiz Style 1**")
            st.checkbox("Activer la musique de fond", key=p+"bg_music_enabled")
            c1,c2=st.columns(2)
            with c1:
                st.selectbox("Ambiance", ["Suspense sombre","Mystère","Tension","Défi intense","Quiz futuriste","Cinématique","Suspense léger","Chill","Pop légère"], key=p+"bg_music_style")
            with c2:
                st.slider("Volume",0.00,0.30,key=p+"bg_music_volume",step=0.01,format="%.2f")
            st.caption("La musique évolue : discrète au départ, tension progressive pendant la réflexion, pression renforcée pendant 3 → 2 → 1, puis impact à la révélation. La voix reste prioritaire.")
            st.radio("Source", ["Musique générée par SuspenseLingo","Ma propre musique"], key=p+"bg_music_source", horizontal=True)
            if st.session_state.get(p+"bg_music_source")=="Ma propre musique":
                st.file_uploader("Importer une musique", type=["mp3","wav","m4a","aac","ogg"], key=p+"bg_music_upload")
            st.caption("La musique choisie est intégrée au fichier vidéo final et bouclée si nécessaire.")
    _save_settings()


nav=st.session_state.get("module_nav","quiz")
n1,n2=st.columns(2,gap="small")
with n1:
    if st.button("🧠  QUIZ TIKTOK PRO",key="nav_quiz",use_container_width=True):
        _save_settings(); st.session_state["module_nav"]="quiz"; st.rerun()
with n2:
    if st.button("🗣️  VOCABULAIRE PRO",key="nav_vocab",use_container_width=True):
        _save_settings(); st.session_state["module_nav"]="vocab"; st.rerun()

if nav=="quiz":
    st.markdown('<div class="qvp-studio-header"><b>🎬 SuspenseLingo Studio</b><span>🧠 QUIZ</span><small>Mise en page Pro • Éditeur interactif</small></div>',unsafe_allow_html=True)

    # Paramètres et contenu en pleine largeur.
    st.markdown('<div class="qvp-settings-card"><div class="qvp-card-heading">⚙️ 1. Paramètres généraux</div>',unsafe_allow_html=True)
    g1,g2=st.columns(2,gap="medium")
    with g1:
        subject_options=[
            "Culture générale","Animaux","Géographie","Histoire","Sciences","Technologie","Cinéma & séries","Sport","Musique","Logique & énigmes","Personnalisé"
        ]
        subject_choice=st.selectbox("Sujet",subject_options,index=0,key="thq_choice")
        if subject_choice=="Personnalisé":
            th_q=st.text_input("Votre sujet","Ex. Capitales du monde",key="thq_custom")
        else:
            th_q=subject_choice
        quiz_language=st.selectbox("🌍 Langue du Quiz",list(QUIZ_LANGUAGES.keys()),key="quiz_language")
        voice_profile=st.selectbox("🎙️ Profil vocal",list(VOICE_PROFILES),index=0,key="voice_profile_q")
        voice_options=list(QUIZ_LANGUAGES[quiz_language].keys())
        voice_q_name=st.selectbox("Voix",voice_options,index=min(VOICE_PROFILES[voice_profile]["prefer"],len(voice_options)-1),key=f"vq_{quiz_language}")
        voice_q=QUIZ_LANGUAGES[quiz_language][voice_q_name]
        quiz_tts_rate=VOICE_PROFILES[voice_profile]["rate"]
    with g2:
        theme_q=st.selectbox("Style visuel",list(THEMES),key="tq",help="Palettes lumineuses et distinctes : les changements s’appliquent à l’aperçu et au rendu vidéo.")
        st.caption("✨ Palettes actualisées : fonds plus lumineux, cartes contrastées et couleurs assorties.")
        style_q=st.radio("Structure",["Style 1 — 4 réponses + révélation","Style 2 — Cumulatif"],key="styleq_compact")
        nb_q=st.slider("Questions",1,15,3,key="nbq")
    g3,g4=st.columns(2,gap="medium")
    with g3:
        if st.session_state.get("cq") == "@QuizMaster_Pro":
            st.session_state["cq"] = "SuspenseLingo"
        channel_q=st.text_input("Chaîne","SuspenseLingo",key="cq")
        hook_presets={
            "Français":["Teste tes connaissances !","Prêt pour le défi ?","Tu penses connaître la réponse ?","Attention, celle-ci est piégeuse !","Seulement les plus forts trouveront !","À toi de jouer !"],
            "Anglais":["Test your knowledge!","Ready for the challenge?","Do you know the answer?","Careful, this one is tricky!","Only the sharpest will get it!","Your turn!"],
            "Espagnol":["¡Pon a prueba tus conocimientos!","¿Listo para el desafío?","¿Conoces la respuesta?","¡Cuidado, esta tiene trampa!","¡Solo los más rápidos acertarán!","¡Te toca!"],
            "Arabe":["اختبر معلوماتك!","هل أنت مستعد للتحدي؟","هل تعرف الإجابة؟","انتبه، هذا السؤال خادع!","فقط الأذكياء سيجيبون بشكل صحيح!","حان دورك!"],
            "Allemand":["Teste dein Wissen!","Bereit für die Herausforderung?","Kennst du die Antwort?","Vorsicht, diese Frage ist knifflig!","Nur die Besten schaffen es!","Du bist dran!"],
            "Italien":["Metti alla prova le tue conoscenze!","Pronto per la sfida?","Conosci la risposta?","Attenzione, questa è insidiosa!","Solo i più forti ci riusciranno!","Tocca a te!"]
        }
        hp=st.selectbox("Hook court",hook_presets.get(quiz_language,hook_presets["Français"])+["Personnalisé"],key="hq_choice")
        if hp=="Personnalisé":
            hook_q=st.text_input("Votre Hook","Teste tes connaissances !",key="hq_custom")
        else:
            hook_q=hp
    with g4:
        cta_presets={
            "Français":["Abonne-toi à SuspenseLingo pour le prochain quiz !","Abonne-toi et relève le prochain défi !","Donne ton score en commentaire !","À combien de bonnes réponses es-tu arrivé ?","Suis SuspenseLingo pour d'autres quiz !"],
            "Anglais":["Subscribe to SuspenseLingo for the next quiz!","Subscribe and take on the next challenge!","Share your score in the comments!","How many did you get right?","Follow SuspenseLingo for more quizzes!"],
            "Espagnol":["¡Suscríbete a SuspenseLingo para el próximo quiz!","¡Suscríbete y acepta el próximo desafío!","¡Comparte tu puntuación en los comentarios!","¿Cuántas respuestas acertaste?","¡Sigue a SuspenseLingo para más quizzes!"],
            "Arabe":["اشترك في SuspenseLingo للتحدي القادم!","اشترك وخض التحدي القادم!","اكتب نتيجتك في التعليقات!","كم إجابة صحيحة حصلت عليها؟","تابع SuspenseLingo للمزيد من الاختبارات!"],
            "Allemand":["Abonniere SuspenseLingo für das nächste Quiz!","Abonniere und stelle dich der nächsten Herausforderung!","Teile dein Ergebnis in den Kommentaren!","Wie viele Antworten hattest du richtig?","Folge SuspenseLingo für weitere Quizze!"],
            "Italien":["Iscriviti a SuspenseLingo per il prossimo quiz!","Iscriviti e affronta la prossima sfida!","Scrivi il tuo punteggio nei commenti!","Quante risposte hai indovinato?","Segui SuspenseLingo per altri quiz!"]
        }
        cp=st.selectbox("CTA final",cta_presets.get(quiz_language,cta_presets["Français"])+["Personnalisé"],key="oq_choice")
        if cp=="Personnalisé":
            outro_q=st.text_input("Votre CTA","Abonne-toi à SuspenseLingo pour le prochain quiz !",key="oq_custom")
        else:
            outro_q=cp
        engagement_presets={
            "Français":["Quel est ton score ? Écris-le en commentaire !","Combien de bonnes réponses as-tu eues ?","Sans tricher… quel est ton score ?","Quelle question t'a piégé ? 😈"],
            "Anglais":["What's your score? Write it in the comments!","How many did you get right?","No cheating… what's your score?","Which question tricked you? 😈"],
            "Espagnol":["¿Cuál es tu puntuación? ¡Escríbela en los comentarios!","¿Cuántas acertaste?","Sin hacer trampa… ¿cuál es tu puntuación?","¿Qué pregunta te engañó? 😈"],
            "Arabe":["ما نتيجتك؟ اكتبها في التعليقات!","كم إجابة صحيحة حصلت عليها؟","بدون غش… ما نتيجتك؟","أي سؤال خدعك؟ 😈"],
            "Allemand":["Wie ist dein Ergebnis? Schreib es in die Kommentare!","Wie viele hattest du richtig?","Ohne zu schummeln… wie ist dein Ergebnis?","Welche Frage hat dich erwischt? 😈"],
            "Italien":["Qual è il tuo punteggio? Scrivilo nei commenti!","Quante ne hai indovinate?","Senza barare… qual è il tuo punteggio?","Quale domanda ti ha ingannato? 😈"]
        }
        engagement_choice=st.selectbox("💬 Engagement / score",engagement_presets.get(quiz_language,engagement_presets["Français"])+["Personnalisé"],key="engagement_choice_q")
        if engagement_choice=="Personnalisé":
            engagement_q=st.text_input("Votre message d'engagement","Quel est ton score ? Écris-le en commentaire !",key="engagement_custom_q")
        else:
            engagement_q=engagement_choice
        st.caption(f"🎙️ {quiz_language} • {voice_q_name} • {voice_profile} — narration et messages dans cette langue.")
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="qvp-settings-card"><div class="qvp-card-heading">💬 2. Messages de motivation</div><div class="qvp-card-sub">Les messages existants restent éditables ici, sans carte intermédiaire supplémentaire.</div>',unsafe_allow_html=True)
    mot_defaults=QUIZ_MOTIVATION_DEFAULTS.get(quiz_language,QUIZ_MOTIVATION_DEFAULTS["Français"])
    mm1,mm2=st.columns(2,gap="medium")
    motivation_presets={
        "Français":{
            "start":["Prêt ? C'est parti !","À toi de jouer !","C'est parti pour le défi !","Concentre-toi… la première question arrive !","Voyons si tu peux faire un sans-faute !"],
            "end":["Bravo ! À bientôt pour un nouveau quiz !","Bien joué ! Rendez-vous pour le prochain défi !","Merci d'avoir joué ! À très vite !","Alors, quel est ton score ? À bientôt !","Prêt pour le prochain quiz ?"]
        },
        "Anglais":{"start":["Ready? Let's go!","Your turn!","Let's start the challenge!","Focus… the first question is coming!","Can you get a perfect score?"],"end":["Great job! See you in the next quiz!","Well played! See you for the next challenge!","Thanks for playing! See you soon!","So, what's your score? See you next time!","Ready for the next quiz?"]},
        "Espagnol":{"start":["¿Listo? ¡Empezamos!","¡Te toca!","¡Comienza el desafío!","Concéntrate… llega la primera pregunta!","¿Puedes conseguir un pleno?"],"end":["¡Bravo! ¡Hasta el próximo quiz!","¡Muy bien! Nos vemos en el próximo desafío!","¡Gracias por jugar! ¡Hasta pronto!","¿Cuál fue tu puntuación? ¡Hasta la próxima!","¿Listo para el próximo quiz?"]},
        "Arabe":{"start":["هل أنت مستعد؟ هيا نبدأ!","حان دورك!","لنبدأ التحدي!","ركز جيدًا… السؤال الأول قادم!","هل تستطيع الحصول على نتيجة كاملة؟"],"end":["أحسنت! نراك في الاختبار القادم!","عمل رائع! نلتقي في التحدي القادم!","شكرًا لمشاركتك! نراك قريبًا!","ما هي نتيجتك؟ نراك لاحقًا!","هل أنت مستعد للاختبار القادم؟"]},
        "Allemand":{"start":["Bereit? Los geht's!","Du bist dran!","Starten wir die Herausforderung!","Konzentriere dich… die erste Frage kommt!","Schaffst du eine perfekte Punktzahl?"],"end":["Großartig! Bis zum nächsten Quiz!","Gut gespielt! Bis zur nächsten Herausforderung!","Danke fürs Mitspielen! Bis bald!","Wie ist dein Ergebnis? Bis zum nächsten Mal!","Bereit für das nächste Quiz?"]},
        "Italien":{"start":["Pronto? Si parte!","Tocca a te!","Inizia la sfida!","Concentrati… arriva la prima domanda!","Riesci a fare punteggio pieno?"],"end":["Bravo! Alla prossima quiz!","Ben fatto! Ci vediamo alla prossima sfida!","Grazie per aver giocato! A presto!","Qual è il tuo punteggio? Alla prossima!","Pronto per il prossimo quiz?"]}
    }
    mp=motivation_presets.get(quiz_language,motivation_presets["Français"])
    with mm1:
        start_options=mp["start"]+["Personnalisé"]
        start_default=mot_defaults["start"] if mot_defaults["start"] in start_options else start_options[0]
        mot_start_choice=st.selectbox("Avant le quiz",start_options,index=start_options.index(start_default),key="mot_start_choice")
        if mot_start_choice=="Personnalisé":
            mot_start_q=st.text_input("Votre message avant le quiz",mot_defaults["start"],key="mot_start_custom")
        else:
            mot_start_q=mot_start_choice
    with mm2:
        end_options=mp["end"]+["Personnalisé"]
        end_default=mot_defaults["end"] if mot_defaults["end"] in end_options else end_options[0]
        mot_end_choice=st.selectbox("À la fin",end_options,index=end_options.index(end_default),key="mot_end_choice")
        if mot_end_choice=="Personnalisé":
            mot_end_q=st.text_input("Votre message de fin",mot_defaults["end"],key="mot_end_custom")
        else:
            mot_end_q=mot_end_choice
    st.caption("Aucune carte intermédiaire : les questions s'enchaînent sans interruption.")
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="qvp-settings-card"><div class="qvp-card-heading">🎯 3. CONTENU — Questions / réponses</div>',unsafe_allow_html=True)
    with st.expander("Source, génération et édition des questions", expanded=not bool(st.session_state.get("q_data"))):
        mode_q=st.radio("Source du contenu",["🤖 IA Gemini","📄 CSV"],horizontal=True,key="mode_q")
        if mode_q=="🤖 IA Gemini":
            st.caption("💡 Changer le thème, la voix, le fond, le hook ou le CTA ne consomme aucun quota Gemini. Le CSV et les modifications manuelles non plus. Une nouvelle requête Gemini est envoyée uniquement si tu demandes un nouveau contenu IA.")
            gen_key=_quiz_generation_key(nb_q,th_q,quiz_language)
            cached_key=st.session_state.get("q_ai_key")
            if cached_key==gen_key and st.session_state.get("q_data") and st.session_state.get("q_source","").startswith("IA"):
                st.info("♻️ Ce quiz IA est déjà en mémoire : aucun appel Gemini ne sera fait pour les changements de style ou de vidéo.")
            bq1,bq2=st.columns(2)
            with bq1:
                if st.button("♻️ Charger / générer ce quiz",key="genq",use_container_width=True):
                    if cached_key==gen_key and st.session_state.get("q_ai_cache"):
                        st.session_state.q_data=[dict(x) for x in st.session_state.q_ai_cache]
                        st.session_state.q_source=f"IA • {th_q} • cache"
                        st.success("✅ Quiz déjà généré : réutilisation du cache, 0 nouvelle requête Gemini.")
                    elif not api_key:
                        st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                    else:
                        try:
                            prompt=f'''Tu es un créateur expert de quiz Shorts. Génère exactement {nb_q} questions DIFFERENTES en {QUIZ_LANGUAGE_LABELS[quiz_language]} sur le sujet « {th_q} ».
Varie les connaissances testées et évite toute répétition entre les questions.
Le sujet demandé est une contrainte stricte : chaque question, ses 4 réponses et son explication doivent appartenir clairement et directement à la thématique « {th_q} ». N'introduis aucun fait hors sujet et ne mélange jamais une autre catégorie.
Chaque objet doit respecter EXACTEMENT cette structure :
{{"question":"...","options":["réponse A","réponse B","réponse C","réponse D"],"reponse_correcte":"A","explication":"..."}}
IMPORTANT : options est une LISTE de 4 chaînes dans l'ordre A, B, C, D.
reponse_correcte est UNIQUEMENT une lettre parmi A, B, C ou D.
Les 4 options doivent être plausibles et une seule correcte.
Retourne UNIQUEMENT le tableau JSON, sans ``` et sans texte avant ou après.'''
                            res_text,_=gemini_generate_text(prompt)
                            data=normalize_questions(parse_json(res_text))
                            if len(data)<nb_q: raise ValueError(f"Gemini n'a fourni que {len(data)} questions sur {nb_q}.")
                            st.session_state.q_data=data[:nb_q]
                            st.session_state.q_ai_cache=[dict(x) for x in st.session_state.q_data]
                            st.session_state.q_ai_key=gen_key
                            st.session_state.q_source=f"IA • {th_q}"
                            st.success(f"✅ {len(data)} questions générées. Cette génération est maintenant en cache.")
                        except Exception as e: st.error(f"Erreur Gemini : {e}")
            with bq2:
                if st.button("⚠️ Nouveau lot IA (1 quota)",key="forceq",use_container_width=True):
                    if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                    else:
                        try:
                            prompt=f'''Génère exactement {nb_q} questions DIFFERENTES en {QUIZ_LANGUAGE_LABELS[quiz_language]} sur « {th_q} ».
Le sujet « {th_q} » est une contrainte stricte : toutes les questions, réponses et explications doivent correspondre directement à cette thématique, sans mélange de catégories.
Format strict : [{{"question":"...","options":["A","B","C","D"],"reponse_correcte":"A","explication":"..."}}].
Une seule bonne réponse. Retourne uniquement le JSON.'''
                            res_text,_=gemini_generate_text(prompt)
                            data=normalize_questions(parse_json(res_text))
                            if len(data)<nb_q: raise ValueError(f"Gemini n'a fourni que {len(data)} questions sur {nb_q}.")
                            st.session_state.q_data=data[:nb_q]
                            st.session_state.q_ai_cache=[dict(x) for x in st.session_state.q_data]
                            st.session_state.q_ai_key=gen_key
                            st.session_state.q_source=f"IA • {th_q}"
                            st.success(f"✅ Nouveau lot IA : {len(data)} questions.")
                        except Exception as e: st.error(f"Erreur Gemini : {e}")
        else:
            st.markdown('<div class="qvp-card"><b>📄 Import CSV</b><div class="qvp-small">Prépare tes questions dans Excel/Google Sheets puis exporte en CSV. Maximum : 15 questions.</div></div>',unsafe_allow_html=True)
            st.download_button("⬇️ Télécharger le modèle CSV", data=csv_template(), file_name="quiz_template.csv", mime="text/csv", key="csvtemplate")
            csv_file=st.file_uploader("Choisir ton fichier CSV",type=["csv"],key="quizcsv")
            if csv_file is not None:
                try:
                    imported=parse_quiz_csv(csv_file); st.session_state.q_data=imported; st.session_state.q_source="CSV manuel"
                    st.success(f"✅ {len(imported)} questions importées.")
                    st.dataframe([{"#":i+1,"Question":q["question"],"A":q["options"][0],"B":q["options"][1],"C":q["options"][2],"D":q["options"][3],"Bonne":q["reponse_correcte"]} for i,q in enumerate(imported)], use_container_width=True, hide_index=True)
                except Exception as e: st.error(f"CSV invalide : {e}")

        if st.session_state.get("q_data"):
            st.success(f"Quiz prêt : {len(st.session_state.q_data)} question(s) • {st.session_state.get('q_source','source manuelle')}")
            st.caption("📄 Pour modifier un lot complet, utilise le CSV. Pour les réglages visuels, utilise l'Éditeur Studio.")
    st.markdown('</div>',unsafe_allow_html=True)

    # V29 — le profil vocal choisi pilote la narration du quiz sans modifier le réglage global de vitesse.
    tts_rate = quiz_tts_rate if "quiz_tts_rate" in locals() else tts_rate

    style_q_full="Style 1 — 4 réponses + révélation" if style_q.startswith("Style 1") else "Style 2 — questions/réponses cumulatives"
    quiz_style_id="2" if style_q_full.startswith("Style 2") else "1"
    qprefix=_qvp_prefix("quiz", quiz_style_id)
    bg_mode_q=st.session_state.get(qprefix+"bg_mode", "✨ Automatique")
    uploaded_bg_q=st.session_state.get(qprefix+"bg_upload")
    bg_mode_clean_q="Généré automatiquement" if str(bg_mode_q).startswith("✨") else "Image personnalisée" if str(bg_mode_q).startswith("🖼️") else "Aucun"
    bg_q=selected_video_background(theme_q,th_q,bg_mode_clean_q,uploaded_bg_q)

    
    # V31.4 — panneau de prévisualisation restauré et réellement visible pendant l’édition.
    st.markdown("""<style>
    [data-testid="column"]:has(.qvp-studio-workspace-anchor){
        position:sticky !important; top:18px !important; align-self:flex-start !important;
        z-index:30 !important; min-width:0 !important;
    }
    .qvp-preview-panel{position:relative !important; z-index:31 !important;}
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="qvp-studio-workspace-title">🎨 ÉDITEUR STUDIO • PRO — aperçu en temps réel</div>',unsafe_allow_html=True)
    st.markdown('<div class="qvp-studio-workspace-note">Sur ordinateur, l’Éditeur Studio et l’Aperçu Interactif commencent exactement au même niveau. L’aperçu reste visible pendant que tu descends dans les réglages.</div>',unsafe_allow_html=True)
    studio_q_left, studio_q_right = st.columns([1.12,0.88], gap="large")
    with studio_q_left:
        render_layout_editor("quiz", "2" if style_q_full.startswith("Style 2") else "1")
    with studio_q_right:
        st.markdown('<div class="qvp-studio-workspace-anchor"></div>',unsafe_allow_html=True)
        # V25 — aperçu permanent en face de l’Éditeur Studio.
        st.markdown('<div class="qvp-preview-panel"><div class="qvp-preview-title">👁️ APERÇU INTERACTIF</div><div class="qvp-preview-note">📌 Aperçu toujours visible en face de l’Éditeur Studio. ⚡ Toute modification de l’Éditeur Studio recalcule automatiquement l’aperçu.</div></div>',unsafe_allow_html=True)
        if style_q_full.startswith("Style 2"):
            preview_state_q=st.radio("État",["Q1 + minuteur","Q2 + R1","Q3 + R1/R2"],horizontal=True,key=f"preview_state_q_{quiz_style_id}")
        else:
            preview_state_q=st.radio("État",["Question + réponses","Compte à rebours","Bonne réponse + explication"],horizontal=True,key="preview_state_q")
        try:
            cfg_q=_layout("quiz",quiz_style_id)
            sample_bg = bg_q if isinstance(bg_q, Image.Image) else selected_video_background(theme_q, th_q, bg_mode_clean_q, uploaded_bg_q)
            live_data=list(st.session_state.get("q_data") or [])
            if live_data:
                q0=live_data[0]
                preview_q=clean_text(q0.get("question") or "Quelle est la capitale de la France ?")
                preview_opts=[clean_text(x) for x in (q0.get("options") or ["Paris","Londres","Rome","Berlin"])][:4]
                while len(preview_opts)<4: preview_opts.append("")
                rc=str(q0.get("reponse_correcte","A")).strip().upper()
                preview_corr=max(0,min(3,ord(rc[0])-65)) if rc and rc[0] in "ABCD" else 0
                preview_expl=clean_text(q0.get("explication") or "Explication de la bonne réponse.")
            else:
                samples={
                    "Culture générale":("Quelle est la capitale de la France ?",["Paris","Londres","Rome","Berlin"],0,"Paris est la capitale de la France."),
                    "Géographie":("Quelle est la capitale du Canada ?",["Toronto","Ottawa","Montréal","Vancouver"],1,"Ottawa est la capitale du Canada."),
                    "Sciences":("Quelle planète est la plus proche du Soleil ?",["Vénus","Mercure","Mars","Jupiter"],1,"Mercure est la planète la plus proche du Soleil."),
                    "Histoire":("En quelle année débute la Révolution française ?",["1789","1815","1914","1945"],0,"La Révolution française débute en 1789."),
                }
                preview_q,preview_opts,preview_corr,preview_expl=samples.get(th_q,samples["Culture générale"])
            if style_q_full.startswith("Style 2"):
                items=list(live_data[:3]) if live_data else []
                preview_samples=[
                    {"question":preview_q,"options":preview_opts,"reponse_correcte":chr(65+preview_corr)},
                    {"question":"Quelle planète est la plus proche du Soleil ?","options":["Vénus","Mercure","Mars","Jupiter"],"reponse_correcte":"B"},
                    {"question":"Quel est le plus grand océan du monde ?","options":["Atlantique","Indien","Arctique","Pacifique"],"reponse_correcte":"D"},
                ]
                while len(items)<3: items.append(preview_samples[len(items)])
                if preview_state_q=="Q1 + minuteur":
                    # État 1 : Q1 active, aucun historique.
                    preview=draw_style2_frame(items,0,theme_q,channel_q,sample_bg,timer=3,timer_fraction=.72,answer_reveal=False,video_title=th_q)
                elif preview_state_q=="Q2 + R1":
                    # État 2 : Q2 remplace Q1 au même emplacement ; seule R1 reste dans l'historique.
                    preview=draw_style2_frame(items,min(1,len(items)-1),theme_q,channel_q,sample_bg,timer=2,timer_fraction=.5,answer_reveal=False,video_title=th_q)
                else:
                    # État 3 : Q3 remplace Q2 ; R1 et R2 restent visibles dans l'historique.
                    preview=draw_style2_frame(items,min(2,len(items)-1),theme_q,channel_q,sample_bg,timer=3,timer_fraction=.5,answer_reveal=False,video_title=th_q)
            elif preview_state_q=="Question + réponses":
                preview=draw_quiz_frame(preview_q,preview_opts,theme_q,1,max(1,int(nb_q)),channel_q,sample_bg,entrance=1.0,motion=0.0,pulse=0.12,video_title=th_q)
            elif preview_state_q=="Compte à rebours":
                preview=draw_quiz_frame(preview_q,preview_opts,theme_q,1,max(1,int(nb_q)),channel_q,sample_bg,entrance=1.0,timer=3,timer_fraction=0.72,pulse=0.55,motion=0.0,video_title=th_q)
            else:
                preview=draw_quiz_frame(preview_q,preview_opts,theme_q,1,max(1,int(nb_q)),channel_q,sample_bg,entrance=1.0,correct_idx=preview_corr,reveal_progress=1.0,pulse=0.15,motion=0.0,video_title=th_q,explanation=preview_expl,explanation_progress=1.0)
            st.markdown("#### 👁️ APERÇU INTERACTIF — édition en direct")
            render_clickable_preview(preview,"quiz",quiz_style_id,cfg_q,"")
            st.caption("⚡ Live : les paramètres généraux, le sujet, les questions et chaque réglage de l’Éditeur Studio sont répercutés ici après chaque modification.")
        except Exception as e:
            st.error(f"Aperçu live indisponible : {e}")

        st.markdown("#### 📱 FORMAT DE SORTIE")
        st.caption("Le gabarit de création reste propre et sans zones interdites affichées. Le format final est choisi automatiquement à l’export selon le réseau.")

        # Action principale immédiatement sous l'aperçu et les commandes rapides.
        q_generate_btn_clicked=st.button("🎬 GÉNÉRER LA VIDÉO",key="makeq_unified",type="primary",use_container_width=True,disabled=not bool(st.session_state.get("q_data")))
        s1,s2=st.columns(2,gap="small")
        with s1:
            if st.button("💾 Enregistrer les réglages",key="studio_save_unified_q",use_container_width=True):
                _save_settings(); st.success("✅ Réglages enregistrés.")
        with s2:
            if st.button("🎲 Nouvelle variation",key="studio_variation_unified_q",use_container_width=True):
                st.session_state["q_variation_seed"]=random.randint(1,999999); st.rerun()


    if q_generate_btn_clicked and st.session_state.get("q_data"):
        try:
            with st.spinner("Création du Short Quiz — mise en page personnalisée..."):
                with tempfile.TemporaryDirectory() as tmp:
                    tic,ding,pop,whoosh=make_sfx(tmp); countdown_sfx=make_sfx_countdown(tic,ding,tmp)
                    clips=[]; total=len(st.session_state.q_data)

                    # Motivation au début : ajoutée comme un clip séparé, sans modifier les questions.
                    if clean_text(mot_start_q):
                        ma=os.path.join(tmp,"mot_start.m4a"); synthesize_audio(_motivation_text_clean(mot_start_q),voice_q,ma,tts_rate); md=audio_duration(ma)
                        if md>0.15:
                            mf=save_frames([(draw_page_template(mot_start_q,theme_q,channel_q,bg_q,p,"intro",st.session_state.get("q1_intro_page_variant","Premium lumineux"),"quiz","1",quiz_language),md/6) for p in [0.08,0.22,0.40,0.60,0.82,1.0]],tmp,"mot_start")
                            mo=os.path.join(tmp,"mot_start.mp4"); make_segment(mf,ma,mo,tmp); clips.append(mo)

                    if style_q_full.startswith("Style 2"):
                        # STYLE 2 — structure cumulative exacte :
                        # Q1 + minuteur → révélation R1 → Q2 + R1 → révélation R2
                        # → Q3 + R1/R2 → etc.
                        # Le titre reste fixe et UNE SEULE question active occupe toujours le même emplacement.
                        # Chaque réponse révélée est ensuite conservée dans l'historique ; la question précédente disparaît. 
                        items=st.session_state.q_data[:15]
                        total=len(items)
                        for idx,q in enumerate(items):
                            bg_question=bg_q
                            corr="ABCD".index(q["reponse_correcte"])
                            answer_text=clean_text(q["options"][corr])
                            qa_raw=os.path.join(tmp,f"s2_q_{idx}.mp3")
                            ans_raw=os.path.join(tmp,f"s2_a_{idx}.mp3")
                            q_words=synthesize_audio(q["question"],voice_q,qa_raw,tts_rate)
                            synthesize_audio(answer_text,voice_q,ans_raw,tts_rate)
                            qdur=audio_duration(qa_raw); adur=audio_duration(ans_raw)
                            qframes=word_timed_frames(qa_raw,q_words,lambda wi,prog: draw_style2_frame(items,idx,theme_q,channel_q,bg_question,answer_reveal=False,motion=prog*.7,video_title=th_q,question_active_word=wi),qdur)
                            frames=[(img,dur) for img,dur in qframes]
                            cdur=3.12; cd_steps=COUNTDOWN_STEPS
                            for j in range(cd_steps):
                                t=j/max(1,cd_steps-1); elapsed=t*cdur
                                if elapsed < 1.02: sec=3; frac=1-(elapsed/1.02)
                                elif elapsed < 2.04: sec=2; frac=1-((elapsed-1.02)/1.02)
                                elif elapsed < 3.0: sec=1; frac=1-((elapsed-2.04)/0.96)
                                else: sec=None; frac=0.0
                                frames.append((draw_style2_frame(items,idx,theme_q,channel_q,bg_question,timer=sec,timer_fraction=frac,answer_reveal=False,motion=t,video_title=th_q),cdur/cd_steps))
                            pop_raw=os.path.join(tmp,f"s2_a_pop_{idx}.m4a")
                            sfx_cfg=_layout("quiz","2")
                            if sfx_cfg.get("sfx_enabled",True):
                                mix_voice_sfx(ans_raw,pop,pop_raw,0,float(sfx_cfg.get("sfx_volume",0.30)))
                            else:
                                pop_raw=ans_raw
                            aframes=[]; a_steps=max(3,min(REVEAL_MAX_STEPS,int(adur*3)))
                            for j in range(a_steps):
                                t=j/max(1,a_steps-1); aframes.append((draw_style2_frame(items,idx,theme_q,channel_q,bg_question,answer_reveal=True,motion=1.0+t*.5,video_title=th_q),adur/a_steps))
                            frames.extend(aframes)
                            audio=os.path.join(tmp,f"s2_full_{idx}.m4a")
                            q_with_fx=os.path.join(tmp,f"s2_q_fx_{idx}.m4a")
                            if sfx_cfg.get("sfx_enabled",True):
                                mix_voice_sfx(qa_raw,whoosh,q_with_fx,0,float(sfx_cfg.get("sfx_volume",0.30))*0.75)
                            else:
                                q_with_fx=qa_raw
                            concat_audio_files([q_with_fx,countdown_sfx,pop_raw],audio)
                            out=os.path.join(tmp,f"s2_{idx}.mp4")
                            make_segment(save_frames(frames,tmp,f"s2f_{idx}"),audio,out,tmp,1.0)
                            clips.append(out)
                            del frames
                            gc.collect()

                    # Style 2 reste entièrement cumulatif : pas de pages d'explication séparées.
                    else:
                        # STYLE 1 : question + 4 réponses, minuteur, révélation verte, explication.
                        for idx,q in enumerate(st.session_state.q_data):
                            corr="ABCD".index(q["reponse_correcte"])
                            bg_question = selected_video_background(theme_q, q.get("question", th_q), bg_mode_clean_q, uploaded_bg_q)
                            qa_raw=os.path.join(tmp,f"q_{idx}.mp3")
                            q_words=synthesize_audio(q["question"],voice_q,qa_raw,tts_rate)
                            qdur=audio_duration(qa_raw)
                            exp_text=clean_text(q.get("explication","")) or f"La bonne réponse est {q['options'][corr]}."
                            ea_raw=os.path.join(tmp,f"exp_{idx}.mp3")
                            exp_words=synthesize_audio(exp_text,voice_q,ea_raw,tts_rate)
                            edur=audio_duration(ea_raw)
                            exp_mix=os.path.join(tmp,f"exp_mix_{idx}.m4a")
                            sfx_cfg=_layout("quiz","1")
                            if sfx_cfg.get("sfx_enabled",True):
                                mix_voice_sfx(ea_raw,ding,exp_mix,0,float(sfx_cfg.get("sfx_volume",0.30))*2.1)
                            else:
                                exp_mix=ea_raw
                            q_with_fx=os.path.join(tmp,f"q_fx_{idx}.m4a")
                            if sfx_cfg.get("sfx_enabled",True):
                                mix_voice_sfx(qa_raw,whoosh,q_with_fx,0,float(sfx_cfg.get("sfx_volume",0.30))*0.75)
                            else:
                                q_with_fx=qa_raw
                            full_audio_raw=os.path.join(tmp,f"question_full_raw_{idx}.m4a")
                            concat_audio_files([q_with_fx,countdown_sfx,exp_mix],full_audio_raw)
                            # Fond musical contrôlé depuis l’Éditeur Studio.
                            full_audio=os.path.join(tmp,f"question_full_{idx}.m4a")
                            music_enabled=bool(st.session_state.get("q1_bg_music_enabled",True))
                            music_volume=float(st.session_state.get("q1_bg_music_volume",0.15))
                            music_style=st.session_state.get("q1_bg_music_style","Suspense léger")
                            music_source=st.session_state.get("q1_bg_music_source","Musique générée par SuspenseLingo")
                            uploaded_music=st.session_state.get("q1_bg_music_upload") if music_source=="Ma propre musique" else None
                            if music_enabled and music_volume>0:
                                if uploaded_music is not None:
                                    music=prepare_custom_background_music(uploaded_music,audio_duration(full_audio_raw),tmp,f"quiz_bg_{idx}")
                                else:
                                    music=make_quiz_background_music(audio_duration(full_audio_raw),tmp,f"quiz_bg_{idx}",1.0,music_style,countdown_start=qdur,countdown_duration=3.12)
                                mix_background_music(full_audio_raw,music,full_audio,1.0,music_volume)
                            else:
                                full_audio=full_audio_raw
                            qframes=word_timed_frames(qa_raw,q_words,lambda wi,prog: draw_quiz_frame(q["question"],q["options"],theme_q,idx+1,total,channel_q,bg_question,entrance=1.0,motion=prog*.9,video_title=th_q,question_active_word=wi),qdur)
                            frames=[(img,dur) for img,dur in qframes]
                            cdur=3.12; cd_steps=COUNTDOWN_STEPS
                            for j in range(cd_steps):
                                t=j/max(1,cd_steps-1); elapsed=t*cdur
                                if elapsed < 1.02: sec=3; frac=1-(elapsed/1.02)
                                elif elapsed < 2.04: sec=2; frac=1-((elapsed-1.02)/1.02)
                                elif elapsed < 3.0: sec=1; frac=1-((elapsed-2.04)/0.96)
                                else: sec=None; frac=0.0
                                frames.append((draw_quiz_frame(q["question"],q["options"],theme_q,idx+1,total,channel_q,bg_question,entrance=1.0,timer=sec,timer_fraction=frac,pulse=0.55+0.45*math.sin(t*math.pi*12),motion=1.0+t*1.2,video_title=th_q),cdur/cd_steps))
                            ex_mix_words=exp_words
                            eframes=word_timed_frames(exp_mix,ex_mix_words,lambda wi,prog: draw_quiz_frame(q["question"],q["options"],theme_q,idx+1,total,channel_q,bg_question,entrance=1.0,correct_idx=corr,reveal_progress=min(1,prog*3),pulse=0.15*(1-prog),motion=2.0+prog,video_title=th_q,explanation=exp_text,explanation_progress=1.0,explanation_active_word=wi),edur)
                            frames.extend(eframes)
                            # Micro-pause de 0,5 s pour laisser assimiler la bonne réponse.
                            pause_audio=os.path.join(tmp,f"exp_pause_{idx}.m4a")
                            subprocess.run([get_ffmpeg(),"-y","-i",exp_mix,"-af","apad=pad_dur=0.50","-t",f"{edur+0.50:.3f}","-c:a","aac","-b:a","160k",pause_audio],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
                            if frames:
                                frames.append((frames[-1][0],0.50))
                            exp_mix=pause_audio
                            concat_audio_files([q_with_fx,countdown_sfx,exp_mix],full_audio_raw)
                            out=os.path.join(tmp,f"qfull_{idx}.mp4")
                            make_segment(save_frames(frames,tmp,f"qfull_{idx}"),full_audio,out,tmp,1.0)
                            clips.append(out)

                    # FIN UNIFIÉE : une seule page au lieu de deux.
                    # La motivation de fin + le CTA + l'engagement sont lus dans une seule séquence
                    # afin d'éviter une page intermédiaire longue et une coupure visuelle.
                    final_parts=[]
                    if clean_text(mot_end_q):
                        final_parts.append(_motivation_text_clean(mot_end_q))
                    if clean_text(outro_q):
                        final_parts.append(clean_text(outro_q))
                    if clean_text(engagement_q):
                        final_parts.append(clean_text(engagement_q))
                    final_cta_text=" ".join(dict.fromkeys([x for x in final_parts if x])).strip()
                    if final_cta_text:
                        oa=os.path.join(tmp,"outro.m4a")
                        synthesize_audio(final_cta_text,voice_q,oa,tts_rate)
                        od=audio_duration(oa)
                        if od>0.15:
                            of=save_frames([(draw_page_template(final_cta_text,theme_q,channel_q,bg_q,p,"outro",st.session_state.get("q1_outro_page_variant","Premium lumineux"),"quiz","1",quiz_language),od/6)
                                            for p in [0.08,0.22,0.40,0.60,0.82,1.0]],tmp,"outro")
                            oo=os.path.join(tmp,"outro.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)

                    final=os.path.join(tmp,"quizvideo_pro_custom.mp4")
                    # Assemblage final robuste : même moteur PTS/audio que le Vocabulaire Style 2.
                    # Le stream-copy précédent pouvait produire un AAC final corrompu et
                    # une durée audio différente de la vidéo après l'ajout musique/motivations.
                    concat_videos_style2(clips,final,tmp)
                    vd_final=video_duration(final); ad_final=audio_duration(final)
                    if vd_final <= 0 or ad_final <= 0 or abs(vd_final-ad_final) > 0.08:
                        raise RuntimeError(f"Synchronisation finale invalide : vidéo {vd_final:.2f}s / audio {ad_final:.2f}s")
                    with open(final,"rb") as f: data=f.read()
                    st.session_state["last_quiz_video_data"] = data
                    st.success("✅ Short Quiz terminé avec ta mise en page.")
                    st.video(data)
                    st.download_button("⬇️ Télécharger quizvideo_pro_custom.mp4",data=data,file_name="quizvideo_pro_custom.mp4",mime="video/mp4",key="dq7")
        except Exception as e:
            st.error(f"Erreur pendant le montage SuspenseLingo : {e}")

else:
    st.markdown('<div class="qvp-studio-header"><b>🎬 SuspenseLingo Studio</b><span>🗣️ VOCABULAIRE</span><small>Mise en page Pro • Éditeur interactif</small></div>',unsafe_allow_html=True)
    # Paramètres et contenu en pleine largeur.
    st.markdown('<div class="qvp-settings-card"><div class="qvp-card-heading">⚙️ 1. Paramètres généraux</div>',unsafe_allow_html=True)
    v1,v2=st.columns(2,gap="medium")
    with v1:
        th_v=st.text_input("Sujet","Voyage",key="thv")
        nb_v=st.slider("Mots",1,15,15,key="nbv")
        langue_v=st.selectbox("Langue cible",list(VOICES_MAP),key="lv")
    with v2:
        voice_tr_name=st.selectbox("Voix traduction",list(VOICES_MAP[langue_v]),key="vtr")
        voice_tr=VOICES_MAP[langue_v][voice_tr_name]
        theme_v=st.selectbox("Style visuel",list(THEMES),key="tv",help="Palettes lumineuses et distinctes : les changements s’appliquent à l’aperçu et au rendu vidéo.")
        st.caption("✨ Palettes actualisées : fonds plus lumineux, cartes contrastées et couleurs assorties.")
        style_v=st.radio("Structure",["Style 1 — Mot → minuteur → traduction","Style 2 — Cumulatif"],key="stylev_compact")
    v3,v4=st.columns(2,gap="medium")
    with v3:
        channel_v=st.text_input("Chaîne","@LingoPulse_Daily",key="cv")
        hook_v=st.text_input("Hook","Apprends ces mots !",key="hv")
    with v4:
        outro_v=st.text_input("Message de fin","Abonne-toi pour un nouveau mot !",key="ov")
        if style_v.startswith("Style 2"):
            outro_v_sub=st.text_input("Sous-message de fin (facultatif)","Nouveau mot demain 👋",key="ov_sub")
        else:
            outro_v_sub=""
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="qvp-settings-card"><div class="qvp-card-heading">🎯 3. CONTENU — Mots / traductions</div>',unsafe_allow_html=True)
    vg_key=_vocab_generation_key(nb_v,th_v,langue_v)
    with st.expander("Source, génération et édition des mots", expanded=not bool(st.session_state.get("v_data"))):
        vb1,vb2=st.columns(2)
        with vb1:
            if st.button("♻️ Charger / générer le vocabulaire",key="genv",use_container_width=True):
                if st.session_state.get("v_ai_key")==vg_key and st.session_state.get("v_ai_cache"):
                    st.session_state.v_data=[dict(x) for x in st.session_state.v_ai_cache]
                    st.success("✅ Vocabulaire déjà généré : cache réutilisé, 0 nouvelle requête Gemini.")
                elif not api_key:
                    st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                else:
                    try:
                        prompt=f'''Génère exactement {nb_v} mots français DIFFERENTS avec leur traduction en {langue_v} sur le sujet « {th_v} ». Évite les répétitions et varie le vocabulaire. Retourne UNIQUEMENT un JSON valide: [{{"fr":"...","trad":"..."}}]'''
                        res_text,_=gemini_generate_text(prompt)
                        data=parse_json(res_text)[:nb_v]
                        if len(data)<nb_v: raise ValueError(f"Gemini n'a fourni que {len(data)} mots sur {nb_v}.")
                        st.session_state.v_data=data
                        st.session_state.v_ai_cache=[dict(x) for x in data]
                        st.session_state.v_ai_key=vg_key
                        st.success("✅ Vocabulaire généré et mis en cache.")
                    except Exception as e: st.error(f"Erreur Gemini : {e}")
        with vb2:
            if st.button("⚠️ Nouveau lot IA vocabulaire (1 quota)",key="forcev",use_container_width=True):
                if not api_key: st.error("Ajoute ta clé API Gemini dans la barre latérale.")
                else:
                    try:
                        prompt=f'''Génère exactement {nb_v} mots français différents avec traduction en {langue_v} sur « {th_v} ». Retourne uniquement [{{"fr":"...","trad":"..."}}].'''
                        res_text,_=gemini_generate_text(prompt)
                        data=parse_json(res_text)[:nb_v]
                        if len(data)<nb_v: raise ValueError(f"Gemini n'a fourni que {len(data)} mots sur {nb_v}.")
                        st.session_state.v_data=data
                        st.session_state.v_ai_cache=[dict(x) for x in data]
                        st.session_state.v_ai_key=vg_key
                        st.success("✅ Nouveau lot vocabulaire généré.")
                    except Exception as e: st.error(f"Erreur Gemini : {e}")
        if st.session_state.get("v_data"):
            st.success(f"Vocabulaire prêt : {len(st.session_state.v_data)} mot(s)")
            st.markdown("### ✏️ Modifier ou ajouter des mots — sans quota Gemini")
            vocab_rows=[{"Français":clean_text(x.get("fr","")),"Traduction":clean_text(x.get("trad",""))} for x in st.session_state.v_data]
            edited_v=st.data_editor(vocab_rows,num_rows="dynamic",use_container_width=True,key="vocab_editor",column_config={"Français":st.column_config.TextColumn("Français",width="medium"),"Traduction":st.column_config.TextColumn("Traduction",width="medium")},hide_index=True)
            ve1,ve2=st.columns(2)
            with ve1:
                if st.button("💾 Enregistrer les modifications",key="savevedit",use_container_width=True):
                    saved=_save_vocab_editor(edited_v)
                    if saved:
                        st.session_state.v_data=saved; st.success(f"✅ {len(saved)} mot(s) enregistré(s), sans appel Gemini.")
                    else: st.error("Aucun mot valide à enregistrer.")
            with ve2:
                if st.button("↩️ Restaurer le dernier lot IA",key="restorev",use_container_width=True):
                    if st.session_state.get("v_ai_cache"):
                        st.session_state.v_data=[dict(x) for x in st.session_state.v_ai_cache]; st.success("✅ Lot IA restauré, 0 quota consommé.")
                    else: st.info("Aucun lot IA en cache.")
    st.markdown('</div>',unsafe_allow_html=True)

    vocab_style_id="2" if style_v.startswith("Style 2") else "1"
    vprefix=_qvp_prefix("vocab", vocab_style_id)
    bg_mode_v=st.session_state.get(vprefix+"bg_mode", "✨ Automatique")
    uploaded_bg_v=st.session_state.get(vprefix+"bg_upload")
    bg_mode_clean_v="Généré automatiquement" if str(bg_mode_v).startswith("✨") else "Image personnalisée" if str(bg_mode_v).startswith("🖼️") else "Aucun"
    bg_v=selected_video_background(theme_v,th_v,bg_mode_clean_v,uploaded_bg_v)

    
    # V31.4 — panneau de prévisualisation restauré et réellement visible pendant l’édition.
    st.markdown("""<style>
    [data-testid="column"]:has(.qvp-studio-workspace-anchor){
        position:sticky !important; top:18px !important; align-self:flex-start !important;
        z-index:30 !important; min-width:0 !important;
    }
    .qvp-preview-panel{position:relative !important; z-index:31 !important;}
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="qvp-studio-workspace-title">🎨 ÉDITEUR STUDIO • PRO — aperçu en temps réel</div>',unsafe_allow_html=True)
    st.markdown('<div class="qvp-studio-workspace-note">Sur ordinateur, l’Éditeur Studio et l’Aperçu Interactif commencent exactement au même niveau. L’aperçu reste visible pendant que tu modifies la mise en page.</div>',unsafe_allow_html=True)
    studio_v_left, studio_v_right = st.columns([1.12,0.88], gap="large")
    with studio_v_left:
        render_layout_editor("vocab", "2" if style_v.startswith("Style 2") else "1")
    with studio_v_right:
        st.markdown('<div class="qvp-studio-workspace-anchor"></div>',unsafe_allow_html=True)
        # V25 — aperçu permanent en face de l’Éditeur Studio (Vocabulaire).
        # Toutes les fonctions du panneau Vocabulaire restent inchangées.
        st.markdown('<div class="qvp-preview-panel"><div class="qvp-preview-title">👁️ APERÇU INTERACTIF — VOCABULAIRE</div><div class="qvp-preview-note">Clique directement sur le mot, la traduction, le minuteur ou le tableau.</div></div>',unsafe_allow_html=True)
        if style_v.startswith("Style 2"):
            preview_state_v=st.radio("État",["Ligne 1 + réflexion","Ligne 2 + réflexion + traduction 1","Ligne 3 + réflexion + traductions 1–2"],horizontal=True,key=f"preview_state_v_{vocab_style_id}")
        else:
            preview_state_v=st.radio("État",["Mot","Compte à rebours","Traduction"],horizontal=True,key=f"preview_state_v_{vocab_style_id}")
        try:
            cfg_v=_layout("vocab",vocab_style_id)
            sample_bg_v=bg_v if isinstance(bg_v,Image.Image) else selected_video_background(theme_v,th_v,bg_mode_clean_v,uploaded_bg_v)
            if style_v.startswith("Style 2"):
                sample_items=[{"fr":"Bonjour","trad":"Hello"},{"fr":"Merci","trad":"Thank you"},{"fr":"Voyage","trad":"Travel"}]
                active=0 if preview_state_v=="Ligne 1 + réflexion" else 1 if preview_state_v=="Ligne 2 + réflexion + traduction 1" else 2
                preview_translation_word = 0 if "traduction" in preview_state_v else -1
                preview_v=draw_vocab_cumulative_frame(sample_items,active,theme_v,channel_v,sample_bg_v,timer=3 if "réflexion" in preview_state_v else None,timer_fraction=.72,reveal=("traduction" in preview_state_v),video_title=th_v,source_active_word=0 if active >= 0 else -1,translation_active_word=preview_translation_word)
            else:
                sample_items=[{"fr":"Bonjour","trad":"Hello"}]; phase_v="mot" if preview_state_v=="Mot" else "countdown" if preview_state_v=="Compte à rebours" else "translation"; preview_v=draw_vocab_frame(sample_items,0,langue_v,theme_v,channel_v,sample_bg_v,phase_v,3,.75,1.0)
            st.markdown("#### 👁️ APERÇU INTERACTIF — édition en direct")
            render_clickable_preview(preview_v,"vocab",vocab_style_id,cfg_v,"")
            st.caption("⚡ Aperçu en direct : modifie l'Éditeur Studio à gauche et le rendu se recalcule automatiquement. L'Éditeur Studio est l'unique panneau de réglage.")
        except Exception as e:
            st.caption(f"Aperçu indisponible pour le moment : {e}")

        st.markdown("#### 📱 FORMAT DE SORTIE")
        st.caption("Le gabarit de création reste propre et sans zones interdites affichées. Le format final est choisi automatiquement à l’export selon le réseau.")

        v_generate_btn_clicked=st.button("🎬 GÉNÉRER LA VIDÉO",key="makev_unified",type="primary",use_container_width=True,disabled=not bool(st.session_state.get("v_data")))
        s1,s2=st.columns(2,gap="small")
        with s1:
            if st.button("💾 Enregistrer les réglages",key="studio_save_unified_v",use_container_width=True):
                _save_settings(); st.success("✅ Réglages enregistrés.")
        with s2:
            if st.button("🎲 Nouvelle variation",key="studio_variation_unified_v",use_container_width=True):
                st.session_state["v_variation_seed"]=random.randint(1,999999); st.rerun()


    if v_generate_btn_clicked and st.session_state.get("v_data"):
        try:
            with st.spinner("Création du Short Vocabulaire Pro..."):
                with tempfile.TemporaryDirectory() as tmp:
                    tic,ding,pop,whoosh=make_sfx(tmp); clips=[]; items=st.session_state.v_data
                    countdown_sfx = make_vocab_style2_countdown_sfx(tic,ding,tmp) if style_v.startswith("Style 2") else make_sfx_countdown(tic,ding,tmp)
                    for idx,item in enumerate(items):
                        fa=os.path.join(tmp,f"fr_{idx}.mp3"); fw=synthesize_audio(item['fr'],VOICES_FR["Henri - Dynamique"],fa,tts_rate); fd=audio_duration(fa)
                        if style_v.startswith("Style 2"):
                            # ==========================================================
                            # VOCABULAIRE STYLE 2 — SÉQUENCE PRO
                            # État unique par ligne :
                            # FR progressive -> FR permanent -> réflexion ->
                            # traduction progressive -> FR+TR permanent -> ligne suivante.
                            # Aucun état ultérieur ne peut effacer une ligne déjà révélée.
                            # Français + voix
                            # → réflexion 3-2-1 + tic/tac
                            # → ding
                            # → traduction + voix
                            # → ligne conservée dans l'historique
                            # ==========================================================
                            sfx_cfg=_layout("vocab","2")

                            # --- 1. VOIX FRANÇAISE + apparition mot par mot ---
                            fwords=word_timed_frames_vocab_style2(
                                fa,fw,
                                lambda wi,prog: draw_vocab_cumulative_frame(
                                    items,idx,theme_v,channel_v,bg_v,
                                    reveal=False,motion=prog,
                                    video_title=th_v,
                                    source_active_word=wi
                                ),
                                fd
                            )

                            word_voice_fx=os.path.join(tmp,f"fr_fx_{idx}.m4a")
                            if sfx_cfg.get("sfx_enabled",True):
                                mix_voice_sfx(
                                    fa,pop,word_voice_fx,0,
                                    float(sfx_cfg.get("sfx_volume",0.30))
                                )
                            else:
                                word_voice_fx=fa

                            fr_clip=os.path.join(tmp,f"fr_{idx}_seg.mp4")
                            make_vocab_style2_segment(
                                save_frames(fwords,tmp,f"vf_{idx}"),
                                word_voice_fx,fr_clip,tmp,1.0
                            )

                            # --- 2. RÉFLEXION : 3-2-1 + TIC/TAC + DING ---
                            # IMPORTANT : le français doit rester affiché pendant toute
                            # la réflexion. On verrouille donc la dernière parole FR
                            # comme état permanent de cette ligne.
                            fr_last_word = max(0, len(fw) - 1)
                            reflection_duration=3.55
                            cframes=[]
                            steps=36

                            for j in range(steps):
                                elapsed=reflection_duration*j/steps
                                if elapsed<1.05:
                                    sec=3
                                    frac=1-(elapsed/1.05)
                                elif elapsed<2.10:
                                    sec=2
                                    frac=1-((elapsed-1.05)/1.05)
                                elif elapsed<3.15:
                                    sec=1
                                    frac=1-((elapsed-2.10)/1.05)
                                else:
                                    sec=None
                                    frac=0.0

                                cframes.append((
                                    draw_vocab_cumulative_frame(
                                        items,idx,theme_v,channel_v,bg_v,
                                        timer=sec,
                                        timer_fraction=max(0.0,frac),
                                        reveal=False,
                                        motion=elapsed/reflection_duration,
                                        video_title=th_v,
                                        # Le mot français reste visible pendant 3-2-1.
                                        source_active_word=fr_last_word
                                    ),
                                    reflection_duration/steps
                                ))

                            count_clip=os.path.join(tmp,f"count_{idx}.mp4")
                            make_vocab_style2_segment(
                                save_frames(cframes,tmp,f"vc_{idx}"),
                                countdown_sfx,count_clip,tmp,1.0
                            )

                            # --- 3. TRADUCTION + VOIX, puis conservation de la ligne ---
                            ta=os.path.join(tmp,f"tr_{idx}.mp3")
                            tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate)
                            td=audio_duration(ta)

                            tf=word_timed_frames_vocab_style2(
                                ta,tw,
                                lambda wi,prog: draw_vocab_cumulative_frame(
                                    items,idx,theme_v,channel_v,bg_v,
                                    reveal=True,motion=prog,
                                    video_title=th_v,
                                    # Le français reste définitivement visible
                                    # pendant que la traduction est prononcée.
                                    source_active_word=fr_last_word,
                                    translation_active_word=wi
                                ),
                                td
                            )

                            tr_fx=os.path.join(tmp,f"tr_fx_{idx}.m4a")
                            if sfx_cfg.get("sfx_enabled",True):
                                mix_voice_sfx(
                                    ta,pop,tr_fx,0,
                                    float(sfx_cfg.get("sfx_volume",0.30))
                                )
                            else:
                                tr_fx=ta

                            tr_clip=os.path.join(tmp,f"tr_{idx}.mp4")
                            make_vocab_style2_segment(
                                save_frames(tf,tmp,f"trf_{idx}"),
                                tr_fx,tr_clip,tmp,1.0
                            )

                            # On regroupe immédiatement les 3 phases du mot.
                            # Cela empêche les petits écarts de timebase de se
                            # cumuler sur 15 mots.
                            item_clip=os.path.join(tmp,f"item_{idx}.mp4")
                            concat_videos_style2(
                                [fr_clip,count_clip,tr_clip],
                                item_clip,tmp
                            )
                            clips.append(item_clip)

                        else:
                            fwords=word_timed_frames(fa,fw,lambda wi,prog: draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"mot",entrance=prog,source_active_word=wi),fd)
                            word_voice_fx=os.path.join(tmp,f"fr_fx_{idx}.m4a")
                            sfx_cfg=_layout("vocab","1")
                            if sfx_cfg.get("sfx_enabled",True): mix_voice_sfx(fa,pop,word_voice_fx,0,float(sfx_cfg.get("sfx_volume",0.30)))
                            else: word_voice_fx=fa
                            fo=os.path.join(tmp,f"fr_{idx}.mp4"); make_segment(save_frames(fwords,tmp,f"vf_{idx}"),word_voice_fx,fo,tmp); clips.append(fo)
                            cframes=[]
                            for j in range(COUNTDOWN_STEPS):
                                t=j/max(1,31); elapsed=t*3.12
                                if elapsed<1.02: sec=3; frac=1-(elapsed/1.02)
                                elif elapsed<2.04: sec=2; frac=1-((elapsed-1.02)/1.02)
                                elif elapsed<3.0: sec=1; frac=1-((elapsed-2.04)/.96)
                                else: sec=None; frac=0.0
                                cframes.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"countdown",sec,frac,1.0),3.12/32))
                            co=os.path.join(tmp,f"count_{idx}.mp4"); make_segment(save_frames(cframes,tmp,f"vc_{idx}"),countdown_sfx,co,tmp,.92); clips.append(co)
                            ta=os.path.join(tmp,f"tr_{idx}.mp3"); tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate); td=audio_duration(ta)
                            tf=word_timed_frames(ta,tw,lambda wi,prog: draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation",entrance=1.0,translation_active_word=wi),td)
                            tr_fx=os.path.join(tmp,f"tr_fx_{idx}.m4a")
                            if sfx_cfg.get("sfx_enabled",True): mix_voice_sfx(ta,pop,tr_fx,0,float(sfx_cfg.get("sfx_volume",0.30)))
                            else: tr_fx=ta
                            tro=os.path.join(tmp,f"tr_{idx}.mp4"); make_segment(save_frames(tf,tmp,f"trf_{idx}"),tr_fx,tro,tmp); clips.append(tro)
                        gc.collect()
                    oa=os.path.join(tmp,"vo.mp3"); synthesize_audio(outro_v,VOICES_FR["Henri - Dynamique"],oa,tts_rate); od=audio_duration(oa)
                    if style_v.startswith("Style 2"):
                        of=save_frames([(draw_page_template(outro_v+((" "+outro_v_sub) if clean_text(outro_v_sub) else ""),theme_v,channel_v,bg_v,p,"outro",st.session_state.get(("v2_" if style_v.startswith("Style 2") else "v1_")+"outro_page_variant","Premium lumineux"),"vocab","2" if style_v.startswith("Style 2") else "1",langue_v),max(.04,od/7)) for p in [.08,.28,.50,.72,.90,1.0]],tmp,"vo")
                    else:
                        of=save_frames([(draw_page_template(outro_v,theme_v,channel_v,bg_v,p,"outro",st.session_state.get("v1_outro_page_variant","Premium lumineux"),"vocab","1",langue_v),max(.04,od/7)) for p in [.08,.28,.50,.72,.90,1.0]],tmp,"vo")
                    oo=os.path.join(tmp,"vo.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)
                    final=os.path.join(tmp,"vocabulaire_pro.mp4")
                    if style_v.startswith("Style 2"):
                        concat_videos_style2(clips,final,tmp)
                    else:
                        concat_videos(clips,final,tmp)
                    with open(final,"rb") as f: data=f.read()
                    st.session_state["last_vocab_video_data"] = data
                    st.success("✅ Short Vocabulaire Pro terminé.")
                    st.video(data)
                    st.download_button("⬇️ Télécharger vocabulaire_pro.mp4",data=data,file_name="vocabulaire_pro.mp4",mime="video/mp4",key="dv4")
        except MemoryError:
            gc.collect(); st.error("La mémoire a été saturée pendant le rendu. Relance l'application puis réessaie.")
        except Exception as e: st.error(f"Erreur pendant le montage : {e}")

# Export persistant : placé après le rendu pour rester disponible après chaque rerun Streamlit.
if st.session_state.get("last_quiz_video_data"):
    render_export_panel(st.session_state["last_quiz_video_data"],"SuspenseLingo_Quiz","export_quiz_persist")
if st.session_state.get("last_vocab_video_data"):
    render_export_panel(st.session_state["last_vocab_video_data"],"SuspenseLingo_Vocabulaire","export_vocab_persist")

st.markdown('</div>',unsafe_allow_html=True)
