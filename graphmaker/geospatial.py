from collections import Counter

import utm


def utm_of_point(point):
    print(point.y, point.x)
    return utm.from_latlon(point.y, point.x)[2]


def identify_utm_zone(df):
    utms = map(utm_of_point, df['geometry'].centroid)
    utm_counts = Counter(utms)
    # most_common returns a list of tuples, and we want the 0,0th entry
    most_common = utm_counts.most_common(1)[0][0]
    return most_common


def reprojected(df):
    utm = identify_utm_zone(df)
    return df.to_crs(f"+proj=utm +zone={utm} +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
