import unittest
import sqlite3
import nurse

class TestNurse(unittest.TestCase):
    
    def test_connectivity(self):
        conn = None
        database = r'C:\sqlite\gui\sqlitestudio-3.3.2\SQLiteStudio\chinook\chinook.db'
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM nurse")
        result = cur.fetchone()
        message = "Count of rows <= 0"
        zero = 0
        self.assertGreater(result[0], zero, message)

if __name__ == '__main__':
    unittest.main()