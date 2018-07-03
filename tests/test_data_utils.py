import json

import numpy
from graphmaker.data_utils import serializable_histogram


def test_serializable_histogram_returns_serializable():
    data = numpy.random.normal(size=100)
    serialized = json.dumps(serializable_histogram(data))
    assert serialized
