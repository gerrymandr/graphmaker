import datetime
import numbers
import statistics

import networkx

from constants import round_to
from reports import serializable_histogram


def add_column_to_graph(graph, column, attribute_name):
    networkx.set_node_attributes(graph, column, attribute_name)


def summary(data):
    if not isinstance(data[0], numbers.Number):
        return {'type': str(type(data[0]))}
    hist = serializable_histogram(data)
    return {'mean': round(statistics.mean(data), round_to),
            'median': round(statistics.mean(data), round_to),
            'max': max(data),
            'min': min(data),
            'variance': round(statistics.variance(data), round_to),
            'histogram': hist}


def zeros(data):
    zeros = [n for n in data if not n]
    return {'number_of_zeros': len(zeros), 'percent_zero': len(zeros)/len(data)}


def column_statistics(column):
    data = list(column)
    print(data)
    return {**summary(data), **zeros(data)}


def column_report(table, column_name, graph):
    return {'column_name': column_name,
            'created': str(datetime.datetime.utcnow()),
            'graph': graph.graph.get('id'),
            'report': column_statistics(table[column_name])}


def map_ids_to_column_entries(table, id_column, data_column):
    return dict(zip(table[id_column], table[data_column]))


def add_columns_and_report(graph, table, columns, id_column):
    """
    Writes some columns from table to the graph as node attributes,
    using id_column to match nodes to rows of the table.

    :graph: networkx graph
    :table: dataframe
    :columns: list of column names
    :id_column: name of the id_column (usually 'GEOID10')
    """

    for column in columns:
        data = map_ids_to_column_entries(table, id_column, column)
        add_column_to_graph(graph, data, column)
    return [column_report(table, column_name, graph)
            for column_name in columns]
