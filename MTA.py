from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime, timedelta
from mta_output_formatting import time_difference, convert_seconds
import pprint

# this is the API request that is used to get realtime train data in GTFS format.
# the url endpoint specifies an individual train line.
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g')
feed.ParseFromString(response.content)

ct = datetime.now()

def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp)

def convert_seconds(seconds):
    return timedelta(seconds = seconds)

# returns a list of all trains traveling either N or S
def filter_direction(direction):
    filtered_trains = []
    for train in get_all_trains():
        if train["direction"] == direction:
            filtered_trains.append(train)
    return filtered_trains

# loops through each train's (filtered by direction) array of stops and returns a list of trains that will stop at the specified station
def filter_stations(station, train_list):
    filtered_stations = []
    for train in train_list:
        for stop in train["next_stops_array"]:
            if stop["stop_id"][:-1] == station:
                filtered_stations.append(train)
    return filtered_stations

# MAIN FUNCTION 
# Returns a dict "best_train" that contains info on the next train arriving at the specified station and direction of travel
def next_train_arrival(station, direction):
    direction_bound_trains = []
    ct_epoch = int(ct.timestamp())
    min_time = 3600
    best_time = 0
    best_train = {}

# loop through feed.entity (all trips) and return a list of trains traveling in the selected direction (direction_bound_trains)
    for train in filter_direction(direction):
        direction_bound_trains.append(train)
# next_train_list contains every train that will stop at the chosen station and is traveling in the chosen direction
    next_train_list = filter_stations(station, direction_bound_trains)
# loop through each train in next train list, find the train with arrival time closest to current time, and return that train, the arrival time, and the seconds to arrival, in dict (best_train)
    for train in next_train_list:
        # arrival_time finds the station in each train's next_stops_array and returns the arrival time for the station
        arrival_time = get_arrival_time_for_station(train, station)
        # time difference subtracts the arrival time (future) from the current time, and returns a delta time in seconds.
        # the smallest time will be filtered and set to min_time.
        # the train with the lowest min time will have its data (arrival time, train obj) set to the best_time and best_train variables
        if time_difference(ct_epoch, arrival_time) < min_time:
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

# this function takes the GTFS feed from the request and creates train objects that will be used in all of our functions.
# each train is called an entity, and if that entity has a 'trip_update" key and an array of stops, then it will contain the information that our program uses.
# entities that don't contain this info will be ignored.
def get_all_trains():
    all_trains = []
    for entity in feed.entity:
        if entity.HasField('trip_update') and len(entity.trip_update.stop_time_update) > 0:
            trip_id = entity.trip_update.trip.trip_id
            route_id = entity.trip_update.trip.route_id
            start_time = entity.trip_update.trip.start_time
            next_arrival = entity.trip_update.stop_time_update[0].arrival.time
            next_station = entity.trip_update.stop_time_update[0].stop_id
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
                "direction" : next_station[-1],
                "start_time" : start_time,
                "next_stop_id" : next_station,
                "next_stop_arrival" : next_arrival,
                "next_stops_array" : all_stops
            }
            all_trains.append(train_dict)
    return all_trains

if __name__ == "__main__":
    train_test = next_train_arrival("G36", "S")

    print(feed)