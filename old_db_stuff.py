import database as db

# rows = list of dictionaries of same format
# insert query must be of form f"INSERT INTO table_name VALUES (?,?,?...)" where number of ? marks must match number of values in dictionary
def add_rows(database, rows, insert_query):
    sql_rows = []
    for row in rows:
        sql_row = tuple(row.values())
        sql_rows.append(sql_row)
    with db.create_connection(database) as connection:
        cursor = connection.cursor()
        cursor.executemany(insert_query, sql_rows)
        connection.commit()
    print("Disconnected")

def add_countries(database):
    with open("countries.txt", "r") as f:
        countries = []
        for country in f:
            countries.append(country.strip())
    for country in countries:
        sql_country = tuple(country)
        sql_insert_countries_query = f"INSERT INTO Countries VALUES (?)"
        connection = db.create_connection(database) # use with db.create_connection as connection...
        cursor = connection.cursor()
        cursor.execute(sql_insert_countries_query, sql_country)
        connection.commit()
        if connection:
            connection.close()
            print("Disconnected")

def add_locations(locations, database):
    sql_locations = []
    for location in locations:
        sql_location = tuple(location.values())
        sql_locations.append(sql_location)
    sql_insert_locations_query = f"INSERT INTO Locations VALUES (?,?,?)"
    with db.create_connection(database) as connection:
        cursor = connection.cursor()
        cursor.executemany(sql_insert_locations_query, sql_locations)
        connection.commit()
        print("Disconnected")

def add_events(events, database):
    for event in events:
        sql_event = tuple(event.values())
        sql_insert_events_query = f"INSERT INTO Events VALUES (?,?,?,?)"
        connection = db.create_connection(database) # use with db.create_connection as connection...
        cursor = connection.cursor()
        cursor.execute(sql_insert_events_query, sql_event)
        connection.commit()
        if connection:
            connection.close()
            print("Disconnected")

def add_products(products, database):
    for product in products:
        sql_product = tuple(product.values())
        sql_insert_products_query = f"INSERT INTO Products VALUES (?,?,?,?,?,?,?,?,?)"
        connection = db.create_connection(database) # use with db.create_connection as connection...
        cursor = connection.cursor()
        cursor.execute(sql_insert_products_query, sql_product)
        connection.commit()
        if connection:
            connection.close()
            print("Disconnected")
