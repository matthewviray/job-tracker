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


@cli.command()
@click.argument("id", type=int)
@click.option("--status", default=None)
@click.option("--notes", default=None)
@click.option("--next-action", default=None)
@click.option("--url", default=None)
def update(id: int, status: str | None, notes: str | None, next_action: str | None, url: str | None) -> None:
    fields = {"status": status, "notes": notes, "next_action": next_action, "url": url}
    updates = {k: v for k, v in fields.items() if v is not None}

    if not updates:
        click.echo("No fields to update.")
        return

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    params = list(updates.values()) + [id]

    with get_connection() as conn:
        cursor = conn.execute(f"UPDATE applications SET {set_clause} WHERE id = ?", params)
        if cursor.rowcount == 0:
            click.echo(f"No application found with ID {id}.")
            return

    click.echo(f"Updated application #{id}.")


@cli.command()
@click.argument("id", type=int)
@click.argument("note")
def log(id: int, note: str) -> None:
    with get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM applications WHERE id = ?", (id,)).fetchone()
        if not exists:
            click.echo(f"No application found with ID {id}.")
            return
        timestamp = datetime.datetime.now().isoformat()
        conn.execute(
            "INSERT INTO activity_log (application_id, timestamp, note) VALUES (?, ?, ?)",
            (id, timestamp, note),
        )
    click.echo(f"Logged: {note}")


@cli.command()
@click.argument("id", type=int)
def show(id: int) -> None:
    from rich.panel import Panel
    from rich.text import Text

    console = Console()

    with get_connection() as conn:
        app = conn.execute(
            "SELECT company, role, status, url, notes, applied_date, next_action FROM applications WHERE id = ?",
            (id,),
        ).fetchone()

        if not app:
            click.echo(f"No application found with ID {id}.")
            return

        logs = conn.execute(
            "SELECT timestamp, note FROM activity_log WHERE application_id = ? ORDER BY timestamp",
            (id,),
        ).fetchall()

        contacts = conn.execute(
            "SELECT name, role, email FROM contacts WHERE application_id = ?",
            (id,),
        ).fetchall()

    company, role, status, url, notes, applied_date, next_action = app

    details = Text()
    details.append(f"Role:        ", style="bold")
    details.append(f"{role}\n")
    details.append(f"Status:      ", style="bold")
    details.append(f"{status}\n")
    details.append(f"Applied:     ", style="bold")
    details.append(f"{applied_date or '—'}\n")
    details.append(f"URL:         ", style="bold")
    details.append(f"{url or '—'}\n")
    details.append(f"Next Action: ", style="bold")
    details.append(f"{next_action or '—'}\n")
    details.append(f"Notes:       ", style="bold")
    details.append(f"{notes or '—'}")

    console.print(Panel(details, title=f"[bold]{company}[/bold]", expand=False))

    if logs:
        console.print("\n[bold]Activity[/bold]")
        for timestamp, note in logs:
            date = timestamp[:10]
            console.print(f"  {date}  {note}")

    if contacts:
        console.print("\n[bold]Contacts[/bold]")
        for name, role, email in contacts:
            parts = "  " + (name or "—")
            if role:
                parts += f"  ({role})"
            if email:
                parts += f"  {email}"
            console.print(parts)


@cli.command()
def stats() -> None:
    from rich.panel import Panel

    console = Console()

    with get_connection() as conn:
        rows = conn.execute("SELECT status, applied_date FROM applications").fetchall()

    if not rows:
        click.echo("No applications found.")
        return

    total = len(rows)
    status_counts: dict[str, int] = {}
    month_counts: dict[str, int] = {}

    for status, applied_date in rows:
        status_counts[status] = status_counts.get(status, 0) + 1
        if applied_date and len(applied_date) >= 7:
            month = applied_date[:7]
            month_counts[month] = month_counts.get(month, 0) + 1

    applied_statuses = {"applied"}
    responded = sum(v for k, v in status_counts.items() if k not in applied_statuses)
    offered = sum(v for k, v in status_counts.items() if k in {"offered", "accepted"})
    response_rate = responded / total * 100
    offer_rate = offered / total * 100

    max_count = max(status_counts.values())
    bar_width = 30

    console.print("\n[bold]Funnel by Status[/bold]")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        bar_len = round(count / max_count * bar_width)
        bar = "█" * bar_len
        console.print(f"  {status:<14} {bar} {count}")

    if month_counts:
        max_month = max(month_counts.values())
        console.print("\n[bold]Applications by Month[/bold]")
        for month in sorted(month_counts):
            bar_len = round(month_counts[month] / max_month * bar_width)
            bar = "█" * bar_len
            console.print(f"  {month}  {bar} {month_counts[month]}")

    console.print(
        f"\nTotal: [bold]{total}[/bold]  |  "
        f"Response rate: [bold]{response_rate:.0f}%[/bold]  |  "
        f"Offer rate: [bold]{offer_rate:.0f}%[/bold]"
    )


@cli.command()
@click.argument("id", type=int)
@click.argument("name")
@click.option("--role", default=None)
@click.option("--email", default=None)
def contact(id: int, name: str, role: str | None, email: str | None) -> None:
    with get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM applications WHERE id = ?", (id,)).fetchone()
        if not exists:
            click.echo(f"No application found with ID {id}.")
            return
        conn.execute(
            "INSERT INTO contacts (application_id, name, role, email) VALUES (?, ?, ?, ?)",
            (id, name, role, email),
        )
    click.echo(f"Added contact: {name} for application #{id}.")
