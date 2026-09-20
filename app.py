import asyncio
import os
import re
import json
import math
import wave
import struct
import subprocess
import tempfile

import edge_tts
import imageio_ffmpeg

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# CONFIGURATION
# ============================================================

WIDTH = 1080
HEIGHT = 1920
FPS = 30

THEMES = {
    "Bleu Nuit & Or": {
        "bg": (15, 23, 42),
        "card": (30, 41, 59),
        "accent": (250, 204, 21),
        "accent2": (59, 130, 246),
    },

    "Chocolat Noir & Or": {
        "bg": (28, 18, 12),
        "card": (54, 38, 28),
        "accent": (245, 158, 11),
        "accent2": (180, 83, 9),
    },

    "Violet & Neon Pink": {
        "bg": (24, 15, 38),
        "card": (48, 30, 74),
        "accent": (236, 72, 153),
        "accent2": (168, 85, 247),
    },

    "Émeraude & Mint": {
        "bg": (6, 28, 20),
        "card": (15, 52, 38),
        "accent": (52, 211, 153),
        "accent2": (16, 185, 129),
    },
}


# ============================================================
# UTILITAIRES
# ============================================================

def ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()


def get_font(size):
    candidates = [
        "Roboto-Bold.ttf",
        "DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    for filename in candidates:
        if os.path.exists(filename):
            try:
                return ImageFont.truetype(filename, size)
            except Exception:
                pass

    return ImageFont.load_default()


def clean_text(text):
    if text is None:
        return ""

    text = str(text)

    text = text.replace("🧠", "")
    text = text.replace("💡", "")
    text = text.replace("🔥", "")
    text = text.replace("⏱️", "")
    text = text.replace("⏳", "")
    text = text.replace("💬", "")
    text = text.replace("📌", "")
    text = text.replace("✨", "")

    text = re.sub(r"(\d+)/(\d+)", r"\1 sur \2", text)

    text = re.sub(
        r"[^\w\s,.?!:;'\-À-ÿ]",
        "",
        text,
        flags=re.UNICODE
    )

    return re.sub(r"\s+", " ", text).strip()


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, font, max_width):
    words = text.split()

    lines = []
    current = ""

    for word in words:
        candidate = word if not current else current + " " + word

        if text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def fit_background(bg_file):
    if not bg_file:
        return None

    img = Image.open(bg_file).convert("RGB")

    src_w, src_h = img.size
    target_ratio = WIDTH / HEIGHT
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_h = HEIGHT
        new_w = int(new_h * src_ratio)
    else:
        new_w = WIDTH
        new_h = int(new_w / src_ratio)

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    left = max(0, (new_w - WIDTH) // 2)
    top = max(0, (new_h - HEIGHT) // 2)

    return img.crop(
        (left, top, left + WIDTH, top + HEIGHT)
    )


def base_image(theme_name, bg_file=None):
    theme = THEMES.get(theme_name, THEMES["Bleu Nuit & Or"])

    if bg_file:
        try:
            img = fit_background(bg_file)
            if img:
                return img
        except Exception:
            pass

    return Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme["bg"]
    )


# ============================================================
# EDGE TTS + WORD TIMINGS
# ============================================================

async def generate_tts_with_timings_async(
    text,
    voice,
    output_audio,
    rate="+15%",
    pitch="+0Hz"
):
    """
    Génère le MP3 ET récupère les WordBoundary d'Edge TTS.

    Retourne :

    [
        {
            "word": "Bonjour",
            "start": 0.0,
            "end": 0.42
        },
        ...
    ]
    """

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=rate,
        pitch=pitch
    )

    word_timings = []

    with open(output_audio, "wb") as audio_file:

        async for chunk in communicate.stream():

            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])

            elif chunk["type"] == "WordBoundary":

                offset = chunk.get("offset", 0)
                duration = chunk.get("duration", 0)

                start = offset / 10_000_000
                end = (offset + duration) / 10_000_000

                word = chunk.get("text", "").strip()

                if word:
                    word_timings.append({
                        "word": word,
                        "start": start,
                        "end": end
                    })

    # Certains retours Edge TTS peuvent contenir des timings
    # très proches les uns des autres.
    # On les nettoie.
    cleaned = []

    for item in word_timings:

        if not cleaned:
            cleaned.append(item)
            continue

        previous = cleaned[-1]

        if item["start"] < previous["start"]:
            continue

        cleaned.append(item)

    return cleaned


def generate_tts_with_timings(
    text,
    voice,
    output_audio,
    rate="+15%",
    pitch="+0Hz"
):
    return asyncio.run(
        generate_tts_with_timings_async(
            text,
            voice,
            output_audio,
            rate,
            pitch
        )
    )


# ============================================================
# DUREE AUDIO
# ============================================================

def audio_duration(path):
    cmd = [
        ffmpeg(),
        "-i",
        path
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    match = re.search(
        r"Duration:\s*(\d+):(\d+):(\d+\.\d+)",
        result.stderr
    )

    if not match:
        return 1.0

    h, m, s = match.groups()

    return (
        int(h) * 3600
        + int(m) * 60
        + float(s)
    )


# ============================================================
# SFX
# ============================================================

def create_sfx(tmpdir):

    tic = os.path.join(tmpdir, "tic.wav")
    ding = os.path.join(tmpdir, "ding.wav")

    # TIC
    with wave.open(tic, "w") as f:

        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(44100)

        duration = 0.13

        for i in range(int(44100 * duration)):

            t = i / 44100

            envelope = math.exp(-t * 30)

            value = int(
                12000
                * math.sin(2 * math.pi * 1100 * t)
                * envelope
            )

            f.writeframes(
                struct.pack("<h", value)
            )

    # DING
    with wave.open(ding, "w") as f:

        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(44100)

        duration = 0.65

        for i in range(int(44100 * duration)):

            t = i / 44100

            envelope = math.exp(-t * 5)

            value = int(
                13000
                * (
                    math.sin(2 * math.pi * 1318 * t)
                    + 0.7 * math.sin(2 * math.pi * 1760 * t)
                )
                * envelope
            )

            value = max(-32767, min(32767, value))

            f.writeframes(
                struct.pack("<h", value)
            )

    return tic, ding


# ============================================================
# RENDU TEXTE MOT PAR MOT
# ============================================================

def draw_word_sync_frame(
    text,
    timings,
    current_index,
    theme_name,
    channel_tag,
    bg_file=None,
    title=None,
    subtitle=None,
    animation_progress=1.0
):

    theme = THEMES.get(
        theme_name,
        THEMES["Bleu Nuit & Or"]
    )

    img = base_image(theme_name, bg_file)
    draw = ImageDraw.Draw(img)

    # voile sombre pour améliorer la lisibilité
    overlay = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 90)
    )

    img = Image.alpha_composite(
        img.convert("RGBA"),
        overlay
    )

    draw = ImageDraw.Draw(img)

    # --------------------------------------------------------
    # PETIT HEADER
    # --------------------------------------------------------

    if title:

        f_title = get_font(42)

        tw = text_width(
            draw,
            title,
            f_title
        )

        draw.text(
            ((WIDTH - tw) / 2, 105),
            title,
            font=f_title,
            fill=theme["accent"]
        )

    # --------------------------------------------------------
    # TEXTE
    # --------------------------------------------------------

    words = [
        item["word"]
        for item in timings
    ]

    if not words:
        words = text.split()

    visible = words[:current_index + 1]

    f_word = get_font(76)

    # largeur maximum
    max_width = 900

    # On construit des lignes.
    lines = []
    current_line = []

    for word in visible:

        candidate = " ".join(
            current_line + [word]
        )

        if text_width(
            draw,
            candidate,
            f_word
        ) <= max_width:

            current_line.append(word)

        else:

            if current_line:
                lines.append(current_line)

            current_line = [word]

    if current_line:
        lines.append(current_line)

    line_height = 105

    total_height = len(lines) * line_height

    y = 730 - total_height / 2

    counter = 0

    for line in lines:

        line_text = " ".join(line)

        line_width = text_width(
            draw,
            line_text,
            f_word
        )

        x = (WIDTH - line_width) / 2

        for word in line:

            word_w = text_width(
                draw,
                word,
                f_word
            )

            is_current = counter == current_index

            if is_current:

                color = theme["accent"]

                # petite animation
                scale = 1.0 + (
                    0.08 * animation_progress
                )

                # ombre
                draw.text(
                    (
                        x + 6,
                        y + 6
                    ),
                    word,
                    font=f_word,
                    fill=(0, 0, 0, 220)
                )

                draw.text(
                    (x, y),
                    word,
                    font=f_word,
                    fill=color
                )

            else:

                draw.text(
                    (
                        x + 4,
                        y + 4
                    ),
                    word,
                    font=f_word,
                    fill=(0, 0, 0, 220)
                )

                draw.text(
                    (x, y),
                    word,
                    font=f_word,
                    fill="white"
                )

            # espace
            space_width = text_width(
                draw,
                " ",
                f_word
            )

            x += word_w + space_width
            counter += 1

        y += line_height

    # --------------------------------------------------------
    # BARRE DE PROGRESSION
    # --------------------------------------------------------

    if timings and current_index >= 0:

        progress = (
            (current_index + 1)
            / len(timings)
        )

        bar_x = 90
        bar_y = 1510
        bar_w = 900
        bar_h = 12

        draw.rounded_rectangle(
            [
                (bar_x, bar_y),
                (bar_x + bar_w, bar_y + bar_h)
            ],
            radius=6,
            fill=(80, 80, 80)
        )

        draw.rounded_rectangle(
            [
                (bar_x, bar_y),
                (
                    bar_x
                    + int(bar_w * progress),
                    bar_y + bar_h
                )
            ],
            radius=6,
            fill=theme["accent"]
        )

    # --------------------------------------------------------
    # SOUS TITRE
    # --------------------------------------------------------

    if subtitle:

        f_sub = get_font(38)

        lines_sub = wrap_text(
            draw,
            subtitle,
            f_sub,
            850
        )

        yy = 1590

        for line in lines_sub[:2]:

            ww = text_width(
                draw,
                line,
                f_sub
            )

            draw.text(
                ((WIDTH - ww) / 2, yy),
                line,
                font=f_sub,
                fill=(220, 220, 220)
            )

            yy += 50

    # --------------------------------------------------------
    # SIGNATURE
    # --------------------------------------------------------

    if channel_tag:

        f_tag = get_font(32)

        tw = text_width(
            draw,
            channel_tag,
            f_tag
        )

        draw.text(
            (
                (WIDTH - tw) / 2,
                1800
            ),
            channel_tag,
            font=f_tag,
            fill=(190, 190, 190)
        )

    return img.convert("RGB")


# ============================================================
# CREATION DES FRAMES SYNCHRONISEES
# ============================================================

def create_word_timeline_frames(
    text,
    timings,
    theme_name,
    channel_tag,
    output_dir,
    bg_file=None,
    title=None,
    subtitle=None
):

    os.makedirs(output_dir, exist_ok=True)

    frames = []

    if not timings:

        img = draw_word_sync_frame(
            text,
            [],
            0,
            theme_name,
            channel_tag,
            bg_file,
            title,
            subtitle
        )

        path = os.path.join(
            output_dir,
            "frame_0000.png"
        )

        img.save(path)

        return [
            {
                "path": path,
                "duration": 2.0
            }
        ]

    for i, item in enumerate(timings):

        start = item["start"]
        end = item["end"]

        duration = max(
            0.06,
            end - start
        )

        # ----------------------------------------------------
        # Petit effet POP au début de chaque mot
        # ----------------------------------------------------

        pop_duration = min(
            0.09,
            duration
        )

        frame1 = draw_word_sync_frame(
            text,
            timings,
            i,
            theme_name,
            channel_tag,
            bg_file,
            title,
            subtitle,
            animation_progress=1.0
        )

        path1 = os.path.join(
            output_dir,
            f"frame_{i:04d}_pop.png"
        )

        frame1.save(path1)

        frames.append({
            "path": path1,
            "duration": pop_duration
        })

        # reste du mot
        remaining = duration - pop_duration

        if remaining > 0.01:

            frame2 = draw_word_sync_frame(
                text,
                timings,
                i,
                theme_name,
                channel_tag,
                bg_file,
                title,
                subtitle,
                animation_progress=0.0
            )

            path2 = os.path.join(
                output_dir,
                f"frame_{i:04d}.png"
            )

            frame2.save(path2)

            frames.append({
                "path": path2,
                "duration": remaining
            })

    return frames


# ============================================================
# VIDEO A PARTIR D'UNE TIMELINE D'IMAGES
# ============================================================

def create_video_from_timeline(
    frames,
    audio_path,
    output_path,
    volume=1.25
):

    workdir = os.path.dirname(
        os.path.abspath(output_path)
    )

    concat_file = os.path.join(
        workdir,
        "timeline.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:

        for frame in frames:

            path = os.path.abspath(
                frame["path"]
            ).replace("\\", "/")

            f.write(
                f"file '{path}'\n"
            )

            f.write(
                f"duration {frame['duration']:.4f}\n"
            )

        # concat exige que la dernière image
        # soit répétée
        if frames:

            last = os.path.abspath(
                frames[-1]["path"]
            ).replace("\\", "/")

            f.write(
                f"file '{last}'\n"
            )

    cmd = [
        ffmpeg(),
        "-y",

        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,

        "-i", audio_path,

        "-filter_complex",
        f"[1:a]volume={volume}[a]",

        "-map", "0:v",
        "-map", "[a]",

        "-r", str(FPS),

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",

        "-c:a", "aac",
        "-b:a", "192k",

        "-pix_fmt", "yuv420p",

        "-shortest",

        "-movflags",
        "+faststart",

        output_path
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )


# ============================================================
# SEGMENT MOT PAR MOT
# ============================================================

def build_word_sync_video(
    text,
    voice,
    tmpdir,
    filename,
    theme_name,
    channel_tag,
    bg_file=None,
    title=None,
    subtitle=None,
    rate="+15%",
    volume=1.25
):

    audio_path = os.path.join(
        tmpdir,
        filename + ".mp3"
    )

    output_path = os.path.join(
        tmpdir,
        filename + ".mp4"
    )

    timings = generate_tts_with_timings(
        clean_text(text),
        voice,
        audio_path,
        rate=rate
    )

    frame_dir = os.path.join(
        tmpdir,
        filename + "_frames"
    )

    frames = create_word_timeline_frames(
        text,
        timings,
        theme_name,
        channel_tag,
        frame_dir,
        bg_file,
        title,
        subtitle
    )

    create_video_from_timeline(
        frames,
        audio_path,
        output_path,
        volume
    )

    return output_path, timings


# ============================================================
# VIDEO SIMPLE IMAGE + AUDIO
# ============================================================

def create_static_video(
    image,
    audio_path,
    output_path,
    duration=None,
    volume=1.25
):

    image_path = output_path + "_image.png"

    image.save(image_path)

    if duration is None:
        duration = audio_duration(
            audio_path
        )

    cmd = [
        ffmpeg(),
        "-y",

        "-loop", "1",
        "-i", image_path,

        "-i", audio_path,

        "-map", "0:v",
        "-map", "1:a",

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",

        "-r", str(FPS),

        "-c:a", "aac",
        "-b:a", "192k",

        "-pix_fmt", "yuv420p",

        "-t", str(duration),

        "-shortest",

        "-movflags",
        "+faststart",

        output_path
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )


# ============================================================
# CONCATENATION
# ============================================================

def concatenate_videos(
    videos,
    output_path,
    tmpdir
):

    list_file = os.path.join(
        tmpdir,
        "videos.txt"
    )

    with open(
        list_file,
        "w",
        encoding="utf-8"
    ) as f:

        for video in videos:

            path = os.path.abspath(
                video
            ).replace("\\", "/")

            f.write(
                f"file '{path}'\n"
            )

    # On réencode pour garantir
    # même format / même FPS / même résolution.

    cmd = [
        ffmpeg(),
        "-y",

        "-f", "concat",
        "-safe", "0",

        "-i", list_file,

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",

        "-r", str(FPS),

        "-c:a", "aac",
        "-b:a", "192k",

        "-pix_fmt", "yuv420p",

        "-movflags",
        "+faststart",

        output_path
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )


# ============================================================
# FRAME QUIZ
# ============================================================

def draw_quiz_frame(
    question,
    options,
    visible_options,
    correct_index,
    phase,
    timer,
    q_num,
    total_q,
    theme_name,
    channel_tag,
    bg_file=None
):

    theme = THEMES.get(
        theme_name,
        THEMES["Bleu Nuit & Or"]
    )

    img = base_image(
        theme_name,
        bg_file
    ).convert("RGBA")

    overlay = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 75)
    )

    img = Image.alpha_composite(
        img,
        overlay
    )

    draw = ImageDraw.Draw(img)

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    f_head = get_font(42)

    header = f"QUIZ  •  {q_num}/{total_q}"

    tw = text_width(
        draw,
        header,
        f_head
    )

    draw.text(
        ((WIDTH - tw) / 2, 100),
        header,
        font=f_head,
        fill=theme["accent"]
    )

    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    f_q = get_font(58)

    question = clean_text(question)

    q_lines = wrap_text(
        draw,
        question,
        f_q,
        850
    )

    y = 280

    for line in q_lines[:4]:

        tw = text_width(
            draw,
            line,
            f_q
        )

        draw.text(
            (
                (WIDTH - tw) / 2 + 4,
                y + 4
            ),
            line,
            font=f_q,
            fill=(0, 0, 0)
        )

        draw.text(
            (
                (WIDTH - tw) / 2,
                y
            ),
            line,
            font=f_q,
            fill="white"
        )

        y += 78

    # --------------------------------------------------------
    # OPTIONS
    # --------------------------------------------------------

    f_opt = get_font(43)

    start_y = max(
        620,
        y + 70
    )

    card_h = 125
    gap = 25

    for i, option in enumerate(options):

        if i > visible_options:
            continue

        yy = start_y + i * (card_h + gap)

        is_correct = (
            phase == "reveal"
            and i == correct_index
        )

        if is_correct:

            fill = (34, 197, 94)
            outline = (74, 222, 128)

        else:

            fill = theme["card"]
            outline = (
                theme["accent"]
                if i == visible_options
                else (90, 90, 100)
            )

        draw.rounded_rectangle(
            [
                (70, yy),
                (1010, yy + card_h)
            ],
            radius=30,
            fill=fill,
            outline=outline,
            width=4
        )

        label = chr(65 + i)

        label_font = get_font(45)

        draw.text(
            (110, yy + 37),
            label,
            font=label_font,
            fill=theme["accent"]
            if not is_correct
            else "white"
        )

        opt = clean_text(option)

        lines = wrap_text(
            draw,
            opt,
            f_opt,
            760
        )

        text_y = yy + 35

        for line in lines[:2]:

            draw.text(
                (190, text_y),
                line,
                font=f_opt,
                fill="white"
            )

            text_y += 48

    # --------------------------------------------------------
    # TIMER
    # --------------------------------------------------------

    if phase == "timer":

        color = (
            (34, 197, 94)
            if timer >= 4
            else
            (245, 158, 11)
            if timer >= 2
            else
            (239, 68, 68)
        )

        radius = 105

        cx = WIDTH // 2
        cy = 1510

        draw.ellipse(
            [
                (
                    cx - radius,
                    cy - radius
                ),
                (
                    cx + radius,
                    cy + radius
                )
            ],
            fill=(15, 23, 42),
            outline=color,
            width=10
        )

        f_timer = get_font(72)

        timer_text = str(timer)

        tw = text_width(
            draw,
            timer_text,
            f_timer
        )

        draw.text(
            (
                cx - tw / 2,
                cy - 45
            ),
            timer_text,
            font=f_timer,
            fill=color
        )

    # --------------------------------------------------------
    # REVEAL
    # --------------------------------------------------------

    if phase == "reveal":

        message = "✓ BONNE RÉPONSE"

        f = get_font(48)

        tw = text_width(
            draw,
            message,
            f
        )

        draw.rounded_rectangle(
            [
                (190, 1480),
                (890, 1595)
            ],
            radius=45,
            fill=(34, 197, 94)
        )

        draw.text(
            (
                (WIDTH - tw) / 2,
                1510
            ),
            message,
            font=f,
            fill="white"
        )

    # --------------------------------------------------------
    # SIGNATURE
    # --------------------------------------------------------

    f_tag = get_font(30)

    tw = text_width(
        draw,
        channel_tag,
        f_tag
    )

    draw.text(
        (
            (WIDTH - tw) / 2,
            1800
        ),
        channel_tag,
        font=f_tag,
        fill=(190, 190, 190)
    )

    return img.convert("RGB")


# ============================================================
# QUIZ : CREATION DES ETAPES
# ============================================================

def build_quiz_video(
    questions,
    hook,
    outro,
    voice,
    theme_name,
    channel_tag,
    motiv_list,
    tmpdir,
    bg_file=None,
    rate="+15%",
    volume=1.25,
    timer_seconds=3
):

    videos = []

    # --------------------------------------------------------
    # HOOK
    # --------------------------------------------------------

    hook_video, _ = build_word_sync_video(
        hook,
        voice,
        tmpdir,
        "hook",
        theme_name,
        channel_tag,
        bg_file,
        title="⚡ ATTENTION",
        rate=rate,
        volume=volume
    )

    videos.append(hook_video)

    # --------------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------------

    total = len(questions)

    for qi, q in enumerate(questions):

        q_prefix = f"q_{qi}"

        # -----------------------------------------------
        # QUESTION
        # -----------------------------------------------

        question_text = (
            f"Question {qi + 1}. "
            f"{q['question']}"
        )

        q_video, _ = build_word_sync_video(
            question_text,
            voice,
            tmpdir,
            q_prefix + "_question",
            theme_name,
            channel_tag,
            bg_file,
            title=f"QUIZ {qi + 1}/{total}",
            rate=rate,
            volume=volume
        )

        videos.append(q_video)

        # -----------------------------------------------
        # OPTIONS
        # -----------------------------------------------

        for oi in range(4):

            option_text = (
                f"Option {chr(65 + oi)}. "
                f"{q['options'][oi]}"
            )

            opt_video, _ = build_word_sync_video(
                option_text,
                voice,
                tmpdir,
                f"{q_prefix}_option_{oi}",
                theme_name,
                channel_tag,
                bg_file,
                title=f"OPTION {chr(65 + oi)}",
                rate="+20%",
                volume=volume
            )

            videos.append(opt_video)

        # -----------------------------------------------
        # TIMER
        # -----------------------------------------------

        tic, ding = create_sfx(tmpdir)

        for sec in range(
            timer_seconds,
            0,
            -1
        ):

            img = draw_quiz_frame(
                q["question"],
                q["options"],
                3,
                get_correct_index(
                    q["reponse_correcte"],
                    q["options"]
                ),
                "timer",
                sec,
                qi + 1,
                total,
                theme_name,
                channel_tag,
                bg_file
            )

            audio = tic

            video_path = os.path.join(
                tmpdir,
                f"{q_prefix}_timer_{sec}.mp4"
            )

            create_static_video(
                img,
                audio,
                video_path,
                duration=1.0,
                volume=1.0
            )

            videos.append(video_path)

        # -----------------------------------------------
        # REVEAL
        # -----------------------------------------------

        correct_index = get_correct_index(
            q["reponse_correcte"],
            q["options"]
        )

        reveal_img = draw_quiz_frame(
            q["question"],
            q["options"],
            3,
            correct_index,
            "reveal",
            0,
            qi + 1,
            total,
            theme_name,
            channel_tag,
            bg_file
        )

        reveal_path = os.path.join(
            tmpdir,
            f"{q_prefix}_reveal.mp4"
        )

        create_static_video(
            reveal_img,
            ding,
            reveal_path,
            duration=0.75,
            volume=1.0
        )

        videos.append(reveal_path)

        # -----------------------------------------------
        # EXPLICATION
        # -----------------------------------------------

        motivation = (
            motiv_list[qi % len(motiv_list)]
            if motiv_list
            else "Bravo !"
        )

        correct_letter = chr(
            65 + correct_index
        )

        explanation = (
            f"La bonne réponse est "
            f"l'option {correct_letter}. "
            f"{q['options'][correct_index]}. "
            f"{q.get('explication', '')}. "
            f"{motivation}"
        )

        exp_video, _ = build_word_sync_video(
            explanation,
            voice,
            tmpdir,
            q_prefix + "_explanation",
            theme_name,
            channel_tag,
            bg_file,
            title="✓ RÉPONSE",
            rate="+12%",
            volume=volume
        )

        videos.append(exp_video)

    # --------------------------------------------------------
    # OUTRO
    # --------------------------------------------------------

    outro_video, _ = build_word_sync_video(
        outro,
        voice,
        tmpdir,
        "outro",
        theme_name,
        channel_tag,
        bg_file,
        title="🔥 À TOI DE JOUER",
        rate=rate,
        volume=volume
    )

    videos.append(outro_video)

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    final_path = os.path.join(
        tmpdir,
        "quiz_final.mp4"
    )

    concatenate_videos(
        videos,
        final_path,
        tmpdir
    )

    return final_path


# ============================================================
# LANGUES
# ============================================================

def get_correct_index(answer, options):

    answer = str(answer).strip().upper()

    if answer.startswith("A") or answer == "1":
        return 0

    if answer.startswith("B") or answer == "2":
        return 1

    if answer.startswith("C") or answer == "3":
        return 2

    if answer.startswith("D") or answer == "4":
        return 3

    for i, option in enumerate(options):

        if str(option).lower() in answer.lower():
            return i

    return 0


def build_language_video(
    words,
    hook,
    outro,
    target_voice,
    target_language,
    theme_name,
    channel_tag,
    motiv_list,
    tmpdir,
    bg_file=None,
    rate="+12%",
