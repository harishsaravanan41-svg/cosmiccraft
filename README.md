# ComicCraft — AI Comic Story Creator using Gemini Models

ComicCraft is a full-stack Generative AI web application built with **FastAPI**, **Google Gemini models** (Gemini 1.5 Flash & Gemini 1.5 Pro), and **Stable Diffusion** (or stylized illustration pipeline). It allows users to input their story prompt, character name, setting, tone, and art style to automatically generate a complete 5-panel comic strip, view it interactively in the browser, and download it as an exportable multi-page PDF.

---

## 📁 Project Architecture & File Structure

```text
comiccraft/
├── app/
│   ├── __init__.py           # Package initializer
│   ├── main.py               # FastAPI entry point, static mount, CORS middleware
│   ├── routes.py             # Route handlers (/generate, /generate-comic/json, /export-success, /test-image, /download)
│   ├── gemini_flash.py       # Activity 2.1: 5-panel comic outline planner with Gemini 1.5 Flash
│   ├── gemini_pro.py         # Activity 2.1: Rich story, caption & dialogue generation with Gemini 1.5 Pro
│   ├── image_generator.py    # Activity 2.1: Panel-wise illustration generation (Diffusers / HF API / Stylized engine)
│   ├── layout_builder.py     # Activity 2.1: Assembles images, story segments, and panel metadata
│   └── exporters.py          # Activity 2.1: Compiles multi-page PDF with FPDF and Unicode fonts
├── templates/
│   ├── index.html            # Input form with scenic background and responsive card
│   ├── comic_preview.html    # Panel-by-panel comic preview page with narration badges
│   └── export_success.html   # Download confirmation page with auto-download and replay button
├── static/
│   ├── panels/               # Generated panel illustration images (.png)
│   ├── exports/              # Exported comic PDFs (.pdf)
│   ├── fonts/                # DejaVuSans.ttf and DejaVuSans-Bold.ttf for PDF rendering
│   └── images/               # Scenic mountain/forest background image
├── .env                      # Active environment configuration with your API keys
├── .env.example              # Template configuration file
├── requirements.txt          # Python dependencies list
└── README.md                 # Complete documentation and setup guide
```

---

## 🚀 Quick Setup & Running Instructions

### 1. Open the Project in VS Code / CMD
1. Extract the downloaded `comiccraft.zip` archive to a folder on your computer (for example: `C:\Projects\comiccraft` or `D:\comiccraft`).
2. Open **Command Prompt (`cmd`)** or **PowerShell**, and navigate to the project directory:
   ```cmd
   cd path\to\comiccraft
   ```
   *(Or in VS Code: click `File` -> `Open Folder...` and select the `comiccraft` folder, then open the integrated terminal with ``Ctrl + ` ``).*

### 2. Create and Activate a Virtual Environment
```cmd
python -m venv comiccraft-env
```
Activate it:
- **On Windows (Command Prompt):**
  ```cmd
  comiccraft-env\Scripts\activate
  ```
- **On Windows (PowerShell):**
  ```powershell
  comiccraft-env\Scripts\Activate.ps1
  ```
- **On macOS / Linux:**
  ```bash
  source comiccraft-env/bin/activate
  ```

### 3. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 4. Configure Your API Keys
Open the `.env` file in the root folder and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
HF_API_KEY=your_huggingface_api_key_here
IMAGE_GEN_MODE=auto
```
> **Tip:** You can obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).  
> If an API key is not yet set, ComicCraft will gracefully run with intelligent structured mock generation so you can test all UI, layout assembly, and PDF export features immediately!

### 5. Launch the FastAPI Server
Run the Uvicorn ASGI server with hot-reload enabled:
```cmd
uvicorn app.main:app --reload
```

---

## 🌐 Accessing the Application

1. **Web User Interface:**
   Open your browser and navigate to:  
   👉 **`http://127.0.0.1:8000`**

2. **Interactive Swagger API Documentation:**
   Explore and test backend endpoints directly at:  
   👉 **`http://127.0.0.1:8000/docs`**

---

## 🧪 Testing the Workflow

1. **Create a Comic:**
   - On the homepage, enter a story prompt (e.g., *"A brave fox explores an enchanted forest."*).
   - Enter a Character Name (e.g., `Free`).
   - Select Setting (`Forest`), Story Tone (`Dramatic`), and Art Style (`Realistic` or `Comic Book`).
   - Click **Generate Comic**.
2. **Review the Comic:**
   - Review each panel sequentially with its title, illustration, scene atmosphere, captions, narration, and character dialogues.
3. **Download PDF:**
   - Click **Download Your Comic as PDF**.
   - You will be redirected to the **Export Success** page, and the high-resolution multi-page PDF will download automatically.
"# ComicCraft" 
