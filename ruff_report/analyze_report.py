from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def analyze(
    project_path: Path | None = typer.Argument(
        None, help="Path to the project directory"
    ),
):
    """Analyze the specified project path.

    If no path is provided, use the current directory.

    """
    if project_path is None:
        project_path = Path.cwd()

    # Add your analysis logic here
    print(f"Analyzing project at: {project_path}")


if __name__ == "__main__":
    app()
