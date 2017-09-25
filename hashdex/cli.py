import os
import click
from .files import DirectoryScanner
from .indexer import Indexer, Hasher, create_connection

DEFAULT_INDEX_LOCATION = '~/.config/hashdex/index.db'


@click.command()
@click.argument('directory', default='.', type=click.Path(exists=True))
@click.option('--index', default=DEFAULT_INDEX_LOCATION, help="index file")
def add(directory, index):
    scanner = DirectoryScanner(directory)

    build_db = not os.path.exists(index)
    indexer = Indexer(create_connection(index), Hasher())
    if build_db:
        indexer.build_db()

    real_files = scanner.get_files()
    with click.progressbar(
            iterable=real_files,
            label="Indexing files...",
            show_percent=True,
            show_pos=True,
            item_show_func=lambda x: x.full_path[-100:] if x is not None else ''
    ) as files:
        for file in files:
            indexer.add_file(file)

    click.echo("Successfully Indexed {0} files".format(len(real_files)))
    click.echo("A total of {0} files are indexed".format(indexer.get_index_count()))


@click.command()
@click.argument('directory', default='.', type=click.Path(exists=True))
@click.option('--index', default=DEFAULT_INDEX_LOCATION, help="index to check against")
@click.option('--rm', default=False, help="delete duplicate files", is_flag=True)
def check(directory, index, rm):

    scanner = DirectoryScanner(directory)
    indexer = Indexer(create_connection(index), Hasher())

    files = scanner.get_files()
    click.echo("{0} files to check".format(len(files)))

    deleted = 0
    for file in files:
        original = indexer.fetch_indexed_file(file)
        if original is not None:
            if rm:
                click.echo('deleting {0} - original file located at {1}'.format(file.full_path, original.full_path))
                os.unlink(file.full_path)
            else:
                click.echo('duplicate file found {0} - original file located at {1}'.format(
                    file.full_path, original.full_path))
            deleted += 1

    click.echo("{0} files of {1} files deleted !".format(deleted, len(files)))


@click.command()
@click.option('--index', default=DEFAULT_INDEX_LOCATION, help="index to check against")
def duplicates(index):
    indexer = Indexer(create_connection(index), Hasher())
    for dupe_result in indexer.get_duplicates():
        click.echo("*" * 150)
        dupes = dupe_result.get_files()

        msg = "\n"
        if not dupe_result.is_equal():
            msg = "BELOW FILES ARE NOT EQUAL !! \n"

        total_dupes = len(dupes)
        for i in range(total_dupes):
            msg += "{0} \n".format(dupes[i])

        click.echo(msg)

    click.echo("*" * 150)


@click.command()
@click.option('--index', default=DEFAULT_INDEX_LOCATION, help="index to check against")
def cleanup(index):
    indexer = Indexer(create_connection(index), Hasher())

    for file in indexer.get_files():
        if not os.path.exists(file.full_path):
            indexer.delete(file)
            click.echo("Deleted {0}".format(file.full_path))


cli = click.Group()
cli.add_command(add)
cli.add_command(check)
cli.add_command(duplicates)
cli.add_command(cleanup)

if __name__ == '__main__':  # pragma: no cover
    cli()
