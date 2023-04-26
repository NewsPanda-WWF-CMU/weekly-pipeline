import pandas as pd
import re

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

def keyword_search_single(sent, D, E, ngo):
    keywords = []
    for df in [D, E, ngo]:
        curr_keywords = df.L2.tolist()
        curr_keywords = [i.strip().lower() for i in curr_keywords]
        curr_cats = df.L1.tolist()
        curr_text = clean(sent).split(' ')
        for c, word in zip(curr_cats, curr_keywords):
            if word in curr_text:
                keywords.append("{}: {}".format(c, word))
    return keywords

example = "Corbetts legacy, perhaps, lies in his early understanding of the link between conservation and community. This path between protection and local welfare is a very tough path and Jim Corbett had a coherent philosophy. Not only did he try to work towards protection of tigers but he was equally sensitive and compassionate towards the villagers, says Bhartari who has supervised research both on Corbett’s legacy and the history of Corbett National Park at the Wildlife Institute of India. He was instrumental in setting up Chhoti Haldwani as a model Kumaoni village. In Corbett, there has been a connection between conservation and local people. When Corbett National Park was formed, the initial boundary was very carefully determined that no rights of villagers were affected. From its inception, it has enjoyed the goodwill of people, because of Jim Corbett. I think thats his legacy, the unique relationship between people and conservation. Today we talk of development, of agriculture, but Corbett spent much of his latter life in trying to improve agriculture in Chhoti Haldwani by spreading seeds, strengthening irrigation and encouraging villagers to grow not just for consumption but for sale. In his house itself, he let a worker run a tea shop to give him a source of living and finally when he went to Kenya, he gifted all his land to the villagers he had settled in Chhoti Haldwani, says Bhartari."
example = "A 45-year-old man from Chamrajanagar in Karnataka was arrested by the Forest Department for attempting to hunt wild animals and also setting fire in forest areas in the Talavadi Forest Range in the Sathyamangalam Tiger Reserve here."
D = pd.read_csv("reference-files/Tag Terms - D.csv", names=["L1", "L2"])
E = pd.read_csv("reference-files/Tag Terms - E.csv", names=["L1", "L2"])
ngo = pd.read_csv("reference-files/Tag Terms - NGO.csv", names=["L1", "L2"])

k = keyword_search_single(example, D, E, ngo)
# print(k)

# ['Agriculture: tea', 'Conservation Keyword: conservation', 'Social: community', 'Species: wildlife']

