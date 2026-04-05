# generate_data.py
import os
import sys
import pandas as pd
import random

# ENV guard - only allow execution in development
if os.environ.get('ENV') != 'development':
    print('ERROR: This script can only be run in development environment')
    print('Set ENV=development to proceed')
    sys.exit(1)

departments = ["ICT", "Library", "Hostel A", "Admin", "Engineering"]
issues = [
    "leaking pipe", "broken light", "car engine failure",
    "blocked drain", "faulty socket", "painting required"
]
categories = ["plumbing", "electrical", "mechanical", "civil"]

data = []

for i in range(300):
    issue = random.choice(issues)
    category = random.choice(categories)

    if "leak" in issue or "pipe" in issue:
        category = "plumbing"
    elif "light" in issue or "socket" in issue:
        category = "electrical"
    elif "engine" in issue:
        category = "mechanical"

    priority = random.choice(["Low", "Medium", "High"])

    data.append([
        random.choice(departments),
        issue,
        category,
        priority
    ])

df = pd.DataFrame(data, columns=[
    "department", "description", "category", "priority"
])

df.to_csv("data/simulated_data.csv", index=False)
