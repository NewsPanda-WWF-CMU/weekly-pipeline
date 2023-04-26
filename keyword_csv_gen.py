import pandas as pd
import random 
from datetime import datetime
import argparse 

def run(config):
    df = pd.read_csv(config.filename)
    df = df[df.source_name != "Parivesh"].reset_index(drop=True)

    print(df)
    idxs = random.sample(list(range(len(df))), config.num_articles)

    outdf = df.iloc[idxs].reset_index(drop=True)
    outdf["keywords"] = ["" for _ in range(len(outdf))]
    cols = ["keywords", "conservation_prediction", "infrastructure_prediction", "source_name", "loc", "x", "y", "title", "description", "publishedAt", "url", "content", "confidence", "infrastructure_confidence"]
    outdf = outdf[cols]

    if config.currdate is None:
        config.currdate=datetime.today().strftime('%Y-%m-%d')
    outdf.to_csv(f"keywords_{config.currdate}.csv", index=False)
    outdf.to_excel(f"keywords_{config.currdate}.xlsx", index=False, engine='xlsxwriter')

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True)
    parser.add_argument('--num_articles', type=int, default=3)
    parser.add_argument('--currdate', type=str, default=None)

    config = parser.parse_args()
    run(config)