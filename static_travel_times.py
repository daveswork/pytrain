import sqlite3
import MTA

def build_static_travel_time_table_north():
    connection = sqlite3.connect("mtainfo.db")
    cursor = connection.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS origin_destination_times_north(
    id INTEGER PRIMARY KEY,
    origin_id TEXT,
    destination_id TEXT,
    time INT
    )
    """
    cursor.execute(create_table_sql)
    connection.commit()
    connection.close()

def build_static_travel_time_table_south():
    connection = sqlite3.connect("mtainfo.db")
    cursor = connection.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS origin_destination_times_south(
    id INTEGER PRIMARY KEY,
    origin_id TEXT,
    destination_id TEXT,
    time INT
    )
    """
    cursor.execute(create_table_sql)
    connection.commit()
    connection.close()


def populate_static_travel_time(timeslist, direction):
    """
    Takes a list genertated from MTA.get_stop_to_stop_times()
    [{'103350_G..S14R'},
    {'destination': 'G24', 'origin': 'G22', 'trip_time': 60},
    {'destination': 'G26', 'origin': 'G24', 'trip_time': 180}
    ...
     {'destination': 'F26', 'origin': 'F25', 'trip_time': 150},
    {'destination': 'F27', 'origin': 'F26', 'trip_time': 120}]

    Expects the first element to be a trip id.
    Populuates the respective table based on the direction in the trip id.
    """

    connection = sqlite3.connect("mtainfo.db")
    cursor = connection.cursor()

    populate_north_table = """
    INSERT INTO origin_destination_times_north(origin_id, destination_id, time)
    VALUES(?,?,?)
    """

    populate_south_table = """
    INSERT INTO origin_destination_times_south(origin_id, destination_id, time)
    VALUES(?,?,?)
    """

    for timedata in timeslist:
        if direction == "N":
            cursor.execute(populate_north_table, [timedata['origin'], timedata['destination'], timedata['trip_time'] ])
            connection.commit()
        elif direction == "S":
            cursor.execute(populate_south_table, [timedata['origin'], timedata['destination'], timedata['trip_time'] ])
            connection.commit()

    connection.close()

def query_static_time_table(origin, direction):
    """
    Takes an origin(eg, "G22") and direction ("N", or "S")
    query_static_time_table("G29", "N")
    output:
    {'origin_id': 'G29', 'destination_id': 'G28', 'time': 180}
    """

    connection = sqlite3.connect("mtainfo.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    sql_north = """
        SELECT origin_id, destination_id, time FROM origin_destination_times_north
        WHERE origin_id = ?
    """
    sql_south = """
        SELECT origin_id, destination_id, time FROM origin_destination_times_south
        WHERE origin_id = ?
    """
    if direction == "N":
        time_table = cursor.execute(sql_north, [origin,]).fetchone()
    elif direction == "S":
        time_table = cursor.execute(sql_south, [origin,]).fetchone()
    connection.close()
    if time_table is None:
        return None
    else:
        return dict(time_table)




if __name__ == "__main__":
    # build_static_travel_time_table_north()
    # build_static_travel_time_table_south()
    # populate_static_travel_time(MTA.get_stop_to_stop_times("S"), "S")

    pass
