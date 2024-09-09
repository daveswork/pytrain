import MTA
import csv_to_db
import datetime


print(type(csv_to_db.get_stations_id_and_name()))

print("Select a stop: ")
starting_point = csv_to_db.mta_select_stop(csv_to_db.get_stations_id_and_name())

print(f'You selected: {starting_point["stop_name"]}')
test = input("Do you want to add a stop? Y/n: ")

arriving_at = MTA.next_train_arrival(starting_point['station_id'], "S")

print(arriving_at)
