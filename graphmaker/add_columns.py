import datetime
import statistics

import networkx

from reports import serializable_histogram


def add_column_to_graph(graph, column):
    networkx.set_node_attributes(graph, column)


def summary(data):
    hist = serializable_histogram(data)
    return {'mean': round(statistics.mean(data), 6),
            'median': round(statistics.mean(data), 6),
            'max': max(data),
            'min': min(data),
            'variance': round(statistics.variance(data), 6),
            'histogram': hist}


def zeros(data):
    zeros = [n for n in data if n == 0]
    return {'number_of_zeros': len(zeros), 'percent_zero': len(zeros)/len(data)}


def column_statistics(column):
    data = list(column.values())
    return {**summary(data), **zeros(data)}


def column_report(table, column_name, graph):
    return {'column_name': column_name,
            'created': datetime.datetime.utcnow(),
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
        add_column_to_graph(graph, data)
    return [column_report(table, column_name, graph)
            for column_name in columns]
