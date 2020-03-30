# Imacropy

Imacropy is interactive macropy.

We provide some agile-development addons for MacroPy, namely:

- [``imacropy.iconsole``](#ipython-extension), IPython extension. **Use macros in the IPython REPL**.

- [``imacropy.console.MacroConsole``](#macroconsole), a macro-enabled equivalent of ``code.InteractiveConsole``. **Embed a REPL that supports macros**.

- [``macropy3``](#bootstrapper), a generic bootstrapper for macro-enabled Python programs. **Use macros in your main program**.

*Changed in v0.2.0.* Due to the addition of `MacroConsole`, which is more deserving of the module name `imacropy.console`, the IPython extension has been renamed to `imacropy.iconsole` (note the second `i`). Please update your IPython profile. This is a permanent rename, `iconsole` will not be renamed again.


## IPython extension

The extension allows to **use macros in the IPython REPL**. (*Defining* macros in the REPL is currently not supported.)

For example:

```ipython
In [1]: from simplelet import macros, let

In [2]: let((x, 21))[2*x]
Out[2]: 42
```

A from-import of macros from a given module clears from the REPL session **all** current macros loaded from that module, and loads the latest definitions **of only the specified** macros from disk. This allows interactive testing when editing macros.

The most recent definition of any given macro remains alive until the next macro from-import from the same module, or until the IPython session is terminated.

Macro docstrings and source code can be viewed using ``?`` and ``??``, as usual.

*Added in v0.3.1.* The line magic `%macros` now prints a human-readable list of macros that are currently imported into the REPL session (or says that no macros are imported, if so).

### Loading the extension

To load the extension once, ``%load_ext imacropy.iconsole``.

To autoload it when IPython starts, add the string ``"imacropy.iconsole"`` to the list ``c.InteractiveShellApp.extensions`` in your ``ipython_config.py``. To find the config file, ``ipython profile locate``.

When the extension loads, it imports ``macropy`` into the REPL session. You can use this to debug whether it is loaded, if necessary.

Currently **no startup banner is printed**, because extension loading occurs after IPython has already printed its own banner. We cannot manually print a banner, because some tools (notably ``importmagic.el`` for Emacs, included in [Spacemacs](http://spacemacs.org/)) treat the situation as a fatal error in Python interpreter startup if anything is printed (and ``ipython3 --no-banner`` is rather convenient to have as the python-shell, to run IPython in Emacs's inferior-shell mode).


## MacroConsole

This is a derivative of, and drop-in replacement for, ``code.InteractiveConsole``, which allows you to **embed a REPL that supports macros**. The difference to `macropy.core.console.MacroConsole` is that this one offers the same semantics as the IPython extension.

Main features of `imacropy.console.MacroConsole`:

 - IPython-like `obj?` and `obj??` syntax to view the docstring and source code of `obj`.
 - Can list macros imported to the session, using the command `macros?`.
 - Catches and reports import errors when importing macros.
 - Allows importing the same macros again in the same session, to refresh their definitions.
   - When you `from somemod import macros, ...`, this console automatically first reloads `somemod`, so that a macro import always sees the latest definitions.
 - Makes viewing macro docstrings easy.
   - When you import macros, beside loading them into the macro expander, the console automatically imports the macro stubs as regular runtime objects. They're functions, so just look at their `__doc__`.
   - This also improves UX. Without loading the stubs, `from unpythonic.syntax import macros, let`, would not define the name `let` at runtime. Now it does, with the name pointing to the macro stub.

Example:

```python
from imacropy.console import MacroConsole
m = MacroConsole()
m.interact()
```

Now we're inside a macro-enabled REPL:

```python
from unpythonic.syntax import macros, let
x = let[((a, 21)) in 2 * a]
assert x == 42
```

Just like in `code.InteractiveConsole`, exiting the REPL (Ctrl+D) returns from the `interact()` call.

Macro docstrings and source code can be viewed like in IPython:

```python
let?
let??
```

If the information is available, these operations also print the filename and the starting line number of the definition of the queried object in that file.

The ``obj?`` syntax is shorthand for ``imacropy.doc(obj)``, and ``obj??`` is shorthand for ``imacropy.sourcecode(obj)``.

Note that just like in IPython, for some reason `help(some_macro)` sees only the generic docstring of `WrappedMacro`, not that of the actual macro stub object. So use the ``?`` syntax to view macro docstrings, as you would in IPython.

*Added in v0.3.1.* The literal command `macros?` now prints a human-readable list of macros that are currently imported into the REPL session (or says that no macros are imported, if so). This shadows the `obj?` docstring lookup syntax for the MacroPy special object `macros`, but that's likely not needed. That can still be invoked manually, using `imacropy.doc(macros)`.


## Bootstrapper

*Added in v0.3.2: Interactive mode.*

The bootstrapper has two roles:

 - It allows starting a **macro-enabled interactive Python interpreter** directly from the command line.
 - It **allows your main program to use macros**.

### Interactive mode

Interactive mode (command-line option `-i`) starts a **macro-enabled interactive Python interpreter**, using `imacropy.console.MacroConsole`. The [readline](https://docs.python.org/3/library/readline.html) and [rlcompleter](https://docs.python.org/3/library/rlcompleter.html) modules are automatically activated and connected to the REPL session, so the command history and tab completion features work as expected, pretty much like in the standard interactive Python interpreter.

The point of this feature is to conveniently allow starting a macro-enabled REPL directly from the command line. In interactive mode, the filename and module command-line arguments are ignored.

If `-p` is given in addition to `-i`, as in `macropy3 -pi`, the REPL starts in **pylab mode**. This automatically performs `import numpy as np`, `import matplotlib.pyplot as plt`, and activates matplotlib's interactive mode, so plotting won't block the REPL. This is somewhat like IPython's pylab mode, but we keep stuff in separate namespaces. This is a convenience feature for scientific interactive use.

**CAUTION**: As of v0.3.2, history is not saved between sessions. This may or may not change in a future release.

### Bootstrapping a script or a module

In this mode, the bootstrapper imports the specified file or module, pretending its ``__name__`` is ``"__main__"``. **This allows your main program to use macros**.

For example, ``some_program.py``:

```python
from simplelet import macros, let

def main():
    x = let((y, 21))[2*y]
    assert x == 42
    print("All OK")

if __name__ == "__main__":
    main()
```

Start it as:

```bash
macropy3 some_program.py
```

A relative path is ok, as long as it is under the current directory. Relative paths including ``..`` are **not** supported. We also support the ``-m module_name`` variant:

```bash
macropy3 -m some_program
```

A dotted module path under the current directory is ok.

If you need to set other Python command-line options:

```bash
python3 <your options here> $(which macropy3) -m some_program
```

This way the rest of the options go to the Python interpreter itself, and the ``-m some_program`` to the ``macropy3`` bootstrapper.


## Installation

### From PyPI

Install as user:

```bash
pip install imacropy --user
```

Install as admin:

```bash
sudo pip install imacropy
```

### From GitHub

As user:

```bash
git clone https://github.com/Technologicat/imacropy.git
cd imacropy
python setup.py install --user
```

As admin, change the last command to

```bash
sudo python setup.py install
```


## Dependencies

[MacroPy3](https://github.com/azazel75/macropy).


## License

[BSD](LICENSE.md). Copyright 2019-2020 Juha Jeronen and University of Jyväskylä.
