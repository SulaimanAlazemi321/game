#!/usr/bin/env python3
"""
Study Hours Updater Script
Adds 2 hours to the study hours counter in the portfolio website
and pushes changes to GitHub.
"""

import re
import subprocess
import sys
from datetime import datetime

def update_study_hours(file_path, hours_to_add=2):
    """
    Update the study hours in the HTML file by adding the specified hours.
    
    Args:
        file_path (str): Path to the HTML file
        hours_to_add (int): Number of hours to add (default: 2)
    
    Returns:
        tuple: (old_hours, new_hours, success)
    """
    try:
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the current study hours value
        hours_pattern = r'<span id="study-hours-value">(\d+)</span>'
        hours_match = re.search(hours_pattern, content)
        
        if not hours_match:
            print("❌ Could not find study hours value in the HTML file")
            return None, None, False
        
        # Get current hours and calculate new hours
        current_hours = int(hours_match.group(1))
        new_hours = current_hours + hours_to_add
        
        # Calculate new percentage (out of 10,000 hours)
        new_percentage = (new_hours / 10000) * 100
        
        # Update the hours value
        content = re.sub(
            r'<span id="study-hours-value">\d+</span>',
            f'<span id="study-hours-value">{new_hours}</span>',
            content
        )
        
        # Update the percentage display
        percentage_pattern = r'<span id="study-hours-percentage"[^>]*>[\d.]+%</span>'
        content = re.sub(
            percentage_pattern,
            f'<span id="study-hours-percentage" style="float: right;">{new_percentage:.2f}%</span>',
            content
        )
        
        # Update the progress bar width
        progress_pattern = r'<div class="skill-level" id="study-skill-bar-level" style="width: [\d.]+%;">'
        content = re.sub(
            progress_pattern,
            f'<div class="skill-level" id="study-skill-bar-level" style="width: {new_percentage:.2f}%;">',
            content
        )
        
        # Update mobile version - percentage in span (handle both closing tag formats)
        mobile_percentage_pattern = r'<span class="percentage"[^>]*>[\d.]+%\s*</span\s*>'
        content = re.sub(
            mobile_percentage_pattern,
            f'<span class="percentage" style="margin-left: 12px;">{new_percentage:.2f}% </span >',
            content
        )
        
        # Update mobile version - study count
        mobile_count_pattern = r'<div class="study-count">\d+ / 10,000</div>'
        content = re.sub(
            mobile_count_pattern,
            f'<div class="study-count">{new_hours} / 10,000</div>',
            content
        )
        
        # Update mobile version - progress bar width
        mobile_progress_pattern = r'<div class="skill-level" style="width: [\d.]+%; height: 100%; background: var\(--primary-color\);">'
        content = re.sub(
            mobile_progress_pattern,
            f'<div class="skill-level" style="width: {new_percentage:.2f}%; height: 100%; background: var(--primary-color);">',
            content
        )
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"✅ Successfully updated study hours (both desktop and mobile versions):")
        print(f"   Previous: {current_hours} hours ({((current_hours/10000)*100):.2f}%)")
        print(f"   New: {new_hours} hours ({new_percentage:.2f}%)")
        print(f"   Added: {hours_to_add} hours")
        
        # Debug: Check if mobile patterns were found and updated (check after updates)
        mobile_percentage_check = re.search(rf'<span class="percentage"[^>]*>{new_percentage:.2f}%\s*</span\s*>', content)
        mobile_count_check = re.search(rf'<div class="study-count">{new_hours} / 10,000</div>', content)
        mobile_progress_check = re.search(rf'<div class="skill-level" style="width: {new_percentage:.2f}%; height: 100%; background: var\(--primary-color\);">', content)
        
        print(f"   📱 Mobile version updates:")
        print(f"      • Percentage span: {'✅ Found and updated' if mobile_percentage_check else '❌ Not found'}")
        print(f"      • Study count: {'✅ Found and updated' if mobile_count_check else '❌ Not found'}")
        print(f"      • Progress bar: {'✅ Found and updated' if mobile_progress_check else '❌ Not found'}")
        
        return current_hours, new_hours, True
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None, None, False
    except Exception as e:
        print(f"❌ Error updating study hours: {str(e)}")
        return None, None, False

def run_git_command(command, description):
    """
    Run a git command and handle errors.
    
    Args:
        command (list): Git command as a list
        description (str): Description of what the command does
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to {description.lower()}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        if e.stdout:
            print(f"   Output: {e.stdout.strip()}")
        return False
    except FileNotFoundError:
        print(f"❌ Git not found. Please make sure Git is installed and in your PATH.")
        return False

def push_to_github():
    """
    Add, commit, and push changes to GitHub.
    
    Returns:
        bool: True if successful, False otherwise
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Update study hours (+2 hours) - {timestamp}"
    
    # Check if we're in a git repository
    if not run_git_command(['git', 'status'], "Checking git status"):
        return False
    
    # Add changes
    if not run_git_command(['git', 'add', 'index.html'], "Adding changes to git"):
        return False
    
    # Check if there are changes to commit
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
        if result.returncode == 0:
            print("ℹ️  No changes to commit")
            return True
    except subprocess.CalledProcessError:
        pass  # There are changes to commit
    
    # Commit changes
    if not run_git_command(['git', 'commit', '-m', commit_message], "Committing changes"):
        return False
    
    # Push to GitHub
    if not run_git_command(['git', 'push'], "Pushing to GitHub"):
        return False
    
    print("✅ Successfully pushed changes to GitHub!")
    return True

def main():
    """
    Main function to update study hours and push to GitHub.
    """
    print("🚀 Study Hours Updater Script")
    print("=" * 50)
    
    # File path
    html_file = "index.html"
    
    # Update study hours
    old_hours, new_hours, success = update_study_hours(html_file, hours_to_add=2)
    
    if not success:
        print("❌ Failed to update study hours. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Ask user if they want to push to GitHub
    while True:
        push_choice = input("🤔 Do you want to push these changes to GitHub? (y/n): ").lower().strip()
        if push_choice in ['y', 'yes']:
            if push_to_github():
                print("\n🎉 All done! Your portfolio has been updated and pushed to GitHub.")
            else:
                print("\n⚠️  Study hours updated locally, but failed to push to GitHub.")
                print("   You can manually push the changes later using:")
                print("   git add index.html")
                print("   git commit -m 'Update study hours (+2 hours)'")
                print("   git push")
            break
        elif push_choice in ['n', 'no']:
            print("\n✅ Study hours updated locally. Changes not pushed to GitHub.")
            print("   You can manually push the changes later if needed.")
            break
        else:
            print("   Please enter 'y' for yes or 'n' for no.")
    
    print("\n📊 Summary:")
    print(f"   • Study hours updated: {old_hours} → {new_hours} hours")
    print(f"   • Progress: {((new_hours/10000)*100):.2f}% of 10,000 hours goal")
    print(f"   • File updated: {html_file}")

if __name__ == "__main__":
    main() 