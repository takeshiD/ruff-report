import typer
from ruff_report.save_report import app as save_app
from ruff_report.analyze_report import app as analyze_app

app = typer.Typer()
app.add_typer(save_app)
app.add_typer(analyze_app)

if __name__ == "__main__":
    app()
