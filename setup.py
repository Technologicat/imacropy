# -*- coding: utf-8 -*-
"""setuptools-based setup.py for imacropy.

Tested on Python 3.6.

Usage as usual with setuptools:
    python3 setup.py build
    python3 setup.py sdist
    python3 setup.py bdist_wheel --universal
    python3 setup.py install

For details, see
    http://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference
or
    python3 setup.py --help
    python3 setup.py --help-commands
    python3 setup.py --help bdist_wheel  # or any command
"""

#########################################################
# General config
#########################################################

# Name of the top-level package of the library.
#
# This is also the top level of its source tree, relative to the top-level project directory setup.py resides in.
#
libname="imacropy"

# Short description for package list on PyPI
#
SHORTDESC="Interactive MacroPy - IPython REPL, generic bootstrapper."

# Long description for package homepage on PyPI
#
DESC="""Imacropy is interactive macropy.

We provide some agile-development addons for MacroPy, namely a generic
macro-enabling bootstrapper, and an IPython extension to macro-enable its REPL.

**Bootstrapper**:

The bootstrapper imports the specified file or module, pretending its ``__name__``
is ``"__main__"``. This allows your main program to use macros.

For example, ``some_program.py``::

    from simplelet import macros, let

    def main():
        x = let((y, 21))[2*y]
        assert x == 42
        print("All OK")

    if __name__ == "__main__":
        main()

Start it as::

    macropy3 some_program.py

or::

    macropy3 -m some_program

The only command-line switch the bootstrapper supports is ``-m module_name``. If
you need to set other Python command-line options::

    python3 <your options here> -m macropy3 -m some_program

The first ``-m`` goes to Python itself, the second to the ``macropy3`` bootstrapper.

**IPython extension**:

The extension allows to **use macros in the IPython REPL**. (*Defining* macros
in the REPL is currently not supported.)

For example::

    In [1]: from simplelet import macros, let

    In [2]: let((x, 21))[2*x]
    Out[2]: 42

A from-import of macros from a given module clears from the REPL session **all**
current macros loaded from that module, and loads the latest definitions **of
only the specified** macros from disk. This allows interactive testing when
editing macros.

The most recent definition of any given macro remains alive until the next macro
from-import from the same module, or until the IPython session is terminated.

Macro docstrings and source code can be viewed using ``?`` and ``??``, as usual.

To load the extension once, ``%load_ext imacropy.console``.

To autoload it when IPython starts, add ``"imacropy.console"`` to the list
``c.InteractiveShellApp.extensions`` in your ``ipython_config.py``. To find
the config file, ``ipython profile locate``.

When the extension loads, it imports ``macropy`` into the REPL session. You can
use this to debug whether it is loaded, if necessary.

Currently **no startup banner is printed**, because extension loading occurs
after IPython has already printed its own banner. We cannot manually print a
banner, because some tools (notably ``importmagic.el`` for Emacs, included in
Spacemacs) treat the situation as a fatal error in Python interpreter startup if
anything is printed (and ``ipython3 --no-banner`` is rather convenient to have
as the python-shell, to run IPython in Emacs's inferior-shell mode).

For more details, see the docstring of ``imacropy.console``.
"""

# Set up data files for packaging.
#
# Directories (relative to the top-level directory where setup.py resides) in which to look for data files.
datadirs  = ()

# File extensions to be considered as data files. (Literal, no wildcards.)
dataexts  = (".py", ".ipynb",  ".sh",  ".lyx", ".tex", ".txt", ".pdf")

# Standard documentation to detect (and package if it exists).
#
standard_docs     = ["README", "LICENSE", "TODO", "CHANGELOG", "AUTHORS"]  # just the basename without file extension
standard_doc_exts = [".md", ".rst", ".txt", ""]  # commonly .md for GitHub projects, but other projects may use .rst or .txt (or even blank).

#########################################################
# Init
#########################################################

import os
from setuptools import setup

# Gather user-defined data files
#
# http://stackoverflow.com/questions/13628979/setuptools-how-to-make-package-contain-extra-data-folder-and-all-folders-inside
#
datafiles = []
#getext = lambda filename: os.path.splitext(filename)[1]
#for datadir in datadirs:
#    datafiles.extend( [(root, [os.path.join(root, f) for f in files if getext(f) in dataexts])
#                       for root, dirs, files in os.walk(datadir)] )

# Add standard documentation (README et al.), if any, to data files
#
detected_docs = []
for docname in standard_docs:
    for ext in standard_doc_exts:
        filename = "".join( (docname, ext) )  # relative to the directory in which setup.py resides
        if os.path.isfile(filename):
            detected_docs.append(filename)
datafiles.append( ('.', detected_docs) )

# Extract __version__ from the package __init__.py
# (since it's not a good idea to actually run __init__.py during the build process).
#
# http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
#
import ast
init_py_path = os.path.join('imacropy', '__init__.py')
version = '0.0.unknown'
try:
    with open(init_py_path) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            print( "WARNING: Version information not found in '%s', using placeholder '%s'" % (init_py_path, version), file=sys.stderr )
except FileNotFoundError:
    print( "WARNING: Could not find file '%s', using placeholder version information '%s'" % (init_py_path, version), file=sys.stderr )

#########################################################
# Call setup()
#########################################################

setup(
    name = "imacropy",
    version = version,
    author = "Juha Jeronen",
    author_email = "juha.m.jeronen@gmail.com",
    url = "https://github.com/Technologicat/imacropy",

    description = SHORTDESC,
    long_description = DESC,

    license = "BSD",

    # free-form text field; http://stackoverflow.com/questions/34994130/what-platforms-argument-to-setup-in-setup-py-does
    platforms = ["Linux"],

    # See
    #    https://pypi.python.org/pypi?%3Aaction=list_classifiers
    #
    # for the standard classifiers.
    #
    classifiers = [ "Development Status :: 4 - Beta",
                    "Environment :: Console",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: BSD License",
                    "Operating System :: POSIX :: Linux",
                    "Programming Language :: Python",
                    "Programming Language :: Python :: 3",
                    "Programming Language :: Python :: 3.6",
                    "Topic :: Software Development :: Libraries",
                    "Topic :: Software Development :: Libraries :: Python Modules",
                    "Framework :: IPython"
                  ],

    # See
    #    http://setuptools.readthedocs.io/en/latest/setuptools.html
    #
    setup_requires = [],
    install_requires = ["macropy3"],
    provides = ["imacropy"],

    # keywords for PyPI (in case you upload your project)
    #
    # e.g. the keywords your project uses as topics on GitHub, minus "python" (if there)
    #
    keywords = ["metaprogramming", "syntactic-macros", "macropy"],

    # Declare packages so that  python -m setup build  will copy .py files (especially __init__.py).
    #
    # This **does not** automatically recurse into subpackages, so they must also be declared.
    #
    packages = ["imacropy"],

    scripts = ["macropy3"],

    zip_safe = False,  # macros are not zip safe, because the zip importer fails to find sources, and MacroPy needs them.

    # Custom data files not inside a Python package
    data_files = datafiles
)
