=======
Hashdex
=======


.. image:: https://img.shields.io/pypi/v/hashdex.svg
        :target: https://pypi.python.org/pypi/hashdex

.. image:: https://img.shields.io/travis/jeff-99/hashdex.svg
        :target: https://travis-ci.org/jeff-99/hashdex

.. image:: https://readthedocs.org/projects/hashdex/badge/?version=latest
        :target: https://hashdex.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/jeff-99/hashdex/shield.svg
     :target: https://pyup.io/repos/github/jeff-99/hashdex/
     :alt: Updates


A file indexer based on content hashes to quickly find duplicate files on your system.
I created this tool because I always forget which pictures from my phone I already uploaded to my Dropbox account.
Now I can just upload all pictures to an uploads directory check these files against the index and only organize
the remaining files.

As easy as..
------------

.. code-block:: bash

    pip install hashdex
    hashdex add /path/to/my-main-pictures-directory
    hashdex check --rm /path/to/my-uploads-directory


* Free software: MIT license
* Documentation: https://hashdex.readthedocs.io.


Features
--------

* create an index of your files
* find duplicate files on your filesystem
* check if files in a directory are already indexed

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

