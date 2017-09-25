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
        if os.path.isfile(self.basepath):
            real_path = os.path.realpath(os.path.expanduser(self.basepath))
            return [File(real_path, os.path.basename(real_path))]
        return self._fetch_files(self.basepath)


class DuplicateFileResult(object):
    def __init__(self):
        self.dupes = []
        self.diffs = []

    def add_duplicate(self, filepath):
        self.dupes.append(filepath)

    def get_files(self):
        return self.dupes + self.diffs

    def add_diff(self, filepath):
        self.diffs.append(filepath)

    def is_equal(self):
        return len(self.dupes) > 0 and len(self.diffs) == 0

    def __eq__(self, other):
        return set(self.dupes) == set(other.dupes) and \
                set(self.diffs) == set(other.diffs)
