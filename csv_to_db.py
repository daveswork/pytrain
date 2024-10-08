import csv
import sqlite3
from simple_term_menu import TerminalMenu

# Source data 
# https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f/about_data

#Station fields
# id, 
# gtfs_stop_id, 
# station_id, 
# complex_id, 
# division, 
# line, 
# stop_name, 
# borough, 
# cbd, 
# daytime_routes, 
# structure, 
# gtfs_latitude, 
# gtfs_longitude, 
# north_direction_label, 
# south_direction_label, 
# ada, 
# ada_northbound, 
# ada_southbound, 
# ada_notes, 
# georeference


def subway_station_csv_to_db(csvfile):
    """
    Takes a csv file and converts it to a sqlite db.
    Data should be sourced from: 
    https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f/about_data

    """
    connection = sqlite3.connect('mtainfo.db')
    cursor = connection.cursor()
    create_table = """
    CREATE TABLE IF NOT EXISTS mtainfo(
        id INTEGER PRIMARY KEY,
        gtfs_stop_id TEXT,
        station_id INTEGER,
        complex_id INTEGER,
        division TEXT,
        line TEXT,
        stop_name TEXT,
        borough TEXT,
        cbd TEXT,
        daytime_routes TEXT,
        structure TEXT,
        gtfs_latitude REAL,
        gtfs_longitude REAL,
        north_direction_label TEXT,
        south_direction_label TEXT,
        ada TEXT,
        ada_northbound TEXT,
        ada_southbound TEXT,
        ada_notes TEXT,
        georeference TEXT)
    """

    cursor.execute(create_table)
    # file = open('MTA_Subway_Stations_20240906.csv')
    file = open(csvfile)
    contents = csv.reader(file)
    next(contents, None)
    insert_records = """

    INSERT INTO mtainfo(
    gtfs_stop_id, station_id, complex_id, division, line, stop_name, borough, cbd, daytime_routes, structure, gtfs_latitude, gtfs_longitude, north_direction_label, south_direction_label, ada, ada_northbound, ada_southbound, ada_notes, georeference) 
    VALUES(
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
    )
    """

    cursor.executemany(insert_records, contents)
    select_all = "SELECT * FROM mtainfo"
    # rows = cursor.execute(select_all).fetchall()
    # for r in rows:
    #     print(r)
    connection.commit()
    connection.close()

def mta_subway_station_query(stop_id):
    """
    Takes stop id of format "G22N" and returns the subway station as a dict.
    Will return 'None' if the station is invalid or not found.
    Sample return value for G22N:
    {'id': 244, 'gtfs_stop_id': 'G22', 'station_id': 281, 'complex_id': 606, 
    'division': 'IND', 'line': 'Crosstown', 'stop_name': 'Court Sq', 
    'borough': 'Q', 'cbd': 'FALSE', 'daytime_routes': 'G', 
    'structure': 'Subway', 'gtfs_latitude': 40.746554, 
    'gtfs_longitude': -73.943832, 'north_direction_label': 'Last Stop', 
    'south_direction_label': 'Brooklyn', 'ada': '1', 'ada_northbound': '1', 
    'ada_southbound': '1', 'ada_notes': '', 
    'georeference': 'POINT (-73.943832 40.746554)'}

    """
    connection = sqlite3.connect('mtainfo.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    gtfs_stop_id = stop_id[:-1]
    sql = """
        SELECT * FROM mtainfo WHERE gtfs_stop_id = ?
    """
    station = cursor.execute(sql, [gtfs_stop_id]).fetchone()
    connection.close()
    if station is None:
        return station
    return dict(station)

def get_stations_id_and_name(line):
    """
    Input: None
    Returns a list of tuples with station names and ids
    Output:
    [('Court Sq', 'G22'),
    ('21 St', 'G24'),
    ('Greenpoint Av', 'G26'),
    ('Nassau Av', 'G28'),
    ('Metropolitan Av', 'G29'),
    ('Broadway', 'G30'),
    ('Flushing Av', 'G31'),
    ('Myrtle-Willoughby Avs', 'G32'),
    ('Bedford-Nostrand Avs', 'G33'),
    ('Classon Av', 'G34'),
    ('Clinton-Washington Avs', 'G35'),
    ('Fulton St', 'G36'),
    ('Hoyt-Schermerhorn Sts', 'A42'),
    ('Bergen St', 'F20'),
    ('Carroll St', 'F21'),
    ('Smith-9 Sts', 'F22'),
    ('4 Av-9 St', 'F23'),
    ('7 Av', 'F24'),
    ('15 St-Prospect Park', 'F25'),
    ('Fort Hamilton Pkwy', 'F26'),
    ('Church Av', 'F27')]

    """
    connection = sqlite3.connect("mtainfo.db")
    cursor = connection.cursor()
    if line == "g":
            sql = """
            SELECT stop_name, stop_id FROM groute
            """
    elif line == "l":
        sql = """
            SELECT stop_name, stop_id FROM lroute
        """
    stations = cursor.execute(sql).fetchall()
    connection.close()
    return stations[::-1]



def mta_select_stop(stations):
    """
    Select a stop prompt and selection menu. 
    Returns a dictionary containing the station id and stop name.
    eg:
    {'station_id': 'G29', 'stop_name': 'Metropolitan Av'}
    """

    options = [station[0] for station in stations]
    terminal_menu = TerminalMenu(options, title="Select a stop:")
    menu_entry_index = terminal_menu.show()
    return {"station_id": stations[menu_entry_index][1], "stop_name": options[menu_entry_index]}
    

if __name__ == "__main__":
    pass