import json
import logging
import os

import pandas
from graphmaker.constants import (fips_to_state_name, graphs_base_path,
                                  valid_fips_codes)
from graphmaker.graph import RookAndQueenGraphs
from graphmaker.match import integrate_over_blocks_in_vtds, match
from graphmaker.reports.column import column_report
from graphmaker.reports.graph_report import graph_report, rook_vs_queen
from graphmaker.resources import BlockPopulationShapefile, VTDShapefile

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


def get_vtd_data_from_blocks(fips, block_df, columns):
    # Block population files have block ids under 'BLOCKID10'
    block_df = block_df.set_index('BLOCKID10')

    data = pandas.DataFrame({column: integrate_over_blocks_in_vtds(
        fips, block_df[column]) for column in columns})
    return data


def vtd_populations_from_blocks(fips):
    block_df = BlockPopulationShapefile(fips).as_df()
    vtd_populations = get_vtd_data_from_blocks(fips, block_df, ['POP10'])
    return vtd_populations

# These functions will add data to every state's graph:


def add_populations_from_blocks():
    for fips in valid_fips_codes():
        state = fips_to_state_name[fips]

        logging.info(
            'Aggregating block-level population data for ' + state + '.')

        vtd_pops = vtd_populations_from_blocks(fips)
        vtd_pops['geoid'] = vtd_pops.index

        graphs = RookAndQueenGraphs.load_fips(fips)

        graphs.add_data_from_dataframe(fips, vtd_pops, ['POP10'])

        population_report = column_report(vtd_pops, 'POP10', graphs.rook.graph)

        with open(os.path.join(graphs_base_path, fips, 'pop10_report.json'), 'w') as f:
            f.write(json.dumps(population_report, indent=2, sort_keys=True))


def add_basic_data_from_census_shapefiles():
    columns = ['ALAND10', 'AWATER10', 'NAME10', 'COUNTYFP10']
    for fips in valid_fips_codes():
        graphs = RookAndQueenGraphs.load_fips(fips)
        shapefile = VTDShapefile(fips).path()
        graphs.add_columns_from_shapefile(shapefile, columns, 'GEOID10')
        graphs.save()


def create_matchings_for_every_state():
    for fips in valid_fips_codes():
        log.info(f"Working on {fips_to_state_name[fips]}")
        match(fips, 'VTD', 'CD')


def build_reports(graphs):
    logging.info('Building reports for rook- and queen-adjacency graphs.')
    rook_synopsis = graph_report(graphs.rook.graph)
    queen_synopsis = graph_report(graphs.queen.graph)

    logging.info('Comparing rook- and queen-adjacency graphs.')
    comparison = {'rook_vs_queen_comparison': rook_vs_queen(
        graphs.rook.graph, graphs.queen.graph)}

    return {'rook_graph_report': rook_synopsis,
            'queen_graph_report': queen_synopsis,
            'comparison': comparison}


def main(args):
    """
    This function is intended to be used as a command line utility for generating
    adjacency graphs from a given shapefile path.
    """
    path = args[0]

    id_column = None
    if len(args) > 1:
        id_column = args[1]

    if not path:
        raise ValueError('Please specify a shapefile to turn into a graph.')

    state_graphs = RookAndQueenGraphs.from_shapefile(path, id_column=id_column)

    result = build_reports(state_graphs)

    state = state_graphs.fips

    with open(os.path.join(graphs_base_path, state, "report.json"), 'w') as f:
        f.write(json.dumps(result, indent=2, sort_keys=True))

    return result


if __name__ == '__main__':
    create_matchings_for_every_state()
