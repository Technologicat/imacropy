# -*- coding: utf-8; -*-

__all__ = ["reload_macro_modules"]

import ast
import importlib

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
