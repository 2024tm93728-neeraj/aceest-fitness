import unittest
import tkinter as tk
from unittest.mock import patch
import sqlite3

# IMPORTANT: prevent matplotlib GUI issues
import matplotlib
matplotlib.use("Agg")

from app import ACEestApp


class TestACEestApp(unittest.TestCase):

    def setUp(self):
        """Setup clean app with in-memory DB"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.app = ACEestApp(self.root)

        # Replace DB with fresh memory DB
        self.app.conn.close()
        self.app.conn = sqlite3.connect(":memory:")
        self.app.cur = self.app.conn.cursor()

        # Recreate tables
        self.app.cur.execute("""
            CREATE TABLE clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                age INTEGER,
                weight REAL,
                program TEXT,
                calories INTEGER
            )
        """)
        self.app.cur.execute("""
            CREATE TABLE progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                week TEXT,
                adherence INTEGER
            )
        """)
        self.app.conn.commit()

    def tearDown(self):
        self.app.conn.close()
        self.root.destroy()

    # 1. Test tables created
    def test_tables_created(self):
        self.app.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in self.app.cur.fetchall()]
        self.assertIn("clients", tables)
        self.assertIn("progress", tables)

    # 2. Test programs loaded
    def test_programs_loaded(self):
        self.assertEqual(len(self.app.programs), 3)

    # 3. Test save_client success
    @patch("tkinter.messagebox.showinfo")
    def test_save_client_success(self, mock_info):
        self.app.name.set("John")
        self.app.age.set(25)
        self.app.weight.set(70)
        self.app.program.set("Fat Loss (FL)")

        self.app.save_client()

        self.app.cur.execute("SELECT * FROM clients WHERE name='John'")
        self.assertIsNotNone(self.app.cur.fetchone())
        mock_info.assert_called_once()

    # 4. Test save_client validation
    @patch("tkinter.messagebox.showerror")
    def test_save_client_validation(self, mock_error):
        self.app.name.set("")
        self.app.program.set("")

        self.app.save_client()
        mock_error.assert_called_once()

    # 5. Test calorie calculation
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

    # 6. Test load_client success
    def test_load_client_success(self):
        self.app.cur.execute("""
            INSERT INTO clients (name, age, weight, program, calories)
            VALUES ('Bob_test', 28, 75, 'Fat Loss (FL)', 1650)
        """)
        self.app.conn.commit()

        self.app.name.set("Bob_test")
        self.app.load_client()

        self.assertEqual(self.app.age.get(), 28)
        self.assertEqual(self.app.weight.get(), 75)

        content = self.app.summary.get("1.0", "end")
        self.assertIn("Bob_test", content)

    # 7. Test load_client not found
    @patch("tkinter.messagebox.showwarning")
    def test_load_client_not_found(self, mock_warning):
        self.app.name.set("Unknown")
        self.app.load_client()
        mock_warning.assert_called_once()

    # 8. Test save_progress
    @patch("tkinter.messagebox.showinfo")
    def test_save_progress(self, mock_info):
        self.app.name.set("John")
        self.app.adherence.set(80)

        self.app.save_progress()

        self.app.cur.execute("SELECT * FROM progress WHERE client_name='John'")
        row = self.app.cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[3], 80)
        mock_info.assert_called_once()

    # 9. Test show_progress_chart - no name
    @patch("tkinter.messagebox.showwarning")
    def test_show_chart_no_name(self, mock_warning):
        self.app.name.set("")
        self.app.show_progress_chart()
        mock_warning.assert_called_once()

    # 10. Test show_progress_chart - no data
    @patch("tkinter.messagebox.showinfo")
    def test_show_chart_no_data(self, mock_info):
        self.app.name.set("John")
        self.app.show_progress_chart()
        mock_info.assert_called_once()

    # 11. Test show_progress_chart success
    @patch("matplotlib.pyplot.show")
    def test_show_chart_success(self, mock_show):
        self.app.name.set("John")

        # Insert progress data
        self.app.cur.execute("""
            INSERT INTO progress (client_name, week, adherence)
            VALUES ('John', 'Week 01 - 2025', 70)
        """)
        self.app.conn.commit()

        self.app.show_progress_chart()
        mock_show.assert_called_once()

    # 12. Edge case: zero weight
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
