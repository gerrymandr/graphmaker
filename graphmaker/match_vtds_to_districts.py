import logging
import os
from collections import Counter
from functools import partial

import numpy
import pandas

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from constants import (cd_matchings_path, fips_to_state_abbreviation,
                       fips_to_state_name, graphs_base_path, valid_fips_codes)
from main import load_graph

logging.basicConfig(level=logging.INFO,
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler('./matching.log')])

# The VTDs have GEOIDs of this form:
# {2-digit state FIPS}{3-digit county code}{>=2-digit VTD code}

# We can match VTDs to CDs like this:
# 1. Use the block-to-VTD file to find a tabulation block for each VTD.
# 2. Use the block-to-CD assignment file to find the CD that contains that block.

# The block assignment files are in this directory on my computer
# (at the same level as the outer graphmaker folder):
baf_path = '../../block_assignments/block_assignments/'

# The block assignment files are named like:
# "BlockAssign_ST{fips}_{2-digit state abbreviation}_{matched unit}
# For example, BlockAssign_ST26_MI_CD assigns blocks to CDs in Michigan.


def block_to_unit_filepath(fips, unit):
    """The units are all-caps: 'VTD' or 'CD'"""
    abbrev = fips_to_state_abbreviation[fips]
    return os.path.join(baf_path, fips, f"BlockAssign_ST{fips}_{abbrev}_{unit}.txt")

# Our objective will be to make a VTD-to-CD assignment CSV.


def blocks_to_vtds_dataframe(fips, name_geoid_column='geoid'):
    df = pandas.read_csv(block_to_unit_filepath(
        fips, 'VTD'), index_col='BLOCKID', dtype=str)
    df[name_geoid_column] = fips + df['COUNTYFP'] + df['DISTRICT']
    return df


def integrate_over_blocks_in_vtds(fips, series, function=numpy.sum):
    blocks = blocks_to_vtds_dataframe(fips)
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

    logging.info(f"{percent}% of {node}'s neighbors have value {best_guess},"
                 f" so our best-guess value for {node} is {best_guess}.")

    return best_guess


def choose_most_common(group, split_percentages=None):
    counts = group.value_counts(dropna=False, normalize=True)
    common = counts.index
    most_common = common[0]

    if len(common) > 1:
        logging.warn(f"More than one CD assigned to these blocks!")
        percentage = round((counts[0] / sum(counts)) * 100, 2)
        logging.warn(f"{percentage}% were assigned to {most_common}")
        split_percentages.append(percentage)

    return most_common


def graph_path(fips, adjacency='rook'):
    return os.path.join(graphs_base_path, fips, adjacency + '.json')


def match_vtds_to_districts(fips, district='CD', split_percentages):
    logging.info(f"Loading blocks for fips code {fips}")
    blocks_to_cds = pandas.read_csv(
        block_to_unit_filepath(fips, district), index_col='BLOCKID', dtype=str)

    blocks_to_vtds = blocks_to_vtds_dataframe(fips)
    blocks_to_vtds[district] = blocks_to_cds['DISTRICT']

    logging.info(
        'Matching each VTD to the most common district assignment of the blocks in the VTD.')

    grouped_by_vtd = blocks_to_vtds.groupby('geoid')
    vtds_to_cds = grouped_by_vtd[district].aggregate(
        partial(choose_most_common, split_percentages=split_percentages))

    graph = load_graph(graph_path(fips))
    for node in vtds_to_cds[vtds_to_cds.isna()].index:
        vtds_to_cds[node] = patch_value_from_neighbors(
            node, vtds_to_cds, graph)

    return vtds_to_cds


def create_matching_for_state(fips, output_file):
    split_percentages = []
    vtds_to_cds = match_vtds_to_districts(fips, split_percentages)

    logging.info('I created a matching of VTDs to CDs.')
    number_missing = len(vtds_to_cds[vtds_to_cds.isna()])
    logging.info(
        f"Remaining missing values: {number_missing}")

    percent_split = round((len(split_percentages) / len(vtds_to_cds))*100, 3)
    plt.title(f"{percent_split}% of VTDs were split")
    plt.hist(split_percentages, bins=100)
    plt.savefig(os.path.join(cd_matchings_path, 'plots', fips + '.png'))
    plt.close()

    logging.info(f"Writing output to {output_file}")
    vtds_to_cds.to_csv(output_file)


def create_matchings_for_every_state():
    for fips in valid_fips_codes():
        logging.info(f"Working on {fips_to_state_name[fips]}")
        create_matching_for_state(fips, os.path.join(
            cd_matchings_path, fips + '.csv'))


def main():
    create_matchings_for_every_state()


if __name__ == '__main__':
    main()
