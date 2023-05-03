# NewsPanda Weekly Pipeline
NewsPanda is a collaboration between Carnegie Mellon University and the World Wide Fund for Nature. This project aims to make extracting conservation-related news articles easier. It scrapes, classifies, and performs some post-processing analysis on these articles. 

The entire pipeline is run on a weekly basis. Currently, this project focuses on news articles in India and Nepal. We are working towards supporting NewsPanda for different countries and languages.

## Quickstart
1. Setup `database.yaml`.
2. Download pretrained model from this [link](https://drive.google.com/file/d/1dKKwpj43PWIg1xuNRbVlMQ4pWkKqL37j/view?usp=sharing) and place it inside `./model` as `./model/model_v0.pt`. See [this README](./model/README.md) for more details. 
3. Setup Selenium driver and Google Drive authentication. (See instructions below.)
4. Run `pipeline.sh`.

## Setup Selenium Driver
In order for `src/parivesh_downloader.py` to work properly, you will need to first have a driver executable for either Chrome or Firefox. (Note: You need to make sure that you also have the browser installed, and that the driver version is compatible with the browser version.) 
- Chrome: Download `chromedriver` [here](https://chromedriver.chromium.org/downloads)
- Firefox: Download `geckodriver` [here](https://github.com/mozilla/geckodriver/releases)

Once you have downloaded your `chromedriver` or `geckodriver`, indicate the path to it using the `--driver_path` argument in `src/parivesh_downloader.py` (The default is `./geckodriver`)

## Setup Google Drive Authentication
In order for `src/google_drive_uploader.py` to work properly, you will need to set up authentication for Google Drive. You will need `client_secrets.json`, `credentials.json`, and `settings.yaml` in your project directory. More detailed instructions can be found [here](https://github.com/sedrickkeh/cheat-sheet/tree/master/pydrive).