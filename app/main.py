import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure required directories exist
os.makedirs(os.path.join(STATIC_DIR, "panels"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "exports"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "fonts"), exist_ok=True)

try:
    from app.routes import router
except ImportError:
    from .routes import router

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Web application utilizing Google Gemini and Stable Diffusion to generate AI-powered personalized comics.",
    version="1.0.0"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include application routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    print("====================================================")
    print("🚀 ComicCraft - AI Comic Story Creator is running!")
    print("📖 Web UI: http://127.0.0.1:8000")
    print("📄 API Docs: http://127.0.0.1:8000/docs")
    print("====================================================")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
