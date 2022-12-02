import spacy
from spacy.tokens import DocBin

import srsly
import typer
from rich import print

from typing import List
from sqlalchemy import null

'''
Python Script to convert a raw doccano output for custom spacy model training

TODO: Define naming convention of files generated

ALL_LABELS: labels that this script will expect to convert (all labels described in our db scheme)
DOCCANO_INPUT_JSONL = name of the file (a Spacy output) that this script reads from. Should not be changing. (.jsonl format)

Example CMDs (for each table):
Trafficker: python .\doccano_to_spacy.py traffickerName traffickerBirthYear traffickerOrigin
Product: python .\doccano_to_spacy.py productName species alive
'''

ALL_LABELS=['newsSource', 'publishDate', 'numOfArrests', 'arrestLocation', \
            'seizureLocation', 'transportMethod', 'traffickerName', \
            'traffickerBirthYear', 'quantity', 'quantityUnit', \
            'destinationLocation', 'obfuscationMethod', 'traffickerOrigin']

PRODUCT_LABELS=['productName', 'species', 'alive']
TRAFFICKER_LABELS=['traffickerName', 'traffickerBirthYear', 'traffickerOrigin']
DOCCANO_INPUT_JSONL = './source_data/all.jsonl'

# BINARY: ~80/20 train-test split
TOTAL_DOCS_LOADED = 315
TOTAL_TR_LOADED = 255
TOTAL_TE_LOADED = 60

def filterLabels(
    label_list: List[str], 
    relations=False, 
    withID=False
): 
    for label in label_list:
        if label not in TRAFFICKER_LABELS: #TODO: Switch to ALL_LABELS when annotation work is finished
            print(f"the given label {label} does not exist within our Doccano annotation")
            print(f"Possible Labels:\n", *TRAFFICKER_LABELS, sep=' ') #TODO: Switch to ALL_LABELS when annotation work is finished
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

def populateDB(input_jsonl):
    nlp = spacy.blank("en")
    db_train, db_test = DocBin(), DocBin() # this will store the training examples

    faultyDocs = []
    loadCnt = 0
    for textLabels in input_jsonl: # your training data, generator
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
        
        db_train.add(doc) if (loadCnt < TOTAL_TR_LOADED) else db_test.add(doc)
        loadCnt = loadCnt + 1
    
    return db_train, db_test, faultyDocs

def main(
    label_list: List[str], 
    relations: bool = typer.Option(False, "--relations/", help="Export relations to .spacy. Default: False"), 
    withID: bool = typer.Option(False, "--id/", help="Export the ids of each doccano text, entites, and relation to .spacy. Default: False"),
    filename: str = typer.Option("trafficker_data_TEST", "--filename", help="Name of the file exported. Defualt: spacy_annotations_filtered.jsonl")
):
    # filter jsonl input
    filter_json = filterLabels(label_list, relations=relations, withID=withID)

    # export data to binary, train/test split
    db_train, db_test, faultyDocs = populateDB(filter_json)

    print("TOTAL DOCS LOADED: " + str(len(db_train) + len(db_test)))
    print("FAILED DOC LOADS: " + str(len(faultyDocs)))

    db_train.to_disk("./binary_data/" + filename  + '_tr.spacy') # save a binary training file
    db_test.to_disk("./binary_data/" + filename  + '_te.spacy') # save a binary training file

if __name__ == '__main__':
    typer.run(main)
