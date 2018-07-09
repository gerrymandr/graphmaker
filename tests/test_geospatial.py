import geopandas
from graphmaker.geospatial import identify_utm_zone, reprojected, utm_of_point
from shapely.geometry import Point


def example_point():
    return Point(-83.7, 42.3)


def test_identify_utm_zone():
    point = example_point()
    data = [{'name': 'example point', 'geometry': point}]
    df = geopandas.GeoDataFrame(data, crs="+init=epsg:4326")

    assert identify_utm_zone(df) == 17


def test_reprojected():
    point = example_point()
    data = [{'name': 'example point', 'geometry': point}]
    df = geopandas.GeoDataFrame(data, crs="+init=epsg:4326")

    reprojected_df = reprojected(df)
    reprojected_point = reprojected_df['geometry'][0]

    assert reprojected_point.x != point.x and reprojected_point.y != point.y


def test_utm_of_point():
    point = example_point()
    assert utm_of_point(point) == 17
