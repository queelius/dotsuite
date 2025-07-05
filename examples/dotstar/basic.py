"""Basic examples of dotstar usage."""

from dotstar import search, find_all, Pattern

# Sample data - a company structure
data = {
    "company": "TechCorp",
    "departments": {
        "engineering": {
            "manager": "Alice",
            "employees": [
                {"name": "Bob", "role": "Backend Dev", "level": 3},
                {"name": "Carol", "role": "Frontend Dev", "level": 2},
                {"name": "Dave", "role": "DevOps", "level": 3}
            ]
        },
        "sales": {
            "manager": "Eve",
            "employees": [
                {"name": "Frank", "role": "Account Exec", "level": 2},
                {"name": "Grace", "role": "Sales Engineer", "level": 3}
            ]
        },
        "hr": {
            "manager": "Henry",
            "employees": [
                {"name": "Iris", "role": "Recruiter", "level": 1}
            ]
        }
    }
}

print("=== Basic Search ===")

# Get all employee names
all_names = search(data, "departments.*.employees.*.name")
print(f"All employees: {all_names}")

# Get all managers
managers = search(data, "departments.*.manager")
print(f"All managers: {managers}")

# Get all level 3 employees
levels = search(data, "departments.*.employees.*.level")
print(f"All levels: {levels}")

print("\n=== Finding Paths ===")

# Find where all level 3 employees are
level_3_locations = find_all(data, "departments.*.employees.*")
for path, employee in level_3_locations:
    if isinstance(employee, dict) and employee.get('level') == 3:
        print(f"Level 3 employee {employee['name']} at {path}")

print("\n=== Using Patterns ===")

# Create reusable patterns
ALL_EMPLOYEES = Pattern("departments.*.employees.*")
EMPLOYEE_NAMES = ALL_EMPLOYEES / "name"
EMPLOYEE_ROLES = ALL_EMPLOYEES / "role"

print(f"All names via pattern: {EMPLOYEE_NAMES.search(data)}")
print(f"All roles via pattern: {EMPLOYEE_ROLES.search(data)}")

print("\n=== Practical Example ===")

# Find all email addresses in a response
api_response = {
    "users": [
        {
            "id": 1,
            "profile": {"email": "alice@example.com", "phone": "555-0001"}
        },
        {
            "id": 2,
            "profile": {"email": "bob@example.com", "phone": "555-0002"}
        }
    ],
    "admins": [
        {"email": "admin@example.com", "level": "super"}
    ]
}

# Get all emails regardless of where they are
all_emails = search(api_response, "*.*.email")
print(f"All emails found: {all_emails}")
