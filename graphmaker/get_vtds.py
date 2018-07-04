import io
import os
import zipfile

import requests


def zfill2(x):
    return str(x).zfill(2)


fips_codes = ['01', '02', '04', '05', '06'] + list(map(zfill2, range(8, 57)))


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
    for fips in fips_codes:
        if fips + ".json" in os.listdir("./graphs"):
            continue
        try:
            download_state_vtds(fips)
        except Exception:
            print("An error occurred for FIPS code " + fips)


if __name__ == '__main__':
    main()
