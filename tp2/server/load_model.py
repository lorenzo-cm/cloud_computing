import pickle
import asyncio
import os


def load_model(model_path):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model


async def watch_model(app, model_path, interval_seconds: int = 5) -> None:
    last_mtime = None
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            mtime = os.path.getmtime(model_path)
            if last_mtime is None or mtime != last_mtime:
                app.state.model = load_model(model_path)
                last_mtime = mtime
                print(
                    f"[reloader] Modelo recarregado. dataset={app.state.model.get('dataset')} at={app.state.model.get('datetime')}"
                )
        except FileNotFoundError:
            print(f"[reloader] Arquivo do modelo não foi encontrad: {model_path}")
            continue
