import numpy


def serializable_histogram(data):
    counts, bin_endpoints = numpy.histogram(data, bins='auto')
    counts = list(map(int, counts))
    bins = list()
    for left, right in zip(bin_endpoints[:-1], bin_endpoints[1:]):
        bins.append([round(float(left), 6), round(float(right), 6)])
    return {'bins': bins, 'counts': counts}
