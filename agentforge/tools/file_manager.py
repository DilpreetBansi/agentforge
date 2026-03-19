"""File management operations."""

import os
from pathlib import Path
from typing import List, Dict, Any
import json


def read_file(path: str) -> str:
    """Read a file.

    Args:
        path: File path

    Returns:
        File contents
    """
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str) -> str:
    """Write to a file.

    Args:
        path: File path
        content: Content to write

    Returns:
        Status message
    """
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def append_file(path: str, content: str) -> str:
    """Append to a file.

    Args:
        path: File path
        content: Content to append

    Returns:
        Status message
    """
    try:
        with open(path, "a") as f:
            f.write(content)
        return f"Successfully appended to {path}"
    except Exception as e:
        return f"Error appending to file: {str(e)}"


def list_files(directory: str = ".", pattern: str = "*") -> List[str]:
    """List files in directory.

    Args:
        directory: Directory path
        pattern: Glob pattern

    Returns:
        List of file paths
    """
    try:
        path = Path(directory)
        files = list(path.glob(pattern))
        return [str(f) for f in files]
    except Exception as e:
        return [f"Error listing files: {str(e)}"]


def search_files(directory: str, query: str) -> List[Dict[str, Any]]:
    """Search for files containing text.

    Args:
        directory: Directory to search
        query: Search query

    Returns:
        List of files with matches
    """
    results = []

    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith((".py", ".txt", ".md", ".json")):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r") as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                results.append(
                                    {
                                        "file": filepath,
                                        "matches": content.lower().count(
                                            query.lower()
                                        ),
                                    }
                                )
                    except:
                        pass

        return results
    except Exception as e:
        return [{"error": str(e)}]


def delete_file(path: str) -> str:
    """Delete a file.

    Args:
        path: File path

    Returns:
        Status message
    """
    try:
        os.remove(path)
        return f"Successfully deleted {path}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"


def get_file_info(path: str) -> Dict[str, Any]:
    """Get information about a file.

    Args:
        path: File path

    Returns:
        File information
    """
    try:
        stat = os.stat(path)
        return {
            "path": path,
            "size_bytes": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_file": os.path.isfile(path),
            "is_dir": os.path.isdir(path),
        }
    except Exception as e:
        return {"error": str(e)}
