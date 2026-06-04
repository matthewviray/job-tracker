# Jobs CLI

A command-line job application tracker that stores applications, recruiter
contacts, and activity logs locally in SQLite. Helps you stay on top of
every application without losing track of where things stand.

## Usage

Install the tool:

    uv add "git+https://github.com/matthewviray/job-tracker.git"

Add a new application:

    jobs add "Farmers Insurance" "Data Science Intern" --status applied

List all applications:

    jobs list
    jobs list --status interviewing
    jobs list --company "Sony"

Update an application:

    jobs update 1 --status interviewing --note "HR screen completed"

View full detail and activity log:

    jobs show 1

Log an activity:

    jobs log 1 "Sent thank-you email"

Add a recruiter contact:

    jobs contact 1 "Jane Smith" --role "HR Recruiter" --email "recruiter@company.com"

View application funnel stats:

    jobs stats