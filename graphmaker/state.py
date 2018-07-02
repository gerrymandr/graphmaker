import collections

State = collections.namedtuple('State', 'name fips ftp_location')


def is_state(folder_name):
    if not folder_name[:2].isdigit():
        return False
    fips = int(folder_name[:2])
    return '.zip' not in folder_name and fips <= 56


def state_from_folder_name(folder, workdir):
    words = folder.split('_')
    name = ' '.join(words[1:])
    fips = words[0]
    ftp_location = workdir + '/' + folder
    return State(name=name, fips=fips, ftp_location=ftp_location)
