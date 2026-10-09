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
# V32.3.6 — interface claire conservée, graphismes thématiques et couleurs harmonisées
# V19 — Motivation milieu supprimée; TTS nettoyé; accroches localisées; suspense audio renforcé
# V23 — Stabilisation interface : colonne droite sticky, aperçu live, génération pro. Aucune fonctionnalité vidéo supprimée.
# ============================================================
st.set_page_config(page_title="SuspenseLingo Studio", page_icon="🎬", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg,#f8fbff 0%,#eef4fb 100%); color:#172033; }
[data-testid="stMain"] { background: transparent; color:#172033; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#ffffff 0%,#f2f6fc 100%); border-right: 1px solid #d9e2ef; }
[data-testid="stSidebar"] * { color:#334155 !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:#334155 !important; }
[data-testid="stSidebar"] .stRadio label { background:#ffffff; border:1px solid #dbe4f0; border-radius:14px; padding:8px 10px; margin:4px 0; }
label, [data-testid="stMarkdownContainer"] { color:#334155; }
[data-testid="stHeader"] { background: rgba(248,251,255,.92); }
.block-container { max-width: 1220px; padding-top: .55rem; padding-bottom: 1rem; }
h1, h2, h3 { letter-spacing: -0.02em; color:#172033; }
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
