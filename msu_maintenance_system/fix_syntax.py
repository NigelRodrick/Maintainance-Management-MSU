import re

# Read the file
with open('c:/Users/dell/Desktop/V1/CENTRAL SERVICES AMENTIES AND MAINTENANCE/msu_maintenance_system/app/utils/access_control.py', 'r') as f:
    content = f.read()

# Fix missing commas in dictionaries throughout the file
# Pattern: dictionary entries without commas
content = re.sub(r'(\"[^"]+\"|\'[^\']+\'|\w+):\s*([^,\n]+)\n(?!\s*[,\]\}])', r'\1: \2,\n', content)

# Write back
with open('c:/Users/dell/Desktop/V1/CENTRAL SERVICES AMENTIES AND MAINTENANCE/msu_maintenance_system/app/utils/access_control.py', 'w') as f:
    f.write(content)

print('Fixed comma syntax errors in access_control.py')
