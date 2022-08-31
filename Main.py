#%% Imports
import os
import pandas as pd
import itertools
import spacy
from spacy import displacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
from spacy.tokens import Token
from spacy.language import Language
import inflect # for plurals
import datetime # for formatting dates
from word2number import w2n #handling numbers written as strings e.g., 'two'
# Functions defined in local files
import database as db
from db_objects import Country, Event, Product, Location
from readPDF import readPDF
from extensions import create_extensions
from entity_ruler import get_entity_list, add_entity_ruler_patterns

# helper to check if value is actually a numeric, return float if it is, else returns False
def try_float(val):
    try:
        float(val)
    except Exception as e:
        return False
    else:
        return float(val)

# Convert the given value to kilograms
def toKg(val, unit):
    val = try_float(val)
    if not val or val < 0:
        return None
    if unit == "kilogram" or unit == "kg":
        return val
    elif unit == "gram":
        return val / 1000
    elif unit == "milogram" or unit == "mg":
        return val / 1_000_000
    elif unit == "pound" or unit == "lb":
        return val / 2.205
    elif unit == "ounce" or unit == "oz":
        return val /  35.274
    elif unit == "ton":
        return val * 907
    elif unit == "tonne":
        return val * 1016
    else:
        return val

def print_tables(database):
    with db.create_connection(database) as connection:
        cursor = connection.cursor()

        query = "SELECT * FROM Countries;"
        print(pd.read_sql_query(query, connection).to_string())

        query = "SELECT * FROM Events;"
        print(pd.read_sql_query(query, connection).to_string())

        query = "SELECT * FROM Products;"
        print(pd.read_sql_query(query, connection).to_string())

        query = "SELECT * FROM Locations;"
        print(pd.read_sql_query(query, connection).to_string())

        query = "SELECT * FROM Locations;"
    print("Disconnected")

# Function to fill Countries table in database from txt file of country names
def fill_countries(dirname):
    database = os.path.join(dirname, "mqp_database.db")
    with db.create_connection(database) as connection:
        # add list of countries to database
        countries = []
        with open("countries.txt", "r") as f:
            for line in f:
                country = Country(line.strip())
                countries.append(country)
        db.add_rows(connection, countries, f"INSERT INTO Countries VALUES (?)")

def main():
    # Get pdf file text
    dirname = os.path.dirname("__file__")

    # create database
    if not os.path.isfile("mqp_database.db"):
        db.create_database()
        # fill countries table in database from file of country names
        fill_countries(dirname)

    database = os.path.join(dirname, "mqp_database.db")

    iterate_files(database)

    # print out database tables
    #print_tables(database)

    with db.create_connection(database) as connection:
        cursor = connection.cursor()

        query = r"""SELECT * FROM Events
                    LEFT JOIN Locations
                    ON Events.location_id = Locations.id
                    LEFT JOIN Products
                    ON Events.id = Products.event_id;""" #WHERE Products.animal IS NOT NULL AND Locations.country IS NOT NULL;
        join = pd.read_sql_query(query, connection)
        join.to_csv("data.csv")
        #print(join.to_string())

    print("Disconnected")

# helper to get singular noun form of a word if it is plural
def get_singular(word):
    inflection = inflect.engine()
    singular_noun = inflection.singular_noun(word)
    if not singular_noun:
        return word
    else:
        return singular_noun

def get_entity_relations(ent):
    for tok in ent:
        lefts = list(tok.lefts)
        rights = list(tok.rights)
        subtree = list(tok.subtree)
        children = list(tok.children)
        ancestors = list(tok.ancestors)
    entity_relations = list(set(lefts + rights + subtree + children + ancestors))
    return entity_relations

# returns -1 if new product, else returns index of duplicate product
def new_product(product, products):
    for prod in products:
        if (prod.event_id == product.event_id and (prod.product_name == product.product_name) and (prod.animal == product.animal)):
            return products.index(prod)
    return -1

# returns -1 if new product, else returns index of duplicate product
def same_weight(new_product, product):
    if new_product.weight_kg is not None:
        return new_product.weight_kg
    elif product.weight_kg is not None:
        return product.weight_kg
    return -1

# returns -1 if new location, else returns index of duplicate location
def new_location(location, locations):
    dirname = os.path.dirname("__file__")
    database = os.path.join(dirname, "mqp_database.db")
    with db.create_connection(database) as connection:
        cursor = connection.cursor()
        query = f"""SELECT id FROM Locations
                    WHERE country = '{location.country}'""" # TODO include city_id in check to see if location is new or not
        try:
            return db.execute_read_query(connection, query)[0][0]
        except Exception as e:
             for loc in locations:
                 if loc.equals(location):
                    return locations.index(loc)
        return -1

#Tries to convert the quantity value into a number if it's not e.g. two -> 2
def checkQuantity(val):
    if try_float(val) == True:
        return val
    else:
        try:
            w2n.word_to_num(val)
        except Exception as e:
            return None
        else:
            return w2n.word_to_num(val)


# TODO don't add products without an animal, set default quantity to be 1 not NULL
def extract_product(doc, ent, products, pid, eid):
    product = Product(id=pid,event_id=eid,product_name=get_singular(ent.text),quantity=1)

    # get relations
    ent_relations = get_entity_relations(ent)
    for tok in ent_relations:
        if (tok.ent_type_ == "ANIMAL") and (product.animal is None): #NOTE use the ent_type_ because extension is buggy
            product.animal = get_singular(tok.text)
        elif (tok.ent_type_ == "QUANTITY"):
            if tok.ent_iob_  == "B":
                if (doc[tok.i + 1]._.is_unit_weight) and (product.weight_kg == None):
                    weight = toKg(tok.text, doc[tok.i + 1].text)
                    product.weight_kg = weight
                # TODO handle prices here
            elif tok.ent_iob_  == "I":
                if (tok._.is_unit_weight) and (product.weight_kg == None):
                    weight = toKg(doc[tok.i - 1].text, tok.text)
                    product.weight_kg = weight
                # TODO handle prices here
        elif (tok.ent_type_ == "CARDINAL"): # OPTIMIZE filling weight into QUANTITY
            product.quantity = checkQuantity(tok.text)
    if new_product(product,products) == -1:
        pid += 1
        if product.animal is not None:
            products.append(product)
    # TODO if not new, check if this product has more info than one already in the list and add the info if it does, use index returned by new product to get product and compare values
    else:
        index = new_product(product, products)
        found_weight = same_weight(product, products[index])
        products[index].weight_kg = found_weight
    return (products, pid)

"""
def extract_quantity(ent, product):
    subtree = list(ent.subtree)
    for tok in subtree:
        if tok.is_digit:
            digit = tok.text
        if tok._.is_unit_weight:
            unit = tok.text  # TODO apply unit conversion function if nescessary
    product.update({"weight_kg": digit + " " + unit})
"""


#is_country_sql = f"SELECT country FROM Countries WHERE country = (?)"
#database = os.path.join(dirname, "mqp_database.db")
#with db.create_connection(database) as connection:
#    cursor = connection.cursor()
#    result = cursor.execute(is_country_sql, ent.text)
#if result.lower() == ent.text.lower():
#    location = {"id": None, "country": ent.text, "city_id": None}
#else:
#    return

# TODO post processing to remove and combine duplicates
# TODO explore Geotext library
def extract_gpe(gpe, event, locations, lid):
    # check if gpe is a country by seeing if it exists in our database
    dirname = os.path.dirname("__file__")
    database = os.path.join(dirname, "mqp_database.db")
    with db.create_connection(database) as connection:
        cursor = connection.cursor()
        query = f"""SELECT COUNT(1) FROM Countries
                    WHERE name = '{gpe}'"""
        # BUG gpe's with apostrophes give syntax error, strip 's before creating query'
        country_exists = None
        try:
            country_exists = db.execute_read_query(connection, query)[0][0]
        except Exception as e:
            pass
        # if gpe in table of Countries
        if country_exists:
        # create location
            location = Location(id=lid,country=gpe)
            # check if it's a new location TODO make this work with whole database by checking database not just single article
            new_loc = new_location(location, locations)
            if new_loc == -1:
                lid += 1 # incremnet location id after new location
                locations.append(location) # add location to list of locations
                event.location_id = lid # add new location id to event
            else:
                event.location_id = new_loc # add location id of previous location to event
        else:
            # TODO handle non-country GPE's better than doing nothing
            pass
    return (locations, lid, event)

def extract_relations(doc, date, eid, pid, lid):

    # store db row entries
    events = []
    products = []
    locations = []

    first_event = True
    event = Event(id=eid, event_date=date)

    # for each sentence in the doc
    for sent in doc.sents:

        # if the first four words contain the word trafficker or traffickers, consider it a new event
        # IDEA make a Trafficker Entity which picks up trafficker and name ans description... with Prodigy?
        # TODO count number of arrests per event, create trafficker object for each trafficker mentioned?
        if ("trafficker" in sent[:4].text) or "traffickers" in sent[:4].text:
            # count number of traffickers arrested
            for ent in sent[:4].ents:
                if ent.label_ == "CARDINAL":
                    event.arrests = checkQuantity(ent.text)
                else:
                    event.arrests = 1
            # if it isn't the first event, append the old event to the list of events
            if not first_event:
                events.append(event)
                eid += 1
            event = Event(id=eid, event_date=date) # create a new event
            first_event = False

        # for each entity in the sentence
        for ent in sent.ents:
            #if ent.label_ == "DATE" and first_event: # OPTIMIZE date collection TODO fill in date by article, don't check for dates anymore
            #    date = ent.text
            if (ent.label_ == "PRODUCT"):
                products,pid = extract_product(doc, ent, products, pid, eid)
            #elif ent.label_ == "QUANTITY":
            #    extract_quantity(ent, product)
            elif ent.label_ == "GPE":
                locations, lid, event = extract_gpe(ent.text, event, locations, lid)

    # append last event
    if not first_event:
        events.append(event)
    return (locations, events, products)


def iterate_files(database):
    directory = os.path.join(os.path.dirname("__file__"), "EAGLE_reports")
    #directory = os.path.join(os.path.dirname("__file__"), "Report_debugging")
    for filename in os.listdir(directory):
        filename = os.path.join(directory, filename)
        fileName, fileExt = filename.split('.') # do not use extra dots plz
        pdf_text = readPDF(fileName, fileExt)

        # Load Spacy transformer
        nlp = spacy.load("en_core_web_trf")

        # Add entity ruler to pipeline
        ruler = nlp.add_pipe("entity_ruler")

        # Add token extensions for entities
        create_extensions()

        # Add patterns to entity ruler
        add_entity_ruler_patterns(ruler) # add extensions to entity tokens?

        doc = nlp.pipe(pdf_text)
        page1 = next(doc)
        # WARNING some months reports have incorrect dates at beginning of text, IDEA use filename to get date?
        full_date = page1.ents[0] # NOTE assumes that first ent always month year format
        month_name = full_date[0].text
        month_num = datetime.datetime.strptime(month_name, '%B').month
        formatted_month_num = f"{month_num:02}"
        short_date = formatted_month_num + "/" + full_date[1].text
        summary = next(doc)

        #displacy.render(summary, style="dep", options={"compact":True})
        #displacy.render(summary, style="ent", options={"compact":True})

        with db.create_connection(database) as connection:
            cursor = connection.cursor()

            query = "SELECT MAX(id) FROM Events;"
            eid = cursor.execute(query).fetchall()[0][0]

            query = "SELECT MAX(id) FROM Products;"
            pid = cursor.execute(query).fetchall()[0][0]

            query = "SELECT MAX(id) FROM Locations;"
            lid = cursor.execute(query).fetchall()[0][0]
        print("Disconnected")

        if (eid is None):
            eid = 0
        if (pid is None):
            pid = 0
        if (lid is None):
            lid = 0
        locations, events, products = extract_relations(summary, short_date, eid+1, pid+1, lid+1)

        db.add_rows(connection, locations, f"INSERT INTO Locations VALUES (?,?,?)")
        db.add_rows(connection, events, f"INSERT INTO Events VALUES (?,?,?,?,?)")
        db.add_rows(connection, products, f"INSERT INTO Products VALUES (?,?,?,?,?,?,?,?,?)")

        print("Rows added")


if __name__=="__main__":
    main()
