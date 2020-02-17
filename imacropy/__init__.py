# -*- coding: utf-8 -*-
"""Imacropy is interactive macropy, a set of agile tools for MacroPy.

- ``imacropy.iconsole``, IPython extension. Use macros in the IPython REPL.

- ``imacropy.console.MacroConsole``, a macro-enabled equivalent of ``code.InteractiveConsole``.
  Embed a REPL that supports macros. It also provides IPython-like docstring and source code
  viewing with the syntax `obj?`, `obj??`.

- ``macropy3``, a generic bootstrapper for macro-enabled Python programs.
  Use macros in your main program.
"""

__version__ = '0.3.1'

# export
from .util import *
