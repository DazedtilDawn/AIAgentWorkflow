```markdown
# Directory Management Component Documentation

## 1. Overview and Purpose

The `DirectoryManager` component provides a set of tools for managing directories within a Python application. It offers functionalities for creating, deleting, listing contents, and checking the existence of directories, all while incorporating robust error handling and logging.  This component aims to simplify directory operations and promote code maintainability by encapsulating these operations within a dedicated class.

## 2. Installation and Setup

To use the `DirectoryManager` component:

1.  **Save the code:** Save the provided Python code as a `.py` file (e.g., `directories.py`).

2.  **Import the component:** Import the `DirectoryManager` class into your Python project.

```python
from directories import DirectoryManager
```

3. **Dependencies:** Ensure that the `os`, `logging` and `shutil` (only used for recursive delete) modules are available. They are part of the Python standard library, so no additional installation is required.

## 3. API Reference

### Class: `DirectoryManager`

A class for managing directories.

#### `__init__(self, base_dir: str = ".")`

Initializes the `DirectoryManager` with a base directory. All directory operations will be relative to this base directory.

**Parameters:**

*   `base_dir` (str, optional): The base directory for all operations. Defaults to the current directory (".").

**Example:**

```python
from directories import DirectoryManager

# Initialize with the current directory as the base
dir_manager = DirectoryManager()

# Initialize with a specific base directory
dir_manager = DirectoryManager("/path/to/my/base/directory")
```

#### `create_directory(self, dir_name: str, exist_ok: bool = False) -> bool`

Creates a new directory under the base directory.

**Parameters:**

*   `dir_name` (str): The name of the directory to create.
*   `exist_ok` (bool, optional):  If `True`, the function will not raise an exception if the target directory already exists.  Defaults to `False`.

**Returns:**

*   `bool`: `True` if the directory was created successfully, `False` if the directory already exists and `exist_ok` is `True`.

**Raises:**

*   `ValueError`: If `dir_name` is empty.
*   `FileExistsError`: If the directory already exists and `exist_ok` is `False`.
*   `OSError`: If there's an error creating the directory (e.g., permission issues).

**Example:**

```python
from directories import DirectoryManager

dir_manager = DirectoryManager()

try:
    if dir_manager.create_directory("new_directory"):
        print("Directory created successfully.")
    else:
        print("Directory already existed")

    dir_manager.create_directory("another_directory", exist_ok=True)  # Doesn't raise error if it exists
except (ValueError, OSError) as e:
    print(f"Error creating directory: {e}")

try:
    dir_manager.create_directory("new_directory") #Creates a directory that already exists, raises error
except (ValueError, OSError) as e:
    print(f"Error creating directory: {e}")

```

#### `delete_directory(self, dir_name: str, recursive: bool = False) -> bool`

Deletes a directory under the base directory.

**Parameters:**

*   `dir_name` (str): The name of the directory to delete.
*   `recursive` (bool, optional): If `True`, delete the directory and all its contents. If `False`, only delete if the directory is empty. Defaults to `False`.

**Returns:**

*   `bool`: `True` if the directory was deleted successfully.

**Raises:**

*   `ValueError`: If `dir_name` is empty.
*   `FileNotFoundError`: If the directory does not exist.
*   `OSError`: If there's an error deleting the directory (e.g., permission issues, directory not empty, etc.).

**Example:**

```python
from directories import DirectoryManager

dir_manager = DirectoryManager()

try:
    dir_manager.delete_directory("empty_directory")  # Deletes an empty directory
    dir_manager.delete_directory("non_empty_directory", recursive=True)  # Deletes a directory and its contents
except (ValueError, FileNotFoundError, OSError) as e:
    print(f"Error deleting directory: {e}")
```

#### `list_directory_contents(self, dir_name: str = ".") -> List[str]`

Lists the contents of a directory under the base directory.

**Parameters:**

*   `dir_name` (str, optional): The name of the directory to list. Defaults to the base directory.

**Returns:**

*   `List[str]`: A list of strings representing the names of the files and directories in the specified directory.

**Raises:**

*   `ValueError`: If `dir_name` is empty.
*   `FileNotFoundError`: If the directory does not exist.
*   `OSError`: If there's an error accessing the directory (e.g., permission issues).

**Example:**

```python
from directories import DirectoryManager

dir_manager = DirectoryManager()

try:
    contents = dir_manager.list_directory_contents()  # Lists contents of the base directory
    print(f"Contents of directory: {contents}")

    contents = dir_manager.list_directory_contents("my_directory") # Lists contents of subdirectory
    print(f"Contents of 'my_directory': {contents}")

except (ValueError, FileNotFoundError, OSError) as e:
    print(f"Error listing directory contents: {e}")
```

#### `check_if_directory_exists(self, dir_name: str) -> bool`

Checks if a directory exists.

**Parameters:**

*   `dir_name` (str): The name of the directory to check.

**Returns:**

*   `bool`: `True` if the directory exists, `False` otherwise.

**Raises:**

*   `ValueError`: If `dir_name` is empty.

**Example:**

```python
from directories import DirectoryManager

dir_manager = DirectoryManager()

if dir_manager.check_if_directory_exists("my_directory"):
    print("Directory exists.")
else:
    print("Directory does not exist.")
```

## 4. Dependencies

The `DirectoryManager` component relies on the following Python standard library modules:

*   `os`: For interacting with the operating system (creating, deleting, listing directories).
*   `logging`: For logging events and errors.
*   `shutil`: Used exclusively in the `delete_directory` function when the `recursive` parameter is set to True. This module is only imported when needed.
*   `typing`: Used for type hinting to improve code clarity and maintainability.

These dependencies are typically readily available in most Python environments. No external installation is usually required.

## 5. Error Handling

The `DirectoryManager` component implements robust error handling using `try...except` blocks and raises exceptions for various error conditions:

*   **ValueError:** Raised if a directory name is empty.
*   **FileNotFoundError:** Raised if a directory does not exist when attempting to delete it or list its contents.
*   **OSError:** Raised if any operating system-level error occurs (e.g., permission issues, directory not empty during deletion).
*   **FileExistsError**: Raised if a directory already exists during creation and `exist_ok` is `False`.

The component also utilizes the `logging` module to record informative messages, warnings, and errors, facilitating debugging and monitoring.

## 6. Performance Considerations

*   **Recursive Deletion:**  The `delete_directory` function with `recursive=True` can be resource-intensive for directories with a large number of files and subdirectories.  Consider the potential performance impact when using this option.
*   **Large Directory Listings:**  Listing the contents of very large directories using `list_directory_contents` can consume significant memory.  If dealing with extremely large directories, consider alternative approaches, such as iterating through the directory contents using `os.scandir`.

## 7. Security Considerations

*   **Input Validation:**  The component performs basic input validation by checking for empty directory names.  However, it's crucial to sanitize directory names further, especially if they originate from user input, to prevent potential path traversal vulnerabilities.  Avoid using directory names that contain characters like "..", "/", or "\".
*   **Permissions:** Ensure that the application has the necessary permissions to create, delete, and list directories within the specified base directory. Incorrect permissions can lead to `OSError` exceptions.
*   **Base Directory Restriction:** It's recommended to restrict the `base_dir` to a specific location within the file system to prevent unintended modifications to sensitive system directories.  Avoid using "/" as the base directory.

## 8. Usage Examples

**Example 1: Basic Directory Management**

```python
from directories import DirectoryManager
import os

# Create a DirectoryManager instance with a specific base directory
base_dir = "my_app_data"
dir_manager = DirectoryManager(base_dir)

# Ensure base directory exists
if not os.path.exists(base_dir):
    os.makedirs(base_dir)


# Create a new directory
new_dir = "user_files"
try:
    if dir_manager.create_directory(new_dir):
        print(f"Directory '{new_dir}' created successfully.")
    else:
        print(f"Directory '{new_dir}' already existed.")
except OSError as e:
    print(f"Error creating directory: {e}")

# List directory contents
try:
    contents = dir_manager.list_directory_contents()
    print(f"Contents of '{base_dir}': {contents}")
except OSError as e:
    print(f"Error listing directory contents: {e}")


# Check if a directory exists
check_dir = "user_files"
if dir_manager.check_if_directory_exists(check_dir):
    print(f"Directory '{check_dir}' exists.")
else:
    print(f"Directory '{check_dir}' does not exist.")

# Delete a directory
try:
    if dir_manager.delete_directory(new_dir):
        print(f"Directory '{new_dir}' deleted successfully.")
    else:
        print(f"Directory '{new_dir}' could not be deleted.  Does it exist?")
except OSError as e:
    print(f"Error deleting directory: {e}")

```

**Example 2: Handling Exceptions**

```python
from directories import DirectoryManager

dir_manager = DirectoryManager()

try:
    # Attempt to create a directory with an invalid name
    dir_manager.create_directory("")
except ValueError as e:
    print(f"Error: {e}")

try:
    # Attempt to delete a non-existent directory
    dir_manager.delete_directory("nonexistent_dir")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

This comprehensive documentation provides a clear understanding of the `DirectoryManager` component, including its purpose, installation, API, error handling, and usage examples.  It addresses important considerations for performance and security to help developers use the component effectively and responsibly.
```