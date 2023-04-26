import argparse
import pandas as pd
from datetime import datetime
from toolkit.topic_cluster import *
import os

def load_positive_events():
    dfs = []
    for _,_,files in os.walk("positive_events"):
        for f in files:
            df = pd.read_csv(f"positive_events/{f}")
            dfs.append(df)
    positive_events = pd.concat(dfs).reset_index(drop=True)
    return positive_events

parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, required=True)
parser.add_argument('--currdate', type=str, default=None)
config = parser.parse_args()

if config.currdate is None:
    config.currdate=datetime.today().strftime('%Y-%m-%d')

df = pd.read_csv(config.data_path)

past_articles = load_positive_events()
combined, clusters = generate_clusters(df, past_articles)

dfs = []
for idx, arr in enumerate(clusters):
    arr = [int(x) for x in arr]
    df2 = combined.loc[arr]
    df2 = df2[["source_name", "loc", "title", "publishedAt", "url"]].sort_values(by=['publishedAt'])
    df2["cluster"] = idx
    df2 = df2.reset_index()
    dfs.append(df2)

df2 = pd.concat(dfs)
df2["related"] = ["" for _ in range(len(df2))]
cols_new = ["related", "index", "source_name", "loc", "title", "publishedAt", "url", "cluster"]
df2 = df2[cols_new]
df2.to_csv(f"event_clusters_{config.currdate}.csv", index=False)
df2.to_excel(f"event_clusters_{config.currdate}.xlsx", index=False, engine='xlsxwriter')