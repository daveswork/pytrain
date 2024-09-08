from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime, timedelta
from mta_output_formatting import time_difference, convert_seconds
import pprint


feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g')
feed.ParseFromString(response.content)

ct = datetime.now()

def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp)

def trip_id_convert(trip_id):
    return f'{datetime.fromtimestamp(int(trip_id[:-8]))} {trip_id[7:-1]}'

def convert_seconds(seconds):
    return timedelta(seconds = seconds)

# def get_train_arrival_time(station):
#     for stop in train["next_stops_array"]:
#         if stop["stop_id"][:-1] == station:
#             my_station_arrival_time = convert_timestamp(stop["arrival_time"]) - ct
#             next_train.append(train)
#             arrival.append(my_station_arrival_time)

def filter_direction(direction):
    filtered_trains = []
    for train in get_all_trains():
        if train["direction"] == direction:
            filtered_trains.append(train)
    return filtered_trains

def filter_stations(station, train_list):
    filtered_stations = []
    for train in train_list:
        for stop in train["next_stops_array"]:
            if stop["stop_id"][:-1] == station:
                filtered_stations.append(train)
    return filtered_stations

def next_train_arrival(station, direction):
    direction_bound_trains = []
    for train in filter_direction(direction):
        direction_bound_trains.append(train)
    next_train_list = filter_stations(station, direction_bound_trains)

    ct_epoch = int(ct.timestamp())
    min_time = 3600
    best_time = 0
    best_train = {}
    for train in next_train_list:
        arrival_time = get_arrival_time_for_station(train, station)
        if time_difference(ct_epoch, arrival_time) < min_time:
            min_time = time_difference(ct_epoch, arrival_time)
            best_time = arrival_time
            best_train = train
    return {
        "train" : best_train,
        "arrival_time" : best_time
    }
        
    
def get_arrival_time_for_station(train, station):
    for stop in train["next_stops_array"]:
        if stop["stop_id"][:-1] == station:
            return stop["arrival_time"]

# def next_train_arrival(station, direction):
#     ct_epoch = int(ct.timestamp())
#     # print(ct_epoch)
#     next_train = []
#     arrival = []
#     min_time = train["next_stops_array"][0]["arrival_time"] 
#     next_train_dict = {
#         "train" : {},
#         "station_arrival_time" : 0
#     }
#     for train in get_all_trains():
#         if train["direction"] == direction:
            
#             # print(min_time)
#             for stop in train["next_stops_array"]:
#                 if stop["stop_id"][:-1] == station:
#                     arrival_time = stop["arrival_time"]
#                     arrival_time_difference = time_difference(ct_epoch, arrival_time)
#                     if arrival_time_difference < min_time:
#                         min_time = arrival_time_difference
#             print("min_time", min_time)
#                     # print(time_to_arrival)
#     # return f'A {next_train[0]["direction"]} bound {next_train[0]["route_id"]} train will arrive at {station} in {arrival[0]}'
    

def get_all_trains():
    all_trains = []
    for entity in feed.entity:
        if entity.HasField('trip_update') and len(entity.trip_update.stop_time_update) > 0:
            trip_id = entity.trip_update.trip.trip_id
            route_id = entity.trip_update.trip.route_id
            start_time = entity.trip_update.trip.start_time
            next_arrival = entity.trip_update.stop_time_update[0].arrival.time
            next_departure = entity.trip_update.stop_time_update[0].departure.time
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

# next_train_arrival("G36", "S")

train_test = next_train_arrival("G36", "S")
pprint.pprint(train_test)

# test_time_1 = 1725814530
# test_time_2 = 1725815130

# print(convert_timestamp(test_time_1))
# print(convert_timestamp(test_time_2))
# time_test = time_difference(test_time_1, test_time_2)
# print(time_test)

# print(convert_timestamp(test_time_1))
# print(convert_timestamp(test_time_2))
# print(convert_timestamp(test_time_2 - test_time_1))
# print(convert_timestamp(test_time_2)-convert_timestamp(test_time_1))