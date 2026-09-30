import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    client = genai.Client(api_key=GEMINI_API_KEY)


def _get_fallback_outline(user_prompt: str) -> list:
    character = "Hero"

    match = re.search(
        r"main character is ([A-Za-z0-9_]+)",
        user_prompt,
        re.IGNORECASE
    )

    if match:
        character = match.group(1)

    return [
        {
            "panel": 1,
            "title": "The Beginning",
            "scene_description": f"{character} begins the adventure.",
            "image_prompt": f"Comic book illustration of {character} beginning an adventure, cinematic lighting, detailed comic art."
        },
        {
            "panel": 2,
            "title": "The Discovery",
            "scene_description": f"{character} discovers something mysterious.",
            "image_prompt": f"Comic book illustration of {character} discovering something mysterious, dramatic lighting, detailed artwork."
        },
        {
            "panel": 3,
            "title": "The Challenge",
            "scene_description": f"{character} faces an unexpected challenge.",
            "image_prompt": f"Action comic book illustration of {character} facing a dangerous challenge, dynamic composition."
        },
        {
            "panel": 4,
            "title": "The Turning Point",
            "scene_description": f"{character} finds a way to overcome the challenge.",
            "image_prompt": f"Heroic comic book illustration of {character} overcoming a challenge, powerful cinematic scene."
        },
        {
            "panel": 5,
            "title": "The New Beginning",
            "scene_description": f"{character} completes the adventure and looks toward the future.",
            "image_prompt": f"Inspiring final comic book illustration of {character} standing victoriously, cinematic sunset."
        }
    ]


def generate_outline(user_prompt: str) -> list:

    prompt = f"""
You are a professional AI comic planner.

Create a complete 5-panel comic story based on this idea:

{user_prompt}

Return ONLY valid JSON.

The JSON must be an array containing exactly 5 objects.

Each object must contain:

- panel: integer
- title: string
- scene_description: string
- image_prompt: string

Make every panel different and make the story progress naturally.

The image_prompt should describe the visual scene for an AI image generator.

Do not use markdown.
Do not use ```json.
Return JSON only.
"""

    if client is None:
        print("[ComicCraft] Gemini client unavailable. Using fallback outline.")
        return _get_fallback_outline(user_prompt)

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        output_text = response.text.strip()

        print("\n=== RAW GEMINI RESPONSE ===\n", output_text)

        output_text = re.sub(
            r"^```(?:json)?",
            "",
            output_text,
            flags=re.IGNORECASE
        )

        output_text = re.sub(
            r"```$",
            "",
            output_text
        ).strip()

        panel_data = json.loads(output_text)

        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        if len(panel_data) != 5:
            raise ValueError(
                f"Expected 5 panels, received {len(panel_data)}."
            )

        required_keys = (
            "panel",
            "title",
            "scene_description",
            "image_prompt"
        )

        for panel in panel_data:
            if not isinstance(panel, dict):
                raise ValueError("Panel is not an object.")

            if not all(key in panel for key in required_keys):
                raise ValueError(
                    f"Missing required keys in panel: {panel}"
                )

        print("[ComicCraft] Gemini outline generated successfully.")

        return panel_data

    except Exception as e:
        print(f"[ComicCraft] Gemini outline error: {e}")
        print("[ComicCraft] Using fallback outline.")

        return _get_fallback_outline(user_prompt)