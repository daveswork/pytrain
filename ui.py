import MTA
import csv_to_db
import datetime
from simple_term_menu import TerminalMenu



def select_a_stop(stations):
    options = [station[0] for station in stations]
    terminal_menu = TerminalMenu(options, title="Select a stop:")
    menu_entry_index = terminal_menu.show()
    return {"station_id": stations[menu_entry_index][1], "stop_name": options[menu_entry_index]}

def select_a_direction():
    """
    Returns a direction character, either "N" or "S".
    """
    options = ["N", "S"]
    terminal_menu = TerminalMenu(options, title="Select a direction:")
    menu_entry_index = terminal_menu.show()
    return options[menu_entry_index]



stations = csv_to_db.get_stations_id_and_name()

starting_point = select_a_stop(stations)
end_point = None
print(f'You selected: {starting_point["stop_name"]}')
direction= select_a_direction()
add_stop = input("Do you want to add a stop? Y/n: ")
if add_stop.upper() == "Y":
    end_point = select_a_stop(stations)
    print(f'Your starting station is : {starting_point["stop_name"]}')
    print(f'Your destination station is: {end_point["stop_name"]}')
else:
    print(f'You selected: {starting_point["stop_name"]}')
    arriving_at = MTA.next_train_arrival(starting_point['station_id'], "S")
    print(arriving_at)
