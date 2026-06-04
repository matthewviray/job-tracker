import datetime

import click
from rich.table import Table
from rich.console import Console

from job_tracker.db import get_connection


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("company")
@click.argument("role")
@click.option("--status", default="applied", show_default=True)
@click.option("--url", default=None)
@click.option("--notes", default=None)
@click.option("--next-action", default=None)
def add(company: str, role: str, status: str, url: str | None, notes: str | None, next_action: str | None) -> None:
    applied_date = datetime.date.today().strftime("%Y-%m-%d")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO applications (company, role, status, url, notes, applied_date, next_action) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (company, role, status, url, notes, applied_date, next_action),
        )
    click.echo(f"Added: {company} — {role} ({status})")


@cli.command(name="list")
@click.option("--status", default=None)
@click.option("--company", default=None)
def list_apps(status: str | None, company: str | None) -> None:
    query = "SELECT id, company, role, status, applied_date, next_action FROM applications WHERE 1=1"
    params: list[str] = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if company:
        query += " AND company LIKE ?"
        params.append(f"%{company}%")

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    if not rows:
        click.echo("No applications found.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Company")
    table.add_column("Role")
    table.add_column("Status")
    table.add_column("Applied")
    table.add_column("Next Action")

    for row in rows:
        table.add_row(*(str(v) if v is not None else "" for v in row))

    Console().print(table)
