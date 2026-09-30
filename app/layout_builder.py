import re


def build_comic_layout(image_paths, full_story, outline):
    """
    Organizes generated images, story text, and outline descriptions into a structured layout.

    Args:
        image_paths (list): List of web paths to the panel images.
        full_story (str): Complete generated comic story narration and dialogue.
        outline (list): 5-panel outline list containing panel metadata.

    Returns:
        list: A list of panel dictionaries ready for preview and export.
    """
    # Split full story into individual panel segments
    if "**Panel" in full_story:
        raw_panels = full_story.split("**Panel")
        story_panels = [f"**Panel {p}" for p in raw_panels if p.strip()]
    elif "Panel " in full_story:
        raw_panels = re.split(r"(?=Panel\s+\d+)", full_story)
        story_panels = [p.strip() for p in raw_panels if p.strip()]
    else:
        # Fallback split by double newlines into chunks
        chunks = [c.strip() for c in full_story.split("\n\n") if c.strip()]
        story_panels = chunks

    # If number of panels doesn't match outline length, pad or align
    total_panels = len(outline)
    while len(story_panels) < total_panels:
        idx = len(story_panels) + 1
        p_info = outline[idx - 1] if idx <= len(outline) else {}
        story_panels.append(
            f"**Panel {idx}**\n**CAPTION** Continuing the saga...\n**NARRATION** {p_info.get('scene_description', '')}"
        )

    layout = []
    for idx, (image, text, panel_info) in enumerate(zip(image_paths, story_panels, outline), start=1):
        lines = text.strip().splitlines()
        # Remove first title line if it matches Panel title
        if len(lines) > 1 and ("panel" in lines[0].lower()):
            cleaned_text = "\n".join(lines[1:]).strip()
        else:
            cleaned_text = text.strip()

        # Format image path to ensure clean web accessibility
        web_image_path = image.replace("\\", "/")
        if not web_image_path.startswith("/") and not web_image_path.startswith("http"):
            web_image_path = "/" + web_image_path

        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": web_image_path,
            "text": cleaned_text,
            "scene_description": panel_info.get("scene_description", ""),
            "image_prompt": panel_info.get("image_prompt", "")
        })

    return layout
