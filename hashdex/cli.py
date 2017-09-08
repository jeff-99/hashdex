import os
import click
from .files import DirectoryScanner
from .indexer import Indexer, Hasher, create_connection


@click.command()
@click.option('--dir', default=".")
@click.option('--index', default='index.db', help="index file")
def index(dir, index):
    scanner = DirectoryScanner(dir)

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
@click.option('--dir', default='.', help="directory to check against index")
@click.option('--index', default='index.db', help="index to check against")
def check(dir, index):

    scanner = DirectoryScanner(dir)
    indexer = Indexer(create_connection(index), Hasher())

    files = scanner.get_files()
    click.echo("{0} files to check".format(len(files)))

    deleted = 0
    for file in files:
        original = indexer.fetch_indexed_file(file)
        if original is not None:
            click.echo('deleting {0} - original file located at {1}'.format(file.full_path, original.full_path))
            os.unlink(file.full_path)
            deleted += 1

    click.echo("{0} files of {1} files deleted !".format(deleted, len(files)))


@click.command()
@click.option('--index', default='index.db', help="index to check against")
def duplicates(index):
    indexer = Indexer(create_connection(index), Hasher())
    for dupes in indexer.get_duplicates():
        click.echo("*" * 150)
        total_dupes = len(dupes)
        msg = "\n"
        for i in range(total_dupes):
            msg += "{0} \n".format(dupes[i])

        click.echo(msg)

    click.echo("*" * 150)


cli = click.Group()
cli.add_command(index)
cli.add_command(check)
cli.add_command(duplicates)
