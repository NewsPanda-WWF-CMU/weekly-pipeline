import os
import time
import argparse
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

def download_file(browser, driver_path, download_path):
    if browser=="firefox":
        firefox_options = selenium.webdriver.firefox.options.Options()
        firefox_options.headless = True  # set to True if you want to run in headless mode
        driver = webdriver.Firefox(options=firefox_options, executable_path='./geckodriver')
    elif browser=="chrome":
        chrome_options = selenium.webdriver.chrome.options.Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options, executable_path='./chromedriver')
    else:
        assert browser in ["firefox", "chrome"]

    driver.get("https://parivesh.nic.in/Online_Proposalby_Status_Forest.aspx?pids=Accepted&st=new&state=-1&year=-1&cat=-1")
    button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ImageButton2")

    button.click()
    driver.implicitly_wait(120)

    while not os.path.exists(f"{download_path}/Records.xls"):
        time.sleep(1)
    time.sleep(20)
    print("Finished downloading Parivesh files!")


def create_parivesh_csv(currdate, download_path):
    excel_path = f"{download_path}/Records.xls"
    df = pd.read_html(excel_path)[0]
    print(df)
    df.to_csv(f"parivesh-files/parivesh_{currdate}.csv", index=False)
    os.system(f"rm {excel_path}")


def run(config):
    if "~" in config.download_path:
        home_dir = os.path.expanduser('~')
        config.download_path = config.download_path.replace('~', home_dir)

    download_file(config.browser, config.driver_path, config.download_path)
    create_parivesh_csv(config.currdate, config.download_path)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--currdate', type=str, default=None)
    parser.add_argument('--browser', type=str, default='firefox', choices=['firefox', 'chrome'])
    parser.add_argument('--driver_path', type=str, default='./geckodriver', help="path to Firefox or Chrome driver")
    parser.add_argument('--download_path', type=str, default='~/Downloads', help="where files are downloaded to by default")
    config = parser.parse_args()
    run(config)