from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import teams, ocr, players

app = FastAPI(title="Thai ID Team OCR API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(teams.router, prefix="/teams", tags=["teams"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(players.router, prefix="/players", tags=["players"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
