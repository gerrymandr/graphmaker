import ftplib
import os


class CensusFTP:
    def __init__(self, workdir='/'):
        self.workdir = workdir

    def __enter__(self):
        self.ftp = ftplib.FTP('ftp2.census.gov')
        self.ftp.login()
        self.ftp.cwd(self.workdir)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ftp.quit()

    def subfolders(self):
        subfolders = []

        def append_if_folder(line):
            if (line[0] == 'd'):
                subfolders.append(parse_directory_item_name(line))

        self.ftp.dir(append_if_folder)
        return subfolders

    def ls(self):
        directory = []
        self.ftp.dir(lambda x: directory.append(parse_directory_item_name(x)))
        return directory

    def download(self, file, destination):
        local_path = os.path.join(destination, file)
        with open(local_path, 'wb') as f:
            self.ftp.retrbinary('RETR ' + file, f.write)
        return local_path

    def download_files(self, files, destination):
        for file in files:
            yield self.download(file, destination)


def parse_directory_item_name(item):
    return item.split()[-1]
