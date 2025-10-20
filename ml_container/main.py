import pandas as pd
import pickle
from fpgrowth_py import fpgrowth
from pathlib import Path
from datetime import datetime
import yaml

CONFIG_FILE = Path("config.yaml")

with open(CONFIG_FILE, "r") as f:
    cfg = yaml.safe_load(f)

MODEL_FILE = Path(cfg["output"]["model_path"])
MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(cfg["dataset"]["file_path"])

playlists_songs = df.groupby("pid")["track_name"].apply(lambda x: list(set(x))).tolist()

freq_items_set, rules = fpgrowth(playlists_songs, minSupRatio=0.05, minConf=0.5)

with open(MODEL_FILE, "wb") as f:
    pickle.dump({
        "freq": freq_items_set,
        "rules": rules,
        "datetime": datetime.now().isoformat(),
        "dataset": cfg["dataset"]["name"],
        }, f)

print(f"Model saved in {MODEL_FILE}")
