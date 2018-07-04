import geopandas as gp
import matplotlib
import matplotlib.pyplot as plt

from main import load_graph

matplotlib.use('Agg')


def shapefile_path(fips):
    return '/'.join(['.', 'tiger_data', fips, 'tl_2012_' + fips + '_vtd10.shp'])


def graph_paths(fips):
    return ('/'.join(['.', 'graphs', 'vtd-adjacency-graphs',
                      'vtd-adjacency-graphs', fips, 'rook.json']),
            '/'.join(['.', 'graphs', 'vtd-adjacency-graphs',
                      'vtd-adjacency-graphs', fips, 'queen.json']))


def degree(graph, node):
    return graph.degree[node]


def degree_chloropleth(fips, id_column='GEOID10'):
    rook_path, queen_path = graph_paths(fips)

    rook = load_graph(rook_path)
    queen = load_graph(queen_path)

    df = gp.read_file(shapefile_path(fips))

    rook_degrees = [degree(rook, df.iloc[i][id_column]) for i in df.index]
    queen_degrees = [degree(queen, df.iloc[i][id_column]) for i in df.index]

    df['rook_degree'] = rook_degrees
    df['queen_degree'] = queen_degrees

    df.plot(column='rook_degree')
    plt.savefig('./rook.png')
    df.plot(column='queen_degree')
    plt.savefig('./queen.png')


def main():
    degree_chloropleth('25')


if __name__ == '__main__':
    main()
