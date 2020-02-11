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

### Loading the extension

To load the extension once, ``%load_ext imacropy.iconsole``.

To autoload it when IPython starts, add the string ``"imacropy.iconsole"`` to the list ``c.InteractiveShellApp.extensions`` in your ``ipython_config.py``. To find the config file, ``ipython profile locate``.

When the extension loads, it imports ``macropy`` into the REPL session. You can use this to debug whether it is loaded, if necessary.

Currently **no startup banner is printed**, because extension loading occurs after IPython has already printed its own banner. We cannot manually print a banner, because some tools (notably ``importmagic.el`` for Emacs, included in [Spacemacs](http://spacemacs.org/)) treat the situation as a fatal error in Python interpreter startup if anything is printed (and ``ipython3 --no-banner`` is rather convenient to have as the python-shell, to run IPython in Emacs's inferior-shell mode).


## MacroConsole

This allows you to **embed a REPL that supports macros**. The difference to `macropy.core.console.MacroConsole` is that this one offers the same semantics as the IPython extension.

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

Macro docstrings can be viewed with `imacropy.doc(some_macro)`:

```python
from imacropy import doc
doc(let)
```

The `doc` function is provided because for some reason, both in `MacroConsole` and in the IPython extension, `help(some_macro)` sees only the generic docstring of `WrappedMacro`, not that of the actual macro stub object. `imacropy.doc` has no paging, but `doc(some_macro)` sees the correct docstring, just like IPython's `some_macro?` does.


## Bootstrapper

The bootstrapper imports the specified file or module, pretending its ``__name__`` is ``"__main__"``. **This allows your main program to use macros**.

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
