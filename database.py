import sqlite3
import logging
from variables import schema
from string import Template
from utilities import func_name
from os.path import isfile, isdir, join
from PIL import Image
from io import BytesIO

def connect_database(config, logger, **kwargs):
    logger = logging.getLogger(func_name())
    logger.debug(kwargs)

    database = config.database

    if not isfile(database):
        logger.warning("Use create database instead")
        return False
    connection = sqlite3.connect(database)
    sqlite_select_Query = "select sqlite_version();"
    cursor = connection.cursor()
    cursor.execute(sqlite_select_Query)
    record = cursor.fetchall()

    logger.debug("SQLite Database Version is: %s ", record)
    return connection


def create_table(logger, table_name, table_schema, connection, **kwargs):
    logger = logging.getLogger(func_name())
    logger.debug(table_name, table_schema, kwargs)

    cursor = connection.cursor()

    field_list = ""
    sql_template = Template("""CREATE TABLE  '${table_name}' (\n${field_list});""")
    for field, field_type in table_schema.items():
        field_list += "\t"
        field_list += " \t\t".join([field, field_type])
        field_list += ",\n"
    sql_create = sql_template.substitute(table_name=table_name, field_list=field_list[:-2])
    logger.debug(sql_create)
    cursor.execute(sql_create)

    cursor.close()


def create_database(config, logger, schema_list, **kwargs):
    """
    Create a database if none exists

    """
    database = config.database
    logger = logging.getLogger(func_name())
    logger.debug(database, schema_list, kwargs)

    connection = sqlite3.connect(database)
    sqlite_select_Query = "select sqlite_version();"
    cursor = connection.cursor()
    cursor.execute(sqlite_select_Query)
    record = cursor.fetchall()
    logger.info("Creating Database {}".format(database))
    logger.debug("SQLite Database Version is: ", record)


    # Put a list of tables from Globals to create schema
    cursor.execute("PRAGMA journal_mode=WAL;")
    logger.debug("Modifying database for WAL access")
    # Create all Schemas if new
    for schema in schema_list:
        table_name = list(schema.keys())[0]
        table_schema = schema[table_name]

        logger.debug('creating table: ', table_name)

        create_table(logger, table_name, table_schema, connection)

    cursor.close()
    connection.close()


def create_table(logger, table_name, table_schema, connection, **kwargs):
    logger = logging.getLogger(func_name())
    logger.debug(table_name, table_schema, kwargs)

    cursor = connection.cursor()

    field_list = ""
    sql_template = Template("""CREATE TABLE  '${table_name}' (\n${field_list});""")
    for field, field_type in table_schema.items():
        field_list += "\t"
        field_list += " \t\t".join([field, field_type])
        field_list += ",\n"
    sql_create = sql_template.substitute(table_name=table_name, field_list=field_list[:-2])
    logger.debug(sql_create)
    cursor.execute(sql_create)

    cursor.close()


def insert_into_db(logger, connection, table, record, **kwargs):
    """
    record is a dictionary
    """
    logger.debug('record filename {}'.format(record['filename_full']))
    logger.info('Writing record to table %s',table)
    logger = logging.getLogger(func_name())
    logger.debug(table, record, **kwargs)
    column_names = list()
    values = list()

    if not connection:
        logger.warning("Connection not valid")
        return False

    cursor = connection.cursor()
    sql_template = Template("""INSERT INTO ${table} (${columns}) VALUES (${values});""")
    column_names = ",".join(list(record.keys()))
    logger.debug(column_names)
    data_values = tuple(record.values())
    num_columns = len(list(record.keys()))
    values = ",".join([' ?'] * num_columns)
    sql_insert = sql_template.substitute(table=table, columns=column_names, values=values)
    logger.debug('columns_names %s', column_names)
    logger.debug("data values %s", data_values)
    logger.debug(sql_insert)
    logger.debug('columns_names',column_names)
    cursor.execute(sql_insert, data_values)
    connection.commit()

    return cursor.lastrowid


def insertImage(logger, connection, table_name, filename, name, image):
    print('inserting image into table {}'.format(table_name))
    try:
        sqlite_insert_blob_query = """ INSERT INTO {table_name}
                                  (filename, userid, headshot_image) VALUES (?, ?, ?)""".format(
            table_name=table_name)

        cursor = connection.cursor()
        # Convert data into tuple format
        data_tuple = (filename, name, image)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        connection.commit()
        print("Image and information {info} inserted successfully as a BLOB into a table {table_name}".format(info=name,
                                                                                                          table_name=table_name))

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)

def get_named_faces(logger,connection,table_name):
    named_faces = dict()
    logger = logging.getLogger(func_name())
    logger.debug("get named faces from table %s", table_name)
    cursor = connection.cursor()
    sql_template = Template("""select * from  ${table} order by user_id;""")
    sql = sql_template.substitute(table_name=table_name)
    cursor.execute(sql)
    records = cursor.fetchall()
    for record in records:
        pass


