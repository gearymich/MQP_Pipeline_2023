import os
import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from spacy.tokens import Span
import srsly
import typer

# TODO:
# 1. REMOVE RULER ONLY MODEL
# 2. FIX CODE TO BE CLEAN
# 3. CLARIFY TEST SPLIT (use same 30 docs that were used for new models)
# 4. IMPLEMENT BOOTSTRAP TESTING
# 5. COLLECT ALL METRICS DONE FROM PREVIOUS MODEL

DOCCANO_JSONL_FILTERED_PATH = './source_data/rules_filter.jsonl'
DOCCANO_JSONL_SPACY_DEFAULT_PATH = './source_data/spacy_default_data.jsonl'
DOCCANO_JSONL_BOTH_PATH = './source_data/spacy_default_and_ruler_data.jsonl'

DOCCANO_JSONL_REAL_PATH = "/Users/geary/MQP_Pipeline/preprocess_utilities/fwd_conversion_script/source_data/all_final.jsonl"

NER_STAT_MODEL_PATH = "/Users/geary/MQP_Pipeline/ner_model/output/model-best"
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
    "EVENT": "UNK"
}

def example_builder_ner(nlp_ner, ner_pipe, textLabels):
    actual_entities = [(ent['start'], ent['end'], ent['label']) for ent in textLabels['entities']]
    actual_dict = {'text': textLabels['text'], 'entities': actual_entities}
    pred_doc = nlp_ner(textLabels['text'])
    pred_doc = ner_pipe(pred_doc)
    pred_entities = [Span(pred_doc, ent.start, ent.end, LABEL_CONV_DICT[ent.label_]) for ent in pred_doc.ents]
    pred_doc.set_ents(pred_entities)
    return Example.from_dict(pred_doc, actual_dict)

def example_builder_both(nlp_both, ner_pipe, textLabels):
    actual_entities = [(ent['start'], ent['end'], ent['label']) for ent in textLabels['entities']]
    actual_dict = {'text': textLabels['text'], 'entities': actual_entities}
    pred_doc = nlp_both(textLabels['text'])
    pred_doc = ner_pipe(pred_doc)
    pred_entities = [Span(pred_doc, ent.start, ent.end, LABEL_CONV_DICT[ent.label_]) for ent in pred_doc.ents]
    pred_doc.set_ents(pred_entities)
    return Example.from_dict(pred_doc, actual_dict)

def example_builder_ruler(nlp_ruler, textLabels):
    actual_entities = [(ent['start'], ent['end'], ent['label']) for ent in textLabels['entities']]
    actual_dict = {'text': textLabels['text'], 'entities': actual_entities}
    pred_doc = nlp_ruler(textLabels['text'])
    return Example.from_dict(pred_doc, actual_dict)

def main(
    ruler: bool = typer.Option(False, "--ruler/", help="Measure 2022 MQP Ruler Data and Labels if specified. Otherwise, measure default SpaCy Model. Default: False (SpaCy Model)"),
    both: bool = typer.Option(False, "--both/", help="Measure both 2022 MQP Ruler Data and Labels and default SpaCy Model. Default: False")
):

    if ruler:
        print("Measuring Ruler Data and Labels")
        nlp_ruler = spacy.blank("en")
        ruler_pipe = nlp_ruler.add_pipe("entity_ruler").from_disk(RULER_PATTERNS_PATH)
        filepath = DOCCANO_JSONL_FILTERED_PATH

    elif both:
        print("Measuring Ruler Data and Labels, with SpaCy Default Model")
        source_nlp = spacy.load("en_core_web_sm")
        nlp_both = spacy.blank("en")
        ruler_pipe = nlp_both.add_pipe("entity_ruler").from_disk(RULER_PATTERNS_PATH)
        ner_pipe = nlp_both.add_pipe("ner", source=source_nlp)
        filepath = DOCCANO_JSONL_BOTH_PATH

    else:
        print("Measuring NER Model")
        source_nlp = spacy.load("en_core_web_sm")
        nlp_ner = spacy.blank("en")
        ner_pipe = nlp_ner.add_pipe("ner", source=source_nlp)
        filepath = DOCCANO_JSONL_SPACY_DEFAULT_PATH

    examples = []
    failCount = 0
    for idx, textLabels in enumerate(srsly.read_jsonl(filepath)):
        try:
            if ruler:
                example = example_builder_ruler(nlp_ruler, textLabels)
            elif both:
                example = example_builder_both(nlp_both, ner_pipe, textLabels)
            else:
                example = example_builder_ner(nlp_ner, ner_pipe, textLabels)

            examples.append(example)

        except Exception as e:
            print(idx, e)
            failCount += 1
            continue

    print("Example with Errors:", failCount)
    scorer = Scorer()
    scores = scorer.score(examples)

    for k, v in scores.items():
        if k in ('ents_p', 'ents_r', 'ents_f', 'ents_per_type'):
            print(k,":", v)

if __name__ == '__main__':
    typer.run(main)