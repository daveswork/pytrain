from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g')
feed.ParseFromString(response.content)

def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp)

ct = datetime.now()

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
        # all_stops = []
        # for stop in entity.trip_update.stop_time_update:
        #     all_stops.append(stop)

        train_dict ={
            "trip_id" : trip_id,
            "route_id" : route_id,
            "direction" : next_station[-1],
            "start_time" : start_time,
            "next_stop_id" : next_station,
            "next_stop_arrival" : next_arrival,
        }
        all_trains.append(train_dict)

print(ct)
for train in all_trains:
    if train["direction"] == "N":
        print(train["trip_id"])
        print(train['next_stop_id'])
        print(convert_timestamp(train["next_stop_arrival"]))
    
# print(feed)