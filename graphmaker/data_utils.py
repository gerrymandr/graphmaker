

def serialize_histogram(hist):
    counts, bin_endpoints = hist
    bins = list()
    for left, right in zip(bin_endpoints[:-1], bin_endpoints[1:]):
        bins.append([round(left, 6), round(right, 6)])
    return {'bins': bins, 'counts': list(counts)}
