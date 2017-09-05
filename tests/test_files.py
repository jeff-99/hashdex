from hashdex.files import DirectoryScanner


def test_scans_simple_dir(mocker):
    mocked_walk = mocker.patch('os.walk')
    mocked_walk.return_value = [('.', [], ['x.txt'])]

    files = DirectoryScanner('.').get_files()
    assert files[0].filename == 'x.txt'


def walk_return_values(dir):
    if dir == '.':
        return [('.', ["dir"], [])]
    else:
        return [('dir', [], ['x.txt'])]

def test_recursive_dir(mocker):
    mocked_walk = mocker.patch('os.walk')
    mocked_walk.side_effect = walk_return_values

    files = DirectoryScanner('.').get_files()
    assert files[0].filename == 'x.txt'
