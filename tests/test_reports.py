import json
from unittest.mock import Mock

import networkx
import numpy
from graphmaker.reports import (edge_set, eigenvalues_hist, graph_statistics,
                                number_connected_components, report,
                                rook_vs_queen, serializable_histogram,
                                unit_contained_in_another)


def test_edge_set_is_insensitive_to_order_of_nodes():
    edges = [(1, 2), (2, 3), (3, 1)]
    edges_with_some_switched = [(2, 1), (3, 2), (3, 1)]
    assert edge_set(edges) == edge_set(edges_with_some_switched)


def test_graph_statistics_works_on_small_example():
    # 1 - 2
    # | / |
    # 4 - 3 - 5
    # degrees 3, 3, 3, 2, 1
    # mean degree 2.4
    # median degree 3
    # min degree 1
    # max degree 3
    edges = [(1, 2), (2, 3), (4, 2), (4, 1), (4, 3), (3, 5)]
    graph = networkx.Graph(edges)
    expected = {'number_of_nodes': 5,
                'number_of_edges': 6,
                'degree_statistics':
                    {'counts': {'3': 3, '2': 1, '1': 1},
                     'min': 1,
                     'max': 3,
                     'mean': 2.4,
                     'median': 3,
                     'variance': 0.8}
                }
    assert graph_statistics(graph) == expected


def test_number_connected_components_works_on_small_example():
    # 1-3  5
    # |/   |\
    # 2    4-6
    graph = networkx.Graph([(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)])
    assert number_connected_components(
        graph) == {"connected_components": 2}


def test_unit_contained_in_another_works_on_small_example():
    # If a unit is contained in another, that container will be its only neighbor.
    # The converse is true as long as the graph has more than 2 nodes.
    # 1 - 4 - 5
    # |   |   |
    # 7   8\  9
    # |   |10 |
    # 2 - 3 - 6
    graph = networkx.Graph([(1, 7), (2, 7), (2, 3), (3, 8),
                            (4, 1), (4, 5), (3, 6), (5, 9), (9, 6), (4, 8), (8, 10)])
    for n in [1, 4, 5, 7, 9, 2, 3, 6]:
        graph.nodes[n]['boundary_node'] = True
    for n in [8, 10]:
        graph.nodes[n]['boundary_node'] = False

    result = unit_contained_in_another(graph)
    result_nodes = result['units_entirely_contained_in_another']

    assert len(result_nodes) == 1
    assert 10 in result_nodes

    result_count = result['number_of_units_entirely_contained_in_another']
    assert result_count == 1


def test_rook_vs_queen_works_on_a_small_example():
    # 1 - 2       1 - 2
    # |   |   vs  | X |
    # 4 - 3       4 - 3
    rook = networkx.Graph([(1, 2), (2, 3), (3, 4), (4, 1)])
    queen = networkx.Graph([(1, 2), (2, 3), (3, 4), (4, 1), (4, 2), (3, 1)])

    result = rook_vs_queen(rook, queen)
    assert result['number_of_rook_edges'] == 4
    assert result['number_of_queen_edges'] == 6
    assert result['common_edges'] == 4
    assert result['symmetric_difference'] == 2
    assert abs(result['percent_common'] - 0.66) <= 0.01


def test_report_calls_every_function():
    mock_graph = Mock()
    mock_reports = [Mock().method() for i in range(4)]

    for mock in mock_reports:
        mock.return_value = dict()

    report(mock_graph, mock_reports)
    assert all(mock.call_count == 1 for mock in mock_reports)


def test_eigenvalues_hist_returns_floats_and_ints():
    graph = networkx.Graph([(0, 1), (1, 2), (2, 3), (3, 0)])
    hist = eigenvalues_hist(graph)['eigenvalues_of_the_laplacian_histogram']
    for left, right in hist['bins']:
        assert isinstance(left, float)
        assert isinstance(right, float)
    for count in hist['counts']:
        assert isinstance(count, int)


def test_serializable_histogram_returns_serializable():
    data = numpy.random.normal(size=100)
    serialized = json.dumps(serializable_histogram(data))
    assert serialized
