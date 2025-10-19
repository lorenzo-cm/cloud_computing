import pickle
from pathlib import Path
import asyncio
import os


MODEL_PATH = Path(os.getenv("model_path", Path("C:/Users/Loren/Desktop/drive/faculdade/9PERIODO/cloud_computing/model.pkl")))

def load_model():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model

async def watch_model(app, interval_seconds: int = 5) -> None:
    last_mtime = None
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            mtime = os.path.getmtime(MODEL_PATH)
            if last_mtime is None or mtime != last_mtime:
                app.state.model = load_model()
                last_mtime = mtime
                print(f"[reloader] Modelo recarregado. dataset={app.state.model.get('dataset')} at={app.state.model.get('datetime')}")
        except FileNotFoundError:
            continue