import os

from constants import tiger_data_path
from utils import download_and_unzip


def zfill2(x):
    return str(x).zfill(2)


fips_codes = ['01', '02', '04', '05', '06'] + list(map(zfill2, range(8, 57)))


def state_zip_url(fips, year='2012'):
    base = "https://www2.census.gov/geo/tiger/TIGER"
    return base + year + "/VTD/tl_" + year + "_" + fips + "_vtd10.zip"


def target_folder(fips):
    return os.path.join(tiger_data_path, fips)


def shp_location(fips, year='2012'):
    return os.path.join(target_folder(fips), "tl_" + year + "_" + fips + "_vtd10.shp")


def download_state_vtds(fips):
    download_and_unzip(state_zip_url(fips), target_folder(fips))


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
