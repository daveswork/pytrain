import sqlite3
from MTA import get_stop_sequence
from csv_to_db import mta_subway_station_query



stops_in_sequence = get_stop_sequence()



for stop in stops_in_sequence:
    print(stop, mta_subway_station_query(stop)["stop_name"])


def build_g_stop_database(stops_list):
    connection = sqlite3.connect('mtainfo.db')
    cursor = connection.cursor()
    create_table = """
    CREATE TABLE IF NOT EXISTS groute(
    id INTEGER PRIMARY KEY,
    stop_id TEXT,
    stop_name TEXT
    )
    """


    cursor.execute(create_table)
    add_stop = """
    INSERT INTO groute(
    stop_id,
    stop_name
    )
    VALUES (?, ?)
    """

    for stop in stops_list:
        cursor.execute(add_stop, [stop[:-1], mta_subway_station_query(stop)["stop_name"]])

    connection.commit()
    connection.close()


# build_g_stop_database(stops_in_sequence)
