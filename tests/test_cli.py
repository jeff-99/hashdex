#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hashdex` package."""

import os

from click.testing import CliRunner
from hashdex.cli import cli
from hashdex.files import File


def test_indexing():
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir("output")
        os.mkdir("input")
        with open('./input/x.txt', 'w') as f:
            f.write("a"*10000)

        result = runner.invoke(cli, ['index', '--dir', './input', '--index', 'output/index.db'])

        print(result)

        assert 'Successfully Indexed 1 files' in result.output


def test_duplicates(mocker):
    runner = CliRunner()

    i = mocker.MagicMock()
    i.get_duplicates.return_value = ["x", "y"]

    mocked_indexer = mocker.patch('hashdex.cli.Indexer')
    mocked_indexer.return_value = i

    result = runner.invoke(cli, ['duplicates'])

    assert 'x' in result.output
    assert 'y' in result.output


def test_check(mocker):
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

        result = runner.invoke(cli, ['check', '--dir', './input'])

        assert f.full_path in result.output
