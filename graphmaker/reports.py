import functools
import statistics
from collections import Counter

import networkx
import numpy
import scipy

from constants import round_to

# import planarity


def serializable_histogram(data):
    counts, bin_endpoints = numpy.histogram(data, bins='auto')
    counts = list(map(int, counts))
    bins = list()
    for left, right in zip(bin_endpoints[:-1], bin_endpoints[1:]):
        bins.append([round(float(left), round_to),
                     round(float(right), round_to)])
    return {'bins': bins, 'counts': counts}


def edge_set(edges):
    return set(tuple(sorted(edge)) for edge in edges)


def dict_with_str_keys(d):
    return {str(key): value for key, value in dict(d).items()}


def graph_statistics(graph):
    degrees = [degree for node, degree in graph.degree]
    degree_counts = Counter(degrees)
    min_degree = min(degree_counts.keys())
    max_degree = max(degree_counts.keys())
    mean_degree = round(statistics.mean(degrees), round_to)
    median_degree = statistics.median(degrees)
    variance = round(statistics.variance(degrees), round_to)
    return {'number_of_nodes': graph.number_of_nodes(),
            'number_of_edges': graph.number_of_edges(),
            'degree_statistics': {
                'counts': dict_with_str_keys(degree_counts),
                'min': min_degree,
                'max': max_degree,
                'mean': mean_degree,
                'median': median_degree,
                'variance': variance
    }}


def eigenvalues_hist(graph):
    laplacian = networkx.laplacian_matrix(graph).todense()
    eigenvalues = numpy.real(scipy.linalg.eigvals(
        laplacian).tolist())
    hist = serializable_histogram(eigenvalues)
    return {'eigenvalues_of_the_laplacian_histogram': hist}


def number_connected_components(graph):
    number = networkx.number_connected_components(graph)
    return {'connected_components': number}


def sizes_of_connected_components(graph):
    sizes = [len(c) for c in networkx.connected_components(graph)]
    return {'sizes_of_connected_components': sizes}

# def planar(graph):
#    is_planar = planarity.is_planar(graph)
#    return {'is_planar': is_planar}


def contained_in_its_neighbor(node, graph):
    return not graph.nodes[node]['boundary_node']


def unit_contained_in_another(graph):
    degree_one_nodes = [node for node in graph.nodes
                        if len(list(graph.neighbors(node))) == 1]
    trapped_nodes = [
        node for node in degree_one_nodes if contained_in_its_neighbor(node, graph)]
    return {'units_entirely_contained_in_another': trapped_nodes,
            'number_of_units_entirely_contained_in_another': len(trapped_nodes)}


def rook_vs_queen(rook_graph, queen_graph):
    rook_edges = edge_set(rook_graph.edges)
    queen_edges = edge_set(queen_graph.edges)
    intersection = len(rook_edges & queen_edges)
    difference = len(rook_edges | queen_edges) - intersection
    return {'number_of_rook_edges': len(rook_edges),
            'number_of_queen_edges': len(queen_edges),
            'common_edges': intersection,
            'symmetric_difference': difference,
            'percent_common': round(intersection / (intersection + difference), round_to)}


def report(graph, reports=[graph_statistics, number_connected_components,
                           # planar,
                           unit_contained_in_another, eigenvalues_hist]):
    return functools.reduce(lambda doc, f: {**doc, **f(graph)}, reports, dict())
