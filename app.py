1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
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
import hashlib
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

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at 10% 0%, #18243d 0%, #0a0e18 38%, #06080d 100%); color:#f4f7fb; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0c111c,#080b12); }
label, [data-testid="stMarkdownContainer"] { color:#edf2f8; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 4rem; }
h1, h2, h3 { letter-spacing: -0.02em; }
[data-testid="stTabs"] button { font-weight: 700; font-size: 1.02rem; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea { border-radius: 14px !important; }
            except Exception as e: st.error(f"Erreur pendant le montage : {e}")
