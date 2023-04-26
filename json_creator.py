import json
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--filename', type=str, required=True)
parser.add_argument('--currdate', type=str, required=True)
args = parser.parse_args()

df = pd.read_csv(args.filename)
df["OBJECTID"] = df.index+1
reordered_cols = ["OBJECTID"]
reordered_cols.extend(df.columns.tolist()[:-1])
df = df[reordered_cols]
df.to_json("ttt.json", orient="records")
with open("ttt.json") as f:
    ddd = json.load(f)

d = {}

# displayFieldName
d["displayFieldName"] = ''

# fieldAliases
fieldAliases = {}
for col in df.columns:
    fieldAliases[col]=col
d['fieldAliases'] = fieldAliases

# geometryType
d['geometrytype']='esriGeometryPoint'

# spatialReference
spatialReference = {'wkid': 4326, 'latestWkid': 4326}
d['spatialReference'] = spatialReference

# fields
fields = [{'name': 'OBJECTID', 'type': 'esriFieldTypeOID', 'alias': 'OBJECTID'},
{'name': 'aware', 'type': 'esriFieldTypeInteger', 'alias': 'aware'},
{'name': 'conservation_label', 'type': 'esriFieldTypeInteger', 'alias': 'conservation_label'},
{'name': 'infrastructure_label', 'type': 'esriFieldTypeInteger', 'alias': 'infrastructure_label'},
{'name': 'conservation_prediction', 'type': 'esriFieldTypeInteger', 'alias': 'conservation_prediction'},
{'name': 'infrastructure_prediction', 'type': 'esriFieldTypeInteger', 'alias': 'infrastructure_prediction'},
{'name': 'source_name', 'type': 'esriFieldTypeString', 'alias': 'source_name', 'length': 255},
{'name': 'loc', 'type': 'esriFieldTypeString', 'alias': 'loc', 'length': 255},
{'name': 'x', 'type': 'esriFieldTypeDouble', 'alias': 'x'},
{'name': 'y', 'type': 'esriFieldTypeDouble', 'alias': 'y'},
{'name': 'title', 'type': 'esriFieldTypeString', 'alias': 'title', 'length': 255},
{'name': 'description', 'type': 'esriFieldTypeString', 'alias': 'description', 'length': 270},
{'name': 'publishedAt', 'type': 'esriFieldTypeString', 'alias': 'publishedAt', 'length': 255},
{'name': 'url', 'type': 'esriFieldTypeString', 'alias': 'url', 'length': 255},
{'name': 'content', 'type': 'esriFieldTypeString', 'alias': 'content', 'length': 356},
{'name': 'confidence', 'type': 'esriFieldTypeDouble', 'alias': 'confidence'},
{'name': 'infrastructure_confidence', 'type': 'esriFieldTypeDouble', 'alias': 'infrastructure_confidence'},
{'name': 'D_agriculture', 'type': 'esriFieldTypeString', 'alias': 'D:agriculture', 'length': 255},
{'name': 'D_extractives___mining', 'type': 'esriFieldTypeString', 'alias': 'D:extractives - mining', 'length': 255},
{'name': 'D_social_conflict', 'type': 'esriFieldTypeString', 'alias': 'D:social conflict', 'length': 255},
{'name': 'D_illegal_wildlife_trade', 'type': 'esriFieldTypeString', 'alias': 'D:illegal wildlife trade', 'length': 255},
{'name': 'D_habitat_loss', 'type': 'esriFieldTypeString', 'alias': 'D:habitat loss', 'length': 255},
{'name': 'D_pollution', 'type': 'esriFieldTypeString', 'alias': 'D:pollution', 'length': 255},
{'name': 'D_fishing', 'type': 'esriFieldTypeString', 'alias': 'D:fishing', 'length': 255},
{'name': 'D_infrastructure', 'type': 'esriFieldTypeString', 'alias': 'D:infrastructure', 'length': 255},
{'name': 'D_species_loss', 'type': 'esriFieldTypeString', 'alias': 'D:species loss', 'length': 255},
{'name': 'D_extractives___oil_and_gas', 'type': 'esriFieldTypeString', 'alias': 'D:extractives - oil and gas', 'length': 255},
{'name': 'D_invasive_species', 'type': 'esriFieldTypeString', 'alias': 'D:invasive species', 'length': 255},
{'name': 'D_climate_change', 'type': 'esriFieldTypeString', 'alias': 'D:climate change', 'length': 255},
{'name': 'D_shipping', 'type': 'esriFieldTypeString', 'alias': 'D:shipping', 'length': 255},
{'name': 'D_governance', 'type': 'esriFieldTypeString', 'alias': 'D:governance', 'length': 255},
{'name': 'D_tourism', 'type': 'esriFieldTypeString', 'alias': 'D:tourism', 'length': 255},
{'name': 'E_species', 'type': 'esriFieldTypeString', 'alias': 'E:species', 'length': 255},
{'name': 'E_conservation_keyword', 'type': 'esriFieldTypeString', 'alias': 'E:conservation keyword', 'length': 255},
{'name': 'E_social', 'type': 'esriFieldTypeString', 'alias': 'E:social', 'length': 255},
{'name': 'E_terrestrial_habitat', 'type': 'esriFieldTypeString', 'alias': 'E:terrestrial habitat', 'length': 255},
{'name': 'E_marine_habitat', 'type': 'esriFieldTypeString', 'alias': 'E:marine habitat', 'length': 255},
{'name': 'E_freshwater_habitat', 'type': 'esriFieldTypeString', 'alias': 'E:freshwater habitat', 'length': 255},
{'name': 'E_atmosphere', 'type': 'esriFieldTypeString', 'alias': 'E:atmosphere', 'length': 255},
{'name': 'E_restoration', 'type': 'esriFieldTypeString', 'alias': 'E:restoration', 'length': 255},
{'name': 'NGO_ngo', 'type': 'esriFieldTypeString', 'alias': 'NGO:ngo', 'length': 255},
{'name': 'entities', 'type': 'esriFieldTypeString', 'alias': 'entities', 'length': 255},
{'name': 'entities_locs', 'type': 'esriFieldTypeString', 'alias': 'entities_locs', 'length': 255},
{'name': 'entities_orgs', 'type': 'esriFieldTypeString', 'alias': 'entities_orgs', 'length': 255},
{'name': 'entities_title', 'type': 'esriFieldTypeString', 'alias': 'entities_title', 'length': 255},
{'name': 'title_polarity', 'type': 'esriFieldTypeDouble', 'alias': 'title_polarity'},
{'name': 'description_polarity', 'type': 'esriFieldTypeDouble', 'alias': 'description_polarity'},
{'name': 'content_polarity', 'type': 'esriFieldTypeDouble', 'alias': 'content_polarity'}]
d['fields'] = fields

# features
features = []
for i in range(len(ddd)):
    curr_d = {}
    curr_d['attributes'] = ddd[i]
    curr_d['geometry'] = {'x': ddd[i]['x'], 'y':ddd[i]['y']}
    features.append(curr_d)
d['features'] = features

with open(f"news_labelled_{args.currdate}_shortlist.json", "w") as f:
    json.dump(d, f)