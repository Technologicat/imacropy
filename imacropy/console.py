# -*- coding: utf-8 -*-
"""Macro-enabled `code.InteractiveConsole`, with some `imacropy` magic.

This differs from `macropy.core.console.MacroConsole` in that we follow
`imacropy` REPL semantics:

  - Each time a ``from mymodule import macros, ...`` is executed in the REPL,
    the system reloads ``mymodule``, to use the latest macro definitions.

    Hence, semi-live updates to macro definitions are possible: hack on your
    macros, re-import, and try out the new version in the REPL; no need to restart
    the REPL session in between.

  - The set of macros available from ``mymodule``, at any given time, is those
    specified **in the most recent** ``from mymodule import macros, ...``.

    Any other macros from ``mymodule``, that were not specified in the most recent
    import, will be unloaded when the import is performed.

  - Each time after importing macros, the corresponding macro stubs are
    automatically imported as regular Python objects.

    Stubs are not directly usable. The intention is to let Python recognize
    the macro name (otherwise there would be no run-time object by that name),
    and to allow viewing macro docstrings (`some_macro.__doc__`).

    Note `help(some_macro)` still won't work; it'll show the docstring for
    the `WrappedMacro` wrapper only. As a workaround, use `imacropy.doc(some_macro)`.
    (No paging, but it sees the correct docstring.)

    This does not affect using the macros in the intended way, as macros,
    since macros are expanded away before run-time.

Based on macropy.core.MacroConsole by Li Haoyi, Justin Holmgren, Alberto Berti and all the other contributors,
2013-2019. Used under the MIT license.
    https://github.com/azazel75/macropy
"""

__all__ = ["MacroConsole"]

import ast
import code
import textwrap
import importlib
from collections import OrderedDict

from macropy.core.macros import ModuleExpansionContext, detect_macros
from macropy import __version__ as macropy_version

from .util import _reload_macro_modules

import macropy.activate  # noqa: F401, boot up MacroPy so ModuleExpansionContext works.


class MacroConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        self._bindings = OrderedDict()
        self._stubs = set()
        self._stubs_dirty = False

    def interact(self, banner=None, exitmsg=None):
        """See `code.InteractiveConsole.interact`.

        The only thing we customize here is that if `banner is None`, in which case
        `code.InteractiveConsole` will print its default banner, we print a line
        containing the MacroPy version before that default banner.
        """
        if banner is None:
            self.write(f"MacroPy {macropy_version} -- Syntactic macros for Python.\n")
        return super().interact(banner, exitmsg)

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            code = ""
        if code is None:  # incomplete input
            return True

        try:
            tree = ast.parse(source)
            # Must reload modules before detect_macros, because detect_macros reads the macro registry
            # of each module from which macros are imported.
            _reload_macro_modules(tree, '__main__')
            # If detect_macros returns normally, it means each fullname can be imported successfully.
            bindings = detect_macros(tree, '__main__')
            if bindings:
                self._stubs_dirty = True
            for fullname, macro_bindings in bindings:
                mod = importlib.import_module(fullname)  # already imported so just a sys.modules lookup
                self._bindings[fullname] = (mod, macro_bindings)

            tree = ModuleExpansionContext(tree, source, self._bindings.values()).expand_macros()

            tree = ast.Interactive(tree.body)
            code = compile(tree, filename, symbol, self.compile.compiler.flags, 1)
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename)
            return False  # erroneous input
        except ModuleNotFoundError as err:  # during macro module lookup
            # In this case, the standard stack trace is long and points only to our code and the stdlib,
            # not the erroneous input that's the actual culprit. Better ignore it, and emulate showsyntaxerror.
            # TODO: support sys.excepthook.
            self.write(f"{err.__class__.__name__}: {str(err)}\n")
            return False  # erroneous input

        self.runcode(code)
        self._refresh_stubs()
        return False  # Successfully compiled. `runcode` takes care of any runtime failures.

    def _refresh_stubs(self):
        """Refresh macro stub imports.

        Called after successfully compiling and running an input, so that
        `some_macro.__doc__` points to the right docstring.
        """
        if not self._stubs_dirty:
            return
        self._stubs_dirty = False

        # We bypass runsource, since it calls us, and we don't need macros in what we do here.
        def internal_execute(source):
            source = textwrap.dedent(source)
            tree = ast.parse(source)
            tree = ast.Interactive(tree.body)
            code = compile(tree, "<console_internal>", "single", self.compile.compiler.flags, 1)
            self.runcode(code)

        # Clear previous stubs, because we override the available set of macros
        # from a given module with those most recently imported from that module.
        for asname in self._stubs:
            source = f"""\
            try:
                del {asname}
            except NameError:
                pass
            """
            internal_execute(source)
        self._stubs = set()

        for fullname, (_, macro_bindings) in self._bindings.items():
            for _, asname in macro_bindings:
                self._stubs.add(asname)
            stubnames = ", ".join("{} as {}".format(name, asname) for name, asname in macro_bindings)
            source = f"""\
            try:
                from {fullname} import {stubnames}
            except ImportError:
                pass
            """
            internal_execute(source)
