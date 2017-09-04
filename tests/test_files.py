
from hashdex.files import DirectoryScanner

def test_scans_simple_dir(mocker):
    mocked_walk = mocker.patch('os.walk')
    mocked_walk.return_value = [('.', [], ['x.txt'])]

    files = DirectoryScanner('.').get_files()
    assert files[0].filename == 'x.txt'
