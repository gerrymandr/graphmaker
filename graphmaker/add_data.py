
import geopandas as gp

from add_columns import add_columns_and_report
from main import load_graph, save_graphs


def zfill2(n):
    return str(n).zfill(2)


states = ['04']


def get_graph_paths(fips):
    return ('./graphs/' + fips + '/rook.json',
            './graphs/' + fips + '/queen.json')


def get_shape_path(fips):
    return '/'.join(['.', 'tiger_data', fips,
                     'tl_2012_' + fips + '_vtd10.shp'])


for state in states:
    data = gp.read_file(get_shape_path(state))
    rook, queen = get_graph_paths(state)
    rook_graph = load_graph(rook)
    result = add_columns_and_report(
        rook_graph, data, ['ALAND10', 'AWATER10', 'NAME10', 'COUNTYFP10'], 'GEOID10')
    print(result)
    queen_graph = load_graph(queen)
    result = add_columns_and_report(
        queen_graph, data, ['ALAND10', 'AWATER10', 'NAME10', 'COUNTYFP10'], 'GEOID10')
    save_graphs(rook_graph, queen_graph)
    print(result)
