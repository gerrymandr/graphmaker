import logging
import os
from collections import Counter
from functools import partial

import numpy
import pandas

from .constants import cd_matchings_path, fips_to_state_name, valid_fips_codes
from .graph import RookAndQueenGraphs
from .resources import BlockAssignmentFile

# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt


# logging.basicConfig(level=logging.INFO)


# The VTDs have GEOIDs of this form:
# {2-digit state FIPS}{3-digit county code}{>=2-digit VTD code}

# We can match VTDs to CDs like this:
# 1. Use the block-to-VTD file to find a tabulation block for each VTD.
# 2. Use the block-to-CD assignment file to find the CD that contains that block.

# The block assignment files are in this directory on my computer
# (at the same level as the outer graphmaker folder):

# The block assignment files are named like:
# "BlockAssign_ST{fips}_{2-digit state abbreviation}_{matched unit}
# For example, BlockAssign_ST26_MI_CD assigns blocks to CDs in Michigan.


# Our objective will be to make a VTD-to-CD assignment CSV.


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

    logging.info(f"{percent}% of {node}'s neighbors have value {best_guess},"
                 f" so our best-guess value for {node} is {best_guess}.")

    return best_guess


def choose_most_common(group, dropna=False, split_percentages=None):
    counts = group.value_counts(dropna=dropna, normalize=True)
    common = counts.index

    try:
        most_common = common[0]
    except KeyError:
        choose_most_common(group, dropna=False,
                           split_percentages=split_percentages)

    if len(common) > 1:
        logging.warn(f"More than one CD assigned to the blocks in this VTD!")
        percentage = round((counts[0] / sum(counts)) * 100, 2)
        logging.warn(f"{percentage}% were assigned to {most_common}")
        split_percentages.append(percentage)

    return most_common


def match_vtds_to_districts(fips, split_percentages, district='CD'):
    logging.info(f"Loading blocks for fips code {fips}")

    blocks_to_cds = BlockAssignmentFile(fips).as_df(unit=district)
    blocks_to_cds = blocks_to_cds.set_index('BLOCKID')

    blocks_to_vtds = blocks_to_vtds_dataframe(fips)
    blocks_to_vtds = blocks_to_vtds.set_index('BLOCKID')
    blocks_to_vtds[district] = blocks_to_cds['DISTRICT']

    logging.info(
        'Matching each VTD to the most common district assignment of the blocks in the VTD.')

    grouped_by_vtd = blocks_to_vtds.groupby('geoid')
    vtds_to_cds = grouped_by_vtd[district].aggregate(
        partial(choose_most_common, split_percentages=split_percentages))

    graph = RookAndQueenGraphs.load_fips(fips).rook.graph

    for node in vtds_to_cds[vtds_to_cds.isna()].index:
        vtds_to_cds[node] = patch_value_from_neighbors(
            node, vtds_to_cds, graph)

    return vtds_to_cds


def create_matching_for_state(fips, output_file, split_rates):
    split_percentages = []
    vtds_to_cds = match_vtds_to_districts(fips, split_percentages)

    logging.info('I created a matching of VTDs to CDs.')
    number_missing = len(vtds_to_cds[vtds_to_cds.isna()])
    logging.info(
        f"Remaining missing values: {number_missing}")

    percent_split = round((len(split_percentages) / len(vtds_to_cds))*100, 3)
    split_rates.append(percent_split)

    # plt.title(f"{percent_split}% of VTDs were split")
    # plt.hist(split_percentages, bins=100)
    # plt.savefig(os.path.join(cd_matchings_path, 'plots', fips + '.png'))
    # plt.close()

    logging.info(f"Writing output to {output_file}")
    vtds_to_cds.to_csv(output_file)


def create_matchings_for_every_state():
    split_rates = []
    for fips in valid_fips_codes():
        logging.info(f"Working on {fips_to_state_name[fips]}")
        create_matching_for_state(fips, os.path.join(
            cd_matchings_path, fips + '.csv'), split_rates)
    print(pandas.DataFrame(split_rates).describe())


def main():
    create_matchings_for_every_state()


if __name__ == '__main__':
    main()
