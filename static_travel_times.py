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

def build_static_travel_time_table_all():
    connection = sqlite3.connect("mtainfo.db")
    cursor = connection.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS origin_destination_times_all(
    id INTEGER PRIMARY KEY,
    line TEXT,
    direction TEXT,
    origin_id TEXT,
    destination_id TEXT,
    time INT
    )
    """
    cursor.execute(create_table_sql)
    connection.commit()
    connection.close()

def populate_static_travel_time_all(timelist):
    """
    Takes a list genertated from MTA.get_stop_to_stop_times()
    [{'origin': 'L29', 'destination': 'L28', 'trip_time': 1726086435, 'direction': 'N', 'line': 'l'}, 
    {'origin': 'L28', 'destination': 'L27', 'trip_time': 120, 'direction': 'N', 'line': 'l'}, 
    {'origin': 'L27', 'destination': 'L26', 'trip_time': 90, 'direction': 'N', 'line': 'l'}
    ...
    {'origin': 'L05', 'destination': 'L03', 'trip_time': 60, 'direction': 'N', 'line': 'l'}, 
    {'origin': 'L03', 'destination': 'L02', 'trip_time': 90, 'direction': 'N', 'line': 'l'}, 
    {'origin': 'L02', 'destination': 'L01', 'trip_time': 150, 'direction': 'N', 'line': 'l'}]

    Expects the first element to be a trip id.
    Populuates the respective table based on the direction in the trip id.
    """
    connection = sqlite3.connect("mtainfo.db")
    cursor = connection.cursor()

    populate_table = """
    INSERT INTO origin_destination_times_all(line, direction, origin_id, destination_id, time)
    VALUES(?,?,?,?,?)
    """

    for timedata in timelist:
        cursor.execute(populate_table, [timedata['line'], timedata['direction'], timedata['origin'], timedata['destination'], timedata['trip_time'] ])
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

def query_static_time_table(origin, direction, line="g"):
    """
    Takes an origin(eg, "G22") and direction ("N", or "S")
    query_static_time_table("G29", "N")
    output:
    {'origin_id': 'G29', 'destination_id': 'G28', 'time': 180}
    """

    connection = sqlite3.connect("mtainfo.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if line == "g":
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
    else:
        sql_all = """
            SELECT origin_id, destination_id, time FROM origin_destination_times_all
            WHERE origin_id = ? AND direction = ? AND line = ?
        """
        time_table = cursor.execute(sql_all, [origin, direction, line]).fetchone()
        connection.close()
        if time_table is None:
            return None
        else:
            return dict(time_table)




if __name__ == "__main__":
    # build_static_travel_time_table_north()
    # build_static_travel_time_table_south()
    # populate_static_travel_time(MTA.get_stop_to_stop_times("S"), "S")
    # build_static_travel_time_table_all()
    # south_times = MTA.get_stop_to_stop_times("S", "l")
    # for times in south_times:
    #     times["direction"] = "S"
    #     times["line"] = "l"
    # populate_static_travel_time_all(south_times)

    # north_times = MTA.get_stop_to_stop_times("N", "l")
    # for times in north_times:
    #     times["direction"] = "N"
    #     times["line"] = "l"
    # populate_static_travel_time_all(north_times)
    pass


