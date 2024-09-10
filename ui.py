import MTA
import csv_to_db
import datetime
from simple_term_menu import TerminalMenu
import mta_output_formatting
import sqlite3
import pprint



def select_a_stop(stations):
    """
    Select a stop prompt and selection menu. 
    Prompts user to select a station.
    Takes a list of tuples with station name and id as input.

    Returns a dictionary containing the station id and stop name.
    Input:
    [('Court Sq', 'G22'),
    ('21 St', 'G24'),
    ('Greenpoint Av', 'G26'),
    ('Nassau Av', 'G28'),
    ...
    ('15 St-Prospect Park', 'F25'),
    ('Fort Hamilton Pkwy', 'F26'),
    ('Church Av', 'F27')]

    Output:
    {'station_id': 'G29', 'stop_name': 'Metropolitan Av'}
    """
    options = [station[0] for station in stations]
    terminal_menu = TerminalMenu(options, title="Select a stop:")
    menu_entry_index = terminal_menu.show()
    return {"station_id": stations[menu_entry_index][1], "stop_name": options[menu_entry_index]}

def select_a_direction():
    """
    Prompts user to select a direction, either "N", or "S".
    Returns a direction character, either "N" or "S".
    """
    options = ["N", "S"]
    terminal_menu = TerminalMenu(options, title="Select a direction:")
    menu_entry_index = terminal_menu.show()
    return options[menu_entry_index]

def station_lookup(station_id):
    """
    Returns the id of a station from the the 'groute' table in the mtainfo db.
    Requires a station id as input.
    Input: str (Three character station id, eg. "F27" )
    Output: int (Index of the station id in the groute table, eg 1)
    """
    connection = sqlite3.connect('mtainfo.db')
    cursor = connection.cursor()
    sql = """
    SELECT id FROM groute WHERE stop_id = ?
    """
    postion = cursor.execute(sql, [station_id]).fetchone()
    if postion:
        return postion[0]
    else:
        return None


if __name__ == "__main__":

    stations = csv_to_db.get_stations_id_and_name()

    starting_point = select_a_stop(stations)
    end_point = None
    print(f'You selected: {starting_point["stop_name"]}')
    add_stop = input("Do you want to add a stop? Y/n: ")

    # 1725907267

    if add_stop.upper() == "Y":
        end_point = select_a_stop(stations)
        print(f'Your starting station is : {starting_point["stop_name"]}')

        print(f'Your destination station is: {end_point["stop_name"]}')
        starting_postion = station_lookup(starting_point["station_id"])
        destination_postion = station_lookup(end_point["station_id"])
        if (starting_postion - destination_postion) > 0:
            direction = "S"
        else:
            direction = "N"
        print(f'Going: {direction}')
        arriving_train = MTA.next_train_arrival(starting_point['station_id'], direction)
        arriving_time = arriving_train['arrival_time']
        destination_time = MTA.get_arrival_time_for_destination(arriving_train, end_point['station_id'])['destination_arrival_time']
        print(f"You train from {starting_point['stop_name']} will depart at {datetime.datetime.fromtimestamp(arriving_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"To {end_point['stop_name']} and will arrive at {datetime.datetime.fromtimestamp(destination_time).strftime('%Y-%m-%d %H:%M:%S')}")
        trip_time = destination_time - arriving_time
        print(f'Total trip time is expected to be: {mta_output_formatting.convert_seconds(trip_time)}')
    else:
        direction = select_a_direction()
        print(f'You selected: {starting_point["stop_name"]}')
        print(f'Going: {direction}')
        arriving_train = MTA.next_train_arrival(starting_point['station_id'], direction)
        print(f"Your train is arriving at {datetime.datetime.fromtimestamp(arriving_train['arrival_time']).strftime('%Y-%m-%d %H:%M:%S')}")
    
