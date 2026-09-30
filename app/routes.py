import os
import traceback

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


# ============================================================
# IMPORT CORE GENERATION MODULES
# ============================================================

try:
    from app.gemini_flash import generate_outline
    from app.gemini_pro import generate_story
    from app.image_generator import generate_image
    from app.layout_builder import build_comic_layout
    from app.exporters import save_pdf

except ImportError:
    from .gemini_flash import generate_outline
    from .gemini_pro import generate_story
    from .image_generator import generate_image
    from .layout_builder import build_comic_layout
    from .exporters import save_pdf


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TEMPLATES_DIR = os.path.join(
    BASE_DIR,
    "templates"
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)


# ============================================================
# JINJA2 TEMPLATE CONFIGURATION
# ============================================================

templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)


# ============================================================
# FASTAPI ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# JSON REQUEST MODEL
# ============================================================

class PromptRequest(BaseModel):
    prompt: str
    character_name: str = "Hero"
    setting: str = "forest"
    tone: str = "dramatic"
    style: str = "comic book"


# ============================================================
# HOME PAGE
# ============================================================

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Loads the ComicCraft homepage.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# ============================================================
# GENERATE COMIC - FORM VERSION
# ============================================================

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...)
):
    """
    Handles the comic generation form.

    Pipeline:

    1. Generate 5-panel outline
    2. Generate story narration/dialogue
    3. Generate panel images
    4. Build comic layout
    5. Export PDF
    6. Display comic preview
    """

    try:

        # ====================================================
        # STEP 0 - PREPARE PROMPT
        # ====================================================

        full_prompt = (
            f"Story: {prompt.strip()}\n"
            f"The main character is {character_name.strip()}.\n"
            f"The setting is {setting.strip()}.\n"
            f"The tone is {tone.strip()}.\n"
            f"The art style is {style.strip()}."
        )

        print()
        print("=" * 60)
        print("[ComicCraft] Starting comic generation...")
        print("=" * 60)


        # ====================================================
        # STEP 1 - GENERATE OUTLINE
        # ====================================================

        print(
            f"[ComicCraft] Step 1: "
            f"Generating outline for character "
            f"'{character_name}'..."
        )

        outline = generate_outline(full_prompt)

        if not isinstance(outline, list):
            raise ValueError(
                "Invalid outline: expected a list."
            )

        if len(outline) == 0:
            raise ValueError(
                "Invalid outline: outline is empty."
            )

        for index, panel in enumerate(outline, start=1):

            if not isinstance(panel, dict):
                raise ValueError(
                    f"Invalid panel {index}: expected dictionary."
                )

            if "image_prompt" not in panel:
                raise ValueError(
                    f"Invalid panel {index}: "
                    f"'image_prompt' is missing."
                )

        print(
            f"[ComicCraft] Outline generated successfully "
            f"with {len(outline)} panels."
        )


        # ====================================================
        # STEP 2 - GENERATE STORY
        # ====================================================

        print(
            "[ComicCraft] Step 2: "
            "Generating full story narration and dialogue..."
        )

        full_story = generate_story(outline)

        if not full_story:
            raise ValueError(
                "Story generation returned empty content."
            )

        print(
            "[ComicCraft] Story generated successfully."
        )


        # ====================================================
        # STEP 3 - GENERATE IMAGES
        # ====================================================

        print(
            f"[ComicCraft] Step 3: "
            f"Generating {len(outline)} panel illustrations "
            f"in '{style}' style..."
        )

        images = []

        for index, panel in enumerate(outline, start=1):

            print(
                f"[ComicCraft] Generating panel "
                f"{index}/{len(outline)}..."
            )

            image_path = generate_image(
                panel["image_prompt"],
                style=style
            )

            if not image_path:
                raise ValueError(
                    f"Image generation failed for panel {index}."
                )

            images.append(image_path)

        print(
            f"[ComicCraft] Successfully generated "
            f"{len(images)} panel images."
        )


        # ====================================================
        # STEP 4 - BUILD COMIC LAYOUT
        # ====================================================

        print(
            "[ComicCraft] Step 4: "
            "Building structured comic layout..."
        )

        layout = build_comic_layout(
            images,
            full_story,
            outline
        )

        if layout is None:
            raise ValueError(
                "Comic layout generation returned empty data."
            )

        print(
            "[ComicCraft] Comic layout created successfully."
        )


        # ====================================================
        # STEP 5 - EXPORT PDF
        # ====================================================

        print(
            "[ComicCraft] Step 5: "
            "Compiling and exporting PDF..."
        )

        pdf_path = save_pdf(layout)

        # ----------------------------------------------------
        # IMPORTANT PDF VALIDATION
        # ----------------------------------------------------

        if not pdf_path:
            raise RuntimeError(
                "PDF export failed: save_pdf() returned "
                "an empty path."
            )

        # Convert Path objects to string if necessary
        pdf_path = os.fspath(pdf_path)

        # Convert relative path into absolute path
        if not os.path.isabs(pdf_path):
            pdf_full_path = os.path.abspath(
                os.path.join(
                    BASE_DIR,
                    pdf_path
                )
            )
        else:
            pdf_full_path = os.path.abspath(
                pdf_path
            )

        # Check whether the PDF actually exists
        if not os.path.isfile(pdf_full_path):
            raise RuntimeError(
                "PDF export failed: generated PDF file "
                f"does not exist:\n{pdf_full_path}"
            )

        print(
            f"[ComicCraft] PDF created successfully:\n"
            f"{pdf_full_path}"
        )


        # ====================================================
        # CREATE WEB-SAFE PDF PATH
        # ====================================================

        try:

            relative_pdf_path = os.path.relpath(
                pdf_full_path,
                BASE_DIR
            )

            web_pdf_path = (
                "/"
                + relative_pdf_path
                .replace("\\", "/")
                .lstrip("/")
            )

        except Exception:

            web_pdf_path = (
                "/"
                + pdf_full_path
                .replace("\\", "/")
                .lstrip("/")
            )

        print(
            f"[ComicCraft] Web PDF path: "
            f"{web_pdf_path}"
        )


        # ====================================================
        # STEP 6 - RENDER COMIC PREVIEW
        # ====================================================

        print(
            "[ComicCraft] Comic generation completed "
            "successfully."
        )

        print("=" * 60)
        print()

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "request": request,

                # Generated data
                "outline": outline,
                "full_story": full_story,
                "images": images,
                "layout": layout,

                # PDF
                "pdf_path": web_pdf_path
            }
        )


    except Exception as e:

        print()
        print("=" * 60)
        print("[ComicCraft] ERROR")
        print("=" * 60)

        traceback.print_exc()

        print("=" * 60)
        print()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GENERATE COMIC - JSON API VERSION
# ============================================================

@router.post("/generate-comic/json")
async def generate_comic_json(
    req: PromptRequest
):
    """
    REST API endpoint for generating comics using JSON.
    """

    try:

        # ====================================================
        # PREPARE PROMPT
        # ====================================================

        full_prompt = (
            f"Story: {req.prompt.strip()}\n"
            f"The main character is "
            f"{req.character_name.strip()}.\n"
            f"The setting is {req.setting.strip()}.\n"
            f"The tone is {req.tone.strip()}.\n"
            f"The art style is {req.style.strip()}."
        )


        # ====================================================
        # STEP 1 - OUTLINE
        # ====================================================

        print(
            "[ComicCraft JSON] Step 1: Generating outline..."
        )

        outline = generate_outline(
            full_prompt
        )

        if not isinstance(outline, list) or not outline:
            raise ValueError(
                "Invalid or empty outline."
            )


        # ====================================================
        # STEP 2 - STORY
        # ====================================================

        print(
            "[ComicCraft JSON] Step 2: Generating story..."
        )

        full_story = generate_story(
            outline
        )

        if not full_story:
            raise ValueError(
                "Story generation returned empty content."
            )


        # ====================================================
        # STEP 3 - IMAGES
        # ====================================================

        print(
            "[ComicCraft JSON] Step 3: Generating images..."
        )

        images = []

        for index, panel in enumerate(
            outline,
            start=1
        ):

            if "image_prompt" not in panel:
                raise ValueError(
                    f"Panel {index} has no image_prompt."
                )

            image_path = generate_image(
                panel["image_prompt"],
                style=req.style
            )

            if not image_path:
                raise ValueError(
                    f"Image generation failed "
                    f"for panel {index}."
                )

            images.append(image_path)


        # ====================================================
        # STEP 4 - LAYOUT
        # ====================================================

        print(
            "[ComicCraft JSON] Step 4: "
            "Building comic layout..."
        )

        layout = build_comic_layout(
            images,
            full_story,
            outline
        )


        # ====================================================
        # STEP 5 - PDF
        # ====================================================

        print(
            "[ComicCraft JSON] Step 5: "
            "Exporting PDF..."
        )

        pdf_path = save_pdf(layout)

        if not pdf_path:
            raise RuntimeError(
                "PDF export failed: empty PDF path."
            )

        pdf_path = os.fspath(pdf_path)

        if not os.path.isabs(pdf_path):
            pdf_full_path = os.path.abspath(
                os.path.join(
                    BASE_DIR,
                    pdf_path
                )
            )
        else:
            pdf_full_path = os.path.abspath(
                pdf_path
            )

        if not os.path.isfile(pdf_full_path):
            raise RuntimeError(
                "PDF file does not exist:\n"
                f"{pdf_full_path}"
            )


        # ====================================================
        # WEB PDF PATH
        # ====================================================

        relative_pdf_path = os.path.relpath(
            pdf_full_path,
            BASE_DIR
        )

        web_pdf_path = (
            "/"
            + relative_pdf_path
            .replace("\\", "/")
            .lstrip("/")
        )


        # ====================================================
        # JSON RESPONSE
        # ====================================================

        return JSONResponse(
            content={
                "status": "success",
                "outline": outline,
                "full_story": full_story,
                "layout": layout,
                "images": images,
                "pdf_path": web_pdf_path
            }
        )


    except Exception as e:

        print()
        print(
            "[ComicCraft JSON] ERROR:"
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# EXPORT SUCCESS PAGE
# ============================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request,
    pdf_path: str
):
    """
    Displays the PDF export success page.
    """

    # --------------------------------------------------------
    # Validate query parameter
    # --------------------------------------------------------

    if not pdf_path:
        raise HTTPException(
            status_code=400,
            detail="PDF path is empty."
        )


    # --------------------------------------------------------
    # Convert web path
    # --------------------------------------------------------

    web_pdf_path = (
        "/"
        + pdf_path
        .replace("\\", "/")
        .lstrip("/")
    )


    # --------------------------------------------------------
    # Render page
    # --------------------------------------------------------

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request,
            "pdf_path": web_pdf_path
        }
    )


# ============================================================
# TEST IMAGE ENDPOINT
# ============================================================

@router.get("/test-image")
async def test_image(
    prompt: str = (
        "A futuristic city at sunset, "
        "sci-fi, cinematic, artstation"
    )
):
    """
    Developer endpoint for testing image generation.
    """

    try:

        image_path = generate_image(
            prompt
        )

        if not image_path:
            raise RuntimeError(
                "Image generation returned an empty path."
            )

        image_path = os.fspath(
            image_path
        )


        # ----------------------------------------------------
        # Convert to web path
        # ----------------------------------------------------

        if os.path.isabs(image_path):

            relative_path = os.path.relpath(
                image_path,
                BASE_DIR
            )

            web_path = (
                "/"
                + relative_path
                .replace("\\", "/")
                .lstrip("/")
            )

        else:

            web_path = (
                "/"
                + image_path
                .replace("\\", "/")
                .lstrip("/")
            )


        return {
            "message": "Image generated successfully",
            "path": web_path
        }


    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# PDF DOWNLOAD ENDPOINT
# ============================================================

@router.get("/download")
async def download_file(
    path: str
):
    """
    Safely downloads the generated PDF.
    """

    # --------------------------------------------------------
    # Validate path
    # --------------------------------------------------------

    if not path:
        raise HTTPException(
            status_code=400,
            detail="PDF path is empty."
        )


    # Prevent "/" or "\" from becoming BASE_DIR
    if path in ["/", "\\"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF path."
        )


    # --------------------------------------------------------
    # Clean web path
    # --------------------------------------------------------

    clean_path = (
        path
        .lstrip("/\\")
        .replace("/", os.sep)
    )


    # --------------------------------------------------------
    # Build absolute path
    # --------------------------------------------------------

    file_full_path = os.path.abspath(
        os.path.join(
            BASE_DIR,
            clean_path
        )
    )


    # --------------------------------------------------------
    # Security check
    #
    # Prevent downloading files outside the project.
    # --------------------------------------------------------

    base_dir_absolute = os.path.abspath(
        BASE_DIR
    )

    try:

        common_path = os.path.commonpath(
            [
                base_dir_absolute,
                file_full_path
            ]
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid file path."
        )


    if common_path != base_dir_absolute:

        raise HTTPException(
            status_code=403,
            detail="Access to this file is not allowed."
        )


    # --------------------------------------------------------
    # Check that the requested file exists
    # --------------------------------------------------------

    if not os.path.exists(file_full_path):

        raise HTTPException(
            status_code=404,
            detail=(
                "Requested PDF file was not found: "
                f"{file_full_path}"
            )
        )


    # --------------------------------------------------------
    # IMPORTANT:
    # Make sure it is actually a FILE.
    # --------------------------------------------------------

    if not os.path.isfile(file_full_path):

        raise HTTPException(
            status_code=400,
            detail=(
                "Requested path is not a file: "
                f"{file_full_path}"
            )
        )


    # --------------------------------------------------------
    # Only allow PDF downloads
    # --------------------------------------------------------

    if not file_full_path.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be downloaded."
        )


    # --------------------------------------------------------
    # Send PDF
    # --------------------------------------------------------

    filename = os.path.basename(
        file_full_path
    )

    print(
        f"[ComicCraft] Downloading PDF: "
        f"{file_full_path}"
    )

    return FileResponse(
        path=file_full_path,
        filename=filename,
        media_type="application/pdf"
    )