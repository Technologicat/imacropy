# -*- coding: utf-8; -*-

__all__ = ["doc", "sourcecode"]

import ast
import importlib
import inspect

from macropy.core.macros import WrappedFunction

def doc(obj):
    """Print an object's docstring, non-interactively.

    Additionally, if the information is available, print the filename
    and the starting line number of the definition of `obj` in that file.
    This is printed before the actual docstring.

    This works around the problem that in a REPL session using
    `imacropy.console` or `imacropy.iconsole`, the builtin `help()`
    fails to see the docstring of the stub, and sees only the generic
    docstring of `WrappedMacro`.

    And that looking directly at `some_macro.__doc__` prints the string
    value as-is, without formatting it.
    """
    if not hasattr(obj, "__doc__") or not obj.__doc__:
        print("<no docstring>")
        return
    try:
        if isinstance(obj, WrappedFunction):
            obj = obj.__wrapped__  # this is needed to make inspect.getsourcefile work with macros
        filename = inspect.getsourcefile(obj)
        source, firstlineno = inspect.getsourcelines(obj)
        print(f"{filename}:{firstlineno}")
    except (TypeError, OSError):
        pass
    print(inspect.cleandoc(obj.__doc__))

def sourcecode(obj):
    """Print an object's source code, non-interactively.

    Additionally, if the information is available, print the filename
    and the starting line number of the definition of `obj` in that file.
    This is printed before the actual source code.
    """
    try:
        if isinstance(obj, WrappedFunction):
            obj = obj.__wrapped__  # this is needed to make inspect.getsourcefile work with macros
        filename = inspect.getsourcefile(obj)
        source, firstlineno = inspect.getsourcelines(obj)
        print(f"{filename}:{firstlineno}")
        for line in source:
            print(line.rstrip("\n"))
    except (TypeError, OSError):
        print("<no source code available>")

# Modeled after macropy.core.macros.detect_macros.
# This is a separate function with duplicate logic, so we don't need to modify MacroPy.
def _reload_macro_modules(tree, from_fullname, from_package=None, from_module=None):
    """Walk an AST, importing and reloading any macro modules the AST says to import.

    Here "macro module" means a module from which `tree` imports macro definitions,
    i.e. `somemod` in `from somemod import macros, ...`.

    Reloading modules from which macro definitions are imported ensures that the
    REPL always has access to the latest macro definitions, even if they are modified
    on disk during the REPL session.

    This is essentially an implementation detail of `imacropy`.
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
