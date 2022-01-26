#project: P2
#submitter: shizmi
#partner: xzimmerman

from math import sin, cos, asin, sqrt, pi
import pandas as pd
from zipfile import ZipFile

class BusDay:
    
    def __init__(self, date):
        self.date = date
        
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("calendar.txt") as f:
                self.df = pd.read_csv(f)
       
        # get date in format we want
        new_date = int(str(self.date)[:10].replace('-',''))
        
        # get day of week
        self.day_of_week = self.date.strftime("%A").lower()

        self.service_ids = []
        
        # search calendar.txt dataframe to pull active service ids based on day of week
        for i in range(len(self.df['start_date'])):
            start_date = self.df['start_date'][i]
            end_date = self.df['end_date'][i]
            date_range = end_date - start_date
            if (end_date - int(new_date)) <= date_range:
                if self.df[self.day_of_week][i] == 1:
                    if self.df['service_id'][i] not in self.service_ids:
                        self.service_ids.append(self.df['service_id'][i])
                        
    def get_trips(self, route_id = None):
        self.df = None
        self.route_id = route_id
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("trips.txt") as f:
                self.df = pd.read_csv(f)
       
        route_list = []
        bikes = None
        trips = self.df[self.df['service_id'].isin(self.service_ids)]
       
        for idx in trips.index:
            
            # if route_id is specified, then search trips.txt dataframe to add 
            # Trip objects to list that match route_id and are active
            if self.route_id == None:
                if trips['bikes_allowed'][idx] == 1:
                    bikes = True
                else:
                    bikes = False
                if Trip(trips['trip_id'][idx],trips['route_short_name'][idx],bikes) not in route_list:
                    route_list.append(Trip(trips['trip_id'][idx],trips['route_short_name'][idx],bikes))
                    
            # if no route_id specified, add all active trips to list
            else:
                if trips['route_short_name'][idx] == self.route_id:
                    if trips['service_id'][idx] in self.service_ids:
                        if trips['bikes_allowed'][idx] == 1:
                            bikes = True
                        else:
                            bikes = False
                        if Trip(trips['trip_id'][idx], trips['route_short_name'][idx], bikes) not in route_list:
                            route_list.append(Trip(trips['trip_id'][idx], trips['route_short_name'][idx],bikes))
                            
        #return sorted route list, sorted by trip_id
        return sorted(route_list, key=lambda x: x.trip_id)
        
    def get_stops(self):
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("stop_times.txt") as f:
                df_stop_times = pd.read_csv(f)
            with zf.open("stops.txt") as f:
                df_stops = pd.read_csv(f)
            with zf.open("trips.txt") as f:
                df_trips = pd.read_csv(f)
                
        # filter dataframes for active stops
        trips = df_trips[df_trips['service_id'].isin(self.service_ids)]
        trips_ids = []
        for idx in trips.index:
            if trips['trip_id'][idx] not in trips_ids:
                trips_ids.append(trips['trip_id'][idx])
                
        stops = df_stop_times[df_stop_times['trip_id'].isin(trips_ids)]
        stop_ids = []
        
        for idx in stops.index:
            if stops['stop_id'][idx] not in stop_ids:
                stop_ids.append(stops['stop_id'][idx])
        stops = df_stops[df_stops['stop_id'].isin(stop_ids)]
        
        # get all active stops for the day
        stops_list = []
        wheelchair = None
        for idx in stops.index:
            wheelchair = stops['wheelchair_boarding'][idx] == 1
            stop_object = Stop(stops['stop_id'][idx], Location(latlon = (stops['stop_lat'][idx], stops['stop_lon'][idx])),wheelchair )
            if stop_object not in stops_list:
                stops_list.append(stop_object)
                    
        return sorted(stops_list, key = lambda x: x.stop_id)
    
    
    def get_stops_rect(self, x_tupe, y_tupe):
        pass
#         x_min, x_max = x_tupe[0], x_tupe[1]
#         y_min, y_max = y_tupe[0], y_tupe[1]
#         stops = self.get_stops()
#         root = Node(stops)
#         root.split()
        
#         def search(node, x_min, x_max, y_min, y_max):
#             list_of_stops = []
#             if not hasattr(node, 'right'):
#                 return list_of_stops
#             if node.right.depth % 2 == 0:
#                 if node.right.val[0].loc.x > x_max:
#                     search(node.left.val, x_min, x_max, y_min, y_max)
#                 else:
#                     search(node.right, x_min, x_max, y_min, y_max)
#             if node.right.depth % 2 != 0:
#                 if node.right.val[0].loc.y > y_max:
#                     search(node.left.val, x_min, x_max, y_min, y_max)
#                 else:
#                     search(node.right, x_min, x_max, y_min, y_max)
                    
#             for i in range(len(node.val)):
#                 if node.val[i].loc.x >= x_min and node.val[i].loc.x <= x_max:
#                     if node.val[i].loc.y >= y_min and node.val[i].loc.y <= y_max:
#                         list_of_stops.append(node.val[i])
#             return list_of_stops
    
#         stops_rect = search(root, x_min, x_max, y_min, y_max)
        
#         return stops_rect
    
    def get_stops_circ(self, xy_tupe, radius):
        pass
#         list_of_stops = []
#         x_min = xy_tupe[0] - radius
#         x_max = xy_tupe[0] + radius
#         y_min = xy_tupe[1] - radius
#         y_max = xy_tupe[1] + radius
        
#         stop_list = self.get_stops_rect((x_min,y_min), (y_min, y_max))
#         for i in range(len(stop_list)):
#             if (stop_list[i].loc.x-xy_tupe[0])**2 + (stop_list[i].loc.y-xy_tupe[1])**2 <= radius ** 2:
#                 list_of_stops.append(stop_list[i])
#         return list_of_stops
        
            
    
    def scatter_stops(self, ax):
        stops = self.get_stops()
        accesible = []
        notaccesible = []
        for i in stops:
            data = []
            wheelchair = i.wheelchair_boarding
            if wheelchair == True:
                locat = i.loc
                x = locat.x
                y = locat.y
                data.append(x)
                data.append(y)
                accesible.append(data)
            else:
                locat = i.loc
                x = locat.x
                y = locat.y
                data.append(x)
                data.append(y)
                notaccesible.append(data)
        red = pd.DataFrame(accesible, columns = ['x', 'y'])
        gray = pd.DataFrame(notaccesible, columns = ['x', 'y'])
        red.plot.scatter(ax=ax, x='x', y='y', color="red")
        gray.plot.scatter(ax=ax, x='x', y='y', color="0.7")

class Node:
    def __init__(self, val):
        self.middle = 0 # x or y coordinate to split
        self.val = val # list of stops
        self.depth = 0
        self.right = None
        self.left = None
        
    def split(self, level = 0):
        l = level
        
        if l < 6:
            # east and west
            if l % 2 == 0:
                self.depth = l
                stop_list = sorted(self.val, key = lambda x: x.loc.x)
                
                self.middle = stop_list.index(stop_list[len(stop_list)//2])
                    
                self.left = Node(stop_list[:self.middle])
                self.left.split(l+1)
                
                self.right = Node(stop_list[self.middle:])
                self.right.split(l+1)

            # north and south
            else:
                self.depth = l
                stop_list = sorted(self.val, key = lambda x: x.loc.y)
                
                self.middle = stop_list.index(stop_list[len(stop_list)//2])
                    
                self.left = Node(stop_list[:self.middle])
                self.left.split(l+1)
                
                self.right = Node(stop_list[self.middle:])
                self.right.split(l+1)
        else:
            return

class Trip:
    def __init__(self,trip_id, route_id, bikes_allowed):
        self.trip_id = trip_id
        self.route_id = route_id
        self.bikes_allowed = bikes_allowed
    def __repr__(self):
        s = "Trip({}, {}, {})"
        return s.format(repr(self.trip_id), repr(self.route_id), repr(self.bikes_allowed))
        
        
class Stop:
    def __init__(self, stop_id, loc, wheelchair_boarding):
        self.stop_id = stop_id
        self.loc = loc
        self.wheelchair_boarding = wheelchair_boarding
    def __repr__(self):
        return "Stop({}, {}, {})".format(repr(self.stop_id), repr(self.loc), self.wheelchair_boarding)

def haversine_miles(lat1, lon1, lat2, lon2):
    """Calculates the distance between two points on earth using the
    harversine distance (distance between points on a sphere)
    See: https://en.wikipedia.org/wiki/Haversine_formula

    :param lat1: latitude of point 1
    :param lon1: longitude of point 1
    :param lat2: latitude of point 2
    :param lon2: longitude of point 2
    :return: distance in miles between points
    """
    lat1, lon1, lat2, lon2 = (a/180*pi for a in [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2
    c = 2 * asin(min(1, sqrt(a)))
    d = 3956 * c
    return d


class Location:
    """Location class to convert lat/lon pairs to
    flat earth projection centered around capitol
    """
    capital_lat = 43.074683
    capital_lon = -89.384261

    def __init__(self, latlon=None, xy=None):
        if xy is not None:
            self.x, self.y = xy
        else:
            # If no latitude/longitude pair is given, use the capitol's
            if latlon is None:
                latlon = (Location.capital_lat, Location.capital_lon)

            # Calculate the x and y distance from the capital
            self.x = haversine_miles(Location.capital_lat, Location.capital_lon,
                                     Location.capital_lat, latlon[1])
            self.y = haversine_miles(Location.capital_lat, Location.capital_lon,
                                     latlon[0], Location.capital_lon)

            # Flip the sign of the x/y coordinates based on location
            if latlon[1] < Location.capital_lon:
                self.x *= -1

            if latlon[0] < Location.capital_lat:
                self.y *= -1

    def dist(self, other):
        """Calculate straight line distance between self and other"""
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self):
        return "Location(xy=(%0.2f, %0.2f))" % (self.x, self.y)