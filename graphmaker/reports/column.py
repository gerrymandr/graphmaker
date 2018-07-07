import datetime
import numbers
import statistics

from constants import round_to
from reports import serializable_histogram


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
    return {'number_of_rows': len(data),
            'number_of_zeros': len(zeros),
            'percent_zero': round((len(zeros)/len(data))*100, round_to)}


def column_statistics(column):
    data = list(column)
    return {**summary(data), **zeros(data)}


def column_report(table, column_name, graph):
    return {'column_name': column_name,
            'created': str(datetime.datetime.utcnow()),
            'graph': graph.graph.get('id'),
            'report': column_statistics(table[column_name])}
