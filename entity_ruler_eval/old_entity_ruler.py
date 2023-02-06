import os
import spacy
import srsly

'''
Code pulled from previous MQP project

Helper functions for creating patterns for entity ruler only needed to be run once.
Entity Rules were saved in .pattern_data/ruler_patterns.jsonl for future use
'''

# Returns list of entities
def get_entity_list(file):
    entity_list = []
    with open(file, "r") as f:
        for line in f:
            entity = line.strip()
            entity_list.append(entity.lower())
            
    entity_list = list(set(entity_list)) # remove duplicates
    return entity_list

# Returns list of patterns {entity_label : entity}
def create_patterns(label, file):
    entity_list = get_entity_list(file)
    patterns = [{"label" : label, "pattern" : ent} for ent in entity_list]
    return patterns

# Adds patterns to entity ruler
def add_entity_ruler_patterns():
    # get path to current directory
    dirname = os.path.dirname(__file__)

    filename = os.path.join(dirname, "token_matching_patterns/animals.txt")  
    animal_patterns = create_patterns("ANIMAL", filename)

    filename = os.path.join(dirname, "token_matching_patterns/animal_products.txt")
    product_patterns = create_patterns("PRODUCT", filename)
    
    return animal_patterns, product_patterns