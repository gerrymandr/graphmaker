import logging
import os
import pathlib

import geopandas as gp
import pandas

from .constants import (block_assignment_path, block_population_path,
                        fips_to_state_abbreviation, tiger_data_path,
                        valid_fips_codes)
from .utils import download_and_unzip

log = logging.getLogger(__name__)


class ZippedCensusResource:
    base_path = ''

    def __init__(self, fips):
        self.fips = fips

    def download(self, *args, **kwargs):
        download_and_unzip(self.url(*args, **kwargs),
                           self.target_folder(*args, **kwargs))

    def target_folder(self):
        return os.path.join(self.base_path, self.fips)

    @classmethod
    def download_all(cls, iterable=valid_fips_codes(), **kwargs):
        pathlib.Path(cls.base_path).mkdir(parents=True, exist_ok=True)

        for fips in iterable:
            log.info(f"Downloading {cls.__name__} for {fips}")
            try:
                cls(fips).download(**kwargs)
            except Exception:
                log.error(
                    f"An error occurred for FIPS code {fips}", exc_info=True)


class CensusShapefileResource(ZippedCensusResource):
    base_url = ''

    def as_df(self):
        return gp.read_file(self.path())

    def path(self):
        return os.path.join(self.target_folder(self.fips), self.file_stem() + '.shp')

    def url(self):
        return self.base_url + self.file_stem() + '.zip'


class BlockPopulationShapefile(CensusShapefileResource):
    base_path = block_population_path
    base_url = "http://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/"

    def file_stem(self):
        return 'tabblock2010_' + self.fips + '_pophu'


class VTDShapefile(CensusShapefileResource):
    base_path = tiger_data_path

    def url(fips, year='2012'):
        base = "https://www2.census.gov/geo/tiger/TIGER"
        return base + year + "/VTD/tl_" + year + "_" + fips + "_vtd10.zip"

    def path(self, year='2012'):
        shapefile_name = "tl_" + year + "_" + self.fips + "_vtd10.shp"
        return os.path.join(self.target_folder(self.fips), shapefile_name)


class BlockAssignmentFile(ZippedCensusResource):
    base_path = block_assignment_path

    def url(self):
        abbrev = fips_to_state_abbreviation[self.fips]
        return "http://www2.census.gov/geo/docs/maps-data/data/baf/" \
            f"BlockAssign_ST{self.fips}_{abbrev}.zip"

    def path(self, unit='VTD'):
        """The units are all-caps: 'VTD' or 'CD'"""
        fips = self.fips
        abbrev = fips_to_state_abbreviation[fips]
        return os.path.join(self.base_path, fips,
                            f"BlockAssign_ST{fips}_{abbrev}_{unit}.txt")

    def as_df(self, unit='VTD'):
        df = pandas.read_csv(self.path(unit), dtype=str)
        if unit == 'VTD':
            df['VTD'] = self.fips + df['COUNTYFP'] + df['DISTRICT']
        return df
