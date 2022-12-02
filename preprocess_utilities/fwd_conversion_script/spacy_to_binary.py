#################################################
# DEPRICATED, USE DOCCANO_TO_BINARY.PY
#
#################################################




import spacy
from spacy.tokens import DocBin
import srsly
import typer

from typing import List
'''
Python Script to convert the formatted annotations into a spacy binary used for training

CONST_output_file:  descibes name of the file that this script will output into (.spacy format)
CONST_input_file:   name of the formatted annotations (built from doccano_to_spacy.py) 
                    that this script reads from (.jsonl format)
'''

CONST_input_file = './format_data/trafficker_filtered.jsonl'
CONST_output_file = './binary_data/trafficker_filtered'

# ~80/20 train-test split
TOTAL_DOCS_LOADED = 315
TOTAL_TR_LOADED = 255
TOTAL_TE_LOADED = 60

def populateDB():
    nlp = spacy.blank("en")
    db_train, db_test = DocBin(), DocBin() # this will store the training examples

    faultyDocs = []
    loadCnt = 0
    for idx, textLabels in enumerate(srsly.read_jsonl(CONST_input_file)) : # your training data, generator
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
            continue
        
        db_train.add(doc) if (loadCnt < TOTAL_TR_LOADED) else db_test.add(doc)
        loadCnt = loadCnt + 1
    
    return db_train, db_test, faultyDocs

if __name__ == '__main__':
    db_train, db_test, faultyDocs = populateDB()
    print("TOTAL DOCS LOADED: " + str(len(db_train) + len(db_test)))
    print("FAILED DOC LOADS: " + str(len(faultyDocs)))
    db_train.to_disk(CONST_output_file + '_tr.spacy') # save a binary training file
    db_test.to_disk(CONST_output_file + '_te.spacy') # save a binary training file