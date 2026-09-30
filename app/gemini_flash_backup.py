import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Check if google-generativeai is installed
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if HAS_GENAI and GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("models/gemini-1.5-flash")
else:
    model = None


def _get_fallback_outline(user_prompt: str) -> list:
    """Provides a structured 5-panel outline if API key is not configured or fails."""
    # Extract keywords or character hints if present
    character = "Hero"
    if "character" in user_prompt.lower():
        match = re.search(r"character\s+is\s+([A-Za-z0-9_]+)", user_prompt, re.IGNORECASE)
        if match:
            character = match.group(1)

    return [
        {
            "panel": 1,
            "title": "The Threshold of Adventure",
            "scene_description": f"{character} stands poised at the edge of the unknown, surveying the surroundings with quiet determination.",
            "image_prompt": f"Dramatic comic panel illustration of {character} standing at the starting boundary, vibrant comic book art style, cinematic lighting."
        },
        {
            "panel": 2,
            "title": "A Mysterious Discovery",
            "scene_description": f"Deeper into the journey, {character} discovers an ancient artifact emitting a soft, pulsing glow.",
            "image_prompt": f"Action comic panel, {character} examining a glowing mystical relic, dynamic perspective, intricate details, vivid atmospheric lighting."
        },
        {
            "panel": 3,
            "title": "Unforeseen Peril",
            "scene_description": f"Suddenly, shadows stir and a sudden tremor shakes the ground, threatening {character}'s quest.",
            "image_prompt": f"Tense comic book panel, ominous shadows and rising obstacles confronting {character}, dramatic angles, high contrast comic shading."
        },
        {
            "panel": 4,
            "title": "The Turning Point",
            "scene_description": f"Gathering inner courage and ingenuity, {character} confronts the challenge head-on with a brilliant maneuver.",
            "image_prompt": f"Heroic comic panel, {character} leaping into action, powerful motion blur, comic speedlines, electrifying energy."
        },
        {
            "panel": 5,
            "title": "A New Dawn",
            "scene_description": f"The dust settles; {character} emerges triumphant under a radiant sky, ready for what lies ahead.",
            "image_prompt": f"Inspiring final comic panel, {character} standing victoriously against a breathtaking horizon, warm golden hour palette, comic style."
        }
    ]


def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini.

    Args:
        user_prompt (str): The user's comic idea prompt.

    Returns:
        list: A list of dictionaries, one for each panel.
    """
    prompt = f"""
You are a professional AI comic planner.

Your task is to generate a strictly formatted JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel" (integer)
- "title" (string)
- "scene_description" (string)
- "image_prompt" (string)

Respond ONLY in this valid JSON format, without any explanations or markdown:
[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 2,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 3,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 4,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 5,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }}
]
"""

    # If model is not initialized (e.g. no key or package), return fallback
    if model is None:
        print("[ComicCraft] Notice: GEMINI_API_KEY not set or invalid. Using structured fallback outline.")
        return _get_fallback_outline(user_prompt)

    try:
        response = model.generate_content(prompt)
        output_text = response.text.strip()
        print("\n=== RAW GEMINI RESPONSE ===\n", output_text)

        # Remove any markdown formatting if present
        if output_text.startswith("```json"):
            output_text = output_text.replace("```json", "", 1).rstrip("`").strip()
        elif output_text.startswith("```"):
            output_text = output_text.replace("```", "", 1).rstrip("`").strip()

        # If wrapped in markdown blocks anywhere
        output_text = re.sub(r"^```(?:json)?", "", output_text, flags=re.MULTILINE)
        output_text = re.sub(r"```$", "", output_text, flags=re.MULTILINE).strip()

        panel_data = json.loads(output_text)

        # Additional structure validation
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        for panel in panel_data:
            if not isinstance(panel, dict) or not all(key in panel for key in ("panel", "title", "scene_description", "image_prompt")):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        print("X JSON Decode Error:", e)
        print("X Full Text Received:\n", output_text)
        # Attempt to recover with regex or fallback
        return _get_fallback_outline(user_prompt)

    except Exception as e:
        print("X Unexpected Error in generate_outline:", e)
        return _get_fallback_outline(user_prompt)
