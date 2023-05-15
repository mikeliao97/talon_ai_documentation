import os
import re
import json
import pprint

# Define the directory to start from
start_dir = '.'

# Create a dictionary to store the replacement mapping
replacements = {}

print("Starting first pass through .py files...")

# First pass: go through .py files and collect replacements
for dirpath, dirnames, filenames in os.walk(start_dir):
    for filename in filenames:
        if filename.endswith('.py'):
            print(f"Processing {filename}...")
            with open(os.path.join(dirpath, filename), 'r') as f:
                code = f.read()
                # Look for mod.tag("header_name", ...), mod.apps("header_name", ...), and ctx.matches with headers
                for match in re.finditer(r'mod\.tag\("([^"]+)"[^)]*\)|mod\.apps\("([^"]+)"[^)]*\)|ctx\.matches\s*=\s*r"""([^"]*)"""', code, re.DOTALL):
                    if match.group(1):
                        header_name = match.group(1)
                        header_type = 'tag'
                    elif match.group(2):
                        header_name = match.group(2)
                        header_type = 'app'
                    else:
                        for header_name in re.findall(r'(tag|app): ([^\n]+)', match.group(3)):
                            header_type, header_name = header_name
                            replacements[f'{header_type}: {header_name.strip()}'] = {}
                        continue
                    print(f"Found {header_type}: {header_name.strip()}")
                    replacements[f'{header_type}: {header_name.strip()}'] = {}
                # Look for function definitions and add them to the replacement mapping
                for match in re.finditer(r'def ([^\(]+)\([^\)]*\):\s*((?:.|\n)*?)(?=def|$)', code):
                    function_name = match.group(1)
                    function_code = match.group(2).strip()
                    # Exclude any comments and the function definition
                    function_code = re.sub(r'""".*?"""', '', function_code, flags=re.DOTALL).strip()
                    if function_code:
                        for header in replacements.keys():
                            if header in code:
                                print(f"Adding function {function_name} to {header}")
                                replacements[header][function_name] = function_code

pprint.pprint(replacements)

# Write the replacement mapping to a JSON file
with open('replacements.json', 'w') as f:
    json.dump(replacements, f, indent=4)

print("Starting second pass through .ai files...")

# Go through .ai files and replace function calls
for dirpath, dirnames, filenames in os.walk(start_dir):
    for filename in filenames:
        if filename.endswith('.ai'):
            print(f"Processing {filename}...")
            with open(os.path.join(dirpath, filename), 'r') as f:
                code = f.read()
            # Extract header from the top of the file
            header_match = re.search(r'(tag|app): ([^\n]+)', code)
            if header_match:
                header = f'{header_match.group(1)}: {header_match.group(2).strip()}'
                print(f"Header found: {header}")
                if header in replacements:
                    # Find and replace function calls
                    for function_name, function_code in replacements[header].items():
                        code = re.sub(r'user\.' + re.escape(function_name) + r'\([^\)]*\)', lambda _: function_code, code)
                    # Write the modified code back to a new file with the same name but with .ai2 extension
                    with open(os.path.join(dirpath, f"{os.path.splitext(filename)[0]}.ai"), 'w') as f:
                        f.write(code)

print("Done.")
