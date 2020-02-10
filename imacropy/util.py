# -*- coding: utf-8; -*-

__all__ = ["doc"]

import ast
import importlib
import textwrap

def doc(obj):
    """Print an object's docstring, non-interactively.

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
    # Emulate help()'s dedenting. Typically, the first line in a docstring
    # has no leading whitespace, while the rest follow the indentation of
    # the function body.
    firstline, *rest = obj.__doc__.split("\n")
    rest = textwrap.dedent("\n".join(rest))
    doc = [firstline, *rest.split("\n")]
    for line in doc:
        print(line)

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
