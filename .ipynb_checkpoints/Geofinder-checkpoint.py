import csv
import time
from collections import Counter
import json
import telluric as tl
from telluric.constants import WGS84_CRS, WEB_MERCATOR_CRS
from geopy.geocoders import Nominatim, Here


class Geofinder:
    
    here = None
    osm = None

    def create(self):
        with open('../accounts.json') as json_file:  
            data = json.load(json_file)
        app_code = data['accounts']['Here']['app_code']
        app_id = data['accounts']['Here']['app_id']
        user_agent = data['accounts']['Here']['user_agent']
        self.here = Here(app_code=app_code, app_id=app_id,user_agent=user_agent)
        self.osm = Nominatim(user_agent="get_setlled")

    
    def get_neighborhoods(self, address, distance=1000):
        if 'barcelona' not in address.lower():
            address += ', Barcelona'
        location = self.here.geocode(address)
        coordinates = self.get_circles_locations(location.point, distance)
        pizza_coordinates = []
        for coordinate in coordinates:
            for i in range(8,65,8):
                coord = coordinate[i]
                pizza_coordinates.append([coord[::-1][0],coord[::-1][1]])

        pizza_coordinates.insert(0,[location.point.latitude,location.point.longitude])
        self.export_coords_to_csv(pizza_coordinates)
        pizza_addresses = []
        for coord in pizza_coordinates:
            pizza_addresses.append(self.osm.reverse(coord))
            time.sleep(3)
        
        neighborhouds = []
        for suburb in pizza_addresses:
            neighborhouds.append(suburb.raw['address']['suburb'])

        return Counter(neighborhouds).most_common()

        
    def export_coords_to_csv(self, coordinates):
        coordinates_copy = coordinates.copy()
        coordinates_copy.insert(0,['lat_dms','lon_dms'])
        with open("coordinates.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(coordinates_copy)
    
    def get_cirlce_location(self, location, distance):
        return (tl.GeoVector.point(location.longitude, location.latitude)
            .reproject(WEB_MERCATOR_CRS)
            .buffer(distance)
            .to_record(WGS84_CRS)['coordinates'][0]
        )

    def get_circles_locations(self, location, distance):
        outer_circle = distance + 400
        coordinates = []
        while distance > 0:
            coordinates.append(self.get_cirlce_location(location, distance))
            distance -= 350
        coordinates.append(self.get_cirlce_location(location, outer_circle))
        return coordinates
