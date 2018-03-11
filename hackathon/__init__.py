from .trips import *
import matplotlib.pyplot as plt
from itertools import combinations
from scipy.spatial.distance import jaccard
from networkx import all_shortest_paths

def similar_routes():

    g = load_graphdata()

    nodes = g.nodes(data='trips')

    # get distinct trips
    trip_ids = set([trip for node in nodes for trip in node[1]])

    # get nodes per trip
    grouped_trips = {}
    for trip_id in trip_ids:
        grouped_trips.update({trip_id: [node[0] for node in nodes if trip_id in node[1]]})

    # True/False list with used nodes
    feature_trips = {}
    for trip_id, values in grouped_trips.items():
        feature_trips.update({trip_id: [True if node[0] in values else False for node in nodes]})

    # compare all the routes with one another
    for routes_combination in combinations(feature_trips, 2):
        distance = jaccard(feature_trips.get(routes_combination[0]), feature_trips.get(routes_combination[1]))
        print('from {1} to {2} distance {0}'.format(distance, *routes_combination))


def display_graph():

    g = load_graphdata()

    nx.draw_networkx(g, pos={n: n for n in g.nodes}, node_size=4, with_labels=True, arrows=True,
                     edge_color=[key for first, second, key in g.edges(keys=True)],
                     labels={n[0]: ','.join(map(str, n[1])) for n in g.nodes(data='trips')})

    plt.show()


def find_intersectionpoints():

    g = load_graphdata()

    # get distinct trips
    trip_ids = set([trip for node in g.nodes(data='trips') for trip in node[1]])

    for id in trip_ids:
        start_point = [node[0] for node in g.nodes(data='start') if node[1] is not None and id in node[1]][0]
        end_point = [node[0] for node in g.nodes(data='end') if node[1] is not None and id in node[1]][0]

        print('Trip: {}'.format(id))
        for route in all_shortest_paths(g, start_point, end_point):
            for first, second in pairwise(route):

                first_trips = set(g.nodes[first]['trips'])
                second_trips = set(g.nodes[second]['trips'])

                diff_trips = first_trips.symmetric_difference(second_trips)

                for trip_id in diff_trips:
                    if trip_id in first_trips:
                        print('{} route {} removed'.format(first, trip_id))
                    else:
                        print('{} route {} added'.format(first, trip_id))
