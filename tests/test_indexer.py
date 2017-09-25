import sqlite3
import six
import os
from tempfile import gettempdir
from hashlib import sha1, md5
from hashdex.files import File, DuplicateFileResult
from hashdex.indexer import Indexer, Hasher, create_connection


class DummyStatResult(object):
    def __init__(self, st_size):
        self.st_size = st_size


def test_create_connection():
    assert isinstance(create_connection(":memory:"), sqlite3.Connection)


def test_create_path_for_connection(mocker):
    patched_os_exists = mocker.patch("os.path.exists")
    patched_os_exists.return_value = False

    mocker.patch("os.makedirs")
    mocker.patch("sqlite3.connect").return_value = "dummy return value"

    connection = os.path.join(gettempdir(), "non/existing/dirs/index.db")
    assert create_connection(connection) == "dummy return value"


class TestIndexer:

    def test_indexer_can_add_file(self, mocker):
        connection = mocker.Mock()

        c1 = mocker.Mock()
        connection.execute.return_value = c1
        c1.fetchone.return_value = (1,)

        cursor = mocker.MagicMock()
        connection.cursor.return_value = cursor

        hasher = mocker.Mock()
        hasher.get_hashes.return_value = ("hash1", "hash2")

        indexer = Indexer(connection, hasher)
        f = File('~/test.txt', 'test.txt')

        indexer.add_file(f)

        cursor.execute.assert_has_calls([
            mocker.call("INSERT OR IGNORE INTO hashes (sha1_hash, md5_hash) VALUES (?,?)", ("hash1", "hash2")),
            mocker.call("INSERT OR IGNORE INTO files (hash_id, full_path, filename) VALUES (?,?,?)",
                        (1, '~/test.txt', 'test.txt')),
        ])

        assert connection.commit.called is True

    def test_logging_of_db_exception_on_file_add(self, mocker):
        connection = mocker.Mock()
        connection.execute.return_value = mocker.Mock()

        cursor = mocker.MagicMock()
        cursor.execute.side_effect = sqlite3.Error()
        connection.cursor.return_value = cursor

        hasher = mocker.Mock()
        hasher.get_hashes.return_value = ("hash1", "hash2")

        indexer = Indexer(connection, hasher)
        f = File('~/test.txt', 'test.txt')

        indexer.add_file(f)

        assert connection.rollback.called is True

    def test_in_index(self, mocker):
        connection = mocker.Mock()
        connection.execute.return_value.fetchone.return_value = ("x",)

        hasher = mocker.Mock()
        hasher.get_hashes.return_value = ("hash1", "hash2")

        f = File("x", "y")
        indexer = Indexer(connection, hasher)

        assert indexer.in_index(f) is True

    def test_fetch_indexed_file(self, mocker):
        connection = mocker.MagicMock()
        connection.cursor.return_value.execute.return_value.fetchone.return_value = ("x", "y")

        hasher = mocker.Mock()
        hasher.get_hashes.return_value = ("hash1", "hash2")

        f = File("x", "y")
        indexer = Indexer(connection, hasher)

        assert indexer.fetch_indexed_file(f).filename == f.filename

    def test_fetch_non_existing_file(self, mocker):
        connection = mocker.MagicMock()
        connection.cursor.return_value.execute.return_value.fetchone.return_value = None

        hasher = mocker.Mock()
        hasher.get_hashes.return_value = ("hash1", "hash2")

        f = File("x", "y")
        indexer = Indexer(connection, hasher)

        assert indexer.fetch_indexed_file(f) is None

    def test_get_index_count(self, mocker):
        connection = mocker.MagicMock()
        connection.cursor.return_value.execute.return_value.fetchone.return_value = (10,)

        indexer = Indexer(connection, mocker.Mock())
        assert indexer.get_index_count() == 10

    def test_get_duplicates(self, mocker):
        connection = mocker.MagicMock()
        connection\
            .cursor.return_value \
            .execute.return_value \
            .fetchall.return_value = [("path1|path2",), (("path3|path4|path5",))]

        mocker.patch("filecmp.cmp").return_value = True

        r1 = DuplicateFileResult()
        r1.add_duplicate("path1")
        r1.add_duplicate("path2")

        r2 = DuplicateFileResult()
        r2.add_duplicate("path3")
        r2.add_duplicate("path4")
        r2.add_duplicate("path5")

        indexer = Indexer(connection, mocker.Mock())
        assert list(indexer.get_duplicates()) == [r1, r2]

    def test_get_duplicates_with_one_file_diff(self, mocker):
        connection = mocker.MagicMock()
        connection \
            .cursor.return_value \
            .execute.return_value \
            .fetchall.return_value = [("path1|path2",), (("path3|path4|path5",))]

        mocker.patch("filecmp.cmp").side_effect = [False, True, True, True]

        r1 = DuplicateFileResult()
        r1.add_duplicate("path1")
        r1.add_diff("path2")

        r2 = DuplicateFileResult()
        r2.add_duplicate("path3")
        r2.add_duplicate("path4")
        r2.add_duplicate("path5")

        indexer = Indexer(connection, mocker.Mock())
        assert list(indexer.get_duplicates()) == [r1, r2]

    def test_build_db(self, mocker):
        connection = mocker.MagicMock()

        indexer = Indexer(connection, mocker.Mock())
        indexer.build_db()
        assert connection.execute.call_count == 4

    def test_db_schema_after_build(self, mocker):
        connection = create_connection(":memory:")

        indexer = Indexer(connection, mocker.Mock())
        indexer.build_db()

        tables = map(
            lambda x: x[0],
            connection.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'").fetchall())

        assert set(tables).issubset(["hashes", "files", "sqlite_sequence"])

    def test_get_files(self, mocker):
        connection = mocker.MagicMock()
        connection \
            .cursor.return_value \
            .execute.return_value \
            .fetchmany.side_effect = [
                [("/full/path.log", "path.log"), ("/full/path2.log", "path2.log")],
                None
            ]

        indexer = Indexer(connection, mocker.Mock())
        assert list(indexer.get_files()) == [File("/full/path.log", "path.log"), ("/full/path2.log", "path2.log")]

    def test_delete_file_from_index(self, mocker):
        connection = mocker.MagicMock()

        indexer = Indexer(connection, mocker.Mock())
        assert indexer.delete(File("/full/path.log", "path.log")) is True

    def test_delete_file_fails(self, mocker):
        connection = mocker.MagicMock()
        connection \
            .cursor.return_value \
            .execute.side_effect = sqlite3.Error()

        indexer = Indexer(connection, mocker.Mock())
        assert indexer.delete(File("/full/path.log", "path.log")) is False


class TestHasher:
    def test_hasher_hashes_file_content(self, mocker):
        if six.PY3:
            mocked_open = mocker.patch("builtins.open")
        else:
            mocked_open = mocker.patch("__builtin__.open")

        file_mock = mocker.MagicMock()
        mocked_open.return_value = file_mock

        mocked_stat = mocker.patch("os.stat")

        mocked_stat.return_value = DummyStatResult(Hasher.BYTE_COUNT - 1)

        file_mock.__enter__.return_value = file_mock
        file_mock.read.return_value = b"content"

        f = File('~/test.txt', 'test.txt')
        hasher = Hasher()
        hashes = hasher.get_hashes(f)

        assert hashes == (sha1(b"content").hexdigest(), md5(b"content").hexdigest())

    def test_hashes_parts_of_big_files(self, mocker):
        if six.PY3:
            mocked_open = mocker.patch("builtins.open")
        else:
            mocked_open = mocker.patch("__builtin__.open")

        file_mock = mocker.MagicMock()
        mocked_open.return_value = file_mock

        mocked_stat = mocker.patch("os.stat")

        hasher = Hasher()

        hasher.BYTE_COUNT = 6
        mocked_stat.return_value = DummyStatResult(hasher.BYTE_COUNT + 1)

        # mock a file with "abcdefg" as content
        file_mock.__enter__.return_value = file_mock
        file_mock.read.side_effect = [b"abc", b"efg"]

        f = File('~/test.txt', 'test.txt')
        hashes = hasher.get_hashes(f)

        assert hashes == (sha1(b"abcefg").hexdigest(), md5(b"abcefg").hexdigest())
