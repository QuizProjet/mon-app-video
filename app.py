import streamlit as st
import google.generativeai as genai
import asyncio
import edge_tts
import json
import os
import re
import unicodedata
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
# QUIZVIDEO PRO — STUDIO
# V19 — Motivation milieu supprimée; TTS nettoyé; accroches localisées; suspense audio renforcé
# V23 — Stabilisation interface : colonne droite sticky, aperçu live, génération pro. Aucune fonctionnalité vidéo supprimée.
# ============================================================
st.set_page_config(page_title="SuspenseLingo Studio", page_icon="🎬", layout="wide")

st.markdown(r"""
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
.qvp-editor-tabs [data-testid="stTabs"] button {font-weight:750 !important;font-size:.78rem !important;padding:7px 8px !important;border-radius:99px !important;}
.qvp-editor-tabs [data-testid="stTabs"] button[aria-selected="true"] {background:#eef3fa !important;}
.qvp-preview-panel {padding:9px 12px !important;}
.qvp-preview-note {margin-bottom:5px !important;}
.qvp-actionbar {position:sticky;bottom:8px;z-index:90;background:rgba(255,255,255,.97);backdrop-filter:blur(10px);border:1px solid #d9e2ef;border-radius:14px;padding:7px;margin-top:10px;box-shadow:0 8px 22px rgba(15,23,42,.10);}
.qvp-fast-note{color:#52637a;font-size:.72rem;margin:2px 0 5px;}

/* V8.5 Studio : interface compacte */
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

/* QuizVideo Pro Studio V14 — refonte visuelle */
.qvp-studio-header{padding:10px 14px!important;margin:0 0 8px!important;border:1px solid #d8e2ef!important;border-radius:14px!important;background:linear-gradient(90deg,#fff,#f6f9fd)!important;box-shadow:0 5px 18px rgba(15,23,42,.06)!important;font-size:1rem!important}
.qvp-studio-header b{font-size:1.02rem!important}
.qvp-studio-header span{padding:5px 11px!important;font-size:.76rem!important;letter-spacing:.02em}
.qvp-studio-header small{font-size:.72rem!important}
[data-testid="stMain"] label{font-weight:650!important;color:#334155!important}
[data-testid="stMain"] input,[data-testid="stMain"] textarea,[data-testid="stMain"] [data-baseweb="select"]>div{border-radius:10px!important}
.qvp-editor-title{font-size:1rem!important;font-weight:850!important;color:#172033!important;margin:2px 0 8px!important}
[data-testid="stVerticalBlock"]:has(.qvp-editor-title){background:#fff!important}
[data-testid="stTabs"] [role="tablist"]{scrollbar-width:thin!important}
[data-testid="stTabs"] button{transition:all .15s ease!important}
.qvp-preview-panel{border:1px solid #cfdbea!important;background:linear-gradient(180deg,#ffffff,#f8fbff)!important;box-shadow:0 10px 28px rgba(15,23,42,.09)!important}
.qvp-preview-title{font-size:.98rem!important;color:#172033!important}
.qvp-preview-note{font-size:.72rem!important;color:#64748b!important}
[data-testid="stImage"] img{border-radius:12px!important;border:1px solid #cbd5e1!important;box-shadow:0 12px 30px rgba(15,23,42,.13)!important}
.qvp-actionbar{box-shadow:0 10px 25px rgba(15,23,42,.12)!important}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]{align-items:flex-start!important}
[data-testid="stSlider"] [role="slider"]{transform:scale(1.05)!important}
button[kind="primary"]{font-weight:850!important}

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

/* V12 — aperçu réduit */
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

/* V21 — interface compacte */
.qvp-studio-header{margin-top:2px!important;margin-bottom:8px!important;}
.qvp-section-card{padding:9px 12px!important;}
.qvp-section-title{margin-bottom:6px!important;}
.qvp-actionbar-v11{margin-top:4px!important;margin-bottom:6px!important;}
.qvp-preview-sticky{top:8px!important;}

/* V27 — poste de travail Studio */
.qvp-studio-workspace-title{margin:22px 0 10px;font-size:1.05rem;font-weight:800;color:#0f172a;}
.qvp-studio-workspace-note{margin:0 0 12px;color:#64748b;font-size:.88rem;}
.qvp-studio-workspace-anchor{height:1px;}
[data-testid="stHorizontalBlock"]:has(.qvp-studio-workspace-anchor) > [data-testid="column"]:last-child{position:sticky!important;top:82px!important;align-self:flex-start!important;z-index:35!important;}
@media (max-width:1050px){[data-testid="stHorizontalBlock"]:has(.qvp-studio-workspace-anchor) > [data-testid="column"]:last-child{position:static!important;}}

/* V22 — Studio 60/40 */
.block-container{max-width:1700px!important;padding-left:1.2rem!important;padding-right:1.2rem!important;}
.qvp-studio-shell{max-width:none!important;width:100%!important;}
.qvp-two-col{width:100%;}
.qvp-settings-card{border:1px solid #d8e2ee;border-radius:16px;padding:14px 15px;background:linear-gradient(180deg,#ffffff,#f7faff);box-shadow:0 6px 20px rgba(15,23,42,.055);margin:0 0 12px;}
.qvp-settings-card .qvp-card-heading{font-size:.84rem;font-weight:900;letter-spacing:.035em;color:#172033;margin:0 0 9px;display:flex;align-items:center;gap:7px;}
.qvp-settings-card .qvp-card-sub{font-size:.72rem;color:#64748b;margin:-5px 0 9px;}
.qvp-settings-card .qvp-section-title{margin-bottom:8px!important;}
.qvp-settings-card .qvp-content-box{margin-top:0!important;}
.qvp-preview-column{position:sticky;top:1rem;align-self:flex-start;z-index:30;}
[data-testid="column"]:has(.qvp-preview-anchor){position:sticky!important;top:1rem!important;align-self:flex-start!important;z-index:40!important;min-width:0!important;}

.qvp-preview-column > div{width:100%;}
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
.qvp-preview-column button[kind="primary"]{background:linear-gradient(135deg,#6d4aff,#3b82f6)!important;color:#fff!important;border-color:#5b45d6!important;}
.qvp-main-grid [data-testid="stHorizontalBlock"]{align-items:flex-start!important;}
.qvp-main-grid{margin-top:4px!important;}
.qvp-main-grid .qvp-editor-wrap{margin-bottom:0!important;}
.qvp-main-grid .qvp-settings-card:last-child{margin-bottom:0!important;}

/* V25 — contraste + hiérarchie */
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

# (Le reste du script demeure inchangé...)
