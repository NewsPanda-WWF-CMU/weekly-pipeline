import argparse
import pandas as pd
pd.set_option('display.precision', 4)

import yaml
from yaml import Loader
import datetime as dt
from datetime import datetime

from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.engine.url import URL
from sqlalchemy.event import listens_for
from sqlalchemy.pool import Pool
from sqlalchemy.dialects import postgresql

with open('database.yaml') as f:
    db_config = yaml.load(f, Loader)

from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key=db_config['api_1'])
    
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
    parser.add_argument('--scrapedate', type=str, default=None)
    config = parser.parse_args()

    if config.scrapedate is None:
        config.scrapedate = str(datetime.now()- dt.timedelta(days=7)).split(' ')[0].strip()

    # get weekly news with limited api access
    whs_sql = """
        select distinct on (id) id::int, name, look, string_agg(iso3, ',') as iso
        from at.whs
        where iso3 like '%%IND%%' 
        or iso3 like '%%NPL%%'
        group by name, id, look
        union
        select id, name, look, iso3 as iso
        from cmu.additional_locations
    """
    with engine.begin() as connection:
        whs = pd.read_sql(whs_sql, connection)

    news = {}
    newsapis = [
        NewsApiClient(api_key=db_config['api_1']), #paid subscription
        NewsApiClient(api_key=db_config['api_2']), #zshi@hotmail.com
        NewsApiClient(api_key=db_config['api_3']), #sjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_4']), #terence.kolter@gmail.com
        NewsApiClient(api_key=db_config['api_5']), #terence.mousavi@gmail.com
        NewsApiClient(api_key=db_config['api_6']), #wsjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_7']), #tsjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_8']), #lsjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_9']), #bsjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_10']), #csjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_11']), #asjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_12']), #dsjsdl280@gmail.com
        NewsApiClient(api_key=db_config['api_13']), #psjsdl280@gmail.com
    ]

    def get_news(row):
        page = 1
        page_size = 100
        try:
            news[row['name']] =  newsapis[0].get_everything(q=row['look'],
                                            from_param=config.scrapedate,
                                            page=page,
                                            sort_by='relevancy',
                                            language='en',
                                            page_size=page_size)
        except: 
            newsapis.pop(0)
            news[row['name']] =  newsapis[0].get_everything(q=row['look'],
                                            from_param=config.scrapedate,
                                            page=page,
                                            sort_by='relevancy',
                                            language='en',
                                            page_size=page_size)        
        articlesRead = len(news[row['name']]['articles'])
        page += 1

    whs.apply(get_news, axis=1)

    news_df = []
    def get_df(row):
        d = pd.DataFrame(news[row['name']]['articles'])
        if d.size != 0:
            d = pd.concat([d.source.apply(pd.Series), d], axis=1).drop(['source'], axis=1)
            d = d.rename({'id': 'source_id', 'name': 'source_name'}, axis=1)
            d['whs'] = row['name']
            news_df.append(d)


    whs.apply(get_df, axis=1)
    news_df = pd.concat(news_df, axis=0)
    news_df['news_id'] = news_df.index
    news_df = news_df.merge(whs, left_on='whs', right_on='name').rename(
        {'id': 'loc_id', 'whs': 'loc', 'iso': 'iso3'}, axis=1).drop('name', axis=1)
    news_df = news_df.drop_duplicates(subset=['title'], keep='first', ignore_index=True)
    print(news_df)

    with engine.begin() as connection:
        news_df.to_sql('weekly_news_english', con=connection, schema='cmu', if_exists='append')

    with engine.begin() as connection:
        news = pd.read_sql_table('weekly_news_english', con=connection, schema='cmu')
        news = news.drop_duplicates(subset=['title', 'content']).drop(['index'], axis=1)
        news.to_sql('weekly_news_english', con=connection, schema='cmu', if_exists='replace')