import functools
import os
import zipfile

import geopandas as gp
import networkx
import pysal

from ftp import CensusFTP
from rundmcmc.make_graph import construct_graph_from_df
from state import is_state, state_from_folder_name


def get_states(workdir='/geo/pvs/tiger2010st'):
    with CensusFTP(workdir) as ftp:
        state_folders = [folder for folder in ftp.subfolders()
                         if is_state(folder)]
        states = [state_from_folder_name(folder, workdir)
                  for folder in state_folders]
        return states


def filetype(filename):
    return filename.split('.')[-1]


def state_vtd_adjacency_graph(state):
    data_dir = './tmp/census_data/'

    download_vtds_for_state(state, data_dir)
    shapefiles = search_for_shapefiles(data_dir)
    dataframe = collect_shapefiles_in_dataframe(shapefiles)

    assert 'GEOID10' in dataframe.columns

    return construct_graph_from_df(dataframe, geoid_col='GEOID10')


def download_vtds_for_state(state, destination):
    with CensusFTP(state.ftp_location) as ftp:
        print("Connected")
        ftp.cwd('VTDS')
        print("In the VTDS folder")
        files = [file for file in ftp.ls() if filetype(file) == 'zip']
        for filepath in ftp.download_files(files, destination):
            print("Downloading " + filepath)
            unzip_and_delete(
                filepath, target_folder=filepath.replace('.zip', ''))


def unzip_and_delete(path_to_zipped, target_folder):
    with zipfile.ZipFile(path_to_zipped) as zipped_file:
        zipped_file.extractall(path=target_folder)
    os.remove(path_to_zipped)


def search_for_shapefiles(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filetype(filename) == 'shp':
                yield os.path.join(dirpath, filename)


def collect_shapefiles_in_dataframe(files):
    dataframes = map(gp.read_file, files)
    big_dataframe = functools.reduce(
        lambda df, new_df: df.append(new_df), dataframes)
    return big_dataframe

# Replaced these with construct_graph:


def weights_from_dataframe(data, id_column='GEOID10'):
    weights = pysal.weights.Rook.from_dataframe(data, idVariable=id_column)
    return weights


def edges(weights):
    for node, neighbors in weights:
        for neighbor in neighbors:
            yield (node, neighbor)


def adjacency_graph_from_dataframe(data):
    weights = weights_from_dataframe(data)
    graph = networkx.Graph(edges(weights))
    return graph


def main():
    pass


if __name__ == '__main__':
    main()
