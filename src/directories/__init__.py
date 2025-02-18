import os
import logging
from typing import List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DirectoryManager:
    """
    A class for managing directories, including creation, deletion, and listing contents.

    Handles basic directory operations with error handling and logging.
    """

    def __init__(self, base_dir: str = "."):
        """
        Initializes the DirectoryManager with a base directory.

        Args:
            base_dir: The base directory for all operations.  Defaults to the current directory.
        """
        self.base_dir = base_dir
        logging.info(f"DirectoryManager initialized with base directory: {self.base_dir}")

    def create_directory(self, dir_name: str, exist_ok: bool = False) -> bool:
        """
        Creates a new directory under the base directory.

        Args:
            dir_name: The name of the directory to create.
            exist_ok: If False raises FileExistsError if target directory already exists.

        Returns:
            True if the directory was created successfully, False otherwise.

        Raises:
            ValueError: If dir_name is empty.
            OSError: If there's an error creating the directory (e.g., permission issues).
        """
        if not dir_name:
            logging.error("Directory name cannot be empty.")
            raise ValueError("Directory name cannot be empty.")

        full_path = os.path.join(self.base_dir, dir_name)

        try:
            os.makedirs(full_path, exist_ok=exist_ok)
            logging.info(f"Directory '{full_path}' created successfully.")
            return True
        except FileExistsError:
            logging.warning(f"Directory '{full_path}' already exists.")
            if not exist_ok:
                raise
            return False
        except OSError as e:
            logging.error(f"Error creating directory '{full_path}': {e}")
            raise OSError(f"Error creating directory '{full_path}': {e}")

    def delete_directory(self, dir_name: str, recursive: bool = False) -> bool:
        """
        Deletes a directory under the base directory.

        Args:
            dir_name: The name of the directory to delete.
            recursive: If True, delete the directory and all its contents.  If False, only delete if the directory is empty.

        Returns:
            True if the directory was deleted successfully, False otherwise.

        Raises:
            ValueError: If dir_name is empty.
            FileNotFoundError: If the directory does not exist.
            OSError: If there's an error deleting the directory (e.g., permission issues, not empty).
        """
        if not dir_name:
            logging.error("Directory name cannot be empty.")
            raise ValueError("Directory name cannot be empty.")

        full_path = os.path.join(self.base_dir, dir_name)

        if not os.path.exists(full_path):
            logging.error(f"Directory '{full_path}' does not exist.")
            raise FileNotFoundError(f"Directory '{full_path}' does not exist.")

        try:
            if recursive:
                import shutil
                shutil.rmtree(full_path)
            else:
                os.rmdir(full_path)

            logging.info(f"Directory '{full_path}' deleted successfully.")
            return True
        except OSError as e:
            logging.error(f"Error deleting directory '{full_path}': {e}")
            raise OSError(f"Error deleting directory '{full_path}': {e}")

    def list_directory_contents(self, dir_name: str = ".") -> List[str]:
        """
        Lists the contents of a directory under the base directory.

        Args:
            dir_name: The name of the directory to list. Defaults to the base directory.

        Returns:
            A list of strings representing the names of the files and directories in the specified directory.

        Raises:
            ValueError: If dir_name is empty.
            FileNotFoundError: If the directory does not exist.
            OSError: If there's an error accessing the directory (e.g., permission issues).
        """
        if dir_name == "":
            logging.error("Directory name cannot be empty.")
            raise ValueError("Directory name cannot be empty.")

        full_path = os.path.join(self.base_dir, dir_name)

        if not os.path.exists(full_path):
            logging.error(f"Directory '{full_path}' does not exist.")
            raise FileNotFoundError(f"Directory '{full_path}' does not exist.")

        try:
            contents = os.listdir(full_path)
            logging.info(f"Contents of directory '{full_path}': {contents}")
            return contents
        except OSError as e:
            logging.error(f"Error listing contents of directory '{full_path}': {e}")
            raise OSError(f"Error listing contents of directory '{full_path}': {e}")

    def check_if_directory_exists(self, dir_name: str) -> bool:
        """
        Checks if a directory exists.

        Args:
            dir_name: The name of the directory to check.

        Returns:
            True if directory exists, False otherwise.

        Raises:
            ValueError: If dir_name is empty.
        """

        if not dir_name:
            logging.error("Directory name cannot be empty.")
            raise ValueError("Directory name cannot be empty.")

        full_path = os.path.join(self.base_dir, dir_name)

        return os.path.exists(full_path) and os.path.isdir(full_path)


# Unit test scaffolding
if __name__ == '__main__':
    import unittest
    import shutil
    import tempfile

    class DirectoryManagerTest(unittest.TestCase):

        def setUp(self):
            self.temp_dir = tempfile.mkdtemp()
            self.dir_manager = DirectoryManager(self.temp_dir)

        def tearDown(self):
             shutil.rmtree(self.temp_dir) #Clean up temp directory and files

        def test_create_directory(self):
            dir_name = "test_dir"
            self.assertTrue(self.dir_manager.create_directory(dir_name))
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, dir_name)))

        def test_create_existing_directory(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            with self.assertRaises(FileExistsError):
                self.dir_manager.create_directory(dir_name)

            self.assertFalse(self.dir_manager.create_directory(dir_name, exist_ok=True))
            #Check that the create function returns false as expected
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, dir_name)))


        def test_delete_directory(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            self.assertTrue(self.dir_manager.delete_directory(dir_name))
            self.assertFalse(os.path.exists(os.path.join(self.temp_dir, dir_name)))

        def test_delete_nonexistent_directory(self):
             dir_name = "nonexistent_dir"
             with self.assertRaises(FileNotFoundError):
                 self.dir_manager.delete_directory(dir_name)


        def test_list_directory_contents(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            file_name = "test_file.txt"
            with open(os.path.join(self.temp_dir, dir_name, file_name), "w") as f:
                f.write("Test content")

            contents = self.dir_manager.list_directory_contents(dir_name)
            self.assertIn(file_name, contents)

        def test_check_if_directory_exists(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            self.assertTrue(self.dir_manager.check_if_directory_exists(dir_name))
            self.assertFalse(self.dir_manager.check_if_directory_exists("nonexistent_dir"))

        def test_create_directory_empty_name(self):
            with self.assertRaises(ValueError):
                self.dir_manager.create_directory("")

        def test_delete_directory_empty_name(self):
            with self.assertRaises(ValueError):
                self.dir_manager.delete_directory("")

        def test_list_directory_contents_empty_name(self):
             with self.assertRaises(ValueError):
                 self.dir_manager.list_directory_contents("")

        def test_check_if_directory_exists_empty_name(self):
            with self.assertRaises(ValueError):
                self.dir_manager.check_if_directory_exists("")

        def test_delete_non_empty_directory(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            file_name = "test_file.txt"
            with open(os.path.join(self.temp_dir, dir_name, file_name), "w") as f:
                f.write("Test content")

            with self.assertRaises(OSError):
                self.dir_manager.delete_directory(dir_name)

            self.assertTrue(self.dir_manager.delete_directory(dir_name, recursive = True))
            self.assertFalse(os.path.exists(os.path.join(self.temp_dir, dir_name)))



    unittest.main()