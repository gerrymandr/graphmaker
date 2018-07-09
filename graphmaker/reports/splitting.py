import numpy
from graphmaker.constants import fips_to_state_name
from graphmaker.resources import BlockAssignmentFile, BlockPopulationShapefile


def splitting_report(fips, unit, part, function_for_splitting_energy='log'):
    df = load_matching_dataframe(fips, unit, part)
    matrix, indices = splitting_matrix(df, unit, part, 'population')

    information_distance = float(
        splitting_energy(matrix, function=function_for_splitting_energy))

    splitting_confidence_vector = splitting_confidence(
        matrix).flatten().tolist()
    unit_indices = {u: i for (u, p), (i, j) in indices.items()}
    confidences = {
        u: splitting_confidence_vector[i] for u, i in unit_indices.items()}

    return {'fips': fips, 'state': fips_to_state_name[fips],
            'unit': unit, 'partitioned_by': part,
            'splitting_energy': information_distance,
            'splitting_confidences': confidences}


def load_matching_dataframe(fips, unit, part, part_name='DISTRICT'):
    blocks_to_parts = BlockAssignmentFile(fips).as_df(part)
    blocks_to_parts = blocks_to_parts.set_index('BLOCKID')

    blocks_to_units = BlockAssignmentFile(fips).as_df(unit)
    blocks_to_units = blocks_to_units.set_index('BLOCKID')
    blocks_to_units[part] = blocks_to_parts[part_name]

    block_pops = BlockPopulationShapefile(fips).as_df()
    blocks_to_units['population'] = block_pops['POP10']

    return blocks_to_units


def splitting_matrix(df, unit, part, weight_column):
    units = df[unit].unique()
    parts = df[part].unique()

    indices = {(u, p): (i, j) for (i, u) in enumerate(units)
               for (j, p) in enumerate(parts)}

    matrix = numpy.zeros((len(units), len(parts)))

    grouped = df.groupby([unit, part])

    for label, group in grouped:
        matrix[indices[label]] = numpy.sum(group[weight_column].values)

    return matrix, indices


def splitting_energy(matrix, function=numpy.log):
    """
    Computes the conditional entropy splitting energy for the given
    :matrix:, whose ij-th entry is expected to be the intersection
    (in terms of population, area, or whatever the user wants)
    of unit i with part j.
    Uses :function: in place of `log` (default is`numpy.log`).
    """
    total = numpy.sum(matrix)
    unit_totals = numpy.sum(matrix, axis=1)

    def prob_i_and_j(i, j):
        return matrix[i, j] / total

    def prob_j_given_i(i, j):
        if unit_totals[i] == 0:
            return 0
        return matrix[i, j] / unit_totals[i]

    def ijth_term(i, j):
        inside = prob_j_given_i(i, j)
        if inside == 0:
            return 0
        return prob_i_and_j(i, j) * function(inside)

    return - numpy.sum(ijth_term(i, j) for (i, j) in numpy.ndindex(*matrix.shape))


def splitting_confidence(matrix):
    """
    Index the units by i and the parts by j.
    The splitting confidence vector is the vector whose ith coordinate is
    the maximum over all j of the probability of being in part j, given
    that you are in unit i. (The maximum over j of prob_j_given_i).
    """
    vector = (numpy.amax(matrix, axis=1) / numpy.sum(matrix, axis=1)).flatten()
    vector[vector == numpy.inf] = 0
    vector = numpy.nan_to_num(vector)
    return vector
