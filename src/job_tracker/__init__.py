from job_tracker.db import init_db
from job_tracker.main import cli


def main() -> None:
    init_db()
    cli(standalone_mode=True)
