import sqlite3
from hashlib import sha1, md5

from .files import File


def create_connection(db):
    return sqlite3.connect(db)


class Hasher(object):
    def get_hashes(self, file):
        with open(file.full_path, 'rb') as f:
            content = f.read(10000)
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
            yield real_dupes
