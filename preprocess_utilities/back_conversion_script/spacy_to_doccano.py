# id, text, entities[(id ,label, start_offset, end_offset)...], relations[(id ,from_id, to_id, type)...]
import json
import sys

from sqlalchemy import null

'''
Python Script to convert from a spacy EntityRuler labeling scheme
to the label scheme used by Doccano. Specifically written for product labeling
(For Bao)

ALL_LABELS: labels that this script will expect to convert (all labels described in our db scheme)
CONST_output_file: descibes name of the file that this script will output into (.jsonl format)
CONST_spacy_file = name of the file (a Spacy output) that this script reads from (.jsonl format)
'''

ALL_LABELS=['newsSource', 'publishDate', 'numOfArrests', 'arrestLocation', \
            'seizureLocation', 'transportMethod', 'traffickerName', \
            'traffickerBirthYear', 'quantity', 'quantityUnit', \
            'destinationLocation', 'obfuscationMethod', 'traffickerOrigin']

CONST_output_file = './doccano_output_data/doccano_trafficker_id.jsonl' # the OUTPUT file
CONST_spacy_file = './spacy_trafficker_id.jsonl' # the INPUT file

def convertDoccano(json_list, output_file=CONST_output_file, withID=False):
    with open(output_file, 'w') as outfile:
        for line in json_list:
            line =json.loads(line)
            line_entities = line.pop("entities")
            
            tmp_ents = []
            for e in line_entities:
                if e['label'] in ALL_LABELS:
                    doccano_content = {"id": -2, "label": e['label'], "start_offset": e['start'], "end_offset": e['end']} if not withID \
                        else {"id": e['id'], "label": e['label'], "start_offset": e['start'], "end_offset": e['end']}

                    tmp_ents.append(doccano_content)
                
                line_entities = tmp_ents

            if (len(line["text"]) > 5):
                entry = {"id": -1, "text": line["text"], "entities": line_entities} if not withID \
                    else {"id": line["id"], "text": line["text"], "entities": line_entities}

                json.dump(entry, outfile)
                outfile.write('\n')


if __name__ == '__main__':
    with open(CONST_spacy_file) as sFile:
        json_list = list(sFile)

    convertDoccano(json_list, withID=True)