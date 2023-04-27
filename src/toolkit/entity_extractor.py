from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from tqdm import tqdm 

tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

entity_extractor = pipeline("ner", model=model, tokenizer=tokenizer)
# example = "Corbetts legacy, perhaps, lies in his early understanding of the link between conservation and community. This path between protection and local welfare is a very tough path and Jim Corbett had a coherent philosophy. Not only did he try to work towards protection of tigers but he was equally sensitive and compassionate towards the villagers, says Bhartari who has supervised research both on Corbett’s legacy and the history of Corbett National Park at the Wildlife Institute of India. He was instrumental in setting up Chhoti Haldwani as a model Kumaoni village. In Corbett, there has been a connection between conservation and local people. When Corbett National Park was formed, the initial boundary was very carefully determined that no rights of villagers were affected. From its inception, it has enjoyed the goodwill of people, because of Jim Corbett. I think thats his legacy, the unique relationship between people and conservation. Today we talk of development, of agriculture, but Corbett spent much of his latter life in trying to improve agriculture in Chhoti Haldwani by spreading seeds, strengthening irrigation and encouraging villagers to grow not just for consumption but for sale. In his house itself, he let a worker run a tea shop to give him a source of living and finally when he went to Kenya, he gifted all his land to the villagers he had settled in Chhoti Haldwani, says Bhartari."
# example = "A 45-year-old man from Chamrajanagar in Karnataka was arrested by the Forest Department for attempting to hunt wild animals and also setting fire in forest areas in the Talavadi Forest Range in the Sathyamangalam Tiger Reserve here."

# ner_results = entity_extractor(example)
# print(ner_results)

def get_entity_list(sent):
    if type(sent)==type("s"): sent = [sent]
    all_ners, all_locs, all_orgs = [], [], []
    for s in sent:
        ner_results = entity_extractor(s)
        for n in ner_results: 
            if n['word'][0]=='#':
                n['entity']='I'+n['entity'][1:]
        ners, locs, orgs = set(), set(), set()
        curr, curr_ent = "", ""
        for i in ner_results:
            if i['entity'][0]=='B' and curr=="":
                curr = i['word']
            elif i['entity'][0]=='I':
                if i['word'][0] == '#':
                    curr+= i['word'].replace('#','')
                else:
                    curr += " " + i['word']
            else: 
                if len(curr) > 1:
                    ners.add(curr)
                    if curr_ent=="LOC": 
                        locs.add(curr)
                    if curr_ent=="ORG":
                        orgs.add(curr)
                curr = i['word']
            curr_ent = i['entity'][2:]
        if len(curr) > 1:
            ners.add(curr)
            if curr_ent=="LOC": 
                locs.add(curr)
            if curr_ent=="ORG": 
                orgs.add(curr)
        all_ners.append(ners)
        all_locs.append(locs)
        all_orgs.append(orgs)
    if type(sent)==type("s"): 
        all_ners = all_ners[0]
        all_locs = all_locs[0]
        all_orgs = all_orgs[0]
    return all_ners, all_locs, all_orgs

# print(get_entity_list(example))


# [{'entity': 'B-PER', 'score': 0.99081236, 'index': 1, 'word': 'Corbett', 'start': 0, 'end': 7}, 
# {'entity': 'B-PER', 'score': 0.99969965, 'index': 33, 'word': 'Jim', 'start': 178, 'end': 181}, 
# {'entity': 'I-PER', 'score': 0.99888176, 'index': 34, 'word': 'Corbett', 'start': 182, 'end': 189}, 
# {'entity': 'B-PER', 'score': 0.9987512, 'index': 65, 'word': 'B', 'start': 349, 'end': 350}, 
# {'entity': 'I-PER', 'score': 0.61289686, 'index': 66, 'word': '##hart', 'start': 350, 'end': 354}, 
# {'entity': 'I-PER', 'score': 0.7242125, 'index': 67, 'word': '##ari', 'start': 354, 'end': 357}, 
# {'entity': 'B-PER', 'score': 0.9976055, 'index': 74, 'word': 'Corbett', 'start': 394, 'end': 401}, 
# {'entity': 'B-LOC', 'score': 0.96409553, 'index': 82, 'word': 'Corbett', 'start': 430, 'end': 437}, 
# {'entity': 'I-LOC', 'score': 0.92487365, 'index': 83, 'word': 'National', 'start': 438, 'end': 446}, 
# {'entity': 'I-LOC', 'score': 0.9825907, 'index': 84, 'word': 'Park', 'start': 447, 'end': 451}, 
# {'entity': 'B-ORG', 'score': 0.9933216, 'index': 87, 'word': 'Wildlife', 'start': 459, 'end': 467}, 
# {'entity': 'I-ORG', 'score': 0.9965251, 'index': 88, 'word': 'Institute', 'start': 468, 'end': 477}, 
# {'entity': 'I-ORG', 'score': 0.9968893, 'index': 89, 'word': 'of', 'start': 478, 'end': 480}, 
# {'entity': 'I-ORG', 'score': 0.97746754, 'index': 90, 'word': 'India', 'start': 481, 'end': 486}, 
# {'entity': 'B-LOC', 'score': 0.9883366, 'index': 98, 'word': 'Ch', 'start': 522, 'end': 524}, 
# {'entity': 'I-LOC', 'score': 0.97295606, 'index': 99, 'word': '##hot', 'start': 524, 'end': 527}, 
# {'entity': 'I-LOC', 'score': 0.9948411, 'index': 100, 'word': '##i', 'start': 527, 'end': 528}, 
# {'entity': 'I-LOC', 'score': 0.9966107, 'index': 101, 'word': 'Hal', 'start': 529, 'end': 532}, 
# {'entity': 'I-LOC', 'score': 0.9958568, 'index': 102, 'word': '##d', 'start': 532, 'end': 533}, 
# {'entity': 'I-LOC', 'score': 0.9937927, 'index': 103, 'word': '##wan', 'start': 533, 'end': 536}, 
# {'entity': 'I-LOC', 'score': 0.9919613, 'index': 104, 'word': '##i', 'start': 536, 'end': 537}, 
# {'entity': 'B-LOC', 'score': 0.8447476, 'index': 108, 'word': 'Ku', 'start': 549, 'end': 551}, 
# {'entity': 'I-LOC', 'score': 0.64085007, 'index': 109, 'word': '##ma', 'start': 551, 'end': 553}, 
# {'entity': 'B-LOC', 'score': 0.5688019, 'index': 114, 'word': 'Corbett', 'start': 569, 'end': 576}, 
# {'entity': 'B-LOC', 'score': 0.9555027, 'index': 128, 'word': 'Corbett', 'start': 650, 'end': 657}, 
# {'entity': 'I-LOC', 'score': 0.9365285, 'index': 129, 'word': 'National', 'start': 658, 'end': 666}, 
# {'entity': 'I-LOC', 'score': 0.97272384, 'index': 130, 'word': 'Park', 'start': 667, 'end': 671}, 
# {'entity': 'B-PER', 'score': 0.99959075, 'index': 164, 'word': 'Jim', 'start': 848, 'end': 851}, 
# {'entity': 'I-PER', 'score': 0.9984753, 'index': 165, 'word': 'Corbett', 'start': 852, 'end': 859}, 
# {'entity': 'B-PER', 'score': 0.99851745, 'index': 192, 'word': 'Corbett', 'start': 994, 'end': 1001}, 
# {'entity': 'B-LOC', 'score': 0.9889008, 'index': 205, 'word': 'Ch', 'start': 1068, 'end': 1070}, 
# {'entity': 'I-LOC', 'score': 0.9869157, 'index': 206, 'word': '##hot', 'start': 1070, 'end': 1073}, 
# {'entity': 'I-LOC', 'score': 0.99478817, 'index': 207, 'word': '##i', 'start': 1073, 'end': 1074}, 
# {'entity': 'I-LOC', 'score': 0.99786407, 'index': 208, 'word': 'Hal', 'start': 1075, 'end': 1078}, 
# {'entity': 'I-LOC', 'score': 0.9960196, 'index': 209, 'word': '##d', 'start': 1078, 'end': 1079}, 
# {'entity': 'I-LOC', 'score': 0.99402136, 'index': 210, 'word': '##wan', 'start': 1079, 'end': 1082}, 
# {'entity': 'I-LOC', 'score': 0.98902786, 'index': 211, 'word': '##i', 'start': 1082, 'end': 1083}, 
# {'entity': 'B-LOC', 'score': 0.9997859, 'index': 257, 'word': 'Kenya', 'start': 1313, 'end': 1318}, 
# {'entity': 'B-LOC', 'score': 0.9903835, 'index': 271, 'word': 'Ch', 'start': 1378, 'end': 1380}, 
# {'entity': 'I-LOC', 'score': 0.97861207, 'index': 272, 'word': '##hot', 'start': 1380, 'end': 1383}, 
# {'entity': 'I-LOC', 'score': 0.9825128, 'index': 273, 'word': '##i', 'start': 1383, 'end': 1384}, 
# {'entity': 'I-LOC', 'score': 0.9977585, 'index': 274, 'word': 'Hal', 'start': 1385, 'end': 1388}, 
# {'entity': 'I-LOC', 'score': 0.9940227, 'index': 275, 'word': '##d', 'start': 1388, 'end': 1389}, 
# {'entity': 'I-LOC', 'score': 0.98735094, 'index': 276, 'word': '##wan', 'start': 1389, 'end': 1392}, 
# {'entity': 'I-LOC', 'score': 0.983621, 'index': 277, 'word': '##i', 'start': 1392, 'end': 1393}, 
# {'entity': 'B-PER', 'score': 0.9976117, 'index': 280, 'word': 'B', 'start': 1400, 'end': 1401}, 
# {'entity': 'I-PER', 'score': 0.6490687, 'index': 281, 'word': '##hart', 'start': 1401, 'end': 1405}, 
# {'entity': 'I-PER', 'score': 0.8614247, 'index': 282, 'word': '##ari', 'start': 1405, 'end': 1408}]