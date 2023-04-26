import numpy as np
import pandas as pd
import torch
import random
import transformers as ppb
from matplotlib import pyplot as plt
import ast
import pandas as pd
import argparse

from requests_oauthlib import OAuth1Session
import os
import json
import yaml
from yaml import Loader

from sqlalchemy import create_engine

import sqlalchemy
from sqlalchemy.engine.url import URL
from sqlalchemy.event import listens_for
from sqlalchemy.pool import Pool

with open('database.yaml') as f:
    db_config = yaml.load(f, Loader)
    
db_url = URL(
            'postgresql',
            host=db_config['host'],
            username=db_config['user'],
            database=db_config['db'],
            password=db_config['pass'],
            port=db_config['port'],
        )
engine = create_engine(db_url)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--currdate', type=str, default=None)
    config = parser.parse_args()

    if config.currdate is None:
        config.currdate = str(datetime.now()).split(' ')[0].strip()

    df = pd.read_excel(f'news_{config.currdate}/news_labelled_{config.currdate}_shortlist.xlsx')
    try: 
        df_cluster = pd.read_excel(f'news_{config.currdate}/event_clusters_{config.currdate}.xlsx')
        df = df[(df['conservation_prediction'] == 1) & (df['source_name'] != "Parivesh")].sort_values('confidence', ascending=False)
        df = df.merge(df_cluster[['title', 'source_name', 'cluster']], how='left', on=['title', 'source_name'])
        df = df[(~df.duplicated(subset=['cluster'])) | (df['cluster'].isnull())]
    except: 
        df = df[(df['conservation_prediction'] == 1) & (df['source_name'] != "Parivesh")].sort_values('confidence', ascending=False)
    df = df.head(10)
    df[['source_name', 'confidence', 'loc', 'title', 'content', 'entities_locs']]
    def get_entities(row):
        if row['entities_locs'] == "[set()]": 
            row['entities_locs'] = "[{}]"
        if row['entities_orgs'] == "[set()]": 
            row['entities_orgs'] = "[{}]"
        if row['entities_title'] == "[set()]": 
            row['entities_title'] = "[{}]"
        row['entities_locs'] = ast.literal_eval(row['entities_locs'])[0]
        row['entities_orgs'] = ast.literal_eval(row['entities_orgs'])[0]
        row['entities_title'] = ast.literal_eval(row['entities_title'])[0]
        row['entities'] = ast.literal_eval(row['entities'])[0]
        return row
    df = df.apply(get_entities, axis=1)

    row = df.iloc[-1]
    locs = row['loc'].replace(" ", "").split(' - ')
    entities_locs = [loc.replace(" ", "").replace("-", "") for loc in row['entities_locs']]
    other_entities = row['entities'].difference(row['entities_locs'])
    other_entities = [loc.replace(" ", "").replace("-", "") for loc in other_entities if len(loc) <= 25]
    locs = [loc for loc in locs if loc not in entities_locs]

    loc_tag = ' '.join(['#' + loc for loc in locs])
    entities_locs_tag = ' '.join(['#' + loc for loc in entities_locs])
    other_entities_tag = ' '.join(['#' + loc for loc in other_entities])
    if loc_tag != '':
        entities_locs_tag = loc_tag + ' ' + entities_locs_tag
    text = "{} {} {}".format(row['title'], entities_locs_tag, other_entities_tag)[:(280-23)]


    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    def tweet_news(row):
        locs = row['loc'].replace(" ", "").split(' - ')
        entities_locs = [loc.replace(" ", "").replace("-", "") for loc in row['entities_locs']]
        other_entities = row['entities'].difference(row['entities_locs'])
        other_entities = [loc.replace(" ", "").replace("-", "") for loc in other_entities if len(loc) <= 25]
        locs = [loc for loc in locs if loc not in entities_locs]

        loc_tag = ' '.join(['#' + loc for loc in locs])
        entities_locs_tag = ' '.join(['#' + loc for loc in entities_locs])
        other_entities_tag = ' '.join(['#' + loc for loc in other_entities])
        if loc_tag != '':
            entities_locs_tag = loc_tag + ' ' + entities_locs_tag
        text = "{} {} {}".format(row['title'], entities_locs_tag, other_entities_tag)[:(280-24)]
        payload = {"text": text + ' ' + row['url']}
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )
        if response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )
        print("Response code: {}".format(response.status_code))
        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
    
    df.apply(tweet_news, axis=1)