## Travel_planner - Two domain agents (Places + Weather)

University-grade reference implementation of a multi-agent travel planning system with:

This release reserves the PyPI package name and establishes the project scaffold.

```sh
uv add travel_planner
```

### What's in the scaffold

- `src/travel_planner/` package with CLI (Typer + Rich), py.typed marker
- Tests with pytest, coverage across Python 3.12/3.13/3.14
- CI via GitHub Actions: lint (Ruff), type check (ty), test matrix, coverage reporting
- Security scanning: CodeQL analysis, Dependabot, zizmor workflow audit
- Docs site with Zensical + mkdocstrings, auto-deployed to GitHub Pages
- Trusted publishing to PyPI with OIDC and build provenance attestation
- `justfile` with dev commands: qa, test, type-check, docs-serve, release
- Issue templates, PR template, contributing guide, code of conduct, security policy
- MIT license, .editorconfig, .gitignore

Built with [Cookiecutter PyPackage](https://github.com/audreyfeldroy/cookiecutter-pypackage).

### Contributors

[@mohammadaliamiri1379](https://github.com/mohammadaliamiri1379) (Mohammadali Amiri) created Travel_planner.
