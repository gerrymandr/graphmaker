import logging
from collections import Counter

import numpy
import pandas

from .collect import collector
from .constants import fips_to_state_name, valid_fips_codes
from .graph import RookAndQueenGraphs
from .resources import BlockAssignmentFile

# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

collect = collector('vtd_splits',
                    ['fips', 'node', 'best_guess_match',
                     'percent_match'], './logs/vtd_splits.csv',
                    {'percent_match': '.4f'})

# VTDs have GEOIDs of this form:
# {2-digit state FIPS}{3-digit county code}{>=2-digit VTD code}

# We can match VTDs to CDs like this:
# 1. Use the block-to-VTD file to find a tabulation block for each VTD.
# 2. Use the block-to-CD assignment file to find the CD that contains that block.

# The block assignment files are in this directory on my computer
# (at the same level as the outer graphmaker folder):

# The block assignment files are named like:
# "BlockAssign_ST{fips}_{2-digit state abbreviation}_{matched unit}
# For example, BlockAssign_ST26_MI_CD assigns blocks to CDs in Michigan.


def integrate_over_blocks_in_vtds(fips, series, unit, function=numpy.sum):
    """
    Integrates the block-level values in :series: to produce vtd-level
    aggregate values.

    :fips: state fips code
    :series: pandas Series, assumed to be indexed by Census block GEOID
    :function: (defaults to sum) the function to use for aggregation
    """
    blocks = BlockAssignmentFile(fips).as_df(unit)
    blocks = blocks.set_index('BLOCKID')
    blocks['data'] = series
    grouped_by_vtd = blocks.groupby(unit)
    vtd_totals = grouped_by_vtd['data'].aggregate(function)
    return vtd_totals


def patch_value_from_neighbors(node, series, graph):
    neighbor_values = Counter(series[neighbor]
                              for neighbor in graph.neighbors(node))

    best_guess, count = neighbor_values.most_common(1)[0]
    degree = graph.degree[node]
    percent = round((count/degree) * 100, 2)

    log.info(f"{percent}% of {node}'s neighbors have value {best_guess},"
             f" so our best-guess value for {node} is {best_guess}.")

    return best_guess


def most_common_values(series):
    counts = series.value_counts(dropna=True)
    if len(counts.index) == 0:
        counts = series.value_counts(dropna=False)
    return counts


def check_for_splits(value_counts, graph, unit, part):
    fips = graph.graph.get('state', '')

    for node, counts in value_counts.items():
        common = counts.index
        most_common = common[0]

        if len(common) > 1:
            log.warn(
                f"More than one {part} assigned to the blocks in {unit} {node}!")
            percentage = counts[most_common] / sum(counts)
            log.warn(
                f"{round(percentage*100, 2)}% were assigned to {part} {most_common}")
            # the first two digits of a block_id is the state fips code
            collect(fips=fips, node=node, best_guess_match=most_common,
                    percent_match=percentage)


def keys_with_na_values(mapping):
    for key, value in mapping.items():
        if pandas.isna(value):
            yield key


def map_units_to_parts_via_blocks(blocks, graph, unit='VTD', part='CD'):
    """
    :blocks: dataframe of blocks with columns for :unit: and :part: assignments
    :graph: networkx adjacency graph with units as nodes
    """
    grouped_by_unit = blocks.groupby(unit)

    value_counts = {node: group[part].agg(most_common_values)
                    for node, group in grouped_by_unit}

    check_for_splits(value_counts, graph, unit, part)

    units_to_parts = {node: counts.idxmax()
                      for node, counts in value_counts.items()}

    # For values that are still NA, use the graph structure
    # to infer a reasonable choice
    for node in keys_with_na_values(units_to_parts):
        units_to_parts[node] = patch_value_from_neighbors(
            node, units_to_parts, graph)

    return units_to_parts


def match(fips, unit, part):
    log.info(f"Loading blocks for fips code {fips}")

    blocks_to_parts = BlockAssignmentFile(fips).as_df(unit=part)
    blocks_to_parts = blocks_to_parts.set_index('BLOCKID')

    blocks_to_units = BlockAssignmentFile(fips).as_def(unit=unit)
    blocks_to_units = blocks_to_units.set_index('BLOCKID')
    blocks_to_units[part] = blocks_to_parts['DISTRICT']

    log.info(
        'Matching each unit to the most common part assignment'
        'of the blocks in the unit.')

    graphs = RookAndQueenGraphs.load_fips(fips)

    for adjacency in ('rook', 'queen'):
        graph = graphs.by_adjacency(adjacency)
        log.info(
            'Matching each unit to the most common part assignment'
            'of the blocks in the unit.')

        units_to_parts = map_units_to_parts_via_blocks(
            blocks_to_units, graph.graph, unit, part)

        log.info(
            f"Created a matching of {unit}s to {part}s for the {adjacency}-adjacency graph.")

        check_for_missing_values(fips, units_to_parts)

        graph.add_columns_from_df(units_to_parts, [part], unit)

    graphs.save()


def save(matching, output_file):
    log.info(f"Writing output to {output_file}")
    matching.to_csv(output_file)


def check_for_missing_values(fips, matching):
    number_missing = len(tuple(keys_with_na_values(matching)))
    if number_missing > 0:
        log.error(f"Something went wrong. {fips} has {number_missing} missing"
                  "assignments.", extra={'fips': fips, 'number_missing': number_missing})


def create_matchings_for_every_state():
    for fips in valid_fips_codes():
        log.info(f"Working on {fips_to_state_name[fips]}")
        match(fips, 'VTD', 'CD')


def main():
    create_matchings_for_every_state()


if __name__ == '__main__':
    main()
