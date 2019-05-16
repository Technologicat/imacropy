# -*- coding: utf-8 -*-
"""IPython extension for a MacroPy-enabled REPL.

To enable::

    %load_ext imacropy.console

To autoload it at IPython startup, put this into your ``ipython_config.py``::

    c.InteractiveShellApp.extensions = ["imacropy.console"]

To find your config file, ``ipython profile locate``.

Notes:

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
"""

import ast
import importlib
from collections import OrderedDict
from functools import partial

from IPython.core.error import InputRejected
from IPython.core.magic import register_cell_magic

from macropy import __version__ as macropy_version
from macropy.core.macros import ModuleExpansionContext, detect_macros

_placeholder = "<interactive input>"
_instance = None

def load_ipython_extension(ipython):
    # FIXME: The banner is injected too late. It seems IPython startup has  already performed when ``load_ipython_extension()`` is called.
    #
    # FIXME: We shouldn't print anything directly here; doing that breaks tools such as the Emacs Python autoimporter (see importmagic.el
    # FIXME: in Spacemacs; it will think epc failed to start if anything but the bare process id is printed). Tools expect to suppress
    # FIXME: **all** of the IPython banner by telling IPython itself not to print it.
    #
    # FIXME: For now, let's just put the info into banner2, and refrain from printing it.
    # https://stackoverflow.com/questions/31613804/how-can-i-call-ipython-start-ipython-with-my-own-banner
    ipython.config.TerminalInteractiveShell.banner2 = "MacroPy {} -- Syntactic macros for Python.".format(macropy_version)
    global _instance
    if not _instance:
        _instance = IMacroPyExtension(shell=ipython)

def unload_ipython_extension(ipython):
    global _instance
    _instance = None

class MacroTransformer(ast.NodeTransformer):
    def __init__(self, extension_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ext = extension_instance
        self.bindings = OrderedDict()

    def visit(self, tree):
        try:
            bindings = detect_macros(tree, '__main__', reload=True)  # macro imports
            if bindings:
                self.ext.macro_bindings_changed = True
                for fullname, macro_bindings in bindings:
                    mod = importlib.import_module(fullname)
                    self.bindings[fullname] = (mod, macro_bindings)
            newtree = ModuleExpansionContext(tree, self.ext.src, self.bindings.values()).expand_macros()
            self.ext.src = _placeholder
            return newtree
        except Exception as err:
            # see IPython.core.interactiveshell.InteractiveShell.transform_ast()
            raise InputRejected(*err.args)

# avoid complaining about typoed macro names...
@register_cell_magic
def ignore_importerror(line, cell):  # ...when their stubs are loaded
    try:
        exec(cell, _instance.shell.user_ns)  # set globals to the shell user namespace to respect assignments
    except ImportError as e:
        pass

@register_cell_magic
def ignore_nameerror(line, cell):  # ...when they are unloaded
    try:
        exec(cell, _instance.shell.user_ns)
    except NameError as e:
        pass

class IMacroPyExtension:
    def __init__(self, shell):
        self.src = _placeholder
        self.shell = shell
        ipy = self.shell.get_ipython()

        self.new_api = hasattr(self.shell, "input_transformers_post")  # IPython 7.0+ with Python 3.5+
        if self.new_api:
            self.shell.input_transformers_post.append(self._get_source_code)
        else:
            ipy.events.register('pre_run_cell', self._get_source_code_legacy)

        self.macro_bindings_changed = False
        self.current_stubs = set()
        self.macro_transformer = MacroTransformer(extension_instance=self)
        self.shell.ast_transformers.append(self.macro_transformer)  # TODO: last or first?

        ipy.events.register('post_run_cell', self._refresh_stubs)

        # initialize MacroPy in the session
        self.shell.run_cell("import macropy.activate", store_history=False, silent=True)

    def __del__(self):
        ipy = self.shell.get_ipython()
        ipy.events.unregister('post_run_cell', self._refresh_stubs)
        self.shell.ast_transformers.remove(self.macro_transformer)
        if self.new_api:
            self.shell.input_transformers_post.remove(self._get_source_code)
        else:
            ipy.events.unregister('pre_run_cell', self._get_source_code_legacy)

    def _get_source_code_legacy(self, info):
        """Get the source code of the current cell just before it runs.

        Does not account for any string transformers.
        """
        self.src = info.raw_cell

    def _get_source_code(self, lines):  # IPython 7.0+ with Python 3.5+
        """Get the source code of the current cell.

        This is a do-nothing string transformer that just captures the text.
        It is intended to run last, just before any AST transformers run.
        """
        self.src = lines
        return lines

    def _refresh_stubs(self, info):
        """Refresh macro stub imports.

        Called after running a cell, so that Jupyter help "some_macro?" works
        for the currently available macros.

        This allows the user to view macro docstrings.
        """
        if not self.macro_bindings_changed:
            return
        self.macro_bindings_changed = False
        internal_execute = partial(self.shell.run_cell,
                                   store_history=False,
                                   silent=True)

        # Clear previous stubs, because our MacroTransformer overrides
        # the available set of macros from a given module with those
        # most recently imported from that module.
        for asname in self.current_stubs:
            internal_execute("%%ignore_nameerror\n"
                             "del {}".format(asname))
        self.current_stubs = set()

        for fullname, (_, macro_bindings) in self.macro_transformer.bindings.items():
            for _, asname in macro_bindings:
                self.current_stubs.add(asname)
            stubnames = ", ".join("{} as {}".format(name, asname) for name, asname in macro_bindings)
            internal_execute("%%ignore_importerror\n"
                             "from {} import {}".format(fullname, stubnames))
