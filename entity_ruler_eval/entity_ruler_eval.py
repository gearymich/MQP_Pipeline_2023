import os
import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from spacy.tokens import Span
import srsly

DOCCANO_JSONL_FILTERED_PATH = './source_data/rules_filter.jsonl'
DOCCANO_JSONL_REAL_PATH = "/Users/geary/MQP_Pipeline/preprocess_utilities/fwd_conversion_script/source_data/all_final.jsonl"
TEMP_PATH = './source_data/rules_unfilter.jsonl'

NER_STAT_MODEL_PATH = "/Users/geary/MQP_Pipeline/ner_model/output/model-best"

RULER_PATTERNS_PATH = "./pattern_data/ruler_patterns.jsonl"

LABEL_CONV_DICT = {
    "PRODUCT": "productName",
    "PERSON": "traffickerName",
    "GPE": "seizureLocation",
    "MONEY": "price",
    "QUANTITY": "quantity",
    "DATE": "publishDate",
    "CARDINAL": "TraffickerBirthYear",
    # convert all other labels to a UNK label
    "ORG": "UNK",
    "NORP": "UNK",
    "TIME": "UNK"
}

if __name__ == '__main__':
    source_nlp = spacy.load("en_core_web_sm")
    nlp = spacy.blank("en")
    # ner = nlp.add_pipe("ner", source=source_nlp)
    ruler = nlp.add_pipe("entity_ruler").from_disk(RULER_PATTERNS_PATH)

    examples = []
    failCount = 0
    for idx, textLabels in enumerate(srsly.read_jsonl(DOCCANO_JSONL_FILTERED_PATH)):
        try:
            actual_entities = [(ent['start'], ent['end'], ent['label']) for ent in textLabels['entities']]
            actual_dict = {'text': textLabels['text'], 'entities': actual_entities}
            
            pred_doc = nlp(textLabels['text'])

            # STARTY EN_CORE_WEB_SM TRANSLATION
            # print(vars(pred_doc.ents[0]))
            # pred_entities = [Span(nlp.make_doc(textLabels['text']), ent.start, ent.end, LABEL_CONV_DICT[ent.label_]) for ent in pred_doc.ents]
            # pred_doc.set_ents(pred_entities)
            # END EN_CORE_WEB_SM TRANSLATION

            example = Example.from_dict(pred_doc, actual_dict)
            examples.append(example)

        except Exception as e:
            print(idx)
            failCount += 1
            continue

    print("Example with Errors:", failCount)
    scorer = Scorer()
    scores = scorer.score(examples)

    for k, v in scores.items():
        if k in ('ents_p', 'ents_r', 'ents_f', 'ents_per_type'):
            print(k,":", v)