import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Annotated, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from ruff_report.datatype import Violation, ViolationList

app = typer.Typer()
console = Console()


def parse_report_file(report_path: Path) -> Optional[List[Violation]]:
    """Parse a Ruff report JSON file and return the violations.

    Args:
        report_path: Path to the report file

    Returns:
        List of Violation objects or None if parsing failed
    """
    try:
        with report_path.open("r") as f:
            report_data = json.load(f)
        
        # Parse the JSON data into Violation objects
        violations = ViolationList.model_validate(report_data).root
        return violations
    except Exception as e:
        console.print(f"[bold red]Error parsing report file {report_path}:[/] {e}")
        return None


def extract_report_metadata(report_filename: str) -> Dict[str, str]:
    """Extract metadata from the report filename.

    Args:
        report_filename: Name of the report file

    Returns:
        Dictionary containing timestamp, branch name, and commit hash
    """
    # Expected format: ruff_report_YYYY-MM-DD-HHMMSS_branch_commithash.json
    parts = report_filename.split("_")
    
    # Default values in case parsing fails
    metadata = {
        "timestamp": "Unknown",
        "branch": "Unknown",
        "commit": "Unknown",
    }
    
    if len(parts) >= 4:
        # Extract timestamp (format: YYYY-MM-DD-HHMMSS)
        try:
            timestamp_str = parts[2]
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d-%H%M%S")
            metadata["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            pass
        
        # Extract branch name (could be multiple parts if branch name contains underscores)
        try:
            # The commit hash is the last part before .json
            commit_with_ext = parts[-1]
            commit_hash = commit_with_ext.split(".")[0]
            metadata["commit"] = commit_hash
            
            # Branch name is everything between timestamp and commit hash
            branch_parts = parts[3:-1]
            metadata["branch"] = "_".join(branch_parts)
        except (IndexError, ValueError):
            pass
    
    return metadata


def display_report_summary(violations: List[Violation], metadata: Dict[str, str]) -> None:
    """Display a summary of the Ruff report.

    Args:
        violations: List of Violation objects
        metadata: Dictionary containing report metadata
    """
    # Create a table for the summary
    table = Table(title="Ruff Report Summary")
    
    # Add metadata
    table.add_section()
    table.add_row("Timestamp", metadata["timestamp"])
    table.add_row("Branch", metadata["branch"])
    table.add_row("Commit", metadata["commit"])
    table.add_row("Total Violations", str(len(violations)))
    
    # Count violations by rule code
    rule_counts = Counter(v.code for v in violations if v.code)
    
    # Add rule counts
    if rule_counts:
        table.add_section()
        table.add_row("Rule Code", "Count", "Description")
        for code, count in rule_counts.most_common(10):  # Show top 10 rules
            table.add_row(code or "Unknown", str(count), "")
    
    console.print(table)


def display_violations_by_file(violations: List[Violation]) -> None:
    """Display violations grouped by file.

    Args:
        violations: List of Violation objects
    """
    # Group violations by filename
    violations_by_file = defaultdict(list)
    for violation in violations:
        violations_by_file[violation.filename].append(violation)
    
    # Create a table for each file
    for filename, file_violations in violations_by_file.items():
        table = Table(title=f"Violations in {filename}")
        table.add_column("Line")
        table.add_column("Column")
        table.add_column("Rule")
        table.add_column("Message")
        
        for violation in sorted(file_violations, key=lambda v: (v.location.row, v.location.column)):
            table.add_row(
                str(violation.location.row),
                str(violation.location.column),
                violation.code or "Unknown",
                violation.message
            )
        
        console.print(table)
        console.print()


def analyze_report(report_path: Path) -> None:
    """Analyze a Ruff report file and display the results.

    Args:
        report_path: Path to the report file
    """
    console.print(f"[bold]Analyzing report:[/] {report_path}")
    
    # Parse the report file
    violations = parse_report_file(report_path)
    if not violations:
        return
    
    # Extract metadata from filename
    metadata = extract_report_metadata(report_path.name)
    
    # Display summary
    display_report_summary(violations, metadata)
    
    # Display violations by file
    display_violations_by_file(violations)


def find_latest_report(report_dir: Path) -> Optional[Path]:
    """Find the latest Ruff report in the specified directory.

    Args:
        report_dir: Directory containing report files

    Returns:
        Path to the latest report file or None if no reports found
    """
    report_files = list(report_dir.glob("*.json"))
    if not report_files:
        return None
    
    # Sort by modification time (newest first)
    return sorted(report_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


@app.command()
def analyze(
    project_path: Path | None = typer.Argument(
        None, help="Path to the project directory"
    ),
    report_dir: Annotated[Path, typer.Option(help="Directory containing report files")] = Path(".ruff_report"),
    report_file: Annotated[Optional[Path], typer.Option(help="Specific report file to analyze")] = None,
):
    """Analyze Ruff reports for the specified project.

    If no path is provided, use the current directory.
    If no report file is specified, the latest report will be analyzed.
    """
    if project_path is None:
        project_path = Path.cwd()
    
    # Resolve the report directory path
    if not report_dir.is_absolute():
        report_dir = project_path / report_dir
    
    if report_file:
        # Use the specified report file
        if not report_file.is_absolute():
            report_file = report_dir / report_file
        
        if not report_file.exists():
            console.print(f"[bold red]Error:[/] Report file {report_file} does not exist")
            return
        
        analyze_report(report_file)
    else:
        # Find and analyze the latest report
        latest_report = find_latest_report(report_dir)
        if not latest_report:
            console.print(f"[bold yellow]Warning:[/] No report files found in {report_dir}")
            return
        
        analyze_report(latest_report)


if __name__ == "__main__":
    app()
