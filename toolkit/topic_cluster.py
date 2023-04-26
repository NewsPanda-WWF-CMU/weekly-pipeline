import pandas as pd 
from tqdm import tqdm 
import ast

def get_overlaps(list1, list2, to_exclude=["india", "nepal"]):
    overlaps = []
    for l in list1:
        if l in list2:
            overlaps.append(l)
    return overlaps

def is_valid(l, new_idx):
    has_new=False
    has_old=False
    for i in l:
        if int(i) >= new_idx: has_new=True
        if int(i) < new_idx: has_old=True
    return has_old and has_new

def clique_main(df, threshold, new_idx):
    nodes = []
    for i in tqdm(range(len(df))):
        for j in range(i+1, len(df)):
            list1 = df["tags"][i]
            list2 = df["tags"][j]
            overlaps = get_overlaps(list1, list2)
            if len(overlaps) > threshold:
                nodes.append((i,j))
    

    with open("edgelist.txt", "w") as f:
        for np in nodes:
            f.write(f"{np[0]},{np[1]}\n")

    import networkx as nx
    G = nx.read_edgelist("edgelist.txt",delimiter=',')

    cliques = []
    for clq in nx.clique.find_cliques(G):
        if len(clq) > 2:
            if is_valid(clq, new_idx):
                cliques.append(clq)
    return cliques

def get_cluster_for_loc(loc, olddf, newdf, threshold=3):
    olddf = olddf[olddf["loc"]==loc]
    olddf = olddf[olddf["source_name"] != "Parivesh"]
    newdf = newdf[newdf["loc"]==loc]
    newdf = newdf[newdf["source_name"] != "Parivesh"]
    if len(newdf)==0: return None
    this_week_keywords, curr_cluster = [], []
    for t in newdf["tags"]:
        this_week_keywords.extend(t)
    this_week_keywords = list(set(this_week_keywords))

    threshold = max(threshold, len(this_week_keywords)/3)
    if len(this_week_keywords)>=20:
        threshold = len(this_week_keywords)/2

    for i in olddf.iterrows():
        overlaps = get_overlaps(this_week_keywords, i[1]["tags"])
        if (len(overlaps) > threshold):
            curr_cluster.append(i[0])
    if len(curr_cluster)==0: 
        if len(newdf)<3:
            return None
        else:
            for i in newdf.iterrows():
                curr_cluster.append(i[0])
            return curr_cluster
    for i in newdf.iterrows():
        curr_cluster.append(i[0])
    return curr_cluster


def generate_clusters(df, past_articles):
    topic_cols = ['D:agriculture', 'D:extractives - mining', 'D:social conflict',
        'D:illegal wildlife trade', 'D:habitat loss', 'D:pollution',
        'D:fishing', 'D:infrastructure', 'D:species loss',
        'D:extractives - oil and gas', 'D:invasive species', 'D:climate change',
        'D:shipping', 'D:governance', 'D:tourism', 'E:species',
        'E:conservation keyword', 'E:social', 'E:terrestrial habitat',
        'E:marine habitat', 'E:freshwater habitat', 'E:atmosphere',
        'E:restoration', 'NGO:ngo']
    topic_cols = ["entities_locs", "entities_orgs", "entities_title"]

    combined = pd.concat([past_articles, df]).reset_index(drop=True)
    combined["tags"] = combined["loc"]
    for i in range(len(combined)):
        curr = []
        for t in topic_cols:
            if combined[t][i]=="[set()]": a = []
            else: a = list(ast.literal_eval(combined[t][i][1:-1]))
            a = [i.lower().strip() for i in a]
            curr = curr + a
        combined["tags"][i] = list(set(curr))

    locs_this_week = list(set(df["loc"].tolist()))
    
    olddf, newdf = combined.iloc[:len(past_articles)], combined.iloc[len(past_articles):]
    clusters = []
    for currloc in locs_this_week:
        currcluster = get_cluster_for_loc(currloc, olddf, newdf)
        if currcluster is None: continue
        clusters.append(currcluster)
        aaa = newdf[newdf["loc"]==currloc]
        this_week_keywords, curr_cluster = [], []
        for t in aaa["tags"]:
            this_week_keywords.extend(t)
        this_week_keywords = list(set(this_week_keywords))
        print(this_week_keywords)

    print(clusters)
    return combined, clusters

    ### OLD:
    # cliques = clique_main(combined, threshold=3, new_idx=len(past_articles))
    # if len(cliques) >= 3:
    #     return combined, cliques

    # cliques = clique_main(combined, threshold=2, new_idx=len(past_articles))
    # if len(cliques) >= 3:
    #     return combined, cliques

    # cliques = clique_main(combined, threshold=1, new_idx=len(past_articles))
    # if len(cliques) >= 3:
    #     return combined, cliques
    # print("NONE")


def clique_cleaner(cliques, new_idx):
    lengthprefs = {5:1, 4:2, 6:3, 3:4, 7:5}
    cliques2 = []
    for c in cliques:
        if len(c) >= 7:
            cliques2.append((7, sorted(c)))
        else:
            cliques2.append((lengthprefs[len(c)], sorted(c)))
    cliques2 = sorted(cliques2)
    
    newused = {}
    final_cliques = []
    cnts = set()
    for c in cliques2:
        c = c[1]
        num_bad_entries = 0
        cap = len(c)//2
        for i in c:
            if i in cnts:
                num_bad_entries+=1
        if num_bad_entries > cap:
            continue
        else:
            isbad = False
            for i in c:
                if int(i) >= new_idx:
                    if int(i) in newused:
                        if newused[int(i)] >= 1:
                            isbad=True
            if isbad: continue

            final_cliques.append(c)
            for i in c:
                cnts.add(i)
            for i in c:
                if int(i) >= new_idx:
                    if int(i) in newused:
                        newused[int(i)]+=1
                    else:
                        newused[int(i)]=1
                        
    return final_cliques

    