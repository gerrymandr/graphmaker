import io
import zipfile

import requests

from constants import fips_to_state_abbreviation


def baf_url(fips):
    abbrev = fips_to_state_abbreviation[fips]
    return "http://www2.census.gov/geo/docs/maps-data/data/baf/" \
        f"BlockAssign_ST{fips}_{abbrev}.zip"


def target_folder(fips):
    return './block_assignments/' + fips + '/'


def download_baf(fips):
    response = requests.get(baf_url(fips))
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(target_folder(fips))


def main():
    for fips in fips_to_state_abbreviation:
        print(
            f"Downloading block assignment files for {fips_to_state_abbreviation[fips]}")
        download_baf(fips)


if __name__ == '__main__':
    main()
