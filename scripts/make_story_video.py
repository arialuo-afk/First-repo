from pathlib import Path
import textwrap
import subprocess
import wave

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/aria.luo/Desktop/Aira Testing/AI 漫剧")
SOURCE = Path("/Users/aria.luo/Downloads/Gemini_Generated_Image_khendnkhendnkhen.png")
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_ONLY_OUTPUT = OUT_DIR / "yin_forest_storyboard_video_only.mp4"
FINAL_OUTPUT = OUT_DIR / "yin_forest_storyboard_with_music.mp4"
AUDIO_OUTPUT = OUT_DIR / "yin_forest_storyboard_bgm.wav"

FPS = 12
VIDEO_SIZE = (1280, 720)
SAMPLE_RATE = 44100

# Crops tuned for the provided 1408x768 storyboard image.
SCENES = [
    {
        "name": "片头总览",
        "timecode": "Story Preview",
        "duration": 3,
        "crop": (0, 0, 1408, 768),
        "subtitle": "阴森林海，乌云压顶。一场荒野中的父女初见，即将揭开序幕。",
    },
    {
        "name": "镜头 1",
        "timecode": "00:00 - 00:05",
        "duration": 5,
        "crop": (18, 114, 327, 357),
        "subtitle": "哈哈大笑声震彻山林。妖娆刚一睁眼，就撞见一张比噩梦还可怕的脸。",
    },
    {
        "name": "镜头 2",
        "timecode": "00:05 - 00:15",
        "duration": 10,
        "crop": (338, 112, 640, 357),
        "subtitle": "这里不是温暖卧室，而是万兽低吼的荒野。林海深处，成片兽眼在黑暗里幽幽发亮。",
    },
    {
        "name": "镜头 3",
        "timecode": "00:15 - 00:25",
        "duration": 10,
        "crop": (675, 112, 976, 357),
        "subtitle": "那双苍绿色的眼睛，像盯住猎物般兴奋。妖娆心里一炸：这男人，简直就是魔鬼。",
    },
    {
        "name": "镜头 4",
        "timecode": "00:25 - 00:35",
        "duration": 10,
        "crop": (1013, 110, 1361, 357),
        "subtitle": "男人高举新生女婴，狂笑着宣告她是自己的女儿。下一瞬，乌云裂开，万丈阳光与百鸟齐鸣一同降临。",
    },
    {
        "name": "镜头 5",
        "timecode": "00:35 - 00:45",
        "duration": 10,
        "crop": (18, 440, 468, 730),
        "subtitle": "可变故突生，他的眼神骤然冰冷。指尖灭魔之光凝聚，死亡的气息瞬间逼近。",
    },
    {
        "name": "镜头 6",
        "timecode": "00:45 - 00:55",
        "duration": 10,
        "crop": (494, 440, 940, 730),
        "subtitle": "男人忽然抱头发狂，拼命捶地。妖娆趁机扭着小身子，在泥水里拼命往远处爬去。",
    },
    {
        "name": "镜头 7",
        "timecode": "00:55 - 01:05",
        "duration": 10,
        "crop": (962, 440, 1364, 730),
        "subtitle": "白光终于散去，他重新抱起像小泥猴一样的妖娆，笑着认回自己的女儿。荒野尽头，也终于有了一丝温柔。",
    },
]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    choices = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    for choice in choices:
        path = Path(choice)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_TITLE = load_font(32, bold=True)
FONT_TEXT = load_font(28)
FONT_SMALL = load_font(22)
FONT_DIALOG = load_font(26, bold=True)


def ease_in_out(t: float) -> float:
    return 3 * t * t - 2 * t * t * t


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def fit_crop(base: Image.Image, frame_size: tuple[int, int], zoom: float, pan_x: float, pan_y: float) -> Image.Image:
    fw, fh = frame_size
    target_ratio = fw / fh
    bw, bh = base.size

    crop_w = int(bw / zoom)
    crop_h = int(bh / zoom)

    if crop_w / crop_h > target_ratio:
        crop_w = int(crop_h * target_ratio)
    else:
        crop_h = int(crop_w / target_ratio)

    max_x = max(0, bw - crop_w)
    max_y = max(0, bh - crop_h)
    x = int(max_x * pan_x)
    y = int(max_y * pan_y)

    frame = base.crop((x, y, x + crop_w, y + crop_h))
    return frame.resize(frame_size, Image.LANCZOS)


def draw_subtitle(draw: ImageDraw.ImageDraw, subtitle: str, width: int, height: int) -> None:
    lines = textwrap.wrap(subtitle, width=22)
    padding = 18
    line_gap = 8

    boxes = []
    total_h = 0
    max_w = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=FONT_TEXT)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        boxes.append((line, w, h))
        total_h += h
        max_w = max(max_w, w)
    total_h += line_gap * (len(lines) - 1)

    box_x0 = (width - max_w) // 2 - padding
    box_y0 = height - total_h - 70
    box_x1 = (width + max_w) // 2 + padding
    box_y1 = height - 36

    draw.rounded_rectangle((box_x0, box_y0, box_x1, box_y1), radius=18, fill=(0, 0, 0, 128))

    y = box_y0 + padding - 2
    for line, w, h in boxes:
        x = (width - w) // 2
        draw.text((x + 1, y + 1), line, font=FONT_TEXT, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=FONT_TEXT, fill=(255, 248, 238))
        y += h + line_gap


def annotate(frame: Image.Image, scene: dict) -> Image.Image:
    annotated = frame.convert("RGBA")
    overlay = Image.new("RGBA", annotated.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = annotated.size

    draw.rounded_rectangle((24, 22, 320, 112), radius=18, fill=(18, 20, 27, 170))
    draw.text((42, 36), scene["name"], font=FONT_TITLE, fill=(255, 244, 225))
    draw.text((44, 78), scene["timecode"], font=FONT_SMALL, fill=(235, 224, 204))

    if scene["name"] != "片头总览":
        dialog = "旁白"
        dialog_bbox = draw.textbbox((0, 0), dialog, font=FONT_DIALOG)
        dialog_w = dialog_bbox[2] - dialog_bbox[0]
        draw.rounded_rectangle((1030, 30, 1068 + dialog_w, 82), radius=16, fill=(214, 129, 84, 210))
        draw.text((1048, 42), dialog, font=FONT_DIALOG, fill=(255, 247, 240))

    draw_subtitle(draw, scene["subtitle"], width, height)
    return Image.alpha_composite(annotated, overlay).convert("RGB")


def make_background(crop: Image.Image) -> Image.Image:
    bg = crop.resize(VIDEO_SIZE, Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=22))
    veil = Image.new("RGBA", VIDEO_SIZE, (25, 18, 15, 90))
    vignette = Image.new("L", VIDEO_SIZE, 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse((-140, -60, VIDEO_SIZE[0] + 140, VIDEO_SIZE[1] + 120), fill=225)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=110))
    vignette_rgb = Image.merge("RGBA", (vignette, vignette, vignette, vignette))
    toned = Image.alpha_composite(bg.convert("RGBA"), veil)
    return Image.composite(toned, Image.new("RGBA", VIDEO_SIZE, (8, 8, 12, 220)), vignette).convert("RGB")


def scene_waveform(total_samples: int, duration: float, base_freq: float, pulse_strength: float) -> np.ndarray:
    t = np.linspace(0, duration, total_samples, endpoint=False)
    slow = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t - np.pi / 2)
    pad = 0.44 * np.sin(2 * np.pi * base_freq * t)
    pad += 0.22 * np.sin(2 * np.pi * base_freq * 2.0 * t + 0.3)
    pad += 0.14 * np.sin(2 * np.pi * base_freq * 3.0 * t + 0.6)

    bell = np.sin(2 * np.pi * (base_freq * 4.0) * t) * np.maximum(0.0, np.sin(2 * np.pi * pulse_strength * t))
    bell *= 0.10

    shimmer = np.sin(2 * np.pi * (base_freq * 0.5) * t + 1.1) * 0.08
    return (pad * (0.45 + 0.25 * slow)) + bell + shimmer


def build_music_track() -> np.ndarray:
    note_map = {
        "A3": 220.00,
        "C4": 261.63,
        "D4": 293.66,
        "E4": 329.63,
        "G3": 196.00,
        "F3": 174.61,
    }
    scene_notes = ["A3", "F3", "D4", "C4", "E4", "G3", "A3", "C4"]
    pieces = []
    rng = np.random.default_rng(7)

    for idx, scene in enumerate(SCENES):
        duration = scene["duration"]
        total_samples = int(duration * SAMPLE_RATE)
        base = scene_waveform(total_samples, duration, note_map[scene_notes[idx]], pulse_strength=0.18 + idx * 0.01)
        t = np.linspace(0, duration, total_samples, endpoint=False)

        envelope = np.minimum(1.0, t / 1.2) * np.minimum(1.0, (duration - t) / 1.4)
        envelope = np.clip(envelope, 0.0, 1.0)

        if idx in (0, 1, 2):
            mood = 0.55
        elif idx in (3, 7):
            mood = 0.72
        elif idx in (4, 5):
            mood = 0.65
        else:
            mood = 0.60

        noise = rng.normal(0.0, 0.02, total_samples)
        noise = np.convolve(noise, np.ones(220) / 220, mode="same")
        piece = (base + noise) * envelope * mood
        pieces.append(piece)

    audio = np.concatenate(pieces)
    audio /= max(1e-6, np.max(np.abs(audio)))
    return (audio * 0.42).astype(np.float32)


def write_wav(samples: np.ndarray, path: Path) -> None:
    pcm = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    stereo = np.column_stack([pcm, pcm])
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(stereo.tobytes())


def mux_video_and_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def render_scene(writer, crop: Image.Image, scene: dict) -> None:
    frames = scene["duration"] * FPS
    background = make_background(crop)

    for idx in range(frames):
        t = idx / max(1, frames - 1)
        eased = ease_in_out(t)
        zoom = 1.0 + 0.05 * eased + 0.03 * np.sin(np.pi * t)
        pan_x = clamp(0.45 + 0.10 * (eased - 0.5), 0.0, 1.0)
        pan_y = clamp(0.48 - 0.06 * (eased - 0.5), 0.0, 1.0)

        frame = background.copy()
        foreground = fit_crop(crop, (1120, 630), zoom=zoom, pan_x=pan_x, pan_y=pan_y)
        framed = Image.new("RGBA", VIDEO_SIZE, (0, 0, 0, 0))
        fg = foreground.convert("RGBA")
        shadow = Image.new("RGBA", (1148, 658), (0, 0, 0, 70)).filter(ImageFilter.GaussianBlur(8))
        framed.alpha_composite(shadow, (66, 28))
        framed.alpha_composite(fg, (80, 35))
        composed = Image.blend(frame.convert("RGBA"), framed, 1.0).convert("RGB")
        composed = annotate(composed, scene)
        writer.append_data(np.array(composed))


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")
    with imageio.get_writer(
        VIDEO_ONLY_OUTPUT,
        fps=FPS,
        codec="libx264",
        quality=6,
        macro_block_size=None,
        output_params=["-preset", "veryfast", "-movflags", "+faststart"],
    ) as writer:
        for scene in SCENES:
            crop = source.crop(scene["crop"])
            render_scene(writer, crop, scene)
    music = build_music_track()
    write_wav(music, AUDIO_OUTPUT)
    mux_video_and_audio(VIDEO_ONLY_OUTPUT, AUDIO_OUTPUT, FINAL_OUTPUT)
    print(FINAL_OUTPUT)


if __name__ == "__main__":
    main()
