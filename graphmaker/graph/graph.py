import datetime
import json
import logging
import os

import geopandas
import networkx
import pandas

from ..constants import graphs_base_path
from ..utils import find_column_with, generate_id, infer_id_column
from .make_graph import construct_graph_from_df

log = logging.getLogger(__name__)


class Graph:
    def __init__(self, graph, path=None):
        self.graph = graph
        self.path = path

    @classmethod
    def load(cls, path):
        with open(path, 'r') as document:
            data = json.load(document)
        graph = networkx.readwrite.json_graph.adjacency_graph(data)
        return cls(graph, path=path)

    def save(self, filepath=None):
        if not filepath:
            filepath = self.path

        data = networkx.readwrite.json_graph.adjacency_data(self.graph)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        log.info(f"Saved the graph to {filepath}")

    def add_columns_from_csv(self, csv_path, columns=None, id_column=None):
        table = pandas.read_csv(csv_path)
        self.add_columns_from_df(table, columns, id_column)

    def add_columns_from_shapefile(self, shapefile, columns=None, id_column=None):
        df = geopandas.read_file(shapefile)
        return self.add_columns_from_df(self, df, columns, id_column)

    def add_columns_from_df(self, table, columns=None, id_column=None):
        if not id_column:
            id_column = infer_id_column(table, id_column)
        if not columns:
            columns = [column for column in table.columns
                       if column != id_column]

        for column in columns:
            data = map_ids_to_column_entries(table, id_column, column)
            add_column_to_graph(self.graph, data, column)

    @classmethod
    def from_shapefile(cls, shapefile, adjacency_type, data_columns=None, id_column=None):
        log.info('Constructing adjacency graph from shapefile ' + str(shapefile))
        df = geopandas.read_file(shapefile)
        return cls.from_df(df, adjacency_type, data_columns, id_column)

    @classmethod
    def from_df(cls, df, adjacency_type, data_columns=None, id_column=None):
        df = df.to_crs({'init': 'epsg:4326'})

        id_column = infer_id_column(df, id_column)
        df.index = df[id_column]

        log.info('Constructing graph.')
        graph = construct_graph_from_df(df, adjacency_type=adjacency_type,
                                        geoid_col=id_column, cols_to_add=data_columns)

        add_metadata(graph, df, type=adjacency_type)

        return cls(graph)


class RookAndQueenGraphs:
    def __init__(self, rook, queen):
        self.rook = rook
        self.queen = queen
        self.fips = rook.graph.graph['state']

    @classmethod
    def load_fips(cls, fips):
        rook = Graph.load(cls.path(fips, 'rook'))
        queen = Graph.load(cls.path(fips, 'queen'))
        return cls(rook, queen)

    @classmethod
    def from_shapefile(cls, shapefile, data_columns=None,  id_column=None):
        log.info(
            'Constructing adjacency graphs from shapefile ' + str(shapefile))
        df = geopandas.read_file(shapefile)

        log.info('Constructing rook graph.')
        rook = Graph.from_df(
            df, adjacency_type='rook', cols_to_add=data_columns, id_column=id_column)

        log.info('Constructing queen graph.')
        queen = Graph.from_df(
            df, adjacency_type='queen', cols_to_add=data_columns, id_column=id_column)

        return cls(rook, queen)

    # Should maybe move all the path configuration to a separate module?
    @classmethod
    def path(cls, fips, adjacency=None):
        if adjacency not in ('rook', 'queen'):
            raise ValueError(
                'The parameter adjacency must be "rook" or "queen".')
        return os.path.join(graphs_base_path, fips, adjacency + '.json')

    def add_columns_from_df(self, df, columns=None, id_column=None):
        self.rook.add_columns_from_df(df,  columns, id_column)
        self.queen.add_columns_from_df(df, columns, id_column)

    def add_columns_from_shapefile(self, shapefile_path, columns=None, id_column=None):
        df = geopandas.read_file(shapefile_path)
        self.add_data_from_df(self, df, columns, id_column)

    def by_adjacency(self, adjacency):
        if adjacency == 'rook':
            return self.rook
        elif adjacency == 'queen':
            return self.queen
        else:
            raise ValueError(
                'The parameter adjacency must be "rook" or "queen".')

    def save(self):
        log.info('Saving graphs.')
        # Save the graphs in their respective homes:
        self.rook.save()
        self.queen.save()


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


def map_ids_to_column_entries(table, id_column, data_column):
    return dict(zip(table[id_column], table[data_column]))


def add_column_to_graph(graph, column, attribute_name):
    networkx.set_node_attributes(graph, column, attribute_name)
