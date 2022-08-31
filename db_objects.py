# Classes for each database object
# DB_Object abstract class with method to return dict of class object's attributes
# Can be initialized without arguments
# NOTE When using arguments to initialize any class object, pass arguments by name to avoid misordering arguments

class DB_Object:
    def entry(self): # method to create a row from the class
        return vars(self)

class Country(DB_Object):
    def __init__(self, country):
        self.country = country

class Location(DB_Object):
    def __init__(self, id=None, country=None, city_id=None):
        self.id = id
        self.country = country
        self.city_id = city_id
    def equals(self, location):
        return (self.country == location.country) and (self.city_id == location.city_id)

# TODO create equality method
class Event(DB_Object):
    def __init__(self, id=None, location_id=None, trafficker_id=None, arrests=None, event_date=None):
        self.id = id
        self.location_id = location_id
        self.trafficker_id = trafficker_id
        self.arrests = arrests
        self.event_date = event_date
    def equals(self, product):
        pass

# TODO create equality method
class Product(DB_Object):
    def __init__(self, id=None, event_id=None, product_name=None, description=None, animal=None, quantity=1, weight_kg=None, price_usd=None, transportation_method=None):
        self.id = id
        self.event_id = event_id
        self.product_name = product_name
        self.description = description
        self.animal = animal
        self.quantity = quantity
        self.weight_kg = weight_kg
        self.price_usd = price_usd
        self.transportation_method = transportation_method
    def equals(self, product):
        pass

class Trafficker(DB_Object):
    def __init__(self, id=None, name=None, organization=None, description=None, sentence=None):
        self.id = id
        self.name = name
        self.organization = organization
        self.description = description
        self.sentence = sentence
    def equals(self, trafficker): # NOTE can't handle one trafficker in multiple organizations, would need special check to see if same trafficker arrested more than once with sentences
        return (self.name == trafficker.name) and (self.organization == trafficker.organization)
