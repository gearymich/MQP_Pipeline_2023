import os
from spacy.tokens import Token
from entity_ruler import get_entity_list

def create_extensions():
    dirname = os.path.dirname("__file__")
    def add_plurals(s_list, p_list):
        for singular in s_list:
            plural = singular + "s"
            p_list.append(plural)
        return p_list

    # Add token extension for animals
    filename = os.path.join(dirname, "model_token_matching/animals.txt")
    animal_extension = get_entity_list(filename)
    animal_extension = add_plurals(get_entity_list(filename), animal_extension)

    animal_getter = lambda token: token.text in animal_extension
    Token.set_extension("is_animal", getter=animal_getter, force=True)

    # Add token extension for units of weight
    filename = os.path.join(dirname, "model_token_matching/weight_units.txt")
    weight_extension = get_entity_list(filename)
    weight_extension = add_plurals(get_entity_list(filename), weight_extension)

    weight_getter = lambda token: token.text in weight_extension
    Token.set_extension("is_unit_weight", getter=weight_getter, force=True)
