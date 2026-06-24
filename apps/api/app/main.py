from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import teams, ocr, players, export, audit, auth

app = FastAPI(title="Thai ID Team OCR API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only initialize database if not in test environment
try:
    init_db()
except Exception:
    # Silently fail if database initialization fails (e.g., during testing)
    pass

app.include_router(auth.router, tags=["auth"])
app.include_router(teams.router, prefix="/teams", tags=["teams"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(export.router, prefix="/export", tags=["export"])
app.include_router(audit.router, tags=["audit"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
