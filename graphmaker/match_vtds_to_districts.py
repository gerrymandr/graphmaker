import logging
import os
from collections import Counter

import numpy
import pandas

from .collect import collector
from .constants import cd_matchings_path, fips_to_state_name, valid_fips_codes
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


def blocks_to_vtds_dataframe(fips, name_geoid_column='geoid'):
    df = BlockAssignmentFile(fips).as_df()
    df[name_geoid_column] = fips + df['COUNTYFP'] + df['DISTRICT']
    return df


def integrate_over_blocks_in_vtds(fips, series, function=numpy.sum):
    """
    Integrates the block-level values in :series: to produce vtd-level
    aggregate values.

    :fips: state fips code
    :series: pandas Series, assumed to be indexed by Census block GEOID
    :function: (defaults to sum) the function to use for aggregation
    """
    blocks = blocks_to_vtds_dataframe(fips, name_geoid_column='geoid')
    blocks = blocks.set_index('BLOCKID')
    blocks['data'] = series
    grouped_by_vtd = blocks.groupby('geoid')
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


def map_units_to_parts_via_blocks(blocks, graph, unit='geoid', part='CD'):
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


def match_vtds_to_districts(fips, graph, district='CD'):
    log.info(f"Loading blocks for fips code {fips}")

    blocks_to_cds = BlockAssignmentFile(fips).as_df(unit=district)
    blocks_to_cds = blocks_to_cds.set_index('BLOCKID')

    blocks_to_vtds = blocks_to_vtds_dataframe(fips)
    blocks_to_vtds = blocks_to_vtds.set_index('BLOCKID')
    blocks_to_vtds[district] = blocks_to_cds['DISTRICT']

    log.info(
        'Matching each VTD to the most common district assignment'
        'of the blocks in the VTD.')

    vtds_to_cds = map_units_to_parts_via_blocks(
        blocks_to_vtds, graph.graph, unit='geoid', part='CD')
    return vtds_to_cds


def create_matching_for_state(fips, adajacency, output_file):
    graphs = RookAndQueenGraphs.load_fips(fips)
    graph = graphs.by_adjacency(adajacency)

    vtds_to_cds = match_vtds_to_districts(fips, graph)

    log.info('Created a matching of VTDs to CDs.')

    number_missing = len(tuple(keys_with_na_values(vtds_to_cds)))
    log.info(
        f"Remaining missing values: {number_missing}",
        extra={'number_missing': number_missing})

    # percent_split = round((len(split_percentages) / len(vtds_to_cds))*100, 3)
    # split_rates.append(percent_split)

    # plt.title(f"{percent_split}% of VTDs were split")
    # plt.hist(split_percentages, bins=100)
    # plt.savefig(os.path.join(cd_matchings_path, 'plots', fips + '.png'))
    # plt.close()

    log.info(f"Writing output to {output_file}")
    # vtds_to_cds.to_csv(output_file)


def create_matchings_for_every_state():
    for fips in valid_fips_codes():
        log.info(f"Working on {fips_to_state_name[fips]}")
        create_matching_for_state(fips, 'queen', os.path.join(
            cd_matchings_path, fips + '.csv'))


def main():
    create_matchings_for_every_state()


if __name__ == '__main__':
    main()
