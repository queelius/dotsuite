"""Basic examples of dotget usage."""

from dotget import get, exists, Path

# Sample data
data = {
    "company": {
        "name": "Acme Corp",
        "employees": [
            {
                "id": 1,
                "name": "Alice Johnson",
                "email": "alice@acme.com",
                "department": {
                    "name": "Engineering",
                    "budget": 500000
                }
            },
            {
                "id": 2,
                "name": "Bob Smith",
                "email": "bob@acme.com",
                "department": {
                    "name": "Sales",
                    "budget": 300000
                }
            }
        ]
    }
}

# Basic access
print(f"Company: {get(data, 'company.name')}")
print(f"First employee: {get(data, 'company.employees.0.name')}")
print(f"Budget: ${get(data, 'company.employees.0.department.budget'):,}")

# With defaults
print(f"CEO: {get(data, 'company.ceo', 'Not specified')}")
print(f"Third employee: {get(data, 'company.employees.2.name', 'No one')}")

# Check existence
if exists(data, "company.employees"):
    print(f"Company has {len(get(data, 'company.employees'))} employees")

# Using Path objects
FIRST_EMPLOYEE = Path("company.employees.0")
print(f"\nUsing paths:")
print(f"Name: {(FIRST_EMPLOYEE / 'name').get(data)}")
print(f"Email: {(FIRST_EMPLOYEE / 'email').get(data)}")
print(f"Dept: {(FIRST_EMPLOYEE / 'department.name').get(data)}")
