import logging
import os

import geopandas as gp
import pandas

from constants import block_population_path, valid_fips_codes
from match_vtds_to_districts import integrate_over_blocks_in_vtds
from utils import download_and_unzip

logging.basicConfig(filename='./add_block_data.log',
                    filemode='w', level=logging.INFO)


block_pop_base = "http://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/"


def url(fips):
    return block_pop_base + "tabblock2010_" + fips + "_pophu.zip"


def block_pop_path_for_state(fips):
    return os.path.join(block_population_path, fips)


def download_blocks_for_state(fips):
    download_and_unzip(url(fips), block_pop_path_for_state(fips))


def block_population_dataframe(fips):
    df = gp.read_file(block_pop_path_for_state(fips))
    return df


def get_vtd_data_from_blocks(fips, block_df, columns):
    # Block population files have block ids under 'BLOCKID10'
    block_df = block_df.set_index('BLOCKID10')
    # Block populations list 2010 census populations under 'POP10'

    data = pandas.DataFrame({column: integrate_over_blocks_in_vtds(
        fips, block_df[column]) for column in columns})
    return data


def create_table_from_block_level_data(fips, output_path):
    block_df = block_population_dataframe(fips)
    vtd_populations = get_vtd_data_from_blocks(fips, block_df, ['POP10'])
    vtd_populations.to_csv(os.path.join(output_path), header=True)


def population_csv_path(fips):
    return os.path.join('.', 'vtd_statistics', fips, 'population.csv')


def main():
    for fips in valid_fips_codes():
        logging.info('Aggregating block-level population data')
        create_table_from_block_level_data(fips, population_csv_path(fips))


if __name__ == '__main__':
    main()
