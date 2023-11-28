import os
import time
import argparse
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_file(browser, driver_path, download_path):
    logging.info(f"Initializing {browser} browser for download.")
    if browser == "firefox":
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.headless = True
        service = FirefoxService(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=firefox_options)
    elif browser == "chrome":
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        logging.error("Invalid browser selection. Choose either 'firefox' or 'chrome'.")
        assert browser in ["firefox", "chrome"]

    logging.info("Accessing the Parivesh website.")
    driver.get("https://parivesh.nic.in/Online_Proposalby_Status_Forest.aspx?pids=Accepted&st=new&state=-1&year=-1&cat=-1")
    
    logging.info("Waiting for the download button to be clickable.")
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_ImageButton2")))
    button.click()

    logging.info("Downloading file. Waiting for download to complete.")
    while not os.path.exists(f"{download_path}/Records.xls"):
        time.sleep(1)
    time.sleep(20)
    logging.info("Finished downloading Parivesh files!")
    driver.quit()

def create_parivesh_csv(currdate, download_path):
    logging.info("Creating CSV from the downloaded Excel file.")
    excel_path = f"{download_path}/Records.xls"
    df = pd.read_html(excel_path)[0]
    df.to_csv(f"parivesh-files/parivesh_{currdate}.csv", index=False)
    os.remove(excel_path)
    logging.info("CSV file created successfully.")

def run(config):
    logging.info("Starting the download and conversion process.")
    if "~" in config.download_path:
        home_dir = os.path.expanduser('~')
        config.download_path = config.download_path.replace('~', home_dir)
    download_file(config.browser, config.driver_path, config.download_path)
    create_parivesh_csv(config.currdate, config.download_path)
    logging.info("Process completed.")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--currdate', type=str, default=None)
    parser.add_argument('--browser', type=str, default='chrome', choices=['firefox', 'chrome'])
    parser.add_argument('--driver_path', type=str, default='./chromedriver', help="path to Firefox or Chrome driver")
    parser.add_argument('--download_path', type=str, default='~/Downloads', help="where files are downloaded to by default")
    config = parser.parse_args()
    run(config)
