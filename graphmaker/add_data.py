from add_columns import add_columns_and_report
from main import load_graph

import os
import geopandas as gp

def zfill2(n):
    return str(n).zfill(2)

states = os.listdir('./graphs/')

def get_graph_paths(fips):
    return ['./graphs/' + fips + '/rook.json',
            './graphs/' + fips + '/queen.json']

def get_shape_path(fips):
    return '/'.join(['.', 'tiger_data', fips,
                     'tl_2012_' + fips + '_vtd10.shp'])

graph = None
data = None
for state in states:
    data = gp.read_file(get_shape_path(state))
    for path in get_graph_paths(state):
        graph = load_graph(path)
        result = add_columns_and_report(graph, data, ['ALAND10', 'AWATER10', 'NAME10'], 'GEOID10')
        print(result)

