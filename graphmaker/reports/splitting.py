import numpy
from graphmaker.constants import fips_to_state_name
from graphmaker.reports.graph_report import serializable_histogram
from graphmaker.resources import BlockAssignmentFile, BlockPopulationShapefile


def splitting_report(fips, unit, part):
    df = load_matching_dataframe(fips, unit, part)
    matrix, indices = splitting_matrix(df, unit, part, 'population')

    information_distance = float(entropy(matrix))

    splitting_confidence_vector = splitting_confidence(
        matrix, indices).flat.tolist()
    unit_indices = {u: i for (u, p), (i, j) in indices.items()}
    confidences = {
        u: splitting_confidence_vector[i] for u, i in unit_indices.items()}

    hist = serializable_histogram(splitting_confidence_vector)

    return {'fips': fips, 'state': fips_to_state_name[fips],
            'unit': unit, 'partitioned_by': part,
            'information_distance': information_distance,
            'splitting_confidences': confidences,
            'splitting_confidence_histogram': hist}


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
    print(grouped.groups)

    for label, group in grouped:
        matrix[indices[label]] = numpy.sum(group[weight_column].values)

    return matrix, indices


def entropy(matrix):
    total = numpy.sum(matrix)
    unit_totals = numpy.sum(matrix, axis=1)

    def prob_i_and_j(i, j):
        return matrix[i, j] / total

    def prob_j_given_i(i, j):
        return matrix[i, j] / unit_totals[i]

    def ijth_term(i, j):
        inside_log = prob_j_given_i(i, j)
        if inside_log == 0:
            return 0
        return prob_i_and_j(i, j) * numpy.log(inside_log)

    return - numpy.sum(ijth_term(i, j) for (i, j) in numpy.ndindex(*matrix.shape))


def splitting_confidence(matrix):
    """
    Index the units by i and the parts by j.
    The splitting confidence vector is the vector whose ith coordinate is
    the maximum over all j of the probability of being in part j, given
    that you are in unit i. (The maximum over j of prob_j_given_i).
    """
    return numpy.amax(matrix, axis=1) / numpy.sum(matrix, axis=1)
