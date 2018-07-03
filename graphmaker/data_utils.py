

def serialize_histogram(hist):
    counts, bin_endpoints = hist
    counts = list(map(int, counts))
    bins = list()
    for left, right in zip(bin_endpoints[:-1], bin_endpoints[1:]):
        bins.append([round(float(left), 6), round(float(right), 6)])
    return {'bins': bins, 'counts': counts}
