import os

import geopandas as gp

from add_columns import add_columns_and_report
from main import load_graph


def zfill2(n):
    return str(n).zfill(2)


states = [folder for folder in os.listdir('./graphs/') if folder.isdigit()]


def get_graph_paths(fips):
    return ['./graphs/' + fips + '/rook.json',
            './graphs/' + fips + '/queen.json']


def get_shape_path(fips):
    return '/'.join(['.', 'tiger_data', fips,
                     'tl_2012_' + fips + '_vtd10.shp'])


for state in states:
    data = gp.read_file(get_shape_path(state))
    for path in get_graph_paths(state):
        graph = load_graph(path)
        result = add_columns_and_report(
            graph, data, ['ALAND10', 'AWATER10', 'NAME10'], 'GEOID10')
        print(result)
