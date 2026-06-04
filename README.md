# job-tracker

A command-line job application tracker that stores applications, recruiter
contacts, and activity logs locally in SQLite. Helps you stay on top of
every application without losing track of where things stand especially with a lot of applications.

## Usage

Install the tool:

    uv tool install "git+https://github.com/matthewviray/job-tracker.git"

Add a new application:

    job-tracker add "Farmers Insurance" "Data Science Intern" --status applied

List all applications:

    job-tracker list
    job-tracker list --status interview
    job-tracker list --company "Sony"

Update an application:

    job-tracker update 1 --status interview --notes "HR screen completed"

View full details and activity log:

    job-tracker show 1

Log an activity:

    job-tracker log 1 "Sent thank-you email"

Add a recruiter contact:

    job-tracker contact 1 "Jane Smith" --role "HR Recruiter" --email "recruiter@company.com"

View application funnel stats:

    job-tracker stats
