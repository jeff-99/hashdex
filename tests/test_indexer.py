import sqlite3
from hashdex.indexer import Indexer, create_connection
from hashdex.files import File


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
