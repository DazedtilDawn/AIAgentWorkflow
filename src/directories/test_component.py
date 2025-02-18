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
    import time
    import psutil  # Import psutil for performance monitoring
    from unittest.mock import patch

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

        def test_list_directory_contents_nonexistent(self):
            dir_name = "nonexistent_dir"
            with self.assertRaises(FileNotFoundError):
                self.dir_manager.list_directory_contents(dir_name)

        def test_create_directory_long_name(self):
            dir_name = "a" * 256  # Create a very long directory name
            self.assertTrue(self.dir_manager.create_directory(dir_name))
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, dir_name)))

        def test_delete_directory_long_name(self):
            dir_name = "a" * 256
            self.dir_manager.create_directory(dir_name)
            self.assertTrue(self.dir_manager.delete_directory(dir_name))
            self.assertFalse(os.path.exists(os.path.join(self.temp_dir, dir_name)))

        def test_create_nested_directories(self):
            dir_name = os.path.join("dir1", "dir2", "dir3")
            self.assertTrue(self.dir_manager.create_directory(dir_name, exist_ok=True))
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, dir_name)))

        def test_list_contents_with_subdirectory(self):
             dir_name = "parent_dir"
             sub_dir_name = "sub_dir"
             self.dir_manager.create_directory(dir_name)
             self.dir_manager.create_directory(os.path.join(dir_name, sub_dir_name))
             contents = self.dir_manager.list_directory_contents(dir_name)
             self.assertIn(sub_dir_name, contents)

        def test_check_if_directory_exists_nested(self):
            dir_name = os.path.join("dir1", "dir2")
            self.dir_manager.create_directory(dir_name, exist_ok=True)
            self.assertTrue(self.dir_manager.check_if_directory_exists(dir_name))

        def test_delete_directory_recursive_with_nested_directories(self):
            dir_name = "parent_dir"
            sub_dir_name = os.path.join(dir_name, "sub_dir")
            file_name = os.path.join(dir_name, "sub_dir", "test_file.txt")

            self.dir_manager.create_directory(sub_dir_name)
            with open(os.path.join(self.temp_dir, file_name), "w") as f:
                f.write("Test content")

            self.assertTrue(self.dir_manager.delete_directory(dir_name, recursive=True))
            self.assertFalse(os.path.exists(os.path.join(self.temp_dir, dir_name)))

        def test_create_directory_with_special_characters(self):
            dir_name = "dir with spaces and !@#$%^&*()"
            self.assertTrue(self.dir_manager.create_directory(dir_name))
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, dir_name)))

        def test_list_directory_contents_with_hidden_file(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            hidden_file_name = ".hidden_file.txt"
            with open(os.path.join(self.temp_dir, dir_name, hidden_file_name), "w") as f:
                f.write("Hidden content")

            contents = self.dir_manager.list_directory_contents(dir_name)
            self.assertIn(hidden_file_name, contents)

        def test_base_dir_does_not_exist(self):
            non_existent_dir = os.path.join(self.temp_dir, "non_existent") #Create a full path, rather than just a directory name
            with self.assertRaises(FileNotFoundError): #expect file not found error because the base directory doesn't exist
                 dir_manager = DirectoryManager(non_existent_dir)
                 dir_manager.list_directory_contents()


        def test_delete_permissions_error(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            full_path = os.path.join(self.temp_dir, dir_name)
            os.chmod(full_path, 0o000)  # Remove all permissions

            with self.assertRaises(OSError):
                self.dir_manager.delete_directory(dir_name)
            os.chmod(full_path, 0o777) #revert permissions so the teardown will still function

        def test_create_permissions_error(self):
            # Create a directory and remove write permissions to simulate a permissions error
            base_dir_name = 'base_dir_no_write'
            base_dir_path = os.path.join(self.temp_dir, base_dir_name)
            os.makedirs(base_dir_path)
            os.chmod(base_dir_path, 0o555)  # Read and execute permissions only

            dir_manager = DirectoryManager(base_dir_path)
            dir_name = "test_dir"
            with self.assertRaises(OSError):
                dir_manager.create_directory(dir_name)

            # Restore permissions so tearDown can clean up
            os.chmod(base_dir_path, 0o777)

    class DirectoryManagerIntegrationTest(unittest.TestCase):
        def setUp(self):
            self.temp_dir = tempfile.mkdtemp()
            self.dir_manager = DirectoryManager(self.temp_dir)

        def tearDown(self):
            shutil.rmtree(self.temp_dir)

        def test_create_and_list_directory(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            contents = self.dir_manager.list_directory_contents()
            self.assertIn(dir_name, contents)

        def test_create_delete_and_check_directory(self):
            dir_name = "test_dir"
            self.dir_manager.create_directory(dir_name)
            self.assertTrue(self.dir_manager.check_if_directory_exists(dir_name))
            self.dir_manager.delete_directory(dir_name)
            self.assertFalse(self.dir_manager.check_if_directory_exists(dir_name))

        @patch('os.listdir')  # Mocking example
        def test_list_directory_contents_mocked(self, mock_listdir):
            mock_listdir.return_value = ["mocked_file1.txt", "mocked_file2.txt"]
            dir_name = "test_dir"
            os.makedirs(os.path.join(self.temp_dir, dir_name), exist_ok=True) #Need to create this so the function does not error out
            contents = self.dir_manager.list_directory_contents(dir_name)
            self.assertEqual(contents, ["mocked_file1.txt", "mocked_file2.txt"])
            mock_listdir.assert_called_once() #assert that listdir was called

        def test_create_delete_nested_directory(self):
            nested_dir = os.path.join("parent_dir", "child_dir")
            self.dir_manager.create_directory(nested_dir, exist_ok = True)
            self.assertTrue(self.dir_manager.check_if_directory_exists(nested_dir))
            self.dir_manager.delete_directory("parent_dir", recursive=True)
            self.assertFalse(self.dir_manager.check_if_directory_exists(nested_dir))

    class DirectoryManagerPerformanceTest(unittest.TestCase):
        def setUp(self):
            self.temp_dir = tempfile.mkdtemp()
            self.dir_manager = DirectoryManager(self.temp_dir)

        def tearDown(self):
            shutil.rmtree(self.temp_dir)

        def test_create_multiple_directories(self):
            num_dirs = 100
            start_time = time.time()
            for i in range(num_dirs):
                self.dir_manager.create_directory(f"dir_{i}")
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time to create {num_dirs} directories: {elapsed_time:.4f} seconds")

            self.assertLess(elapsed_time, 1)  # Adjust threshold as needed

        def test_list_large_directory(self):
            dir_name = "large_dir"
            self.dir_manager.create_directory(dir_name)
            num_files = 1000
            for i in range(num_files):
                with open(os.path.join(self.temp_dir, dir_name, f"file_{i}.txt"), "w") as f:
                    f.write("test")

            start_time = time.time()
            self.dir_manager.list_directory_contents(dir_name)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time to list {num_files} files: {elapsed_time:.4f} seconds")

            self.assertLess(elapsed_time, 1)  # Adjust threshold as needed

        def test_recursive_delete_large_directory(self):
            dir_name = "large_dir"
            self.dir_manager.create_directory(dir_name)
            num_files = 500
            for i in range(num_files):
                with open(os.path.join(self.temp_dir, dir_name, f"file_{i}.txt"), "w") as f:
                    f.write("test")

            start_time = time.time()
            self.dir_manager.delete_directory(dir_name, recursive=True)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time to recursively delete {num_files} files: {elapsed_time:.4f} seconds")

            self.assertLess(elapsed_time, 2)  # Adjust threshold as needed

        def test_create_directory_resource_usage(self):
            dir_name = "test_dir"
            start_cpu = psutil.cpu_percent()
            start_memory = psutil.virtual_memory().used

            self.dir_manager.create_directory(dir_name)

            end_cpu = psutil.cpu_percent()
            end_memory = psutil.virtual_memory().used

            cpu_usage = end_cpu - start_cpu
            memory_usage = end_memory - start_memory

            print(f"CPU usage: {cpu_usage:.4f}%")
            print(f"Memory usage: {memory_usage:.4f} bytes")

            self.assertLess(cpu_usage, 5)    # Adjust threshold as needed
            self.assertLess(memory_usage, 1024 * 1024) # 1MB Adjust threshold as needed

    unittest.main()