import logging
import os
import pathlib

import geopandas as gp
import pandas

from .constants import (block_assignment_path, block_population_path,
                        fips_to_state_abbreviation, tiger_data_path,
                        valid_fips_codes)
from .utils import download_and_unzip, resolve_fips

log = logging.getLogger(__name__)


class Resource:
    def __init__(self, url):
        self.url = url

    def download(self, target=None):
        if not target:
            raise ValueError(
                'Please specific a target folder for your download.')
        download_and_unzip(self.url, target)


class ResourceType:
    def __init__(self, tiger, url, res_type):
        self.tiger = tiger
        self.url = url
        self.res_type = res_type

    def _get(self, fips_or_state):
        fips = resolve_fips(fips_or_state)
        return Resource(url=f"{self.url}tl_{self.tiger.year}_{fips}_{self.res_type.lower()}.zip")

    def __getattr__(self, *args, **kwargs):
        return self._get(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self._get(*args, **kwargs)


class Tiger:
    def __init__(self, year):
        self.year = year
        self.url = f"https://www2.census.gov/geo/tiger/TIGER{year}/"

    def __getattr__(self, res):
        return ResourceType(tiger=self, url=f"{self.url}{res.upper()}/", res_type=res)


class ZippedCensusResource:
    base_path = ''

    def __init__(self, fips, download=False):
        self.fips = fips
        if download and not os.path.exists(self.path()):
            self.download()

    def download(self, target=None, *args, **kwargs):
        if target:
            self._target = target
            target = self.target_folder(*args, **kwargs)
        download_and_unzip(self.url(*args, **kwargs), target)

    def target_folder(self):
        return os.path.join(self.base_path, self.fips)

    def url(self):
        raise NotImplementedError('ZippedCensusResources must implement url')

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

    def file_stem(self):
        raise NotImplementedError('CensusShapefileResources must specify their '
                                  'file_stem.')

    def as_df(self):
        return gp.read_file(self.path())

    def path(self):
        return os.path.join(self.target_folder(), self.file_stem() + '.shp')

    def url(self):
        return self.base_url + self.file_stem() + '.zip'


class BlockPopulationShapefile(CensusShapefileResource):
    base_path = block_population_path
    base_url = "http://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/"

    def file_stem(self):
        return 'tabblock2010_' + self.fips + '_pophu'

    def as_df(self):
        df = super().as_df()
        return df.set_index('BLOCKID10')


class VTDShapefile(CensusShapefileResource):
    base_path = tiger_data_path

    def url(self, year='2012'):
        base = "https://www2.census.gov/geo/tiger/TIGER"
        return base + year + "/VTD/tl_" + year + "_" + self.fips + "_vtd10.zip"

    def path(self, year='2012'):
        shapefile_name = "tl_" + year + "_" + self.fips + "_vtd10.shp"
        return os.path.join(self.target_folder(), shapefile_name)


class CensusTractShapefile(CensusShapefileResource):
    base_path = tiger_data_path

    def url(self, year='2012'):
        base = "https://www2.census.gov/geo/tiger/TIGER"
        return base + year + "/VTD/tl_" + year + "_" + self.fips + "_tract10.zip"

    def path(self, year='2012'):
        shapefile_name = "tl_" + year + "_" + self.fips + "_tract10.shp"
        return os.path.join(self.target_folder(), shapefile_name)


class BlockAssignmentFile(ZippedCensusResource):
    _base_path = block_assignment_path

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
