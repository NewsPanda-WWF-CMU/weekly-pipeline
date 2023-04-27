import pandas as pd
import re
from transformers import AutoTokenizer, AutoModel
import torch
import random
import numpy as np

def clean(text):
    text = text.strip().lower()
    text = re.sub('[^A-Za-z0-9 ]+', '', text)
    return text

def do_keyword_search(df, keywords, prefix):
    for l1 in keywords.L1.value_counts().keys():
        has_keywords = []
        curr_df = keywords[keywords["L1"] == l1.strip()]
        curr_keywords = curr_df.L2.tolist()
        curr_keywords = [i.strip().lower() for i in curr_keywords]
        for idx, row in df.iterrows():
            curr_has_keywords = []
            # Check if keyword appears in title OR description OR content
            curr_text = ""
            try: curr_text = clean(row.content).split(' ')
            except: pass
            try: curr_text += clean(row.title).split(' ')
            except: pass
            try: curr_text += clean(row.description).split(' ')
            except: pass
            for word in curr_keywords:
                if word in curr_text:
                    curr_has_keywords.append(word)
            has_keywords.append(','.join(curr_has_keywords))
        df["{}:{}".format(prefix, l1.strip().lower())] = has_keywords
    return df

def add_keywords_tags(df):
    D = pd.read_csv("reference-files/Tag Terms - D.csv", names=["L1", "L2"])
    E = pd.read_csv("reference-files/Tag Terms - E.csv", names=["L1", "L2"])
    ngo = pd.read_csv("reference-files/Tag Terms - NGO.csv", names=["L1", "L2"])
    df = do_keyword_search(df, D, "D")
    df = do_keyword_search(df, E, "E")
    df = do_keyword_search(df, ngo, "NGO")
    return df

def get_tokenizer_and_model(model_name):
    assert model_name.lower() in ["bert", "distilbert", "roberta", "bert-large", "roberta-large"]
    print(model_name.lower())
    if model_name.lower()=="bert":
        tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        bertmodel = AutoModel.from_pretrained('bert-base-uncased')
    elif model_name.lower()=="distilbert":
        tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        bertmodel = AutoModel.from_pretrained('distilbert-base-uncased')
    elif model_name.lower()=="roberta":
        tokenizer = AutoTokenizer.from_pretrained('roberta-base')
        bertmodel = AutoModel.from_pretrained('roberta-base')
    elif model_name.lower()=="bert-large":
        tokenizer = AutoTokenizer.from_pretrained('bert-large-uncased')
        bertmodel = AutoModel.from_pretrained('bert-large-uncased')
    elif model_name.lower()=="roberta-large":
        tokenizer = AutoTokenizer.from_pretrained('roberta-large')
        bertmodel = AutoModel.from_pretrained('roberta-large')
    return tokenizer, bertmodel

def set_random_seeds(seed):
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)