import os
import sqlite3
from sqlite3 import Error

def create_database():
    dirname = os.path.dirname("__file__")
    database = os.path.join(dirname, "mqp_database.db")

    sql_create_countries_table = """ CREATE TABLE IF NOT EXISTS Countries (
                                    name text PRIMARY KEY
                                ); """

    sql_create_cities_table = """ CREATE TABLE IF NOT EXISTS Cities (
                                    id integer PRIMARY KEY,
                                    city text NOT NULL,
                                    country text,
                                    FOREIGN KEY (country) REFERENCES Countries (name)
                                ); """

    sql_create_locations_table = """ CREATE TABLE IF NOT EXISTS Locations (
                                    id integer PRIMARY KEY,
                                    country text NOT NULL,
                                    city_id integer,
                                    FOREIGN KEY (country) REFERENCES Countries (country),
                                    FOREIGN KEY (city_id) REFERENCES Cities (id)
                                ); """

    # OPTIMIZE event should be able to have multiple traffickers
    # IDEA maybe swap trafficker id in event to event id in trafficker, then would need to figure out when to create Traffickers in relation to Events
    sql_create_events_table = """ CREATE TABLE IF NOT EXISTS Events (
                                        id integer PRIMARY KEY,
                                        location_id integer,
                                        trafficker_id integer,
                                        arrests integer,
                                        event_date text,
                                        FOREIGN KEY (location_id) REFERENCES locations (id),
                                        FOREIGN KEY (trafficker_id) REFERENCES traffickers (id)
                                    ); """

    sql_create_products_table = """ CREATE TABLE IF NOT EXISTS Products (
                                        id integer PRIMARY KEY,
                                        event_id integer,
                                        product_name text NOT NULL,
                                        description text,
                                        animal text,
                                        quantity integer,
                                        weight_kg real,
                                        price_usd real,
                                        transportation_method text,
                                        FOREIGN KEY (event_id) REFERENCES events (id)
                                    ); """

    # NOTE assumption is all traffickers mentioned in text are arrested, sentence is legal outcome after arrest (ex. 2 years prison)
    sql_create_traffickers_table = """ CREATE TABLE IF NOT EXISTS Traffickers (
                                    id integer PRIMARY KEY,
                                    name text,
                                    organization text,
                                    description text,
                                    sentence text
                                ); """

    sql_create_nationalities_table = """ CREATE TABLE IF NOT EXISTS Nationalities (
                                    trafficker_id integer,
                                    country text,
                                    FOREIGN KEY (trafficker_id) REFERENCES Traffickers (id),
                                    FOREIGN KEY (country) REFERENCES Countries (country)
                                ); """

    sql_create_roles_table = """ CREATE TABLE IF NOT EXISTS Roles (
                                    trafficker_id integer,
                                    role text,
                                    FOREIGN KEY (trafficker_id) REFERENCES Traffickers (id)
                                ); """

    with create_connection(database) as connection:
        # create tables
        tables = [sql_create_countries_table, sql_create_cities_table, sql_create_locations_table, sql_create_events_table, sql_create_products_table, sql_create_traffickers_table, sql_create_nationalities_table, sql_create_roles_table]
        if connection is not None:
            for table in tables:
                create_table(connection, table)
        else:
            print("Error! Cannot create the database connection.")

        connection.commit()
        print("Database Created")
    print("Disconnected")

def create_connection(db_file):
    """ create a database connection to the SQLite database specified by db_file """
    # :param db_file: database file
    # :return: Connection object or None

    connection = None
    try:
        connection = sqlite3.connect(db_file, timeout=5)
        print("Connected Successfully")
        return connection
    except Error as e:
        print(e)

    return connection

def create_table(connection, create_table_sql):
    """ create a table from the create_table_sql statement """
    # :param connection: Connection object
    # :param create_table_sql: a CREATE TABLE statement
    # :return:

    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except Error as e:
        print(e)

def drop_table(connection, drop_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(drop_table_sql)
    except Exception as e:
        print(e)

# rows = list of dictionaries of same format
# insert query must be of form f"INSERT INTO table_name VALUES (?,?,?...)" where number of ? marks must match number of values in dictionary
def add_rows(connection, rows, insert_query):
    sql_rows = []
    for row in rows:
        sql_row = tuple(row.entry().values())
        sql_rows.append(sql_row)
    cursor = connection.cursor()
    cursor.executemany(insert_query, sql_rows)
    connection.commit()

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
