import unittest
import os
from main import ensure_directory_exists, save_check_status, load_check_status

class TestMainFunctions(unittest.TestCase):

    def setUp(self):
        self.chat_id = 12346  # Dummy chat ID for these tests to avoid collision with previous tests

    def test_ensure_directory_exists(self):
        # Ensure directory is created when it doesn't exist
        dir_name = f"{self.chat_id}_test_dir"
        ensure_directory_exists(dir_name)
        self.assertTrue(os.path.exists(dir_name))
        os.rmdir(dir_name)  # Cleanup after the test

    def test_save_load_check_status(self):
        # Test saving and loading check status
        statuses = ["not_checked", "checked"]
        for status in statuses:
            save_check_status(status)
            loaded_status = load_check_status()
            self.assertEqual(status, loaded_status)

    # You can add more test methods here to test other remaining functions

    def tearDown(self):
        # Cleanup actions after each test, if needed
        pass

if __name__ == "__main__":
    unittest.main()
