import os
from datetime import datetime
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
EXPORT_FOLDER = os.path.join(STATIC_DIR, "exports")
FONTS_DIR = os.path.join(STATIC_DIR, "fonts")
FONT_PATH = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

os.makedirs(EXPORT_FOLDER, exist_ok=True)


class ComicPDF(FPDF):
    def header(self):
        # Decorative top line
        self.set_draw_color(40, 40, 40)
        self.set_line_width(0.3)

    def footer(self):
        self.set_y(-12)
        try:
            self.set_font('DejaVu', '', 8)
        except Exception:
            self.set_font('Helvetica', '', 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"ComicCraft AI — Page {self.page_no()}", align="C")


def save_pdf(layout: list) -> str:
    """
    Compiles the full comic layout into a multi-page PDF file using FPDF.
    Each panel's image, title, and narration are placed on separate pages.

    Args:
        layout (list): List of panel dicts containing image_path, title, text, scene_description.

    Returns:
        str: Relative path to the saved PDF file (e.g. 'static/exports/comic_20260926.pdf')
    """
    pdf = ComicPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=15, top=15, right=15)
    pdf.set_auto_page_break(auto=True, margin=15)

    content_width = pdf.w - 30

    # Register Unicode font if available
    has_unicode_font = False
    if os.path.exists(FONT_PATH):
        try:
            pdf.add_font('DejaVu', '', FONT_PATH)
            if os.path.exists(FONT_BOLD_PATH):
                pdf.add_font('DejaVu', 'B', FONT_BOLD_PATH)
            has_unicode_font = True
        except TypeError:
            try:
                pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
                if os.path.exists(FONT_BOLD_PATH):
                    pdf.add_font('DejaVu', 'B', FONT_BOLD_PATH, uni=True)
                has_unicode_font = True
            except Exception as e:
                print(f"[ComicCraft] Font uni=True failed: {e}")
        except Exception as e:
            print(f"[ComicCraft] Font registration failed: {e}")

    font_family = 'DejaVu' if has_unicode_font else 'Helvetica'

    for panel in layout:
        pdf.add_page()
        pdf.set_text_color(20, 20, 20)

        # 1. Panel Header & Title
        panel_idx = panel.get("panel", 1)
        panel_title = panel.get("title", f"Panel {panel_idx}")
        
        pdf.set_font(font_family, 'B' if has_unicode_font else '', 16)
        pdf.set_text_color(30, 45, 70)
        pdf.set_x(15)
        pdf.cell(content_width, 10, f"Panel {panel_idx}: {panel_title}", ln=True, align="C")
        pdf.ln(2)

        # 2. Image Placement
        image_web_path = panel.get("image_path", "")
        clean_img_path = image_web_path.lstrip("/").replace("/", os.sep)
        local_image_path = os.path.join(BASE_DIR, clean_img_path)
        if not os.path.exists(local_image_path):
            local_image_path = os.path.join(STATIC_DIR, "panels", os.path.basename(clean_img_path))

        y_image = pdf.get_y()
        image_height = 92
        
        if os.path.exists(local_image_path):
            pdf.set_draw_color(50, 50, 50)
            pdf.set_line_width(0.8)
            pdf.rect(15, y_image, content_width, image_height)
            pdf.image(local_image_path, x=15.5, y=y_image + 0.5, w=content_width - 1, h=image_height - 1)
            pdf.set_y(y_image + image_height + 6)
        else:
            pdf.set_y(y_image)
            pdf.set_font(font_family, '', 11)
            pdf.set_x(15)
            pdf.multi_cell(content_width, 8, f"[Illustration: {image_web_path}]", align="C")
            pdf.ln(4)

        # 3. Scene Description
        scene_desc = panel.get("scene_description", "")
        if scene_desc:
            pdf.set_font(font_family, '', 10)
            pdf.set_text_color(100, 105, 115)
            safe_desc = scene_desc if has_unicode_font else scene_desc.encode('latin-1', 'replace').decode('latin-1')
            pdf.set_x(15)
            pdf.multi_cell(content_width, 5, f"Scene Atmosphere: {safe_desc}", align="L")
            pdf.ln(3)

        # 4. Narration and Dialogue Text
        story_text = panel.get("text", "")
        story_lines = story_text.strip().splitlines()

        if story_lines and story_lines[0].strip().lower().startswith("**panel"):
            story_lines = story_lines[1:]

        cleaned_text = "\n".join(story_lines).strip()
        safe_text = cleaned_text if has_unicode_font else cleaned_text.encode('latin-1', 'replace').decode('latin-1')

        for line in safe_text.splitlines():
            line_str = line.strip()
            if not line_str:
                pdf.ln(1)
                continue

            pdf.set_x(15)
            if "**CAPTION**" in line_str or line_str.startswith("CAPTION"):
                pdf.set_font(font_family, 'B' if has_unicode_font else '', 11)
                pdf.set_text_color(180, 70, 20)
                pdf.multi_cell(content_width, 5.5, line_str)
            elif "**NARRATION**" in line_str or line_str.startswith("NARRATION"):
                pdf.set_font(font_family, '', 10.5)
                pdf.set_text_color(30, 30, 40)
                pdf.multi_cell(content_width, 5.5, line_str)
            elif "**DIALOGUE**" in line_str or line_str.startswith("DIALOGUE"):
                pdf.set_font(font_family, '', 11)
                pdf.set_text_color(15, 80, 150)
                pdf.multi_cell(content_width, 5.5, line_str)
            elif "**IMAGE PROMPT**" in line_str or line_str.startswith("IMAGE PROMPT"):
                pdf.set_font(font_family, '', 8.5)
                pdf.set_text_color(120, 120, 120)
                pdf.multi_cell(content_width, 4.5, line_str)
            else:
                pdf.set_font(font_family, '', 10.5)
                pdf.set_text_color(25, 25, 30)
                pdf.multi_cell(content_width, 5.5, line_str)

    # 5. Output PDF with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_physical_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(pdf_physical_path)

    return f"static/exports/{filename}"
