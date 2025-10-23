import os
import pickle
from datetime import datetime
from pathlib import Path

import pandas as pd
from fpgrowth_py import fpgrowth


DATASET_NAME = os.getenv("DATASET_NAME", "ds1")
DATASET_FILE_PATH = os.getenv("DATASET_FILE_PATH", "data/2023_spotify_ds1.csv")
MODEL_PATH = os.getenv("MODEL_PATH", "model")
MIN_SUP_RATIO = os.getenv("MIN_SUP_RATIO", 0.04)
MIN_CONF = os.getenv("MIN_CONF", 0.01)

MODEL_FILE = Path(MODEL_PATH) / "model.pkl"
MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATASET_FILE_PATH)

playlists_songs = df.groupby("pid")["track_name"].apply(lambda x: list(set(x))).tolist()

freq_items_set, rules = fpgrowth(
    playlists_songs, minSupRatio=MIN_SUP_RATIO, minConf=MIN_CONF
)

with open(MODEL_FILE, "wb") as f:
    pickle.dump(
        {
            "freq": freq_items_set,
            "rules": rules,
            "datetime": datetime.now().isoformat(),
            "dataset": DATASET_NAME,
        },
        f,
    )

print(f"Model saved in {MODEL_FILE}")
