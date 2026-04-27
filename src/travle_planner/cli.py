"""Console script for travle_planner."""

import typer
from rich.console import Console

from travle_planner import utils

app = typer.Typer()
console = Console()


@app.command()
def main() -> None:
    """Console script for travle_planner."""
    console.print("Replace this message by putting your code into travle_planner.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
