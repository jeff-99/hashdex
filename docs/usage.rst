=====
Usage
=====

Hashdex is a command-line utility for quickly checking your files for duplicates

Create an Hashdex
-----------------

To initialize an hashdex you need to add some files/directories to the index..

.. highlight:: sh
.. code-block:: bash

    # directory
    hashdex add /path/to/directory

    # file
    hashdex add /path/to/file.txt


This will create an index file in the users home folder (**~/.config/hashdex/index.db**)
If you want to create an index in another location you can specify the **--index** option to the command

.. code-block:: bash

    hashdex add --index /path/to/index.db /path/to/directory

Once you have added all the necessary directories to the index we can begin checking directories against the index.
To check all files in a directory against the index execute the following

Check new files against index
-----------------------------

.. code-block:: bash

    # directory
    hashdex check --index /path/to/index.db /path/to/directory/to/check

    # file
    hashdex check /path/to/file.txt

This will list all files in the given directory which are already indexed with the indexed file path.
You can add the **--rm** flag to delete all files in the given directory which are found in the index, so you will be
left with only new files. In addition to the **--rm** flag you can also pass an **--mv** option with an existing path
to move duplicate files to the given directory.

.. code-block:: bash

    # remove duplicates
    hashdex check --rm /path/to/directory/to/check

    # move duplicates
    hashdex check --mv ./duplicates /path/to/directory/to/check

Find duplicate files
--------------------

To get a list of all duplicate files within already indexed files you can execute::

    hashdex duplicates --index /path/to/index.db


Cleanup the index
-----------------

Overtime files will be deleted from your system or moved to another location. So once in a while you should clean up
the index with the following command::

    hashdex cleanup --index /path/to/index.db

