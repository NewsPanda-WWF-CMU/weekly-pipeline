import numpy as np
import pandas as pd
import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import torch
import transformers as ppb
import argparse
from textblob import TextBlob
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm 
from datetime import datetime
from utils import add_keywords_tags
from toolkit.entity_extractor import get_entity_list
from toolkit.geolocator import get_geomap

def get_tokenizer_and_model(model_name):
    assert model_name.lower() in ["bert", "distilbert", "roberta"]
    print(model_name.lower())
    if model_name.lower()=="bert":
        tokenizer = ppb.BertTokenizer.from_pretrained('bert-base-uncased')
        bertmodel = ppb.BertModel.from_pretrained('bert-base-uncased')
    elif model_name.lower()=="distilbert":
        tokenizer = ppb.DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
        bertmodel = ppb.DistilBertModel.from_pretrained('distilbert-base-uncased')
    elif model_name.lower()=="roberta":
        tokenizer = ppb.RobertaTokenizer.from_pretrained('roberta-base')
        bertmodel = ppb.RobertaModel.from_pretrained('roberta-base')
    return tokenizer, bertmodel


class MyModel(torch.nn.Module):
    def __init__(self, config, bertmodel):
        super(MyModel, self).__init__()
        self.bertmodel = bertmodel
        self.fc1 = torch.nn.Linear(768 + 53, 768)
        self.fc2 = torch.nn.Linear(config.fc2dim, 2)
        self.relu = torch.nn.ReLU()
        self.dropout = torch.nn.Dropout(config.dropout)
        
    def forward(self, input_ids, attention_mask, prep_features):
        a = self.bertmodel(input_ids, attention_mask=attention_mask)
        x1 = self.bertmodel(input_ids, attention_mask=attention_mask).last_hidden_state[:,0,:]
        x2 = prep_features
        x = torch.cat((x1, x2), dim=1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

def get_df_from_file(config, engine):
    if config.load_from_db:
        query = f"select * from {config.load_input_file}"
        # Columns: (['index', 'source_id', 'source_name', 'author', 'title', 'description',
        #    'url', 'urlToImage', 'publishedAt', 'content', 'loc', 'news_id',
        #    'loc_id', 'look', 'iso3'])
        with engine.begin() as connection:
            df = pd.read_sql(query, connection)
    else:
        df = pd.read_csv(config.load_input_file, lineterminator='\n')
    return df


def run(config):
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
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

    tokenizer, bertmodel = get_tokenizer_and_model(config.model_name)

    model = MyModel(config, bertmodel)
    model.load_state_dict(torch.load(config.model_path))
    model.to(device)
    model.eval()

    # Load from file:
    if config.load_input_file is not None:
        df = get_df_from_file(config, engine)
        df = df[df['content'].notna()]
        titles = df.title.tolist()
        descriptions = df.description.tolist()
        contents = df.content.tolist()

        # Train topic model
        vectorizer = TfidfVectorizer()
        vectorizer.fit(contents)
        vector = vectorizer.transform(contents)
        lda = LatentDirichletAllocation(n_components=50, random_state=42)
        lda.fit(vector)
        topics = lda.transform(vector)

        out_predictions, out_confidence = [], []
        sents_1, sents_2, sents_3 = [], [], []
        for idx, x in tqdm(enumerate(contents), total=len(contents)):
            x = tokenizer(x, truncation=True, padding="max_length", max_length=512, return_tensors = "pt")
            curr_topic = topics[idx]
            try: sent1=TextBlob(titles[idx]).sentiment.polarity
            except: sent1=0.0
            try: sent2=TextBlob(descriptions[idx]).sentiment.polarity
            except: sent2=0.0
            try: sent3=TextBlob(contents[idx]).sentiment.polarity
            except: sent3=0.0
            curr_sent = np.array([sent1, sent2, sent3])
            sents_1.append(sent1)
            sents_2.append(sent2)
            sents_3.append(sent3)
            combined = np.concatenate((curr_sent, curr_topic))
            prep_features = torch.from_numpy(combined).unsqueeze(0).float().to(device)

            input_ids = x["input_ids"].to(device)
            attention_mask = x["attention_mask"].to(device)
            outputs = model(input_ids, attention_mask, prep_features)
            scores = torch.softmax(outputs[0], axis=0)
            if scores[0]>config.threshold:
                out_predictions.append(0)
            else:
                out_predictions.append(1)
            confidence = torch.max(scores)
            out_confidence.append(confidence.item())
        df["label"] = out_predictions
        df["confidence"] = out_confidence
        if config.save_name is None:
            config.save_name = "news_labelled_{}".format(datetime.today().strftime('%Y-%m-%d'))
        df = add_keywords_tags(df)
        print(df.columns)
        
        cols_to_remove = ['label_conservation_wwf', 'label_infrastructure_wwf', 'label_conservation_david', 'group']
        for ctr in cols_to_remove:
            try:
                df = df.drop([ctr], axis=1)
            except: 
                continue
            
        df = df.rename({'label': 'conservation_prediction'}, axis=1)
        df["infrastructure_prediction"] = np.zeros((len(df), 1))
        df["infrastructure_confidence"] = np.zeros((len(df), 1))
        df["conservation_label"] = ["" for _ in range(len(df))]
        df["infrastructure_label"] = ["" for _ in range(len(df))]
        df["title_polarity"] = sents_1
        df["description_polarity"] = sents_2
        df["content_polarity"] = sents_3

        # Geolocation
        x_arr, y_arr = [], []
        if config.skip_geolocation:
            x_arr = [0 for i in range(len(df))]
            y_arr = [0 for i in range(len(df))]
        else:
            geomap = get_geomap()
            for l in df["loc"].tolist():
                if l in geomap:
                    x_arr.append(geomap[l][0])
                    y_arr.append(geomap[l][1])
                else:
                    print("NOT IN GEOMAP:", l)
                    x_arr.append(0)
                    y_arr.append(0)
        df["x"] = x_arr
        df["y"] = y_arr

        # Entity extraction
        entities, entities_locs, entities_orgs = [], [], []
        for idx, c in tqdm(enumerate(df.content)):
            # print(f"{idx} / {len(df)}")
            if not config.world:
                ne, ne_locs, ne_orgs = get_entity_list(c)
            else:
                ne, ne_locs, ne_orgs = None, None, None
            entities.append(ne)
            entities_locs.append(ne_locs)
            entities_orgs.append(ne_orgs)
        df["entities"] = entities
        df["entities_locs"] = entities_locs
        df["entities_orgs"] = entities_orgs

        entities_title = []
        for idx, (c, c2) in tqdm(enumerate(zip(df.title, df.content))):
            if not config.world:
                if type(c) != type("hello"):
                    ne,_,_ = get_entity_list(c2)
                else:
                    ne, _, _ = get_entity_list(c)
            else:
                ne = None
            entities_title.append(ne)
        df["entities_title"] = entities_title

        # Rearrange columns
        cols_new = ['conservation_label', 'infrastructure_label', 'conservation_prediction', 'infrastructure_prediction', 'source_name', 'loc', 'x', 'y', 'title', 'description', 'publishedAt', 'url', 'content', 'confidence', 'infrastructure_confidence', 'D:agriculture', 'D:extractives - mining', 'D:social conflict', 'D:illegal wildlife trade', 'D:habitat loss', 'D:pollution', 'D:fishing', 'D:infrastructure', 'D:species loss', 'D:extractives - oil and gas', 'D:invasive species', 'D:climate change', 'D:shipping', 'D:governance', 'D:tourism', 'E:species', 'E:conservation keyword', 'E:social', 'E:terrestrial habitat', 'E:marine habitat', 'E:freshwater habitat', 'E:atmosphere', 'E:restoration', 'NGO:ngo', "entities", "entities_locs", "entities_orgs", "entities_title", "title_polarity", "description_polarity", "content_polarity"]
        df = df[cols_new]

        if config.world: config.save_name = config.save_name+"_world"
        df.to_csv(f"{config.save_name}_masterlist.csv", index=False)
        df.to_excel(f"{config.save_name}_masterlist.xlsx", index=False, engine='xlsxwriter')
        # df.to_json(f"{config.save_name}_masterlist.json", orient="records")

        df["aware"] = ["" for _ in range(len(df))]
        cols_new = ['aware', 'conservation_label', 'infrastructure_label', 'conservation_prediction', 'infrastructure_prediction', 'source_name', 'loc', 'x', 'y', 'title', 'description', 'publishedAt', 'url', 'content', 'confidence', 'infrastructure_confidence', 'D:agriculture', 'D:extractives - mining', 'D:social conflict', 'D:illegal wildlife trade', 'D:habitat loss', 'D:pollution', 'D:fishing', 'D:infrastructure', 'D:species loss', 'D:extractives - oil and gas', 'D:invasive species', 'D:climate change', 'D:shipping', 'D:governance', 'D:tourism', 'E:species', 'E:conservation keyword', 'E:social', 'E:terrestrial habitat', 'E:marine habitat', 'E:freshwater habitat', 'E:atmosphere', 'E:restoration', 'NGO:ngo', "entities", "entities_locs", "entities_orgs", "entities_title", "title_polarity", "description_polarity", "content_polarity"]
        df = df[cols_new]
        shortlist = df[df.conservation_prediction==1].reset_index(drop=True)
        shortlist.to_csv(f"{config.save_name}_shortlist.csv", index=False)
        shortlist.to_excel(f"{config.save_name}_shortlist.xlsx", index=False, engine='xlsxwriter')
        # shortlist.to_json(f"{config.save_name}_shortlist.json", orient="records")
        

    # Streaming input
    else:
        while(True):
            print("Enter input article: ")
            x = input()
            if (x == "stop"):
                break
            x_input = tokenizer(x, truncation=True, padding="max_length", max_length=512, return_tensors = "pt")
            prep_features = torch.zeros(1, 53).to(device)
            prep_features[0][2] = TextBlob(x).sentiment.polarity
            input_ids = x_input["input_ids"].to(device)
            attention_mask = x_input["attention_mask"].to(device)
            outputs = model(input_ids, attention_mask, prep_features)
            preds = torch.argmax(outputs[0], axis=0)
            print("Prediction: {}".format(preds))
            confidence = torch.max(torch.softmax(outputs[0], axis=0))
            print("Confidence: {}".format(confidence))
            print("====================\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', default="roberta", type=str, choices=["bert", "distilbert", "roberta"],
                        help='name of directory to store model/training contents')
    parser.add_argument('--fc2dim', default=768, type=int)
    parser.add_argument('--dropout', default=0.2, type=float)
    parser.add_argument('--model_path', required=True, type=str)
    parser.add_argument('--load_from_db', action='store_true')
    parser.add_argument('--load_input_file', type=str, default=None)
    parser.add_argument('--save_name', type=str, default=None)
    parser.add_argument('--threshold', type=float, default=0.5)
    parser.add_argument('--skip_geolocation', action='store_true')
    parser.add_argument('--world', action='store_true')

    config = parser.parse_args()
    print("Configs: {}".format(config))

    run(config)
    