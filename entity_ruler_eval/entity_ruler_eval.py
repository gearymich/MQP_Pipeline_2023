import os
from typing import List, Dict
import random
from statistics import mean, stdev

import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from spacy.tokens import Span
import srsly
import typer

import logging

'''
Precision, Recall, And F1-Scores calculated from spacy.scorer Scorer Class.
Ground truth is imported from doccano labeled data via .jsonl files 
(filtered based on what type of NER is being tested). 
'''

# TODO:
# 1. REMOVE RULER ONLY MODEL
# 2. FIX CODE TO BE CLEAN
# 3. CLARIFY TEST SPLIT (use same 30 docs that were used for new models)
# 4. IMPLEMENT BOOTSTRAP TESTING
# 5. COLLECT ALL METRICS DONE FROM PREVIOUS MODEL

TOTAL_TR_LOADED = 300
TOTAL_TE_LOADED = 30

DOCCANO_JSONL_SPACY_DEFAULT_PATH = './source_data/spacy_default_data.jsonl'
DOCCANO_JSONL_SPACY_RULER_PATH = './source_data/spacy_default_and_ruler_data.jsonl'

RULER_PATTERNS_PATH = "./pattern_data/ruler_patterns.jsonl"

LABEL_CONV_DICT = {
    "PRODUCT": "productName",
    "PERSON": "traffickerName",
    "GPE": "seizureLocation",
    "DATE": "publishDate",
    "CARDINAL": "traffickerBirthYear",
    # convert all other labels to a UNK label
    "MONEY": "UNK",
    "QUANTITY": "UNK",
    "ORG": "UNK",
    "NORP": "UNK",
    "TIME": "UNK",
    "LANGUAGE": "UNK",
    "LOC": "UNK",
    "LAW": "UNK",
    "ORDINAL": "UNK",
    "PERCENT": "UNK",
    "FAC": "UNK",
    "WORK_OF_ART": "UNK",
    "EVENT": "UNK",
    # ruler labels: do not convert
    "species": "species",
    "productName": "productName"
}

'''
Load a .jsonl file into a list of dictionaries
'''
def load_data(filepath: str) -> List[Dict]:
    jsonl = list(srsly.read_jsonl(filepath))
    # random.shuffle(jsonl)
    return jsonl

'''
Split a list of dictionaries (.jsonl format) into train and test sets.
(No validation set is used in this script)
(train and test if-else flipped from other script)
'''
def train_test_val_split(jsonl):
    train_jsonl = []
    test_jsonl = []
    for i, textLabels in enumerate(jsonl):
        if i < TOTAL_TE_LOADED:
            test_jsonl.append(textLabels)
        elif i < TOTAL_TR_LOADED + TOTAL_TE_LOADED:
            train_jsonl.append(textLabels)
    
    return train_jsonl, test_jsonl

'''bootstrap the test set'''
def bootstrap_test_jsonl(test_jsonl, num_samples=TOTAL_TE_LOADED):
    all_bootstrapped_jsonl = []

    for _ in range(100):
        bootstrapped_jsonl = []

        for _ in range(num_samples):
            a_json = random.choice(test_jsonl)
            bootstrapped_jsonl.append(a_json)

        all_bootstrapped_jsonl.append(bootstrapped_jsonl)

    return all_bootstrapped_jsonl

# def bootstrap_test_jsonl(test_jsonl, num_samples=TOTAL_TE_LOADED):
#     bootstrapped_jsonl = []

#     for _ in range(num_samples):
#         a_json = random.choice(test_jsonl)
#         bootstrapped_jsonl.append(a_json)

#     return bootstrapped_jsonl


'''
Uses both Default SpaCy NER and 2022 Ruler
'''
def example_builder(nlp, ner_pipe, text_labels):
    actual_entities = [(ent['start'], ent['end'], ent['label']) for ent in text_labels['entities']]
    actual_dict = {'text': text_labels['text'], 'entities': actual_entities}
    pred_doc = nlp(text_labels['text'])
    pred_doc = ner_pipe(pred_doc)
    pred_entities = [Span(pred_doc, ent.start, ent.end, LABEL_CONV_DICT[ent.label_]) for ent in pred_doc.ents]
    pred_doc.set_ents(pred_entities)
    return Example.from_dict(pred_doc, actual_dict)

def main(
    ruler: bool = typer.Option(False, "--ruler/", help="Temp")
):
    logging.basicConfig(level=logging.DEBUG, filename="./logging/bootstrap-ruler.txt", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

    source_nlp = spacy.load("en_core_web_sm")
    nlp = spacy.blank("en")
    
    if ruler:
        print("Measuring Default SpaCy NER w/ 2022 Entity Ruler")
        filepath = DOCCANO_JSONL_SPACY_RULER_PATH
        ruler_pipe = nlp.add_pipe("entity_ruler").from_disk(RULER_PATTERNS_PATH)
        ner_pipe = nlp.add_pipe("ner", source=source_nlp)
        example_builder_wrapper = lambda text_labels: example_builder(nlp, ner_pipe, text_labels)

    else:
        print("Measuring Default SpaCy NER Model ONLY")
        filepath = DOCCANO_JSONL_SPACY_DEFAULT_PATH
        ner_pipe = nlp.add_pipe("ner", source=source_nlp)
        example_builder_wrapper = lambda text_labels: example_builder(nlp, ner_pipe, text_labels)

    jsonl = load_data(filepath)
    _, test_jsonl = train_test_val_split(jsonl)
    all_bootstrapped_jsonl = bootstrap_test_jsonl(test_jsonl)

    # outer loop goes through each bootstrapped sample
    # inner loop builds the examples, scores them, and logs the results
    ents_p_all = []
    ents_r_all = []
    ents_f_all = []
    ents_per_type_all = []

    for idx, bootstrapped_jsonl in enumerate(all_bootstrapped_jsonl):
        failCount = 0
        examples = []

        for text_labels in bootstrapped_jsonl:
            try:
                example = example_builder_wrapper(text_labels)
                examples.append(example)
            except Exception as e:
                failCount += 1
                continue

        logging.info("{0} Example with Errors: {1}".format(idx, failCount))
        scorer = Scorer()
        scores = scorer.score(examples)

        for k, v in scores.items():
            if k in ('ents_p', 'ents_r', 'ents_f', 'ents_per_type'):
                logging.info("{0}, : {1}".format(k, v))
                if k == 'ents_p': ents_p_all.append(v)
                if k == 'ents_r': ents_r_all.append(v)
                if k == 'ents_f': ents_f_all.append(v)
                if k == 'ents_per_type': ents_per_type_all.append(v)
        
        logging.info("")
    
    logging.info("Average/STD of Precision: {0}, {1}".format(mean(ents_p_all), stdev(ents_f_all)))
    logging.info("Average/STD of Recall: {0}, {1}".format(mean(ents_r_all), stdev(ents_f_all)))
    logging.info("Average/STD of F1: {0}, {1}".format(mean(ents_f_all), stdev(ents_f_all)))

    inorder_p = sorted(ents_p_all)
    lb_p = (inorder_p[1] + inorder_p[2])/2
    ub_p = (inorder_p[97] + inorder_p[98])/2

    logging.info("95% Confidence Interval Precision: LOWER - {0}, UPPER - {1}".format(lb_p, ub_p))

    inorder_r = sorted(ents_r_all)
    lb_r = (inorder_r[1] + inorder_r[2])/2
    ub_r = (inorder_r[97] + inorder_r[98])/2

    logging.info("95% Confidence Interval Recall: LOWER - {0}, UPPER - {1}".format(lb_r, ub_r))
    inorder_f = sorted(ents_f_all)
    lb_f = (inorder_f[1] + inorder_f[2])/2
    ub_f = (inorder_f[97] + inorder_f[98])/2

    logging.info("95% Confidence Interval F1: LOWER - {0}, UPPER - {1}".format(lb_f, ub_f))

if __name__ == '__main__':
    typer.run(main)