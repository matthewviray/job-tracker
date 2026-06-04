import datetime

import click

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
