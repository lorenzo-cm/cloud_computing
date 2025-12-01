import os
import pickle
from datetime import datetime
from pathlib import Path

import pandas as pd
from fpgrowth_py import fpgrowth


DATASET_NAME = os.getenv("DATASET_NAME", "ds1")
DATASET_FILE_PATH = os.getenv("DATASET_FILE_PATH", "data/2023_spotify_ds1.csv")
MODEL_PATH = Path(os.getenv("MODEL_PATH", "model/model.pkl"))
MIN_SUP_RATIO = float(os.getenv("MIN_SUP_RATIO", 0.04))
MIN_CONF = float(os.getenv("MIN_CONF", 0.01))
VERSION = os.getenv("VERSION", "0.0")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATASET_FILE_PATH)

playlists_songs = df.groupby("pid")["track_name"].apply(lambda x: list(set(x))).tolist()

freq_items_set, rules = fpgrowth(
    playlists_songs, minSupRatio=MIN_SUP_RATIO, minConf=MIN_CONF
)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(
        {
            "freq": freq_items_set,
            "rules": rules,
            "datetime": datetime.now().isoformat(),
            "dataset": DATASET_NAME,
            "version": VERSION,
        },
        f,
    )

print(f"Model saved in {MODEL_PATH}")
