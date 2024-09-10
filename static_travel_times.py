import sqlite3


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


def populate_static_travel_time(timeslist):
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
    trip_id = next(iter(timeslist[0]))
    direction = trip_id[-4]
    connection = sqlite3.connect("mtainfo.db")
    cursor = connection.cursor()

    populate_north_table = """
    INSERT INTO origin_destination_times_north(origin_id, destination_id, time)
    VALUES(? ? ?)
    """

    populate_south_table = """
    INSERT INTO origin_destination_times_south(origin_id, destination_id, time)
    VALUES(? ? ?)
    """

    for i in range(1,len(timeslist)):
        if direction == "N":
            cursor.execute(populate_north_table, [timeslist[i]['origin'], timeslist[i]['destination'], timeslist[i]['trip_time'] ])
            connection.commit()
        elif direction == "S":
            cursor.execute(populate_south_table, [timeslist[i]['origin'], timeslist[i]['destination'], timeslist[i]['trip_time'] ])
            connection.commit()

    connection.close()

if __name__ == "__main__":
    # build_static_travel_time_table_north()
    # build_static_travel_time_table_south()
    pass
