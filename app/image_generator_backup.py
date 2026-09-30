import os
import re
import time
import hashlib
import random
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PANELS_DIR = os.path.join(STATIC_DIR, "panels")
FONTS_DIR = os.path.join(STATIC_DIR, "fonts")

os.makedirs(PANELS_DIR, exist_ok=True)

HF_API_KEY = os.getenv("HF_API_KEY")
IMAGE_GEN_MODE = os.getenv("IMAGE_GEN_MODE", "auto").lower()

_local_pipe = None


def sanitize_filename(prompt: str) -> str:
    """Creates a clean, safe filename from a prompt."""
    clean_text = re.sub(r'[^a-zA-Z0-9_\- ]', '', prompt[:40]).strip().replace(' ', '_').lower()
    if not clean_text:
        clean_text = "comic_panel"
    hash_suffix = hashlib.md5(prompt.encode('utf-8')).hexdigest()[:6]
    timestamp = int(time.time() * 1000) % 1000000
    return f"{clean_text}_{timestamp}_{hash_suffix}.png"


def _generate_stylized_comic_art(prompt: str, output_path: str, style: str = "comic book") -> str:
    """
    Generates an authentic comic-style illustration using PIL.
    Matches tones, lighting, silhouettes, and typography based on prompt and art style.
    """
    width, height = 768, 512
    style_lower = (style or "comic book").lower()
    prompt_lower = prompt.lower()

    # Determine color palette based on theme & style
    if "noir" in style_lower or "black and white" in prompt_lower:
        bg_color_top = (35, 35, 40)
        bg_color_bot = (10, 10, 15)
        accent_color = (220, 220, 220)
        border_color = (255, 255, 255)
    elif "anime" in style_lower:
        bg_color_top = (120, 180, 240)
        bg_color_bot = (250, 210, 225)
        accent_color = (255, 120, 160)
        border_color = (40, 40, 60)
    elif "realistic" in style_lower:
        bg_color_top = (45, 65, 85)
        bg_color_bot = (20, 35, 45)
        accent_color = (230, 180, 90)
        border_color = (30, 30, 30)
    elif "pixel" in style_lower:
        bg_color_top = (60, 40, 110)
        bg_color_bot = (30, 15, 60)
        accent_color = (0, 230, 180)
        border_color = (255, 255, 255)
    else:  # Classic Comic Book
        bg_color_top = (255, 100, 70)
        bg_color_bot = (255, 210, 60)
        accent_color = (30, 120, 230)
        border_color = (20, 20, 20)

    # Contextual palette overrides
    if "forest" in prompt_lower or "wood" in prompt_lower or "tree" in prompt_lower:
        bg_color_top = (35, 85, 65)
        bg_color_bot = (15, 45, 30)
        accent_color = (245, 170, 65)
    elif "space" in prompt_lower or "futuristic" in prompt_lower or "sci-fi" in prompt_lower:
        bg_color_top = (20, 25, 70)
        bg_color_bot = (5, 5, 25)
        accent_color = (0, 220, 255)

    img = Image.new("RGB", (width, height), bg_color_top)
    draw = ImageDraw.Draw(img)

    # 1. Sky & Atmosphere Gradient
    for y in range(height):
        ratio = y / height
        r = int(bg_color_top[0] * (1 - ratio) + bg_color_bot[0] * ratio)
        g = int(bg_color_top[1] * (1 - ratio) + bg_color_bot[1] * ratio)
        b = int(bg_color_top[2] * (1 - ratio) + bg_color_bot[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    center_x, center_y = width // 2, height // 2
    random.seed(int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 10000)

    # 2. Midground Mountains or Architecture
    horizon_points = [(0, height)]
    num_peaks = 7
    step = width // num_peaks
    for i in range(num_peaks + 1):
        x = i * step
        y = height - random.randint(120, 280)
        horizon_points.append((x, y))
    horizon_points.append((width, height))
    draw.polygon(horizon_points, fill=(int(bg_color_bot[0]*0.7), int(bg_color_bot[1]*0.7), int(bg_color_bot[2]*0.7)))

    # 3. Scenic Trees / Ruin Silhouettes
    for x in range(20, width - 20, 45):
        h_tree = random.randint(140, 260)
        w_tree = random.randint(30, 60)
        base_y = height - 15
        draw.polygon([(x, base_y - h_tree), (x - w_tree//2, base_y), (x + w_tree//2, base_y)], fill=(12, 18, 20))

    # 4. Focal Energy / Sun Burst
    burst_radius = random.randint(70, 110)
    for r_burst in range(burst_radius, 0, -8):
        glow_color = (
            min(255, accent_color[0] + 40),
            min(255, accent_color[1] + 40),
            min(255, accent_color[2] + 40)
        )
        draw.ellipse([center_x - r_burst, center_y - r_burst - 40, center_x + r_burst, center_y + r_burst - 40], outline=glow_color, width=3)

    # 5. Hero Character Silhouette in Foreground
    char_w, char_h = 90, 150
    char_base_y = height - 35
    draw.ellipse([center_x - 22, char_base_y - char_h, center_x + 22, char_base_y - char_h + 45], fill=(10, 10, 15))
    draw.polygon([
        (center_x, char_base_y - char_h + 35),
        (center_x - 45, char_base_y),
        (center_x + 45, char_base_y)
    ], fill=(10, 10, 15))

    # 6. Comic Action Speedlines
    for _ in range(16):
        dist1 = random.randint(110, 190)
        dist2 = random.randint(220, 360)
        sign = random.choice([-1, 1])
        p1 = (center_x + int(dist1 * 1.5 * sign), center_y + int(dist1 * sign))
        p2 = (center_x + int(dist2 * 1.5 * sign), center_y + int(dist2 * sign))
        draw.line([p1, p2], fill=(255, 255, 255), width=random.randint(1, 2))

    # 7. Comic Panel Outer Frame & Borders
    border_thick = 10
    draw.rectangle([0, 0, width, height], outline=border_color, width=border_thick)
    draw.rectangle([border_thick, border_thick, width - border_thick, height - border_thick], outline=(0, 0, 0), width=2)

    # 8. Art Style Badge (Top Left)
    badge_w, badge_h = 160, 36
    draw.rectangle([18, 18, 18 + badge_w, 18 + badge_h], fill=(20, 20, 20), outline=accent_color, width=2)

    font_path = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")
    try:
        font_badge = ImageFont.truetype(font_path, 13)
        font_caption = ImageFont.truetype(font_path, 12)
    except Exception:
        font_badge = ImageFont.load_default()
        font_caption = ImageFont.load_default()

    draw.text((26, 28), f"{style.upper()} STYLE", fill=(255, 255, 255), font=font_badge)

    # 9. Prompt Caption Box (Bottom)
    banner_y = height - 55
    draw.rectangle([18, banner_y, width - 18, height - 18], fill=(15, 15, 15), outline=(200, 200, 200), width=1)
    prompt_snip = prompt if len(prompt) < 70 else prompt[:67] + "..."
    draw.text((28, banner_y + 11), f"SCENE: {prompt_snip}", fill=(240, 240, 240), font=font_caption)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    return output_path


def _generate_with_hf_api(prompt: str, output_path: str) -> bool:
    """Attempts Hugging Face Inference API if HF_API_KEY is available."""
    if not HF_API_KEY or HF_API_KEY == "your_huggingface_api_key_here":
        return False

    try:
        import requests
        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": prompt, "options": {"wait_for_model": True}}
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=45)
        if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"[ComicCraft] HF API response: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ComicCraft] HF API error: {e}")
        return False


def _generate_with_local_diffusers(prompt: str, output_path: str) -> bool:
    """Attempts local Stable Diffusion with PyTorch if available."""
    global _local_pipe
    try:
        import torch
        from diffusers import StableDiffusionPipeline

        if _local_pipe is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_id = "runwayml/stable-diffusion-v1-5"
            print(f"[ComicCraft] Loading local model {model_id} on {device}...")
            if device == "cuda":
                _local_pipe = StableDiffusionPipeline.from_pretrained(
                    model_id, torch_dtype=torch.float16
                ).to("cuda")
            else:
                _local_pipe = StableDiffusionPipeline.from_pretrained(
                    model_id
                ).to("cpu")

        image = _local_pipe(prompt, num_inference_steps=20).images[0]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        return True
    except Exception as e:
        print(f"[ComicCraft] Local diffusers error: {e}")
        return False


def generate_image(prompt: str, filename: str = None, style: str = "comic book") -> str:
    """
    Generates a comic-style image based on prompt and saves to static/panels.

    Args:
        prompt (str): Image generation prompt.
        filename (str, optional): Target filename. Defaults to None.
        style (str, optional): Art style.

    Returns:
        str: Relative web path to the saved image (e.g. static/panels/filename.png)
    """
    if not filename:
        filename = sanitize_filename(prompt)

    full_output_path = os.path.join(PANELS_DIR, filename)

    # 1. Local diffusers if explicitly requested
    if IMAGE_GEN_MODE == "local":
        if _generate_with_local_diffusers(prompt, full_output_path):
            return f"static/panels/{filename}"

    # 2. Hugging Face Inference API if key provided
    if (IMAGE_GEN_MODE in ("api", "auto")) and HF_API_KEY:
        if _generate_with_hf_api(prompt, full_output_path):
            return f"static/panels/{filename}"

    # 3. High quality stylized comic illustration
    _generate_stylized_comic_art(prompt, full_output_path, style=style)
    return f"static/panels/{filename}"
