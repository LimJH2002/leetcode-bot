import unittest
from main import save_members, load_members, save_data, load_data
import os

class TestDataHandlers(unittest.TestCase):

    def setUp(self):
        self.chat_id = 12345  # Dummy chat ID
        self.members = {"user1", "user2", "user3"}
        save_members(self.chat_id, self.members)

    def test_load_members(self):
        loaded_members = load_members(self.chat_id)
        self.assertEqual(self.members, loaded_members)

    def test_save_load_data(self):
        daily_progress = {"user1": True, "user2": False}
        penalties = {"user1": 10, "user2": 5}
        credits = {"user1": 2, "user2": 3}
        
        save_data(self.chat_id, daily_progress, penalties, credits)
        loaded_daily_progress, loaded_penalties, loaded_credits = load_data(self.chat_id)
        
        self.assertEqual(daily_progress, loaded_daily_progress)
        self.assertEqual(penalties, loaded_penalties)
        self.assertEqual(credits, loaded_credits)

    def test_empty_members(self):
      save_members(self.chat_id, set())
      loaded_members = load_members(self.chat_id)
      self.assertEqual(set(), loaded_members)

    def test_special_characters(self):
        special_members = {"user_ö", "user_ß", "user_ñ"}
        save_members(self.chat_id, special_members)
        loaded_members = load_members(self.chat_id)
        self.assertEqual(special_members, loaded_members)

    def test_data_overwrite(self):
        first_set = {"user1", "user2", "user3"}
        second_set = {"user4", "user5", "user6"}

        save_members(self.chat_id, first_set)
        save_members(self.chat_id, second_set)

        loaded_members = load_members(self.chat_id)
        self.assertEqual(second_set, loaded_members)

    def tearDown(self):
      # Cleanup files after test
      files = [f"{self.chat_id}/members.txt", f"{self.chat_id}/daily_progress.txt", f"{self.chat_id}/penalties.txt", f"{self.chat_id}/credits.txt"]
      for file in files:
          if os.path.exists(file):
              os.remove(file)

if __name__ == "__main__":
    unittest.main()
