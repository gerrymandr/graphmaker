import os

import geopandas as gp
import pandas

from add_columns import add_columns_and_report
from constants import (cd_matchings_path, graphs_base_path, tiger_data_path,
                       valid_fips_codes)
from main import load_graph, save_graphs


def zfill2(n):
    return str(n).zfill(2)


def get_graph_paths(fips):
    return (os.path.join(graphs_base_path, fips, 'rook.json'),
            os.path.join(graphs_base_path, fips, 'queen.json'))


def get_shape_path(fips):
    return os.path.join(tiger_data_path, fips, 'tl_2012_' + fips + '_vtd10.shp')


def add_data_from_shapefile(fips, shapefilepath, columns, id_column):
    data = gp.read_file(shapefilepath)
    return add_data_from_dataframe(fips, data, columns, id_column)


def add_data_from_dataframe(fips, data, columns, id_column):
    rook, queen = get_graph_paths(fips)

    rook_graph = load_graph(rook)
    rook_result = add_columns_and_report(rook_graph, data, columns, id_column)

    queen_graph = load_graph(queen)
    queen_result = add_columns_and_report(
        queen_graph, data, columns, id_column)

    save_graphs(rook_graph, queen_graph)

    return rook_result, queen_result


# These functions will add data to every state's graph:

def add_basic_data_from_census_shapefiles():
    columns = ['ALAND10', 'AWATER10', 'NAME10', 'COUNTYFP10']
    for state in valid_fips_codes():
        add_data_from_shapefile(
            state, get_shape_path(state), columns, 'GEOID10')


def add_cds_to_graphs():
    for state in valid_fips_codes():
        cds = pandas.read_csv(os.path.join(
            cd_matchings_path, state + '.csv'), dtype=str, header=None, names=['geoid', 'CD'])
        add_data_from_dataframe(state, cds, ['CD'], 'geoid')


if __name__ == '__main__':
    add_cds_to_graphs()
