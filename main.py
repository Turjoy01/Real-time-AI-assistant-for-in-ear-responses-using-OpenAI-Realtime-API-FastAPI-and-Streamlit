from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.routes import websocket, api
from backend.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Earbud Assistant - Passive Listening Mode",
    description="Silent AI assistant that only speaks when questions are detected",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(api.router, tags=["API"])

@app.get("/")
async def root():
    return {
        "message": "AI Earbud Assistant - Passive Listening Mode",
        "mode": "The AI listens silently and only responds to detected questions",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("🎧 AI Earbud Assistant starting in PASSIVE LISTENING mode")
    logger.info("AI will remain SILENT unless a question is detected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )

    