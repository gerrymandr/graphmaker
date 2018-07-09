import numpy
import pandas
import pytest
from graphmaker.reports.splitting import (splitting_energy, load_matching_dataframe,
                                          splitting_matrix, splitting_report)


# Replace these dataframes with mocks
@pytest.mark.skip('Need to re-write with mocks - real data takes too long.')
def test_load_matching_dataframe_has_the_right_columns():
    df = load_matching_dataframe('26', 'VTD', 'CD')
    assert 'VTD' in df.columns and 'CD' in df.columns and 'population' in df.columns


def example():
    return pandas.DataFrame({'VTD': ['1', '1', '2', '2', '3', '3'],
                             'CD': ['a', 'a', 'a', 'b', 'b', 'b'],
                             'pop': [1, 1, 1, 1, 1, 1]})


def test_splitting_matrix():
    df = example()

    matrix, _ = splitting_matrix(df, 'VTD', 'CD', 'pop')

    assert numpy.array_equal(matrix, numpy.array([[2, 0], [1, 1], [0, 2]]))


def test_splitting_matrix_includes_all_labels():
    df = example()

    matrix, indices = splitting_matrix(df, 'VTD', 'CD', 'pop')

    expected = set((v, c) for v in df['VTD'].unique()
                   for c in df['CD'].unique())

    assert set(indices.keys()) == expected

    # and no key errors occur

    for index in indices.values():
        assert matrix[index] is not None


def test_shape_of_matrix_has_columns_for_parts_and_rows_for_units():
    df = example()
    matrix, _ = splitting_matrix(df, 'VTD', 'CD', 'pop')
    assert matrix.shape == (3, 2)


def test_splitting_energy_is_zero_when_unit_determines_part():
    matrix = numpy.eye(8)
    assert splitting_energy(matrix) == 0


@pytest.mark.skip('Need to re-write with mocks - it takes too long.')
def test_splitting_report():
    report = splitting_report('26', 'VTD', 'CD')
    assert report
