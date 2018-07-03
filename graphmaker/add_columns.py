import networkx

# Use tablib to add any column of data to the graph as a node attribute
# (or edge attribute!)
# pandas, csv, json, or dict


def add_column_to_graph(graph, column):
    networkx.set_node_attributes(graph, column)
