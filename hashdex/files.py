import os
from collections import namedtuple

File = namedtuple('File', ['full_path', 'filename'])


class DirectoryScanner(object):
    def __init__(self, basepath):
        self.basepath = basepath

    def _fetch_files(self, dir):
        file_list = []
        for root, subdirs, files in os.walk(dir):
            for file in files:
                file_list.append(File(os.path.join(root, file), file))

        return file_list

    def get_files(self):
        return self._fetch_files(self.basepath)
