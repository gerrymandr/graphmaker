import functools
import statistics
from collections import Counter

import networkx

# import planarity


def edge_set(edges):
    return set(tuple(sorted(edge)) for edge in edges)


def graph_statistics(graph):
    degrees = [degree for node, degree in graph.degree]
    degree_counts = Counter(degrees)
    min_degree = min(degree_counts.keys())
    max_degree = max(degree_counts.keys())
    mean_degree = round(statistics.mean(degrees), 6)
    median_degree = statistics.median(degrees)
    return {"number_of_nodes": graph.number_of_nodes(),
            "number_of_edges": graph.number_of_edges(),
            "degree_statistics": {
                "counts": dict(degree_counts),
                "min": min_degree,
                "max": max_degree,
                "mean": mean_degree,
                "median": median_degree
    }}


def number_connected_components(graph):
    number = networkx.number_connected_components(graph)
    return {"connected_components": number}


# def planar(graph):
#    is_planar = planarity.is_planar(graph)
#    return {"is_planar": is_planar}


def unit_contained_in_another(graph):
    trapped_nodes = [node for node in graph.nodes
                     if len(list(graph.neighbors(node))) == 1]
    return {"units_entirely_contained_in_another": trapped_nodes,
            "number_of_units_entirely_contained_in_another": len(trapped_nodes)}


def rook_vs_queen(rook_graph, queen_graph):
    rook_edges = edge_set(rook_graph.edges)
    queen_edges = edge_set(queen_graph.edges)
    return {"number_of_rook_edges": len(rook_edges),
            "number_of_queen_edges": len(queen_edges),
            "size_of_intersection": len(rook_edges & queen_edges)}


def report(graph, reports=[graph_statistics, number_connected_components,
                           # planar,
                           unit_contained_in_another]):
    return functools.reduce(lambda doc, f: {**doc, **f(graph)}, reports, dict())
