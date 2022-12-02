import srsly
from typing import List
from random import *

DOCCANO_INPUT_JSONL = './all.jsonl'

# BINARY: ~80/20 train-test split
TOTAL_DOCS_LOADED = 315
TOTAL_TR_LOADED = 255
TOTAL_TE_LOADED = 60

TOTAL_RANDOMIZED = 30

def filterLabels(): 
    final_jsonl = []
    for textLabels in srsly.read_jsonl(DOCCANO_INPUT_JSONL):
        if (randint(1, 100) < 90):
            continue 

        textLabels = {"id": textLabels.pop("id"), "text": textLabels.pop("text")}
        final_jsonl.append(textLabels)   

    return final_jsonl


def main():
    # filter jsonl input
    filter_json = filterLabels()
    srsly.write_jsonl('./all_filtered.jsonl', filter_json)

if __name__ == '__main__':
    main()
