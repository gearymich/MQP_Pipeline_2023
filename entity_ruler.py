import os
import inflect # for plurals

# Returns list of entities
def get_entity_list(file):
    entity_list = []
    with open(file, "r") as f:
        for line in f:
            entity = line.strip()
            entity_list.append(entity.lower())
    entity_list = set(entity_list) # remove duplicates
    entity_list = list(entity_list)
    entity_list.sort()
    return entity_list

# Returns list of patterns {entity_label : entity}
def create_patterns(label, file):
    entity_list = get_entity_list(file)
    patterns = []
    inflection = inflect.engine()
    for ent in entity_list:
        patterns.append({"label" : label, "pattern" : ent})
        patterns.append({"label" : label, "pattern" : inflection.plural_noun(ent)})
    return patterns

# Adds patterns to entity ruler
def add_entity_ruler_patterns(ruler):
    dirname = os.path.dirname("__file__")

    filename = os.path.join(dirname, "model_token_matching/animals.txt")
    animal_patterns = create_patterns("ANIMAL", filename)
    ruler.add_patterns(animal_patterns)

    filename = os.path.join(dirname, "model_token_matching/animal_products.txt")
    animal_product_patterns = create_patterns("PRODUCT", filename)
    ruler.add_patterns(animal_product_patterns)
