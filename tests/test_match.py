from unittest.mock import MagicMock, patch

import networkx
import pandas
from graphmaker.match_vtds_to_districts import map_units_to_parts_via_blocks


def imperfect_matching():
    blocks = pandas.DataFrame(data={'blockid': ['a', 'b', 'c', 'd', 'e'],
                                    'unit': ['1', '1', '1', '2', '2'],
                                    'district': [1, 1, 2, 2, 2]})
    # block 'c' is in unit '1' but assigned to district 2
    blocks.set_index('blockid')
    return blocks


def test_match_when_units_perfectly_map_to_parts():
    blocks = pandas.DataFrame(data={'blockid': [1, 2, 3, 4],
                                    'unit': [1, 1, 2, 2],
                                    'district': [1, 1, 2, 2]})
    blocks.set_index('blockid')

    graph = MagicMock()

    matching = map_units_to_parts_via_blocks(
        blocks, graph, unit='unit', part='district')

    assert matching[1] == 1 and matching[2] == 2


def test_match_unit_to_most_common_part_if_match_not_perfect():
    blocks = imperfect_matching()

    graph = MagicMock()

    matching = map_units_to_parts_via_blocks(
        blocks, graph, unit='unit', part='district')

    assert matching['1'] == 1 and matching['2'] == 2


@patch('graphmaker.match_vtds_to_districts.collect')
def test_match_collects_splits(mock_collect):
    blocks = imperfect_matching()
    graph = MagicMock()

    map_units_to_parts_via_blocks(
        blocks, graph, unit='unit', part='district')
    mock_collect.assert_called()

    kwargs = mock_collect.call_args[1]
    assert kwargs['node'] == '1'


def test_match_na_nodes_using_their_neighbors():
    blocks = pandas.DataFrame(data={'blockid': [1, 2, 3, 4],
                                    'unit': [1, 1, 2, 2],
                                    'district': [None, None, 2, 2]})
    blocks.set_index('blockid')

    graph = networkx.Graph([(1, 2)])

    matching = map_units_to_parts_via_blocks(
        blocks, graph, unit='unit', part='district')

    assert matching[1] == 2

# TODO: Cool graph generator-based tests
