import datetime
import logging
import uuid

import geopandas

from make_graph import construct_graph_from_df


def find_column_with(columns, pattern):
    candidates = [col for col in columns if 'id' in col.strip().lower()]
    if len(candidates) == 1:
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


def add_metadata(graph, df):
    state_col = find_column_with(df.columns, 'state')
    if state_col:
        graph['state'] = df[state_col][0]
    graph['id'] = uuid.uuid4()
    graph['created'] = datetime.datetime.isoformat()


def construct_rook_and_queen_graphs(shapefile, id_column=None, data_columns=None):
    df = geopandas.read_file(shapefile)

    id_column = infer_id_column(df, id_column)
    df.index = df[id_column]

    logging.info('Constructing rook graph.')
    rook_graph = construct_graph_from_df(
        df, geoid_col=id_column, cols_to_add=data_columns, queen=False)

    logging.info('Constructing queen graph.')
    queen_graph = construct_graph_from_df(
        df, geoid_col=id_column, cols_to_add=data_columns, queen=True)

    add_metadata(rook_graph, df)
    add_metadata(queen_graph, df)

    return rook_graph, queen_graph
