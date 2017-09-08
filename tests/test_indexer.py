import sqlite3
import six
from hashlib import sha1, md5
from hashdex.files import File
from hashdex.indexer import Indexer, Hasher, create_connection


def test_create_connection():
    assert isinstance(create_connection(":memory:"), sqlite3.Connection)


def test_indexer_can_add_file(mocker):
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


def test_logging_of_db_exception_on_file_add(mocker):
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


def test_in_index(mocker):
    connection = mocker.Mock()
    connection.execute.return_value.fetchone.return_value = ("x",)

    hasher = mocker.Mock()
    hasher.get_hashes.return_value = ("hash1", "hash2")

    f = File("x", "y")
    indexer = Indexer(connection, hasher)

    assert indexer.in_index(f) is True


def test_fetch_indexed_file(mocker):
    connection = mocker.MagicMock()
    connection.cursor.return_value.execute.return_value.fetchone.return_value = ("x", "y")

    hasher = mocker.Mock()
    hasher.get_hashes.return_value = ("hash1", "hash2")

    f = File("x", "y")
    indexer = Indexer(connection, hasher)

    assert indexer.fetch_indexed_file(f).filename == f.filename


def test_fetch_non_existing_file(mocker):
    connection = mocker.MagicMock()
    connection.cursor.return_value.execute.return_value.fetchone.return_value = None

    hasher = mocker.Mock()
    hasher.get_hashes.return_value = ("hash1", "hash2")

    f = File("x", "y")
    indexer = Indexer(connection, hasher)

    assert indexer.fetch_indexed_file(f) is None


def test_get_index_count(mocker):
    connection = mocker.MagicMock()
    connection.cursor.return_value.execute.return_value.fetchone.return_value = (10,)

    indexer = Indexer(connection, mocker.Mock())
    assert indexer.get_index_count() == 10


def test_get_duplicates(mocker):
    connection = mocker.MagicMock()
    connection\
        .cursor.return_value \
        .execute.return_value \
        .fetchall.return_value = [("path1|path2",), (("path3|path4|path5",))]

    indexer = Indexer(connection, mocker.Mock())
    assert list(indexer.get_duplicates()) == [["path1", "path2"], ["path3", "path4", "path5"]]


def test_build_db(mocker):
    connection = mocker.MagicMock()

    indexer = Indexer(connection, mocker.Mock())
    indexer.build_db()
    assert connection.execute.call_count == 4


def test_db_schema_after_build(mocker):
    connection = create_connection(":memory:")

    indexer = Indexer(connection, mocker.Mock())
    indexer.build_db()

    tables = map(
        lambda x: x[0],
        connection.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'").fetchall())

    assert set(tables).issubset(["hashes", "files", "sqlite_sequence"])


def test_hasher_hashes_file_content(mocker):
    if six.PY3:
        mocked_open = mocker.patch("builtins.open")
    else:
        mocked_open = mocker.patch("__builtin__.open")

    file_mock = mocker.MagicMock()
    mocked_open.return_value = file_mock

    file_mock.__enter__.return_value = file_mock
    file_mock.read.return_value = b"content"

    f = File('~/test.txt', 'test.txt')
    hasher = Hasher()
    hashes = hasher.get_hashes(f)

    assert hashes == (sha1(b"content").hexdigest(), md5(b"content").hexdigest())
