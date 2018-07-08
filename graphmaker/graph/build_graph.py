import datetime
import logging
import uuid

log = logging.getLogger(__name__)


def find_column_with(columns, pattern):
    candidates = [col for col in columns if pattern in col.strip().lower()]
    if len(candidates) == 1:
        return candidates[0]
    else:
        return None


def infer_id_column(dataframe, id_column=None):
    if id_column:
        log.info('The user specified the id_column.')
        return id_column

    candidate = find_column_with(dataframe.columns, 'geoid')
    if candidate:
        log.info('Inferred the id_column by the presence of \'geoid\'.')
        return candidate

    candidate = find_column_with(dataframe.columns, 'id')
    if candidate:
        log.warn('Inferred the id_column by the presence of \'id\'.')
        return candidate
    else:
        raise ValueError('No id_column was specified, and I was unable to find '
                         'a plausible id_column in the dataframe.')


def generate_id():
    return str(uuid.uuid4())[:8]


def add_metadata(graph, df, **other_fields):
    state_col = find_column_with(df.columns, 'state')
    if state_col:
        graph.graph['state'] = df[state_col][0]
    else:
        # Rhode island's special shapefiles are the only ones without
        graph.graph['state'] = '44'
    graph.graph['id'] = generate_id()
    graph.graph['created'] = str(datetime.datetime.utcnow())

    # add whatever other metadata the user wants to add
    for key, value in other_fields.items():
        graph.graph[key] = value
