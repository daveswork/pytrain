import MTA
import csv_to_db
import datetime
from simple_term_menu import TerminalMenu
import mta_output_formatting
import sqlite3
import train_ascii
import random
import time
import pprint


ascii_art = [train_ascii.metrocard, train_ascii.train, train_ascii.small_train, \
             train_ascii.pt_logo1, train_ascii.pt_logo2, train_ascii.pt_logo3, \
             train_ascii.pt_logo4, train_ascii.pt_logo5,train_ascii.skyline_1, \
             train_ascii.skyline_2 ]

def logos():
    print(ascii_art[random.randint(0, len(ascii_art)-1)])

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

def station_lookup(station_id, line):
    """
    Returns the id of a station from the the 'groute' table in the mtainfo db.
    Requires a station id as input.
    Input: str (Three character station id, eg. "F27" )
    Output: int (Index of the station id in the groute table, eg 1)
    """
    connection = sqlite3.connect('mtainfo.db')
    cursor = connection.cursor()
    if line == "g":
        sql = """
        SELECT id FROM groute WHERE stop_id = ?
        """
    elif line == "l":
        sql = """
        SELECT id FROM lroute WHERE stop_id = ?
        """
    postion = cursor.execute(sql, [station_id]).fetchone()
    if postion:
        return postion[0]
    else:
        return None
    
def arriving_display(starting_point, direction, end_point,originating_time=None, line= "g"):
        """
        Takes the following inputs:
        starting_point = dict (eg {'station_id': 'G29', 'stop_name': 'Metropolitan Av'})
        direction = str (eg. "N" or "S")
        end_point  dict (eg {'station_id': 'G29', 'stop_name': 'Metropolitan Av'})
        originating time = int (epoch time to set to retrieve the next traing. eg 1726062182)
        Returns arrival epoch time in seconds as int eg (1726062182)
        
        """
        starting_postion = station_lookup(starting_point["station_id"], line)
        destination_postion = station_lookup(end_point["station_id"], line)
        number_of_stops = starting_postion - destination_postion
        if number_of_stops < 0:
            number_of_stops = number_of_stops * -1
        print("Originating time:", originating_time)
        arriving_train = MTA.next_train_arrival(starting_point['station_id'], direction, originating_time, line=line)
        arriving_time = arriving_train['arrival_time']
        destination_time = MTA.get_arrival_time_for_destination(arriving_train, end_point['station_id'])['destination_arrival_time']
        # print('You train from { :>30} will depart at \n {: >20}'.format(starting_point['stop_name'], datetime.datetime.fromtimestamp(arriving_time).strftime('%Y-%m-%d %H:%M:%S')))
        # print('Your train to {:>22} will depart at {:>20}'.format(starting_point['stop_name'],datetime.datetime.fromtimestamp(arriving_time).strftime('%Y-%m-%d %H:%M:%S') ))
        print(f"Departure time {datetime.datetime.fromtimestamp(arriving_time).strftime('%Y-%m-%d %H:%M:%S')} {starting_point['stop_name']}")
        # print(f"To {end_point['stop_name']} and will arrive at \n {datetime.datetime.fromtimestamp(destination_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Arrival time   {datetime.datetime.fromtimestamp(destination_time).strftime('%Y-%m-%d %H:%M:%S')} {end_point['stop_name']}")
        print(f'Number of stops: {number_of_stops}')
        trip_time = destination_time - arriving_time
        print(f'Total trip time is expected to be: {mta_output_formatting.convert_seconds(trip_time)}')
        # print(MTA.is_train_slow(arriving_train))
        logos()
        return arriving_time

def new_trip(stations, line):
    """
    Takes a list of stations eg:
    [('Court Sq', 'G22'),
    ('21 St', 'G24'),
    ('Greenpoint Av', 'G26'),
    ...
    ('15 St-Prospect Park', 'F25'),
    ('Fort Hamilton Pkwy', 'F26'),
    ('Church Av', 'F27')]

    Generates dialog for a new trip.
    """
    starting_point = select_a_stop(stations)
    print(f'You selected: {starting_point["stop_name"]}')
    add_stop = input("Do you want to add a stop? Y/n: ")

    if add_stop.upper() == "Y":
        end_point = select_a_stop(stations)
        print(f'Your starting station is : {starting_point["stop_name"]}')

        print(f'Your destination station is: {end_point["stop_name"]}')
        starting_postion = station_lookup(starting_point["station_id"], line)
        destination_postion = station_lookup(end_point["station_id"], line)
        if (starting_postion - destination_postion) > 0:
            direction = "S"
        else:
            direction = "N"
        print(f'Going: {direction}')
        new_arriving_time = arriving_display(starting_point, direction, end_point, line=line)

        next_train = input("Do you want to get the next train? (Y/n): ").upper()
        while next_train == "Y":
            new_arriving_time = arriving_display(starting_point, direction, end_point, new_arriving_time, line=line)
            next_train = input("Do you want to get the next train? (Y/n): ").upper()
    else:
        direction = select_a_direction()
        print(f'You selected: {starting_point["stop_name"]}')
        print(f'Going: {direction}')
        arriving_train = MTA.next_train_arrival(starting_point['station_id'], direction, line=line)
        print(f"Your train is arriving at \n {datetime.datetime.fromtimestamp(arriving_train['arrival_time']).strftime('%Y-%m-%d %H:%M:%S')}")
        # print(arriving_train)
        # if arriving_train['arrival_time'] > 0:
        #     print(MTA.is_train_slow(arriving_train))
        logos() 

def select_a_line():
    options = ["G", "L"]
    terminal_menu = TerminalMenu(options, title="Select a line:")
    menu_entry_index = terminal_menu.show()
    return options[menu_entry_index].lower()

def main():
    line = select_a_line()
    stations = csv_to_db.get_stations_id_and_name(line)
    end_point = None
    new_trip(stations, line)
    another_trip = input("Do you want schedule another trip (Y/n): ").upper()
    while another_trip == "Y":
        new_trip(stations, line)
        another_trip = input("Do you want schedule another trip (Y/n): ").upper()



if __name__ == "__main__":
    main()

    
