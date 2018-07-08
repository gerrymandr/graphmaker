import io
import logging
import uuid
import zipfile

import requests

log = logging.getLogger(__name__)


def download_and_unzip(url, target):
    response = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(target)


def infer_id_column(dataframe, patterns=None, id_column=None):
    if not patterns:
        patterns = ['geoid', 'id']

    if id_column:
        log.info('The user specified the id_column.')
        return id_column

    for i, pattern in enumerate(patterns):
        candidate = find_column_with(dataframe.columns, pattern)
        if candidate:
            log.info(f"Inferred the id_column by the presence of '{pattern}'"
                     "(#{i} choice).")
            return candidate

    raise ValueError('No id_column was specified, and I was unable to find '
                     'a plausible id_column in the dataframe.')


def find_column_with(columns, pattern):
    candidates = [col for col in columns if pattern in col.strip().lower()]
    if len(candidates) == 1:
        return candidates[0]
    else:
        return None


def generate_id():
    return str(uuid.uuid4())[:8]
