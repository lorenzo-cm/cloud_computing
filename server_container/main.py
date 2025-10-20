import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from load_model import load_model, watch_model
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()
    print(f"[startup] Modelo carregado. dataset={app.state.model.get('dataset')}")

    task = asyncio.create_task(watch_model(app, interval_seconds=5))
    
    yield
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def recommend(songs_seen: list[str], rules: list) -> list[str]:
    recommendations = {}
    
    for antecedent, consequent, confidence in rules:
        if set(antecedent).issubset(songs_seen):
            for c in consequent:
                if c not in songs_seen:
                    recommendations[c] = recommendations.get(c, 0) + confidence

    return sorted(recommendations, key=recommendations.get, reverse=True)

class RecommendationRequest(BaseModel):
    songs_seen: list[str]

@app.post("/api/recommend")
async def recommend_songs(request: RecommendationRequest):
    model = app.state.model
    return {
        "songs": recommend(request.songs_seen, model["rules"]),
        "version": model.get("version", "0.0"),
        "model_date": model.get("datetime", datetime.now().isoformat()),
    }
