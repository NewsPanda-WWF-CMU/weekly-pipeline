# NewsPanda Weekly Pipeline
NewsPanda is a collaboration between Carnegie Mellon University and the World Wide Fund for Nature. This project aims to make extracting conservation-related news articles easier. It scrapes, classifies, and performs some post-processing analysis on these articles. 

The entire pipeline is run on a weekly basis. Currently, this project focuses on news articles in India and Nepal. We are working towards supporting NewsPanda for different countries and languages.

## Quickstart
1. Setup `database.yaml`.
2. Download pretrained model from this [link](https://drive.google.com/file/d/1dKKwpj43PWIg1xuNRbVlMQ4pWkKqL37j/view?usp=sharing) and place it inside `./model` as `./model/model_v0.pt`. See [this README](./model/README.md) for more details. 
3. Run `pipeline.sh`.