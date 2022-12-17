.. _getting_started-installation:

============
Installation
============

Contributor CI can be installed from pypi, or from source. For either, it's
recommended that you create a virtual environment, if you have not already
done so.


Install from Pypi
=================

To install from pypi:

.. code:: console

   $ pip install contributor-ci


Install from GitHub
===================

If you want to install directly from GitHub (perhaps a development release
or a tag) you can clone the repository:

.. code:: console

    $ git clone git@github.com:vsoch/contributor-ci
    # you can also do git clone https://github.com/vsoch/contributor-ci
    $ cd contributor-ci
    $ python setup.py install
    # pip install . or pip install -e . for development

Installation of adds an executable, `cci` to your path.

```bash
$ which cci
/opt/conda/bin/cci
```

See the :ref:`getting-started` pages for next steps.
