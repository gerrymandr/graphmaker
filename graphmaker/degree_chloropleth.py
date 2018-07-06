import os

import geopandas as gp
import matplotlib
import matplotlib.pyplot as plt

from add_data import get_graph_paths, get_shape_path
from constants import graphs_base_path, valid_fips_codes
from geospatial import reprojected
from main import load_graph

matplotlib.use('Agg')


def degree(graph, node):
    return graph.degree[node]


def degree_chloropleth(fips, id_column='GEOID10'):
    rook_path, queen_path = get_graph_paths(fips)

    rook = load_graph(rook_path)
    queen = load_graph(queen_path)

    df = gp.read_file(get_shape_path(fips))
    df = reprojected(df)

    rook_degrees = [degree(rook, df.iloc[i][id_column]) for i in df.index]
    queen_degrees = [degree(queen, df.iloc[i][id_column]) for i in df.index]

    df['rook_degree'] = rook_degrees
    df['queen_degree'] = queen_degrees

    plt.axis('off')

    df.plot(column='rook_degree')
    rook_png_path = os.path.join(graphs_base_path, fips, 'rook.png')

    if os.path.isfile(rook_png_path):
        os.remove(rook_png_path)
    plt.savefig(rook_png_path)

    df.plot(column='queen_degree')
    queen_png_path = os.path.join(graphs_base_path, fips, 'queen.png')

    if os.path.isfile(queen_png_path):
        os.remove(queen_png_path)
    plt.savefig(queen_png_path)


def main():
    for fips in valid_fips_codes():
        degree_chloropleth(fips)


if __name__ == '__main__':
    main()
