from job_tracker.db import init_db


def main() -> None:
    init_db()
    print("Hello from job-tracker!")
