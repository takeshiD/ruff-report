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
        return "unknown-commit"


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
    target_root: Annotated[Path, typer.Option(help="git-repo directory path")] = Path("."),
    report_root: Annotated[Path, typer.Option(help="report directory path")] = Path(
        ".ruff_report"
    ),
    report_name: Annotated[str, typer.Option(help="report name")] = "ruff_report",
):
    """Ruffの実行結果をタイムスタンプ付きで保存する."""
    timestamp: str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    branch_name = get_git_branchname()
    commit_hash = get_git_commithash()

    # Ruffの実行結果を取得
    ruff_result_text = get_ruff_result_text(target_root)
    if ruff_result_text is None:
        print("Failed to get ruff results", file=sys.stderr)
        sys.exit(1)

    # レポート保存用のディレクトリを作成
    report_dir = Path(report_root)
    report_dir.mkdir(parents=True, exist_ok=True)

    # ファイル名を生成(タイムスタンプ、ブランチ名、コミットハッシュを含む)
    short_hash = commit_hash[:8]  # コミットハッシュの短縮版
    safe_branch_name = branch_name.replace("/", "-")  # ファイル名に使えない文字を置換

    report_filename = f"{report_name}_{timestamp}_{safe_branch_name}_{short_hash}.json"
    report_path = report_dir / report_filename

    # レポートを保存
    try:
        with report_path.open("w") as f:
            f.write(ruff_result_text)
        print(f"Ruff report saved to {report_path}")
    except Exception as e:
        print(f"Error saving ruff report: {e}", file=sys.stderr)
        return 1
    else:
        return 0


def main():
    """メイン関数."""
    app()


if __name__ == "__main__":
    main()
