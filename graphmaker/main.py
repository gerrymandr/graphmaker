import json
import logging
import os
import pathlib
import sys

import networkx
import pandas

from add_columns import add_columns_and_report
from build_graph import construct_rook_and_queen_graphs
from reports import report, rook_vs_queen

logging.basicConfig(level=logging.DEBUG)


def build_reports(rook_graph, queen_graph):
    logging.info('Building reports for rook- and queen-adjacency graphs.')
    rook_synopsis = report(rook_graph)
    queen_synopsis = report(queen_graph)

    logging.info('Comparing rook- and queen-adjacency graphs.')
    comparison = {'rook_vs_queen_comparison': rook_vs_queen(
        rook_graph, queen_graph)}

    return {'rook_graph_report': rook_synopsis,
            'queen_graph_report': queen_synopsis,
            'comparison': comparison}


def save_graphs(rook_graph, queen_graph):
    logging.info('Saving graphs.')

    # Ensure that the paths exist:
    state = rook_graph.graph['state']
    path = f"./graphs/{state}/"
    pathlib.Path(f"./graphs/{state}/").mkdir(parents=True, exist_ok=True)

    # Save the graphs in their respective homes:
    save(rook_graph, filepath=os.path.join(path, 'rook.json'))
    save(queen_graph, filepath=os.path.join(path, 'queen.json'))


def save(graph, location='./graphs/', filepath=None):
    if not filepath:
        filepath = os.path.join(location, graph.graph['id'] + ".json")
    try:
        with open(filepath, 'w') as f:
            json.dump(f, networkx.json_graph(graph))
        print(f"Saved the graph to {filepath}")
    except Exception:
        logging.error('Unable to write the graphs to file.')


def add_columns_from_csv_to_graph(graph, csv_path, id_column, columns=None):
    table = pandas.read_csv(csv_path)
    add_columns_from_df_to_graph(graph, table, id_column, columns)


def add_columns_from_df_to_graph(graph, table, id_column, columns=None):
    if not columns:
        columns = [column for column in table.columns if column != id_column]
    return add_columns_and_report(graph, table, columns, id_column)


def main(args):
    path = args[0]

    if not path:
        raise ValueError('Please specify a shapefile to turn into a graph.')

    rook, queen = construct_rook_and_queen_graphs(path)
    save_graphs(rook, queen)

    return build_reports(rook, queen)


def load_graph(path):
    with open(path, 'r') as document:
        data = json.load(document)
    graph = networkx.readwrite.json_graph.adjacency_graph(data)
    return graph


if __name__ == '__main__':
    result = main(sys.argv[1:])
    print(json.dumps(result, indent=2))
