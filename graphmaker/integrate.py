import geopandas
import numpy
import pandas
from graphmaker.graph import RookAndQueenGraphs
from graphmaker.resources import BlockAssignmentFile
from graphmaker.utils import infer_id_column


def integrate(fips, filepath, columns, unit, save=True):
    df = load_df(filepath)
    totals = pandas.DataFrame(data={column:
                                    integrate_over_blocks_in_units(
                                        fips, df[column], unit)
                                    for column in columns})

    if save:
        graphs = RookAndQueenGraphs.load_fips(fips)
        graphs.add_columns_from_df(totals, columns, unit)
        graphs.save()
    return totals


def load_df(filepath, id_column=None):
    extension = filepath.split('.')[-1]
    if extension == 'csv' or extension == 'txt':
        df = pandas.read_csv(filepath)
    elif extension == 'shp':
        df = geopandas.read_file(filepath)
    else:
        raise ValueError(
            'Unrecognized file extension. I know csv, txt, and shp.')

    if not id_column:
        id_column = infer_id_column(df, ['blockid', 'block', 'id'])

    df = df.set_index(id_column)
    return df


def integrate_over_blocks_in_units(fips, series, unit, function=numpy.sum):
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
