import os
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    client = genai.Client(api_key=GEMINI_API_KEY)


def _get_fallback_story(outline: list) -> str:
    """Fallback story if Gemini is unavailable."""

    story_parts = []

    for idx, panel in enumerate(outline, start=1):

        title = panel.get("title", f"Panel {idx}")
        desc = panel.get("scene_description", "")
        img_p = panel.get("image_prompt", "")

        part = f"""**Panel {idx}: {title}**
**CAPTION** The story continues...
**NARRATION** {desc}
**DIALOGUE** "I have to keep moving forward!"
**IMAGE PROMPT** {img_p}"""

        story_parts.append(part)

    return "\n\n".join(story_parts)


def generate_story(outline: list) -> str:

    formatted_items = []

    for i, item in enumerate(outline):

        if isinstance(item, dict):

            panel_num = item.get("panel", i + 1)
            title = item.get("title", "Untitled")
            desc = item.get("scene_description", "")
            img_p = item.get("image_prompt", "")

            formatted_items.append(
                f"""Panel {panel_num}: {title}
Scene: {desc}
Visual: {img_p}"""
            )

        else:

            formatted_items.append(
                f"{i + 1}. {item}"
            )

    formatted_outline = "\n\n".join(formatted_items)

    prompt = f"""
You are a professional comic book writer.

Create a complete 5-panel comic story from the following outline.

PANEL OUTLINE:

{formatted_outline}

Requirements:

1. Keep exactly 5 panels.
2. Each panel must continue the story naturally.
3. Give every panel different narration.
4. Give every panel different dialogue.
5. Do NOT repeat dialogue between panels.
6. Make the story engaging and cinematic.
7. Keep the main character consistent.
8. The dialogue should match the events happening in that panel.

For every panel use exactly this format:

**Panel <number>: <Title>**
**CAPTION** [short atmospheric caption]
**NARRATION** [2-3 sentences describing the action]
**DIALOGUE** [character dialogue]
**IMAGE PROMPT** [visual description]

Return only the comic story.
"""

    if client is None:
        print(
            "[ComicCraft] Gemini client unavailable. "
            "Using fallback story."
        )
        return _get_fallback_story(outline)

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        if response.text and response.text.strip():

            story = response.text.strip()

            print(
                "[ComicCraft] Gemini story generated successfully."
            )

            return story

        print(
            "[ComicCraft] Gemini returned an empty response. "
            "Using fallback story."
        )

        return _get_fallback_story(outline)

    except Exception as e:

        print(f"[ComicCraft] Gemini story error: {e}")

        return _get_fallback_story(outline)