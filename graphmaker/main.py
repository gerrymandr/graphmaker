import json
import logging
import os
import pathlib

import networkx
import pandas

from add_columns import add_columns_and_report
from build_graph import construct_rook_and_queen_graphs
from constants import graphs_base_path
from reports import report, rook_vs_queen

# logging.basicConfig(level=logging.DEBUG)


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


def main(args):
    path = args[0]

    id_column = None
    if len(args) > 1:
        id_column = args[1]

    if not path:
        raise ValueError('Please specify a shapefile to turn into a graph.')

    rook, queen = construct_rook_and_queen_graphs(path, id_column=id_column)
    save_graphs(rook, queen)

    result = build_reports(rook, queen)

    state = rook.graph['state']
    with open(os.path.join(graphs_base_path, state, "report.json"), 'w') as f:
        f.write(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    pass
