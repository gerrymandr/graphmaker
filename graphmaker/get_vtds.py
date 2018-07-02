import io
import json
import os
import zipfile

import networkx
import requests

from make_graph import construct_graph_from_file


def zfill2(x):
    return str(x).zfill(2)


fips_codes = ['01', '02'] + list(map(zfill2, range(4, 57)))


def state_zip_url(fips, year='2012'):
    base = "https://www2.census.gov/geo/tiger/TIGER"
    return base + year + "/VTD/tl_" + year + "_" + fips + "_vtd10.zip"


def target_folder(fips):
    return "./tiger_data/" + fips


def shp_location(fips, year='2012'):
    return os.path.join(target_folder(fips), "tl_" + year + "_" + fips + "_vtd10.shp")


def download_state_vtds(fips):
    response = requests.get(state_zip_url(fips))
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(target_folder(fips))


def output_location(fips):
    return "./graphs/" + fips + ".json"


def main():
    for fips in fips_codes[5:]:
        try:
            download_state_vtds(fips)
            graph = construct_graph_from_file(shp_location(
                fips), 'GEOID10', ['ALAND10', 'COUNTYFP10'])
            with open(output_location(fips), "w+") as f:
                json.dump(networkx.json_graph.adjacency_data(graph), f)
        except Exception:
            print("An error occurred for FIPS code " + fips)


if __name__ == '__main__':
    main()
