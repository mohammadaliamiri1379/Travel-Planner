# Travel_planner

![PyPI version](https://img.shields.io/pypi/v/travel_planner.svg)

 implementation of a multi-agent travel planning system with:

- Orchestrator agent (planning + aggregation)
- Two domain agents (Places + Weather)
- MCP-style tool abstraction servers (FastAPI + Pydantic)
- Microsoft-style agent registry/routing layer
- AWS integration wrapper (boto3)
- API gateway exposing `POST /chat`


* [GitHub](https://github.com/mohammadaliamiri1379/Travel-Planner) | | [Documentation](https://github.com/mohammadaliamiri1379/Travel-Planner)
* Created by [Mohammadali Amiri](- Orchestrator agent (planning + aggregation)) | GitHub [@mohammadaliamiri1379](https://github.com/mohammadaliamiri1379) | PyPI [@mohammadaliamiri1379](https://pypi.org/user/mohammadaliamiri1379/)
* MIT License

## Features

* TODO

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://github.com/mohammadaliamiri1379/Travel-Planner
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/travel_planner.git
cd travel_planner

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `travle_planner`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

Travel_planner was created in 2026 by Mohammadali Amiri.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
