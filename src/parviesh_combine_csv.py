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
from selenium.webdriver.support.ui import Select

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_checkpoint(checkpoint_file='last_checkpoint.txt'):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as file:
            return file.read().strip()
    return None

def write_checkpoint(region, checkpoint_file='last_checkpoint.txt'):
    with open(checkpoint_file, 'w') as file:
        file.write(region)


def cleanup(download_path, keep_combined_csv=True):
    for fname in os.listdir(download_path):
        if fname.endswith('.xls') or fname.endswith('last_checkpoint.txt') or fname.endswith('.csv') and not (keep_combined_csv and fname == 'combined_parivesh.csv'):
            os.remove(os.path.join(download_path, fname))

def wait_for_download(download_path):
    logging.info("Waiting for the file to download.")
    while not any(fname.endswith(".xls") for fname in os.listdir(download_path)):
        time.sleep(1)
    time.sleep(5)  # Additional wait to ensure file is fully downloaded

def get_state_options(driver):
    logging.info("Fetching state options for the selected region.")
    select_state = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddl3"))
    return [option.get_attribute('value') for option in select_state.options if option.get_attribute('value') != 'Select']

def download_and_process_files(driver, region, region_name, download_path, currdate):
    logging.info(f"Processing region - {region_name}")
    # Select Region
    select_region = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddl1"))
    select_region.select_by_value(region)

    # Click Search
    search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Button1")))
    search_button.click()

    # Wait for the state dropdown to be populated
    WebDriverWait(driver, 10).until(
        lambda driver: Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddl3")).options[1].get_attribute('value') != 'Select'
    )
    search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Button1")))

    # Fetch state options for the selected region
    states = get_state_options(driver)

    logging.info(f"Total States:{len(states)}")
    for i, state in enumerate(states, 1):
        logging.info(f"Processing state {state} ({i}/{len(states)}) in region {region_name}")
        # Select State
        select_state = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddl3"))
        select_state.select_by_value(state)

        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Button1")))
        search_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ImageButton2")))

        # Click Export to CSV
        export_button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ImageButton2")
        export_button.click()

        # Wait for download to complete
        wait_for_download(download_path)

        # Convert to CSV and store
        for fname in os.listdir(download_path):
            if fname.endswith(".xls"):
                logging.info(f"Converting {fname} to CSV.")
                file_path = os.path.join(download_path, fname)
                with open(file_path, 'r') as file:
                    content = file.read().strip()
                    if not content or '<table' not in content:
                        logging.info(f"File {fname} is empty or does not contain table data. Skipping.")
                        os.remove(file_path)
                        continue
                df = pd.read_html(file_path)[0]
                csv_name = f"parivesh_{region_name}_{state}_{currdate}.csv"
                df.to_csv(os.path.join(download_path, csv_name), index=False)
                os.remove(file_path)

def run(config):
    logging.info("Starting the region and state data extraction process.")
    if "~" in config.download_path:
        home_dir = os.path.expanduser('~')
        config.download_path = config.download_path.replace('~', home_dir)

    # Set up WebDriver
    options = webdriver.ChromeOptions() if config.browser == 'chrome' else webdriver.FirefoxOptions()
    options.add_argument('--headless')
    service_class = ChromeService if config.browser == 'chrome' else FirefoxService
    service = service_class(executable_path=config.driver_path)
    driver_class = webdriver.Chrome if config.browser == 'chrome' else webdriver.Firefox
    driver = driver_class(service=service, options=options)

    driver.get("https://parivesh.nic.in/Online_Proposalby_Status_Forest.aspx?pids=Accepted&st=new&state=-1&year=-1&cat=-1")

    # Define regions
    regions = ['1', '2', '3', '5', '8', '9', '14', '20', '15', '12', '13', '19', '6', '10', '17', '11', '7', '16', '18']
    region_names = {
        '1': 'Bangalore',
        '2': 'Bhopal',
        '3': 'Bhubaneswar',
        '5': 'Chandigarh',
        '8': 'Chennai',
        '9': 'Dehradun',
        '14': 'Gandhinagar',
        '20': 'Guwahati',
        '15': 'Hyderabad',
        '12': 'Jaipur',
        '13': 'Jammu',
        '19': 'Kolkata',
        '6': 'Lucknow',
        '10': 'Nagpur',
        '17': 'Raipur',
        '11': 'Ranchi',
        '7': 'Shillong',
        '16': 'Shimla',
        '18': 'Vijayawada'
    }
    last_checkpoint = read_checkpoint()

    started = False
    total_regions = len(regions)
    for i, region in enumerate(regions, 1):
        region_name = region_names[region]
        if last_checkpoint is None or started or region == last_checkpoint:
            started = True
            logging.info(f"Starting processing for region {region_name} ({i}/{total_regions})")
            download_and_process_files(driver, region, region_name, config.download_path, config.currdate)
            write_checkpoint(region)
            logging.info(f"Completed processing for region {region_name} ({i}/{total_regions})")


        # Combine all CSV files into one
    all_csv_files = [f for f in os.listdir(config.download_path) if f.endswith('.csv')]
    combined_df = pd.concat([pd.read_csv(os.path.join(config.download_path, f)) for f in all_csv_files], ignore_index=True)
    combined_df.to_csv(os.path.join(config.download_path, f"parivesh-files/parivesh_{currdate}.csv"), index=False)
    logging.info("All regions and states processed. Combined CSV created.")
    cleanup(config.download_path)
    logging.info("Cleanup completed.")

    driver.quit()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--currdate', type=str, default=time.strftime("%Y%m%d"))  # Default to current date if not specified
    parser.add_argument('--browser', type=str, default='chrome', choices=['firefox', 'chrome'])
    parser.add_argument('--driver_path', type=str, default='./chromedriver', help="path to Firefox or Chrome driver")
    parser.add_argument('--download_path', type=str, default='./', help="where files are downloaded to by default")
    config = parser.parse_args()
    run(config)