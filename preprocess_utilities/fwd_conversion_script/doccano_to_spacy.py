#################################################
# DEPRICATED, USE DOCCANO_TO_BINARY.PY
#
#################################################

import srsly
import typer
from rich import print

from typing import List
from sqlalchemy import null

'''
Python Script to convert a raw doccano output for use in spacy

NOTE: It is possible (and maybe better) to go from doccano's export, do filtering,
and convert to a spacy binary. However, having the intermediary .jsonl file
allows for the data to be checked more easily for correctness, and gives
insight to what the data looks like/how to interact with it

TODO: Find better way to define input/output names other than with poorly named constants
TODO: Define more label lists for filtering
TODO: Define naming convention of files generated

ALL_LABELS: labels that this script will expect to convert (all labels described in our db scheme)
DOCCANO_INPUT_JSONL = name of the file (a Spacy output) that this script reads from (.jsonl format)

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

def main(
    label_list: List[str], 
    # bool = typer.Option(False, "--force/--no-force", "-f/-F")
    relations: bool = typer.Option(False, "--relations/", help="Export relations to .spacy. Default: False"), 
    withID: bool = typer.Option(False, "--id/", help="Export the ids of each doccano text, entites, and relation to .spacy. Default: False"),
    filename: str = typer.Option("./format_data/spacy_annotations_filtered", "--filename", help="Name of the file exported. Defualt: spacy_annotations_filtered.jsonl")
):
    filename = "./format_data/" + filename + ".jsonl"
    filter_json = filterLabels(label_list, relations=relations, withID=withID)
    srsly.write_jsonl(filename, filter_json)

if __name__ == '__main__':
    typer.run(main)
