import numpy as np
import pandas as pd
import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from toolkit.entity_extractor import get_entity_list
import datetime as dt
from datetime import datetime
import argparse

def get_df_weekly(engine):
    sql_cmd = """
        select * 
        from cmu.weekly_news_english
    """
    with engine.begin() as connection:
        df = pd.read_sql(sql_cmd, connection)
    return df

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--currdate', type=str, default=None)
    config = parser.parse_args()

    if config.currdate is None:
        config.currdate = str(datetime.now()).split(' ')[0].strip()

    with open('database.yaml') as f:
        db_config = yaml.load(f)
        
    db_url = URL(
                'postgresql',
                host=db_config['host'],
                username=db_config['user'],
                database=db_config['db'],
                password=db_config['pass'],
                port=db_config['port'],
            )
    engine = create_engine(db_url)

    df = get_df_weekly(engine)
    to_keep = ["source_name", "url", "publishedAt", "title", "description", "content", "loc"]
    to_remove = [str(x) for x in df.columns if x not in to_keep]
    df = df.drop(columns=to_remove, axis=1)

    # Incorporate Parivesh data
    def convert_time(t):
        tt = t.split(' ')
        dd,mm,yyyy = tt[0].split('-')
        return f"{yyyy}-{mm}-{dd}T{tt[1]}Z"
    
    df_parivesh = pd.read_csv(f"parivesh_files/parivesh_{config.currdate}.csv")
    currdate_with_time = f"{config.currdate} 23:59:00"
    currdate_obj = datetime.strptime(currdate_with_time, '%Y-%m-%d %H:%M:%S')
    last_week = currdate_obj - dt.timedelta(days=7)

    okrows = []
    for i in range(len(df_parivesh)):
        if type(df_parivesh["recodate"][i]) != type("a"): 
            continue    # skip None rows
        currd = datetime.strptime(df_parivesh["recodate"][i], '%d-%m-%Y %H:%M:%S')
        if currd >= last_week:
            okrows.append(i)

    newdf = df_parivesh.loc[okrows].reset_index(drop=True)
    newdf["source_name"] = ["Parivesh" for _ in range(len(newdf))]
    newdf["publishedAt"] = [convert_time(i) for i in newdf.recodate.tolist()]
    newdf["url"] = [f"https://forestsclearance.nic.in/viewreport.aspx?pid={pid}" for pid in newdf["Proposal_no"]]
    newdf["title"] = ["" for _ in range(len(newdf))]
    newdf["description"] = ["" for _ in range(len(newdf))]
    newdf["content"] = newdf["Proposal_Name"]
    newdf["loc"] = newdf["State_Name"]
    to_remove = [str(x) for x in newdf.columns if x not in to_keep]
    newdf = newdf.drop(columns=to_remove, axis=1)
    df = pd.concat([df, newdf])
    df = df.reset_index(drop=True)

    # Filter to only include last week's articles:
    okrows = []
    for i in range(len(df)):
        currd = df["publishedAt"][i].split('T')
        currd = currd[0]+" "+currd[1][:-1]
        currd = datetime.strptime(currd, '%Y-%m-%d %H:%M:%S')
        if currd >= last_week:
            okrows.append(i)
    df = df.loc[okrows].reset_index(drop=True)
    print(df)

    # Filter to remove rows with hyphen:
    okrows = []
    for i in range(len(df)):
        if "-" in df["loc"][i]: continue
        else:
            okrows.append(i)
    df = df.loc[okrows].reset_index(drop=True)

    df.to_csv(f"articles_all_{config.currdate}.csv", index=False)