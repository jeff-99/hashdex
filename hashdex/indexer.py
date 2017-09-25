import math
import os
import sqlite3
import filecmp
from hashlib import sha1, md5

from hashdex.files import DuplicateFileResult
from .files import File


def create_connection(db):
    if db == ':memory:':
        connection_string = db
    else:
        connection_string = os.path.expanduser(db)
        dirname = os.path.dirname(connection_string)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    return sqlite3.connect(connection_string)


class Hasher(object):

    BYTE_COUNT = int(10e5)  # 1MB

    def get_hashes(self, file):
        filesize = os.stat(file.full_path).st_size
        with open(file.full_path, 'rb') as f:
            content = b""
            if filesize < self.BYTE_COUNT:
                content += f.read(filesize)
            else:
                part_count = int(math.floor(self.BYTE_COUNT / 2))
                content += f.read(part_count)

                f.seek(part_count, os.SEEK_END)
                content += f.read(part_count)

            sha_hash = sha1(content).hexdigest()
            md5_hash = md5(content).hexdigest()

        return (sha_hash, md5_hash)


class Indexer(object):
    def __init__(self, connection, hasher):
        self.connection = connection
        self.hasher = hasher

    def build_db(self, ):
        self.connection.execute("""
            CREATE TABLE hashes (
                hash_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sha1_hash TEXT,
                md5_hash TEXT
            )
        """)
        self.connection.execute("CREATE UNIQUE INDEX idx_hashes ON hashes ( sha1_hash , md5_hash )")
        self.connection.execute("""
            CREATE TABLE files (
                hash_id INTEGER,
                full_path TEXT,
                filename TEXT,
                FOREIGN KEY(hash_id) REFERENCES hashes(hash_id)
            )
        """)
        self.connection.execute("CREATE UNIQUE INDEX idx_paths ON files ( full_path )")

    def _check_index(self, sha1_hash, md5_hash):
        return self.connection.execute("SELECT hash_id FROM hashes WHERE sha1_hash = ? AND md5_hash = ? ",
                                       [sha1_hash, md5_hash]).fetchone()

    def add_file(self, file):
        sha_hash, md5_hash = self.hasher.get_hashes(file)

        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO hashes (sha1_hash, md5_hash) VALUES (?,?)", (sha_hash, md5_hash))
            hash_id = self._check_index(sha_hash, md5_hash)[0]
            cursor.execute(
                "INSERT OR IGNORE INTO files (hash_id, full_path, filename) VALUES (?,?,?)",
                (hash_id, file.full_path, file.filename)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)
            self.connection.rollback()

    def in_index(self, file):
        sha_hash, md5_hash = self.hasher.get_hashes(file)
        return self._check_index(sha_hash, md5_hash) is not None

    def fetch_indexed_file(self, file):
        sha_hash, md5_hash = self.hasher.get_hashes(file)
        data = self.connection.cursor().execute("""
            SELECT full_path, filename
            FROM files f
            JOIN hashes h ON h.hash_id = f.hash_id
            WHERE h.sha1_hash = ? AND h.md5_hash = ?
        """, (sha_hash, md5_hash)).fetchone()
        if data is None:
            return None
        return File(data[0], data[1])

    def get_index_count(self):
        return self.connection.cursor().execute("SELECT COUNT(*) FROM hashes").fetchone()[0]

    def get_duplicates(self):
        cursor = self.connection.cursor()

        dupes = cursor.execute("""
            SELECT GROUP_CONCAT(full_path , '|') FROM files f
            JOIN hashes h ON h.hash_id = f.hash_id
            GROUP BY h.hash_id
            HAVING COUNT(h.hash_id) > 1
        """).fetchall()
        for (dupe,) in dupes:
            real_dupes = dupe.split("|")

            result = DuplicateFileResult()

            first = real_dupes[0]
            result.add_duplicate(first)
            for next in real_dupes[1:]:
                same = filecmp.cmp(first, next)
                if not same:
                    result.add_diff(next)
                else:
                    result.add_duplicate(next)

            yield result

    def get_files(self):
        cursor = self.connection.cursor()
        cursor = cursor.execute("SELECT full_path, filename FROM files")

        while True:
            results = cursor.fetchmany(1000)
            if results is None:
                break

            for result in results:
                yield File(result[0], result[1])

    def delete(self, file):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM files WHERE full_path = ?", (file.full_path, ))
            cursor.execute("""
                DELETE FROM hashes WHERE hash_id IN (
                    SELECT hash_id
                    FROM hashes h
                    LEFT JOIN files f ON h.hash_id = f.hash_id
                    WHERE f.full_path IS NONE
                )
            """)
            return True
        except sqlite3.Error:
            return False
