from nyct_gtfs import NYCTFeed

nyc_feed = NYCTFeed("G")
trains = nyc_feed.trips

for train in trains:
    print(train)