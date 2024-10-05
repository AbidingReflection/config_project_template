import os
import re
from datetime import datetime, timezone

def extract_number(entry):
    match = re.match(r'^(\d+)', entry)
    if match:
        return int(match.group(1))  # Extract and return leading number if present
    return float('inf')  # Sort entries without numbers later


def delete_existing_file_trees(output_prefix):
    """Delete existing file trees matching the output_path prefix."""
    directory = os.path.dirname(output_prefix) or "."
    for file_name in os.listdir(directory):
        if file_name.startswith(os.path.basename(output_prefix)) and file_name.endswith('.txt'):
            file_path = os.path.join(directory, file_name)
            try:
                os.remove(file_path)
                print(f"Deleted existing file: {file_path}")
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")


def generate_file_tree(target_path, output_path, exclude_prefixes=None, exclude_suffixes=None, exclude_filetypes=None, exclude_folders=None, delete_existing=False):
    if exclude_prefixes is None:
        exclude_prefixes = []
    if exclude_suffixes is None:
        exclude_suffixes = []
    if exclude_filetypes is None:
        exclude_filetypes = []
    if exclude_folders is None:
        exclude_folders = []
    
    if delete_existing:
        delete_existing_file_trees(output_path)
    
    timestamp = datetime.now(timezone.utc).strftime('%y%m%dZ%H%M%S')
    output_file = f"{output_path}_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(f"Target Path: {target_path}\n")
        file.write(f"Output Path: {output_file}\n")
        file.write(f"Exclude Prefixes: {', '.join([f'\'{prefix}\'' for prefix in exclude_prefixes])}\n")
        file.write(f"Exclude Suffixes: {', '.join([f'\'{suffix}\'' for suffix in exclude_suffixes])}\n")
        file.write(f"Exclude Filetypes: {', '.join([f'\'{filetype}\'' for filetype in exclude_filetypes])}\n")

        file.write(f"Exclude Folders: {', '.join([f'\'{folder}\'' for folder in exclude_folders])}\n\n")
        
        file.write(f"{os.path.basename(target_path)}/\n")
        
        def walk_directory(current_path, prefix="│   "):
            try:
                entries = sorted(os.listdir(current_path), key=lambda entry: (extract_number(entry), entry))
                entries = [e for e in entries if os.path.basename(e) not in exclude_folders]  # Skip excluded folders
                
                for i, entry in enumerate(entries):
                    full_path = os.path.join(current_path, entry)
                    connector = "└──" if i == len(entries) - 1 else "├──"
                    if os.path.isdir(full_path):
                        file.write(f"{prefix}{connector} {entry}/\n")
                        new_prefix = prefix + ("    " if connector == "└──" else "│   ")
                        walk_directory(full_path, new_prefix)
                    else:
                        if any(entry.startswith(p) for p in exclude_prefixes):
                            continue
                        if any(entry.endswith(s) for s in exclude_suffixes):
                            continue
                        if any(entry.endswith(ft) for ft in exclude_filetypes):
                            continue
                        file.write(f"{prefix}{connector} {entry}\n")
            except PermissionError:
                # Handle Permission Denied for both last and non-last items
                connector = "└──" if prefix.endswith("└──") else "├──"
                file.write(f"{prefix}{connector} [Permission Denied]\n")

        walk_directory(target_path)

# Example usage
target_path = r"C:\Users\decjg\projects\config_project_template"
output_file_name = r"C:\Users\decjg\projects\config_project_template\scripts\output\file_tree"
exclude_prefixes = ["file_tree_"]
exclude_suffixes = []
exclude_filetypes = []
exclude_folders = ['.git', 'venv', "__pycache__", "logs", ".pytest_cache"]

generate_file_tree(target_path, output_file_name, exclude_prefixes, exclude_suffixes, exclude_filetypes, exclude_folders, delete_existing=True)
