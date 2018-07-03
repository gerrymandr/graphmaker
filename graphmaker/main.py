import json
import logging

import networkx
import pandas

from add_columns import add_columns_and_report
from build_graph import construct_rook_and_queen_graphs
from reports import report, rook_vs_queen

logging.basicConfig(level=logging.DEBUG)


def save_graphs(rook_graph, queen_graph):
    logging.info('Saving graphs.')
    save(rook_graph, './graphs/out_rook.json')
    save(queen_graph, './graphs/out_queen.json')


def build_reports(rook_graph, queen_graph):
    logging.info('Building reports for rook- and queen-adjacency graphs.')
    rook_synopsis = report(rook_graph)
    queen_synopsis = report(queen_graph)

    logging.info('Comparing rook- and queen-adjacency graphs.')
    comparison = {"rook_vs_queen_comparison": rook_vs_queen(
        rook_graph, queen_graph)}

    return {"rook_graph_report": rook_synopsis,
            "queen_graph_report": queen_synopsis,
            "comparison": comparison}


def save(graph, location):
    try:
        with open(location, "w+") as f:
            json.dump(f, networkx.json_graph(graph))
    except Exception:
        logging.error('Unable to write the graphs to file.')


def add_columns_from_csv_to_graph(graph, csv_path, id_column, columns=None):
    table = pandas.read_csv(csv_path)
    if not columns:
        columns = [column for column in table.columns if column != id_column]
    return add_columns_and_report(graph, table, columns, id_column)


def main():
    rook, queen = construct_rook_and_queen_graphs(
        "C:\\Users\\maxhu\\Downloads\\tl_2012_26_vtd10\\tl_2012_26_vtd10.shp", "GEOID10", None)

    for graph in (rook, queen):
        result = add_columns_from_csv_to_graph(
            graph, './26_data.csv', 'GEOID10')
        print(result)

    save_graphs(rook, queen)

    return build_reports(rook, queen)


if __name__ == '__main__':
    print(main())
