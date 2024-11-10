import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

def extract_number(entry: str) -> int:
    """Extract leading number for sorting, default to infinity if none found."""
    match = re.match(r'^(\d+)', entry)
    return int(match.group(1)) if match else float('inf')

def archive_existing_file_trees(output_prefix: Path) -> None:
    """Archive existing file trees by moving them to an 'archive' folder."""
    archive_dir = output_prefix.parent / 'archive'
    archive_dir.mkdir(exist_ok=True)
    
    for file_path in output_prefix.parent.glob(f"{output_prefix.stem}*.txt"):
        try:
            archived_file_path = archive_dir / file_path.name
            file_path.rename(archived_file_path)
            print(f"Archived existing file: {file_path} -> {archived_file_path}")
        except OSError as e:
            print(f"Error archiving file {file_path}: {e}")

class ExclusionFilter:
    """Callable class to filter out files and directories based on exclusion rules."""
    def __init__(self, prefixes: List[str], suffixes: List[str], filetypes: List[str], folders: List[str]):
        self.prefixes = prefixes
        self.suffixes = suffixes
        self.filetypes = filetypes
        self.folders = folders

    def __call__(self, entry: Path) -> bool:
        return (
            any(entry.name.startswith(prefix) for prefix in self.prefixes) or
            any(entry.name.endswith(suffix) for suffix in self.suffixes) or
            entry.suffix in self.filetypes or
            entry.name in self.folders
        )

def format_exclusions(exclude_config: Dict[str, List[str]]) -> str:
    """Format exclusions for output file."""
    formatted_exclusions = "Exclusions:\n"
    for key, values in exclude_config.items():
        formatted_exclusions += f"  {key.capitalize()}:\n"
        if values:
            for value in values:
                formatted_exclusions += f"    - {value}\n"
        else:
            formatted_exclusions += "    - None\n"
    return formatted_exclusions

def generate_file_tree(
    target_path: Path, 
    output_path: Path, 
    exclude_config: Dict[str, List[str]], 
    archive_previous: bool = True
) -> None:
    """Generate a file tree for target_path and save to output_path."""
    
    exclude_filter = ExclusionFilter(
        exclude_config.get("prefixes", []),
        exclude_config.get("suffixes", []),
        exclude_config.get("filetypes", []),
        exclude_config.get("folders", [])
    )

    # Archive existing file trees if enabled
    if archive_previous:
        archive_existing_file_trees(output_path)

    timestamp = datetime.now(timezone.utc).strftime('%y%m%dZ%H%M%S')
    output_file = f"{output_path}_{timestamp}.txt"

    with open(output_file, 'w', encoding='utf-8') as file:
        # Write header paths
        file.write(f"Target Path: {target_path}\n")
        file.write(f"Output Path: {output_file}\n\n")
        
        # Write the root target directory
        file.write(f"{target_path.name}/\n")

        def walk_directory(current_path: Path, prefix: str = "│   "):
            try:
                entries = sorted(current_path.iterdir(), key=lambda entry: (extract_number(entry.name), entry.name))
                entries = [entry for entry in entries if not exclude_filter(entry)]

                for i, entry in enumerate(entries):
                    connector = "└──" if i == len(entries) - 1 else "├──"
                    if entry.is_dir():
                        file.write(f"{prefix}{connector} {entry.name}/\n")
                        walk_directory(entry, prefix + ("    " if connector == "└──" else "│   "))
                    else:
                        file.write(f"{prefix}{connector} {entry.name}\n")
            except PermissionError as e:
                file.write(f"{prefix}└── [Permission Denied: {current_path}]\n")

        # Walk the directory and write the file tree structure
        walk_directory(target_path)
        
        # Write exclusions after the file tree
        file.write("\n" + format_exclusions(exclude_config))

if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    target_path = current_dir.parent
    output_dir = current_dir / 'output'
    output_dir.mkdir(exist_ok=True)

    exclude_config = {
        "prefixes": ["file_tree_"],
        "suffixes": [],
        "filetypes": [],
        "folders": ['.git', 'venv', "__pycache__", "logs", ".pytest_cache"]
    }

    generate_file_tree(target_path, output_dir / 'file_tree', exclude_config, archive_previous=True)
