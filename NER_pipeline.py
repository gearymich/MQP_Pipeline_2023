import pandas as pd
import os
import spacy
from spacy import displacy
import warnings
# supress warnings, if you are debugging, dont use this line
warnings.filterwarnings("ignore")

dirname = os.path.dirname("__file__")
filename = os.path.join(dirname, 'eagle-briefing-july-public.csv')

files = pd.read_csv(filename)
text = list(files['text'])

# create a language pattern
# pattern = 'NP: {<DT>?<JJ>*<NN>}' # this will be important to play with, have multiple types of patterns

# SPACY
# nlp = spacy.load("en_core_web_lg") # python -m spacy download en_core_web_lg
nlp = spacy.load("en_core_web_trf") # python -m spacy download en_core_web_trf
docs = nlp.pipe(text)
for doc in docs:
    sentence_spans = list(doc.sents)
    #displacy.render(sentence_spans, style="dep", options={"compact":True}) # square arrow dependacy thing
    """
    PERSON:      People, including fictional.
    NORP:        Nationalities or religious or political groups.
    FAC:         Buildings, airports, highways, bridges, etc.
    ORG:         Companies, agencies, institutions, etc.
    GPE:         Countries, cities, states.
    LOC:         Non-GPE locations, mountain ranges, bodies of water.
    PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
    EVENT:       Named hurricanes, battles, wars, sports events, etc.
    WORK_OF_ART: Titles of books, songs, etc.
    LAW:         Named documents made into laws.
    LANGUAGE:    Any named language.
    DATE:        Absolute or relative dates or periods.
    TIME:        Times smaller than a day.
    PERCENT:     Percentage, including ”%“.
    MONEY:       Monetary values, including unit.
    QUANTITY:    Measurements, as of weight or distance.
    ORDINAL:     “first”, “second”, etc.
    CARDINAL:    Numerals that do not fall under another type.
    """

    displacy.render(doc, style="ent", options={"compact":True})

    #for ent in doc.ents:
    #    print(ent.text, ent.label_)
