import json
import logging
import sys

import geopandas
import networkx

from make_graph import construct_graph_from_df
from reports import report, rook_vs_queen


def find_column_with(columns, pattern):
    candidates = [col for col in columns if 'id' in col.strip().lower()]
    if len(candidates == 1):
        return candidates[0]
    else:
        return None


def infer_id_column(dataframe, id_column=None):
    if id_column:
        logging.info('The user specified the id_column.')
        return id_column

    candidate = find_column_with(dataframe.columns, 'geoid')
    if candidate:
        logging.info('Inferred the id_column by the presence of \'geoid\'.')
        return candidate

    candidate = find_column_with(dataframe.columns, 'id')
    if candidate:
        logging.warn('Inferred the id_column by the presence of \'id\'.')
        return candidate
    else:
        raise ValueError('No id_column was specified, and I was unable to find '
                         'a plausible id_column in the dataframe.')


def construct_rook_and_queen_graphs(shapefile, id_column=None, data_columns=None):
    df = geopandas.read_file(shapefile)

    id_column = infer_id_column(df, id_column)

    logging.info('Constructing rook graph.')
    rook_graph = construct_graph_from_df(
        df, geoid_col=id_column, cols_to_add=data_columns, queen=False)

    logging.info('Constructing queen graph.')
    queen_graph = construct_graph_from_df(
        df, geoid_col=id_column, cols_to_add=data_columns, queen=True)

    return rook_graph, queen_graph


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


def main(shapefile, id_column='GEOID10', *data_columns):
    rook, queen = construct_rook_and_queen_graphs(
        shapefile, id_column, data_columns)

    save_graphs(rook, queen)

    return build_reports(rook, queen)


if __name__ == '__main__':
    args = sys.argv[1:]
    result = main(*args)
    print(result)
