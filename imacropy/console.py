# -*- coding: utf-8 -*-
"""Macro-enabled equivalent of `code.InteractiveConsole`.

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
    and to allow viewing macro docstrings and source code easily using
    ``some_macro?``, ``some_macro??``.

    This does not affect using the macros in the intended way, as macros,
    since macros are expanded away before run-time.

Based on macropy.core.MacroConsole by Li Haoyi, Justin Holmgren, Alberto Berti and all the other contributors,
2013-2019. Used under the MIT license.
    https://github.com/azazel75/macropy
"""

__all__ = ["MacroConsole"]

import ast
import code
import importlib
from collections import OrderedDict

from macropy.core.macros import ModuleExpansionContext, detect_macros

# Modeled after macropy.core.macros.detect_macros.
# This is a separate function with duplicate logic, so we don't need to modify MacroPy.
def reload_macro_modules(tree, from_fullname, from_package=None, from_module=None):
    """Walk an AST, importing and reloading any macro modules the AST says to import.

    Here "macro module" means a module from which `tree` imports macro definitions,
    i.e. `somemod` in `from somemod import macros, ...`.

    Reloading modules from which macro definitions are imported ensures that the
    REPL always has access to the latest macro definitions, even if they are modified
    on disk during the REPL session.
    """
    macro_modules = []
    for stmt in tree.body:
        if (isinstance(stmt, ast.ImportFrom) and
            stmt.module and stmt.names[0].name == 'macros' and
            stmt.names[0].asname is None):  # noqa: E129
            fullname = importlib.util.resolve_name('.' * stmt.level + stmt.module, from_package)
            macro_modules.append(fullname)
    for fullname in macro_modules:
        try:
            mod = importlib.import_module(fullname)
            mod = importlib.reload(mod)
        except ModuleNotFoundError:
            pass


class MacroConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        self.bindings = OrderedDict()

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            code = ""
        if code is None:  # incomplete input
            return True

        try:
            tree = ast.parse(source)
            reload_macro_modules(tree, '__main__')
            # if detect_macros returns normally, it means each fullname can be imported successfully.
            for fullname, macro_bindings in detect_macros(tree, '__main__'):
                mod = importlib.import_module(fullname)  # already imported so just a sys.modules lookup
                self.bindings[fullname] = (mod, macro_bindings)
            tree = ModuleExpansionContext(tree, source, self.bindings.values()).expand_macros()

            tree = ast.Interactive(tree.body)
            code = compile(tree, filename, symbol,
                           self.compile.compiler.flags, 1)
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
        return False  # Successfully compiled. `runcode` takes care of any runtime failures.
