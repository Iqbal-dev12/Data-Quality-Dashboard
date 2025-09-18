#!/usr/bin/env python3
"""
Comprehensive fix for all indentation issues in dashboard.py
"""

def fix_dashboard_indentation():
    # Read the file
    with open('frontend/dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Find and fix specific problematic sections
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # Fix the specific indentation issues around the Details tab
        if line_num >= 894 and line_num <= 1078:
            # Fix the "with left:" block content
            if line.strip().startswith('# show filtered table') and not line.startswith('\t\t\t'):
                line = '\t\t\t' + line.strip()
            elif line.strip().startswith('view_df = rows_df') and not line.startswith('\t\t\t'):
                line = '\t\t\t' + line.strip()
            elif line.strip().startswith('if st.session_state.show_') and not line.startswith('\t\t\t'):
                line = '\t\t\t' + line.strip()
            elif line.strip().startswith('view_df = rows_df[rows_df["status"]') and not line.startswith('\t\t\t\t'):
                line = '\t\t\t\t' + line.strip()
            elif line.strip().startswith('elif st.session_state.show_') and not line.startswith('\t\t\t'):
                line = '\t\t\t' + line.strip()
            
            # Fix the "with right:" block
            elif line.strip() == 'with right:' and not line.startswith('\t\t'):
                line = '\t\tswith right:'
            elif line.strip().startswith('st.markdown("<div class=\'section-title\'>Extra Metrics') and not line.startswith('\t\t\t'):
                line = '\t\t\t' + line.strip()
            elif line.strip().startswith('st.metric("% Missing') and not line.startswith('\t\t\t'):
                line = '\t\t\t' + line.strip()
            elif line.strip().startswith('st.metric("Duplicate rows') and not line.startswith('\t\t\t'):
                line = '\t\t\t' + line.strip()
            
            # Fix other indentation issues in the Details tab
            elif line.strip() and line_num > 894 and line_num < 1078:
                if not line.startswith('\t') and not line.startswith('with tab_'):
                    # This line should be indented
                    if line.strip().startswith('#') or line.strip().startswith('try:') or line.strip().startswith('except'):
                        line = '\t\t\t' + line.strip()
                    elif line.strip().startswith('def ') or line.strip().startswith('if ') or line.strip().startswith('else:'):
                        line = '\t\t\t' + line.strip()
                    elif line.strip().startswith('st.') or line.strip().startswith('styled') or line.strip().startswith('view_df'):
                        line = '\t\t\t' + line.strip()
                    elif line.strip().startswith('c1, c2, c3') or line.strip().startswith('with c'):
                        line = '\t\t\t' + line.strip()
        
        fixed_lines.append(line)
        i += 1
    
    # Write the fixed content back
    with open('frontend/dashboard.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed all indentation issues in dashboard.py")

if __name__ == "__main__":
    fix_dashboard_indentation()
