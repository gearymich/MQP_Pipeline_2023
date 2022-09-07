# helper to check if a word is plural
def check_plural(word, file):
    if word.endswith("s") and word[:-1] in get_entity_list(file):
        return word[:-1]
    else:
        return word

def extract_date(ent, event, events):
    if events:
        event.update({"event_date": ent.text})


def extract_product(ent, products, pid, eid):
    product = {"id": pid, "event_id": eid, "product_name": ent.text, "description": None, "animal": None,
               "quantity": None, "weight_kg": None, "price_usd": None, "transportation_method": None}
    lefts = list(ent.lefts)
    subtree = list(ent.subtree)
    for tok in lefts:
        if tok._.is_animal:
            print(tok.text)
            if product.get("animal") is None:
                product.update({"animal": check_plural(tok.text, "animals.txt")})
        elif tok.is_digit:
            product.update({"quantity": tok.text})
    if product not in products:
        products.append(product)
    return product


def extract_quantity(ent, product):
    subtree = list(ent.subtree)
    for tok in subtree:
        if tok.is_digit:
            digit = tok.text
        if tok._.is_unit_weight:
            unit = tok.text  # TODO apply unit conversion function if nescessary
    product.update({"weight_kg": digit + " " + unit})


def extract_gpe(ent, event, locations, lid):
    location = {"id": lid, "country": ent.text, "city_id": None}
    event.update({"location_id": lid})
    locations.append(location)


def extract_relations(doc):

    events = []
    products = []
    locations = []

    # NOTE table primary keys, will increment before first use to 0
    eid = -1
    pid = -1
    lid = -1

    is_event = False
    for sent in doc.sents:
        if "trafficker" in sent[:4].text: # new event
            if is_event:
                events.append(event)
            eid += 1
            event = {"id" : eid, "location_id" : None, "trafficker_id" : None, "event_date" : None}
            is_event = True

        for ent in sent.ents:
            #print(ent.text, list(ent.subtree))
            if ent.label_ == "DATE":
                if events:
                    event.update({"event_date" : ent.text})
            elif ent.label_ == "PRODUCT":
                pid += 1
                product = extract_product(ent, products, pid, eid)
            elif ent.label_ == "QUANTITY":
                extract_quantity(ent, product)
            elif ent.label_ == "GPE":
                lid += 1
                extract_gpe(ent, event, locations, lid)
    print("events", events)
    print("products", products)
    print("locations", locations)
    return (locations, events, products)
