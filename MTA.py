from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime, timedelta
from mta_output_formatting import time_difference, convert_seconds
import pprint
import csv_to_db 
import static_travel_times

# this is the API request that is used to get realtime train data in GTFS format.
# the url endpoint specifies an individual train line.
# feed contains the info we use in the program
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g')
feed.ParseFromString(response.content)

# current time
ct = datetime.now()

# convert 10 digit POSIX timestamp used in feed to readable format
def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp)

# 
def convert_seconds(seconds):
    return timedelta(seconds = seconds)

# returns a list of all trains traveling either N or S
def filter_direction(direction):
    filtered_trains = []
    # loops throught the feed and appends trains to filtered_trains list if they are going in the specified direction 
    for train in get_all_trains():
        if train["direction"] == direction:
            filtered_trains.append(train)
    return filtered_trains

# takes a list of train objs and a station as args
# loops through each train's array of stops and returns a list of trains that will stop at the specified station
def filter_stations(station, train_list):
    filtered_stations = []
    for train in train_list:
        for stop in train["next_stops_array"]:
            if stop["stop_id"][:-1] == station:
                filtered_stations.append(train)
    return filtered_stations

# MAIN FUNCTION 
# Returns a dict that contains info on the next train arriving at the specified station. Takes station and direction as args.
def next_train_arrival(station, direction, future_time = None):
    direction_bound_trains = []
    if future_time is None:
        ct_epoch = int(ct.timestamp())
    else:
        ct_epoch = future_time
    min_time = 3600
    best_time = 0
    best_train = {}

# loop through all_trains list returned from get_trains_function and appends trains traveling in the selected direction to direction_bound_trains
    for train in filter_direction(direction):
        direction_bound_trains.append(train)
# next_train_list contains every train that will stop at the chosen station. It is created using the list of direction bound trains that has been filtered for direction. 
    next_train_list = filter_stations(station, direction_bound_trains)
# loop through each train in next train list, find the train with arrival time closest to current time, and return that train, the arrival time, and the seconds to arrival, in dict (best_train)
    for train in next_train_list:
        # arrival_time finds the station in each train's next_stops_array and returns the arrival time for the station
        arrival_time = get_arrival_time_for_station(train, station)
        # time difference subtracts the arrival time (future) from the current time, and returns a delta time in seconds.
        # the smallest time will be filtered and set to min_time.
        # the train with the lowest min time will have its data (arrival time, train obj) set to the best_time and best_train variables
        if time_difference(ct_epoch, arrival_time) < min_time and time_difference(ct_epoch, arrival_time) > 0:
            min_time = time_difference(ct_epoch, arrival_time)
            best_time = arrival_time
            best_train = train
    # the function returns a dict containing the entire train obj(best_train), as well as arrival time for the station, and seconds to arrival.
    return {
        "train" : best_train,
        "arrival_time" : best_time,
        "arriving_in" : time_difference(ct_epoch, best_time)
    }

# loop through the next_stops_array of a train object and return the arrival time for the stop that matches the stop_id (station)
def get_arrival_time_for_station(train, station):
    for stop in train["next_stops_array"]:
        if stop["stop_id"][:-1] == station:
            return stop["arrival_time"]

# this function takes the train object returned from the next_train_arrival function as a first argument and a destination station as its second argument.
# it returns the train object it took as the first argument, but with a 'destination_arrival_time' key value pair added. 
# because this train object is the first train arriving to the chosen platform, its arrival time at the destination platform will be the quickest arrival time available.
def get_arrival_time_for_destination(train_obj, end_station):
    new_train_obj = {
        **train_obj,
        "destination_arrival_time" : 0
    }
    # find the station in the stops array and add it's arrival time to new_train_obj
    for stop in train_obj["train"]["next_stops_array"]:
        if stop["stop_id"][:-1] == end_station:
            new_train_obj = {
                **train_obj,
                "destination_arrival_time" : stop["arrival_time"]
            }
    return new_train_obj

# this function takes a train at the end of the feed from the MTA and uses it's stop array to build an ordered route of stops.
#  trains that have not embarked on their routes are located at the end of the feed, and have the entire route contained in their stop array.
def get_stop_sequence():
    stops = []
    for stop in feed.entity[-2].trip_update.stop_time_update:
        stops.append(stop.stop_id)
    return stops

def get_vehicle_by_id(trip_id):
    for entity in feed.entity:
        if entity.HasField("vehicle") and entity.vehicle.trip.trip_id == trip_id:
            print("V", entity)
        elif entity.HasField("trip_update")  and len(entity.trip_update.stop_time_update) > 0 and entity.trip_update.trip.trip_id == trip_id:
            print(entity)

def get_stop_to_stop_times(direction):
    stop_times = []
    stop_to_stop_times = []
    for stop_time in filter_direction(direction)[-1]["next_stops_array"]:
        stop_and_time = (stop_time["stop_id"], stop_time["arrival_time"])
        stop_times.append(stop_and_time)
    i = 0
    while i < len(stop_times) - 1:
        stop_time_dict = {
            "origin" : stop_times[i][0][:-1],
            "destination" : stop_times[i + 1][0][:-1],
            "trip_time" : time_difference(stop_times[i][1], stop_times[i+1][1]) 
        }
        stop_to_stop_times.append(stop_time_dict)
        i += 1
    return stop_to_stop_times

def is_train_slow(train_obj):
    trip_id = train_obj["train"]["trip_id"]
    last_station_id = train_obj["train"]["next_stops_array"][0]["stop_id"]
    last_station_arrival = train_obj["train"]["next_stops_array"][0]["arrival_time"]
    next_station_id = train_obj["train"]["next_stops_array"][1]["stop_id"]
    next_station_arrival = train_obj["train"]["next_stops_array"][1]["arrival_time"]
    train_dict = {
        "trip_id" : trip_id,
        "origin" : last_station_id,
        "destination" : next_station_id,
        "trip_time" : time_difference(last_station_arrival, next_station_arrival)
    }
    # print(train_dict)
    # print(static_travel_times.query_static_time_table(last_station_id[:-1], last_station_id[-1]))
    if static_travel_times.query_static_time_table(last_station_id[:-1], last_station_id[-1])["time"] < train_dict["trip_time"]:
        return "Expect delays..."
    else:
        return "Train on time."

# this function takes the GTFS feed from the request and returns a list of train objects that will be used in all of our functions.
# each train is called an entity, and if that entity has a 'trip_update" key and an array of stops, then it will contain the information that our program uses.
# entities that don't contain this info will be ignored.
def get_all_trains():
    all_trains = []
    for entity in feed.entity:
        if entity.HasField('trip_update') and len(entity.trip_update.stop_time_update) >= 1:
            trip_id = entity.trip_update.trip.trip_id
            route_id = entity.trip_update.trip.route_id
            start_time = entity.trip_update.trip.start_time
            last_station = entity.trip_update.stop_time_update[0].stop_id
            last_station_departure = entity.trip_update.stop_time_update[0].departure.time
            all_stops = []
            for stop in entity.trip_update.stop_time_update:
                arrival_time = stop.arrival.time
                stop_id = stop.stop_id
                stop_dict = {
                    "arrival_time" : arrival_time,
                    "stop_id": stop_id
                }
                all_stops.append(stop_dict)

            train_dict ={
                "trip_id" : trip_id,
                "route_id" : route_id,
                "direction" : last_station[-1],
                "start_time" : start_time,
                "last_station" : last_station,
                "last_station_departure" : str(convert_timestamp(last_station_departure)),
                "next_stops_array" : all_stops
            }
            all_trains.append(train_dict)
    return all_trains

if __name__ == "__main__":
    train_test = next_train_arrival("G36", "S")
    print(train_test["train"])
    # print(feed.entity[-2])
   

    print(is_train_slow(next_train_arrival("G36", "S")))

    # query_test = static_travel_times.query_static_time_table("G32", "N")
    # print(query_test)