import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
import argparse 

from geopy.geocoders import Nominatim
import numpy as np
import time
from tqdm import tqdm

from geopy.exc import GeocoderTimedOut
def do_geocode(loc, districts_dict, attempt=1, max_attempts=5):
    if loc in districts_dict:
        return districts_dict[loc][0], districts_dict[loc][1]
    try:
        return getlatlong(loc)
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            time.sleep(2.0)
            return do_geocode(loc, districts_dict, attempt=attempt+1)
        raise

def getlatlong(loc):
    location = Nominatim(user_agent="GetLoc")
    getLocation = location.geocode(loc)
    try:
        return getLocation.latitude, getLocation.longitude
    except:
        return 0, 0

def load_districts_dict():
    districts_df = pd.read_csv("reference-files/districts_XY.csv")
    districts_dict = {}
    for i in range(len(districts_df)):
        districts_dict[districts_df.district[i]] = (districts_df.lat[i], districts_df.long[i])
    return districts_dict

def run(config):
    date = config.currdate
    curr_articles = pd.read_csv(f"./articles_all_{date}.csv")
    all_parivesh = pd.read_csv(f"./parivesh-files/parivesh_{date}.csv")
    all_parivesh["url"] = [f"https://forestsclearance.nic.in/viewreport.aspx?pid={pid}" for pid in all_parivesh["Proposal_no"]]
    cols_to_keep = ['url', 'Proposal_Name', 'user_agency_name', 'area_applied', 'Proposal_Status', 'New_Status']
    all_parivesh = all_parivesh[cols_to_keep]

    df = all_parivesh.merge(curr_articles[['url']])
    print(df)
    filename = f"parivesh_{date}.csv"

    districts_dict = load_districts_dict()
    districts_arr, urls_arr = [None for i in range(len(df))], [None for i in range(len(df))]
    lats, longs = [None for i in range(len(df))], [None for i in range(len(df))]
    for idx, url in enumerate(tqdm(df.url)):
        page = requests.get(url, verify=False)
        soup = BeautifulSoup(page.text, 'html.parser')

        ### District ###
        table_cells = soup.find_all('tr')
        iscurrent = False
        for s in table_cells:
            if iscurrent:
                district = s.find_all('td')[1].text
                districts_arr[idx] = district
                iscurrent = False
            if "District Name" in str(s) and len(str(s)) < 5000:
                iscurrent = True

        ### Links ###
        urls = soup.find_all('a')
        hrefs = set()
        for i in urls:
            try: curr_url = str(i['href'])
            except: continue
            curr_url = f"https://forestsclearance.nic.in/{curr_url}"
            hrefs.add(curr_url)
        hrefs = list(hrefs)
        urls_arr[idx] = hrefs

    same_articles_arr = [None for i in range(len(df))]
    for i in tqdm(range(len(df))):
        curr_title, curr_url = df.Proposal_Name[i], df.url[i]
        new_df = all_parivesh[(all_parivesh.Proposal_Name==curr_title) & (all_parivesh.url != curr_url)]
        same_articles_arr[i] = new_df.url.tolist()
        currlat, currlong = do_geocode(districts_arr[i], districts_dict)
        lats[i], longs[i] = currlat, currlong

    df['districts'] = districts_arr
    df['links'] = urls_arr
    df['same_articles'] = same_articles_arr
    df['lat'] = lats
    df['long'] = longs
    df.to_csv(filename, index=False)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--currdate', type=str, default=None)
    config = parser.parse_args()
    run(config)