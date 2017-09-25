from hashdex.files import DirectoryScanner, DuplicateFileResult


class TestDirectoryScanner():

    def test_scans_simple_dir(self, mocker):
        mocked_walk = mocker.patch('os.walk')
        mocked_walk.return_value = [('.', [], ['x.txt'])]

        files = DirectoryScanner('.').get_files()
        assert files[0].filename == 'x.txt'

    def test_recursive_dir(self, mocker):
        mocked_walk = mocker.patch('os.walk')
        mocked_walk.return_value = iter([('.', ["dir"], []), ('dir', [], ['x.txt'])])

        files = DirectoryScanner('.').get_files()
        assert files[0].filename == 'x.txt'

    def test_path_is_file(self):
        files = DirectoryScanner(__file__).get_files()
        assert len(files) == 1
        assert files[0].full_path == __file__


class TestDuplicateFileResult():
    def test_add_duplicate(self):
        d = DuplicateFileResult()

        d.add_duplicate("x")
        assert d.get_files() == ["x"]

        d.add_duplicate("y")
        assert d.get_files() == ["x", "y"]

    def test_add_diff(self):
        d = DuplicateFileResult()
        d.add_diff("x")
        assert d.get_files() == ["x"]

        d.add_diff("y")
        assert d.get_files() == ["x", "y"]

    def test_is_equal(self):
        d = DuplicateFileResult()
        d.add_duplicate("x")

        assert d.is_equal() is True

    def test_is_not_equal(self):
        d = DuplicateFileResult()
        d.add_diff("x")

        assert d.is_equal() is False

    def test_compare_duplicate_results(self):
        d1 = DuplicateFileResult()
        d1.add_duplicate("x")
        d1.add_diff("y")

        d2 = DuplicateFileResult()
        d2.add_diff("x")
        d2.add_duplicate("y")

        assert d1 != d2

        d3 = DuplicateFileResult()
        d3.add_duplicate("x")
        d3.add_diff("y")

        d4 = DuplicateFileResult()
        d4.add_diff("y")
        d4.add_duplicate("x")

        assert d3 == d4
