import unittest
import tkinter as tk
from unittest.mock import patch
import sqlite3
from app import ACEestApp


class TestACEestApp(unittest.TestCase):

    def setUp(self):
        """Setup app with in-memory DB and clean tables"""
        self.root = tk.Tk()
        self.root.withdraw()  # prevent GUI window
        self.app = ACEestApp(self.root)

        # Switch to in-memory DB for isolation
        self.app.conn.close()
        self.app.conn = sqlite3.connect(":memory:")
        self.app.cur = self.app.conn.cursor()
        self.app.init_db()

        # Ensure tables are empty before each test
        self.app.cur.execute("DELETE FROM clients")
        self.app.cur.execute("DELETE FROM progress")
        self.app.conn.commit()

    def tearDown(self):
        """Cleanup"""
        self.app.conn.close()
        self.root.destroy()

    # 1. Test database tables created
    def test_tables_created(self):
        self.app.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in self.app.cur.fetchall()]
        self.assertIn("clients", tables)
        self.assertIn("progress", tables)

    # 2. Test save_client success
    @patch("tkinter.messagebox.showinfo")
    def test_save_client_success(self, mock_info):
        self.app.name.set("John")
        self.app.age.set(25)
        self.app.weight.set(70)
        self.app.program.set("Fat Loss (FL)")

        self.app.save_client()

        self.app.cur.execute("SELECT * FROM clients WHERE name='John'")
        row = self.app.cur.fetchone()

        self.assertIsNotNone(row)
        mock_info.assert_called_once()

    # 3. Test save_client validation error
    @patch("tkinter.messagebox.showerror")
    def test_save_client_validation(self, mock_error):
        self.app.name.set("")
        self.app.program.set("")

        self.app.save_client()

        mock_error.assert_called_once()

    # 4. Test calorie calculation in DB
    def test_calorie_calculation(self):
        self.app.name.set("Alice")
        self.app.age.set(30)
        self.app.weight.set(60)
        self.app.program.set("Muscle Gain (MG)")

        with patch("tkinter.messagebox.showinfo"):
            self.app.save_client()

        self.app.cur.execute("SELECT calories FROM clients WHERE name='Alice'")
        calories = self.app.cur.fetchone()[0]

        self.assertEqual(calories, 60 * 35)

    # 5. Test load_client success
    @patch("tkinter.messagebox.showwarning")
    def test_load_client_success(self, mock_warning):
        # Insert test data
        self.app.cur.execute("""
            INSERT INTO clients (name, age, weight, program, calories)
            VALUES ('Bob', 28, 75, 'Fat Loss (FL)', 1650)
        """)
        self.app.conn.commit()

        self.app.name.set("Bob")
        self.app.load_client()

        self.assertEqual(self.app.age.get(), 28)
        self.assertEqual(self.app.weight.get(), 75)
        self.assertEqual(self.app.program.get(), "Fat Loss (FL)")
        self.assertFalse(mock_warning.called)

    # 6. Test load_client not found
    @patch("tkinter.messagebox.showwarning")
    def test_load_client_not_found(self, mock_warning):
        self.app.name.set("Unknown")

        self.app.load_client()

        mock_warning.assert_called_once()

    # 7. Test save_progress
    @patch("tkinter.messagebox.showinfo")
    def test_save_progress(self, mock_info):
        self.app.name.set("John")
        self.app.adherence.set(85)

        self.app.save_progress()

        self.app.cur.execute("SELECT * FROM progress WHERE client_name='John'")
        row = self.app.cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[3], 85)
        mock_info.assert_called_once()

    # 8. Test program data loaded
    def test_programs_loaded(self):
        self.assertEqual(len(self.app.programs), 3)
        self.assertIn("Fat Loss (FL)", self.app.programs)

    # 9. Edge case: zero weight calorie
    def test_zero_weight(self):
        self.app.name.set("Zero")
        self.app.age.set(20)
        self.app.weight.set(0)
        self.app.program.set("Beginner (BG)")

        with patch("tkinter.messagebox.showinfo"):
            self.app.save_client()

        self.app.cur.execute("SELECT calories FROM clients WHERE name='Zero'")
        calories = self.app.cur.fetchone()[0]

        self.assertEqual(calories, 0)


if __name__ == "__main__":
    unittest.main()
