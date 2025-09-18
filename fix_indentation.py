#!/usr/bin/env python3
"""
Quick fix for dashboard.py indentation issues
"""

# Read the file
with open('frontend/dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the indentation issues around line 895-1078
fixed_lines = []
in_details_else_block = False
details_else_line = None

for i, line in enumerate(lines):
    line_num = i + 1
    
    # Find the Details tab else block
    if 'else:' in line and line_num > 890 and line_num < 900:
        details_else_line = line_num
        in_details_else_block = True
        fixed_lines.append(line)
        continue
    
    # Fix indentation for Details tab content
    if in_details_else_block and line_num > details_else_line and line_num < 1079:
        # If line starts with tab, add another tab
        if line.startswith('\t') and not line.startswith('\t\t'):
            line = '\t' + line
        # If line starts with spaces, convert to tabs and add extra tab
        elif line.startswith('    ') and not line.startswith('\t'):
            # Convert 4 spaces to 1 tab, then add extra tab
            stripped = line.lstrip(' ')
            indent_level = (len(line) - len(stripped)) // 4
            line = '\t' * (indent_level + 2) + stripped
    
    # End of Details tab
    if 'with tab_settings:' in line:
        in_details_else_block = False
    
    fixed_lines.append(line)

# Write the fixed file
with open('frontend/dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Fixed indentation issues in dashboard.py")
