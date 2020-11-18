#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hashdex` package."""

import os
import re

from click.testing import CliRunner
from hashdex.cli import cli
from hashdex.files import File, DuplicateFileResult


def test_main_command_shows_help():
    runner = CliRunner()

    result = runner.invoke(cli)
    assert "Usage" in result.output


def test_version_command():
    runner = CliRunner()

    result = runner.invoke(cli, ['-v'])
    pattern = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+')

    assert pattern.match(result.output)


def test_adding_to_index():
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir("output")
        os.mkdir("input")
        with open('./input/x.txt', 'w') as f:
            f.write("a"*10000)

        result = runner.invoke(cli, ['add', './input', '--index', 'output/index.db'])

        assert 'Successfully Indexed 1 files' in result.output


def test_duplicates(mocker):
    runner = CliRunner()

    r1 = DuplicateFileResult()
    r1.add_duplicate("x")
    r1.add_duplicate("y")
    r1.add_diff("z")

    i = mocker.MagicMock()
    i.get_duplicates.return_value = [r1]

    mocked_indexer = mocker.patch('hashdex.cli.Indexer')
    mocked_indexer.return_value = i

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['duplicates', '--index', './index.db'])

    assert 'x' in result.output
    assert 'y' in result.output
    assert 'NOT EQUAL' in result.output


def test_duplicates_with_non_equal_duplicates(mocker):
    runner = CliRunner()

    r1 = DuplicateFileResult()
    r1.add_diff("x")

    i = mocker.MagicMock()
    i.get_duplicates.return_value = [r1]

    mocked_indexer = mocker.patch('hashdex.cli.Indexer')
    mocked_indexer.return_value = i

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['duplicates', '--index', './index.db'])

    assert 'x' in result.output
    assert 'NOT EQUAL' in result.output


def test_check_without_rm(mocker):
    f = File("./x.txt", 'x.txt')
    i = mocker.MagicMock()
    i.fetch_indexed_file.return_value = f

    mocked_indexer = mocker.patch('hashdex.cli.Indexer')
    mocked_indexer.return_value = i

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir("output")
        os.mkdir("input")
        with open('./input/x.txt', 'w') as df:
            df.write("a" * 10000)

        result = runner.invoke(cli, ['check', './input', '--index', './index.db'])

        assert os.path.exists('./input/x.txt') is True
        assert f.full_path in result.output


def test_check_with_rm(mocker):
    f = File("./x.txt", 'x.txt')
    i = mocker.MagicMock()
    i.fetch_indexed_file.return_value = f

    mocked_indexer = mocker.patch('hashdex.cli.Indexer')
    mocked_indexer.return_value = i

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir("output")
        os.mkdir("input")
        with open('./input/x.txt', 'w') as df:
            df.write("a" * 10000)

        result = runner.invoke(cli, ['check', '--rm', '--index', './index.db', './input'])

        assert os.path.exists('./input/x.txt') is False
        assert f.full_path in result.output


def test_move_duplicate_files_on_check(mocker):
    f = File("./x.txt", 'x.txt')
    i = mocker.MagicMock()
    i.fetch_indexed_file.return_value = f

    mocked_indexer = mocker.patch('hashdex.cli.Indexer')
    mocked_indexer.return_value = i

    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir("output")
        os.mkdir("input")
        with open('./input/x.txt', 'w') as df:
            df.write("a" * 10000)

        result = runner.invoke(cli, ['check', '--mv', './output/', '--index', './index.db', './input'])

        assert os.path.exists('./input/x.txt') is False
        assert os.path.exists('./output/x.txt') is True
        assert f.full_path in result.output


def test_cleanup_old_files(mocker):
    runner = CliRunner()

    i = mocker.MagicMock()
    i.get_files.return_value = [
        File("./existing.txt", "existing.txt"),
        File("./non-existing.txt", "non-existing.txt")
    ]

    mocked_indexer = mocker.patch('hashdex.cli.Indexer')
    mocked_indexer.return_value = i

    with runner.isolated_filesystem():
        with open('./existing.txt', 'w') as df:
            df.write("a" * 10000)

        result = runner.invoke(cli, ['cleanup', '--index', './index.db'])

    assert 'Deleted ./non-existing.txt' in result.output
