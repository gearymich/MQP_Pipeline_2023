import os
import random
from typing import List

import spacy
from spacy.tokens import DocBin

import srsly
import typer
from rich import print

'''
Python Script to convert a raw doccano output for custom spacy model training
to a binary format that can be used to train a spacy model.

ALL_LABELS: labels that this script will expect to convert (all labels described in our db scheme)
DOCCANO_INPUT_JSONL = name of the file (a Spacy output) that this script reads from. Should not be changing. (.jsonl format)

Example CMDs (for each table):
Trafficker: python .\doccano_to_binary.py traffickerName traffickerBirthYear traffickerOrigin --filename spacy_annotations_trafficker
Product: python .\doccano_to_binary.py productName species --filename spacy_annotations_product
Event: python .\doccano_to_binary.py newsSource publishDate --filename spacy_annotations_event
EventProduct: python .\doccano_to_binary.py quantity quantityUnit price priceUnit --filename spacy_annotations_eventproduct

tags:
    --relations Export relations to .spacy. Default: False 
    --id "Export the ids of each doccano text, entites, and relation to .spacy. Default: False
    --filename Name of the file exported. Defualt: spacy_annotations_filtered.spacy

    --bootstrap Bootstrap the test set. Default: False
'''

EVENTPRODUCT_LABELS=['quantity', 'quantityUnit', 'price', 'priceUnit']
EVENTTRAFFICKER_LABELS=[]
EVENT_LABELS=['newsSource', 'publishDate']
PRODUCT_LABELS=['productName', 'species']
TRAFFICKER_LABELS=['traffickerName', 'traffickerBirthYear', 'traffickerOrigin']

ALL_LABELS = EVENTPRODUCT_LABELS + EVENTTRAFFICKER_LABELS + EVENT_LABELS + PRODUCT_LABELS + TRAFFICKER_LABELS + ['seizureLocation', ]
REDUCED_LABELS = ['publishDate', 'seizureLocation', 'traffickerName', 'traffickerBirthYear', 'species', 'productName' ]

DOCCANO_INPUT_JSONL = './source_data/all_final.jsonl'

# BINARY: ~80/10/10 train-test-val split
TOTAL_DOCS_LOADED = 300
TOTAL_TR_LOADED = 240
TOTAL_TE_LOADED = 30
TOTAL_VAL_LOADED = 30

def filterLabels(
    label_list: List[str], 
    relations=False, 
    withID=False
): 
    '''Filter the labels from the doccano output. Returns a list of dictionaries (.jsonl format)'''
    for label in label_list:
        if label not in ALL_LABELS: #TODO: Switch to ALL_LABELS when annotation work is finished
            print(f"the given label {label} does not exist within our Doccano annotation")
            print(f"Possible Labels:\n", *ALL_LABELS, sep=' ') #TODO: Switch to ALL_LABELS when annotation work is finished
            raise typer.Exit()

    final_jsonl = []
    for textLabels in srsly.read_jsonl(DOCCANO_INPUT_JSONL):
        relationList = textLabels.pop('relations')
        entList = textLabels.pop('entities')
        finalEntList = []
        finalRelationList = []

        # filter out entities in list with labels not being used            
        for ent in entList:
            if ent['label'] in label_list:
                finalEntList.append({"start": ent['start_offset'], "end": ent['end_offset'], "label": ent['label']} if not withID \
                    else {"id": ent['id'], "start": ent['start_offset'], "end": ent['end_offset'], "label": ent['label']})
        
        if relations:
            finalRelationList = relationList
  
        # return filtered + reformated entity
        textLabels['entities'] = finalEntList
        textLabels['relations'] = finalRelationList

        textLabels = {  "entities": textLabels.pop("entities"), "relations": textLabels.pop("relations"), 
                        "text": textLabels.pop("text")} \
                        if not withID else \
                    {   "id": textLabels.pop("id"),
                        "entities": textLabels.pop("entities"), "relations": textLabels.pop("relations"), 
                        "text": textLabels.pop("text")
                    }
    
        final_jsonl.append(textLabels)   

    return final_jsonl

'''Split a list of dictionaries (.jsonl format) into train, test, and validation sets'''
def train_test_val_split(jsonl):
    train_jsonl = []
    test_jsonl = []
    val_jsonl = []

    for i, textLabels in enumerate(jsonl):
        if i < TOTAL_TR_LOADED:
            train_jsonl.append(textLabels)
        elif i < TOTAL_TR_LOADED + TOTAL_TE_LOADED:
            test_jsonl.append(textLabels)
        else:
            val_jsonl.append(textLabels)
    
    return train_jsonl, test_jsonl, val_jsonl

def genBinaries(jsonl):
    '''Converts a list of dictionaries (.jsonl format) to a spacy DocBin object'''
    nlp = spacy.blank("en")
    db_train = DocBin()

    faultyDocs = []
    loadCnt = 0
    for textLabels in jsonl: # your training data, generator
        doc = nlp(textLabels['text'])
        ents = []
        for ent in textLabels['entities']:
            start, end, label = ent['start'], ent['end'], ent['label']
            span = doc.char_span(start, end, label=label)
            ents.append(span)
            
        try:
            doc.ents = ents

        except Exception as exc:
            print(exc)
            faultyDocs.append(exc)
            continue
        
        db_train.add(doc)
        loadCnt = loadCnt + 1
    
    return db_train, faultyDocs

def bootstrap_test_jsonl(test_jsonl, num_samples=TOTAL_TE_LOADED):
    '''bootstrap the test set'''
    bootstrapped_jsonl = []
    for _ in range(num_samples):
        a_json = random.choice(test_jsonl)
        bootstrapped_jsonl.append(a_json)
    
    return bootstrapped_jsonl

def main(
    # label_list: List[str], 
    relations: bool = typer.Option(False, "--relations/", help="Export relations to .spacy. Default: False"), 
    withID: bool = typer.Option(False, "--id/", help="Export the ids of each doccano text, entites, and relation to .spacy. Default: False"),
    filename: str = typer.Option("trafficker_data_TEST", "--filename", help="Name of the file exported. Defualt: spacy_annotations_filtered.jsonl"),
    bootstrap: bool = typer.Option(False, "--bootstrap/", help="Bootstrap the test set. Default: False")
):
    if not os.path.exists("./binary_data/" + filename):
        os.makedirs("./binary_data/" + filename)

    filter_jsonl = filterLabels(ALL_LABELS, relations=relations, withID=withID)
    # # uncomment to save filtered jsonl to disk
    print("Saving filtered jsonl to disk")
    srsly.write_jsonl(f"./binary_data/{filename}/{filename}.jsonl", filter_jsonl)
    exit()

    # else
    train_jsonl, test_jsonl, val_jsonl = train_test_val_split(filter_jsonl)

    db_train, faultyDocs = genBinaries(train_jsonl)
    db_train.to_disk(f"./binary_data/{filename}/{filename}_tr.spacy")

    if bootstrap:
        for i in range(0, 10):
            a_test_jsonl = bootstrap_test_jsonl(test_jsonl)
            db_test, faultyDocs = genBinaries(a_test_jsonl)
            db_test.to_disk(f"./binary_data/{filename}/{filename}_te_{i}.spacy")
    else:
        db_test, faultyDocs = genBinaries(test_jsonl)
        db_test.to_disk(f"./binary_data/{filename}/{filename}_te.spacy")

    db_val, faultyDocs = genBinaries(val_jsonl)
    db_val.to_disk(f"./binary_data/{filename}/{filename}_va.spacy")

    print("TOTAL DOCS LOADED: " + str(len(db_train) + len(db_test) + len(db_val)))
    print("FAILED DOC LOADS: " + str(len(faultyDocs)))

if __name__ == '__main__':
    typer.run(main)
