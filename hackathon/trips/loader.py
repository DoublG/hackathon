import glob
import gpxpy.gpx
import os
from networkx import nx
from ..helpers import pairwise

root_folder = os.path.abspath(os.path.dirname(__file__))


def load_trips(source_folder='../data/trip_examples/*.gpx', accuracy=2):

    files = glob.glob(os.path.join(root_folder, source_folder))

    trips = []
    for id, file in enumerate(files):
        print('id: {} source: {}'.format(id, file))

        gpx_file = open(file, 'r')
        gpx = gpxpy.parse(gpx_file)

        # gimme all the points
        points = [(point.latitude, point.longitude)
                  for track in gpx.tracks for segment in track.segments for point in segment.points]

        # average out the routes to 2 decimals (we are interested in the zone instead of the exact route)
        # 2 decimals 1km https://en.wikipedia.org/wiki/Decimal_degrees
        points = [(round(point[0], accuracy), round(point[1], accuracy)) for point in points]

        trips.append((file, list(dict.fromkeys(points))))  # remove duplicates but keep ordering (python 3.6)

    return trips


def load_graphdata():

    loaded_trips = load_trips()
    print('{} trips loaded'.format(len(loaded_trips)))

    g = nx.MultiDiGraph()
    for i, trip in enumerate(loaded_trips):
        source, geopoints = trip

        for first, second in list(pairwise(iter(geopoints))):
            g.add_edge(first, second, key=i, source=source)

        #add start & endpoints
        g.nodes[geopoints[0]].setdefault('start', []).append(i)
        g.nodes[geopoints[-1]].setdefault('end', []).append(i)

        #add current trip to nodes
        for point in geopoints:
            g.nodes[point].setdefault('trips', []).append(i)

    startpoints = [n for n in g.nodes(data='start') if n[1] is not None]
    print('start: {}'.format(startpoints))

    endpoints = [n for n in g.nodes(data='end') if n[1] is not None]
    print('end: {}'.format(endpoints))

    print('{} nodes {} edges'.format(g.number_of_nodes(), g.number_of_edges()))

    return g
