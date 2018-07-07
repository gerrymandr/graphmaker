import json

import networkx

from .constants import graphs_base_path


class Graph:
    def __init__(self):
        rook =

    def _load(self, path):
        with open(path, 'r') as document:
            data = json.load(document)
        graph = networkx.readwrite.json_graph.adjacency_graph(data)
        return graph

    def _save(self, graph, path):
        if not filepath:
            filepath = os.path.join(location, self.id + ".json")
        data = networkx.readwrite.json_graph.adjacency_data(graph)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        print(f"Saved the graph to {filepath}")

    def add_columns_from_csv(self, csv_path, id_column, columns=None):
        table = pandas.read_csv(csv_path)
        self.add_columns_from_df(table, id_column, columns)

    def add_columns_from_df(self, table, id_column, columns=None):
        if not columns:
            columns = [
                column for column in table.columns if column != id_column]
        return add_columns_and_report(self, table, columns, id_column)

    def save(self):
        logging.info('Saving graphs.')

        # Ensure that the paths exist:
        state = self.rook.graph['state']
        path = os.path.join(graphs_base_path, state)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        # Save the graphs in their respective homes:
        save(self.rook, filepath=os.path.join(path, 'rook.json'))
        save(self.queen, filepath=os.path.join(path, 'queen.json'))
