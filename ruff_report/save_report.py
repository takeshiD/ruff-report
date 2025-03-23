"""pre-commitフック用のスクリプト ruffの出力をタイムスタンプ付きで保存."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer()

def get_git_root() -> Path | None:
    try:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],  # noqa: S607
                text=True,
            ).strip(),
        )
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository", file=sys.stderr)
        return None

def get_git_branchname() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],  # noqa: S607
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return "unknown-branch"

def get_git_commithash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],  # noqa: S607
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return "unknown-branch"

def get_ruff_result_text(target_dir: Path | str) -> str | None:
    target_dir = Path(target_dir)
    try:
        completed_result = subprocess.run(
            ["ruff", "check", str(target_dir), "--output-format", "json"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        completed_result.check_returncode()
    except Exception as e:  # noqa: BLE001
        print(f"Error running ruff: {e}", file=sys.stderr)
        return None
    else:
        return completed_result.stdout

@app.command()
def save(
    target_root: Annotated[Path, typer.Option(help="git-repo directory path")] = Path(".ruff_report"),
    report_root: Annotated[Path, typer.Option(help="report directory path")] = Path(".ruff_report"),
    report_name: Annotated[str, typer.Option(help="report name")] = "ruff_report",
):
    timestamp: str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    branch_name = get_git_branchname()
    commit_hash = get_git_commithash()
    # ruff_result_text = get_ruff_result_text()
