**0.3.2** (in progress)

- Fix crash in `from somemod import macros, ...` when `somemod` has no `macros` attribute. (Typically this happens when trying to import macros from a module that doesn't define any.)
- Bootstrapper: add interactive mode (`macropy3 -i`) to conveniently start a macro-enabled REPL.

---

**0.3.1** 21 February 2020

- Fix bug when importing a nonexistent macro (typoed name) from a module that itself imports successfully.
  - Now the macro imports are validated before committing any changes.
- Add a `%macros` line magic to the IPython extension, and a `macros?` command to `MacroConsole`.

  These both implement the same feature, in the two different consoles: print a human-readable list of macros that are currently imported into the REPL session (or say that no macros are imported, if so).

  In `MacroConsole`, this shadows the `obj?` docstring lookup syntax for the MacroPy special object `macros`, but that's likely not needed. That can still be invoked manually, using `imacropy.doc(macros)`.

---

**0.3.0** 18 February 2020

- Remove silly `help_function` parameter added in 0.2.x, always use `imacropy.doc` (`MacroConsole` behavior now consistent with IPython).
- Modernize setup script.
  - Now the PyPI long description is auto-generated from `README.md`, so it automatically stays up to date.
  - Non-package datafiles removed from PyPI package.

---

**0.2.2** 17 February 2020 (hotfix)

- Fix macro stub loader broken in 0.2.1.
- Fix viewing of macro source code with `??`.

---

**0.2.1** 17 February 2020

- Add IPython-like `obj?`, `obj??` syntax for viewing docstrings and source code.

---

**0.2.0** 11 February 2020

-  Add `imacropy.console.MacroConsole`, a macro-enabled `code.InteractiveConsole`, with the same semantics as the IPython extension. This allows you to embed a REPL that supports macros.

- Rename IPython extension module to `imacropy.iconsole` (note the second `i`), because the new basic console is more deserving of the module name `imacropy.console`. **Please update your IPython profile.** This is a permanent rename, the module will not be renamed again.

- Fix issue [#2](https://github.com/Technologicat/imacropy/issues/2), should now work correctly with a stock MacroPy. Thanks **@bogiebro**.

---

**0.1.0** 16 May 2019

Agile tools for MacroPy3. First version released as separate project.

This project supersedes the `macropy3` bootstrapper script in [`unpythonic`](https://github.com/Technologicat/unpythonic), as well as [MacroPy pull request #20](https://github.com/azazel75/macropy/pull/20).
