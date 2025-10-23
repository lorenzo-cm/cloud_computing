import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from load_model import load_model, watch_model
from pydantic import BaseModel

MODEL_DIR = Path(
    os.getenv(
        "model_dir",
        Path(
            "/home/lorenzo-cm/faculdade/9PERIODO/cloud_computing/playlist-recommender/model"
        ),
    )
)

MODEL_FILE_PATH = MODEL_DIR / "model.pkl"


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(watch_model(app, MODEL_FILE_PATH, interval_seconds=5))

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


def recommend(rules: list, songs: list[str], k=10) -> list[str]:
    recommendations: dict[str, float] = {}

    for antecedent, consequent, confidence in rules:
        if set(antecedent).issubset(songs):
            for c in consequent:
                if c not in songs:
                    recommendations[c] = recommendations.get(c, 0) + confidence

    return sorted(recommendations, key=lambda x: recommendations[x], reverse=True)[:k]


class RecommendationRequest(BaseModel):
    songs: list[str]


@app.post("/api/recommend")
async def recommend_songs(request: RecommendationRequest):
    model = app.state.model
    recommended_songs = []

    try:
        recommended_songs = recommend(model["rules"], request.songs)
    except Exception:
        pass

    return JSONResponse(
        {
            "songs": recommended_songs,
            "version": model.get("version", "0.0"),
            "model_date": model.get("datetime", datetime.now().isoformat()),
        }
    )
