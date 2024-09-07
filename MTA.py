from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g')
feed.ParseFromString(response.content)

ct = datetime.now()

def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp)

def next_train_arrival(station, direction):
    result = []
    for train in get_all_trains():
        if train["direction"] == direction:
            print(train['trip_id'])

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
            # print(next_arrival)
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


# for train in all_trains:
#     if train["direction"] == "N":
#         print(train)
    
# print(feed)
# print(all_trains[0]["next_stops_array"])
# for stop in all_trains[3]["next_stops_array"]:
#     print("ID", stop["stop_id"])
#     print("TIME", convert_timestamp(stop["arrival_time"]))
   

test_time_1 = 1725741847
test_time_2 = 1725742387

# print(type(ct))
# print(convert_timestamp(test_time_1))
# print(convert_timestamp(test_time_2))

# time_test = convert_timestamp(test_time_2) - convert_timestamp(test_time_1)
# print(time_test)
next_train_arrival("G26", "N")