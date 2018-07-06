import io
import zipfile

import requests


def download_and_unzip(url, target):
    response = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(target)
