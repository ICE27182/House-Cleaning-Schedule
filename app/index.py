

from flask import Blueprint, render_template, send_file
index = Blueprint("index", __name__)

# Generated by ChatGPT-4o with modification
import os
def file_tree(directory: str = ".", prefix: str = "", full_dir: str = "../") -> str:
    """
    Recursively generates the file tree of a directory as a string.

    Args:
        directory (str): The directory to display the file tree for.
        prefix (str): The prefix used for indentation (used internally for recursion).

    Returns:
        str: The directory tree structure as a string.
    """
    lines = []
    
    try:
        # Get all files and directories in the given directory
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return f"{prefix}Permission denied: {directory}\n"
    except FileNotFoundError:
        return f"{prefix}Directory not found: {directory}\n"

    # Iterate over each entry
    for i, entry in enumerate(entries):
        if entry.startswith('.') or entry == "__pycache__":
            continue
        # Check if it's the last entry in the directory
        is_last = (i == len(entries) - 1)
        
        # Full path of the entry
        entry_path = os.path.join(directory, entry)

        # Add the appropriate prefix for this entry
        connector = "└── " if is_last else "├── "
        lines.append(
            f"{prefix}{connector}" +
            (
                f"{entry}" if os.path.isdir(entry_path) else
                (f"<a href=\"{full_dir}{entry}\" download>{entry}</a>")
            )
        )
        
        # If the entry is a directory, recurse into it
        if os.path.isdir(entry_path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(file_tree(entry_path, new_prefix, f"{full_dir}{entry}/"))

    return "<p>" + "</p><p>".join(lines) + "</p>"

from random import random as rd
@index.route("/dont_click")
def route_dont_click():
    return render_template(
        "index.html", 
        random = str(rd()),
        files = file_tree()
    )

@index.route('/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    filepath = os.path.join(index.root_path, "..",filename)
    return send_file(filepath)