import os
import re

# Define the path to the directory containing the .talon files.
# Replace 'your_path_here' with the actual path.
path = '.'

# This will hold our tag mappings.
tag_map = {}

# First, loop over all the files in the directory to build the tag map.
for dirpath, dirnames, filenames in os.walk(path):
    for filename in filenames:
        if filename.endswith('.talon'):
            with open(os.path.join(dirpath, filename), 'r') as file:
                lines = file.readlines()

                # Look for the 'tag: ' line to find the tag name.
                tag_name_line = [line for line in lines if line.startswith('tag:')]
                if tag_name_line:
                    tag_name = tag_name_line[0].replace('tag:', '').strip()

                    # Store the content of the file (excluding the 'tag:' line and '-' lines) in the map.
                    tag_content = [line for line in lines if not line.startswith('tag:') and line.strip() != '-']
                    tag_map[tag_name] = tag_content

# Now, loop over the files again to replace the tags.
for dirpath, dirnames, filenames in os.walk(path):
    for filename in filenames:
        if filename.endswith('.talon'):
            with open(os.path.join(dirpath, filename), 'r') as file:
                lines = file.readlines()

                # Look for lines with 'tag(): ' and replace them with the corresponding tag content.
                new_lines = []
                for line in lines:
                    match = re.search(r'tag\(\):\s*(\S+)', line)
                    if match:
                        tag_name = match.group(1)
                        if tag_name in tag_map:
                            new_lines.append(f'### {tag_name}\n')  # Add the tag name as a comment.
                            new_lines.extend(tag_map[tag_name])
                    else:
                        new_lines.append(line)

                # Remove any '-' lines from the new lines.
                new_lines = [line for line in new_lines if line.strip() != '-']

                # Write the new lines to a .ai file.
                with open(os.path.join(dirpath, filename.replace('.talon', '.ai')), 'w') as output_file:
                    output_file.write(''.join(new_lines))
                    print(f"Modified and created new file: {os.path.join(dirpath, filename.replace('.talon', '.ai'))}")
