import unittest
from unittest.mock import patch
import tkinter as tk
import os
import sqlite3

from app import ACEestApp


class TestACEestApp(unittest.TestCase):

    def setUp(self):
        # Use test DB to avoid conflicts
        self.test_db = "test_aceest.db"

        # Patch DB_NAME dynamically
        import app
        app.DB_NAME = self.test_db

        # Remove old test DB
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        # Setup Tkinter root (hidden)
        self.root = tk.Tk()
        self.root.withdraw()

        # Initialize app
        self.app = ACEestApp(self.root)

    def tearDown(self):
        self.app.conn.close()
        self.root.destroy()

        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    # 1. Test DB tables created
    def test_tables_created(self):
        self.app.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [t[0] for t in self.app.cur.fetchall()]

        self.assertIn("clients", tables)
        self.assertIn("progress", tables)
        self.assertIn("workouts", tables)
        self.assertIn("metrics", tables)

    # 2. Test programs loaded
    def test_programs_loaded(self):
        self.assertIn("Fat Loss (FL) – 3 day", self.app.programs)
        self.assertIn("Muscle Gain (MG) – PPL", self.app.programs)

    # 3. Test save_client validation (missing name)
    @patch("tkinter.messagebox.showerror")
    def test_save_client_no_name(self, mock_error):
        self.app.program.set("Fat Loss (FL) – 3 day")
        self.app.save_client()
        mock_error.assert_called_once()

    # 4. Test save_client validation (missing program)
    @patch("tkinter.messagebox.showerror")
    def test_save_client_no_program(self, mock_error):
        self.app.name.set("Neeraj")
        self.app.save_client()
        mock_error.assert_called_once()

    # 5. Test save_client success
    @patch("tkinter.messagebox.showinfo")
    def test_save_client_success(self, mock_info):
        self.app.name.set("Neeraj")
        self.app.weight.set(70)
        self.app.program.set("Fat Loss (FL) – 3 day")

        self.app.save_client()

        self.app.cur.execute("SELECT * FROM clients WHERE name='Neeraj'")
        result = self.app.cur.fetchone()

        self.assertIsNotNone(result)
        mock_info.assert_called_once()

    # 6. Test calorie calculation
    def test_calorie_calculation(self):
        self.app.name.set("TestUser")
        self.app.weight.set(80)
        self.app.program.set("Muscle Gain (MG) – PPL")

        self.app.save_client()

        self.app.cur.execute("SELECT calories FROM clients WHERE name='TestUser'")
        calories = self.app.cur.fetchone()[0]

        self.assertEqual(calories, 80 * 35)

    # 7. Test load_client not found
    @patch("tkinter.messagebox.showwarning")
    def test_load_client_not_found(self, mock_warn):
        self.app.name.set("Unknown")
        self.app.load_client()
        mock_warn.assert_called_once()

    # 8. Test load_client success
    def test_load_client_success(self):
        # Insert test data
        self.app.cur.execute("""
            INSERT OR REPLACE INTO clients
            (name, age, height, weight, program, calories, target_weight, target_adherence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Rahul", 25, 175, 70, "Fat Loss (FL) – 3 day", 1540, 65, 80))
        self.app.conn.commit()

        self.app.name.set("Rahul")
        self.app.load_client()

        self.assertEqual(self.app.age.get(), 25)
        self.assertEqual(self.app.weight.get(), 70)

    # 9. Test save_progress
    @patch("tkinter.messagebox.showinfo")
    def test_save_progress(self, mock_info):
        self.app.name.set("Amit")
        self.app.adherence.set(85)

        self.app.save_progress()

        self.app.cur.execute("SELECT * FROM progress WHERE client_name='Amit'")
        result = self.app.cur.fetchone()

        self.assertIsNotNone(result)
        mock_info.assert_called_once()

    # 10. Test ensure_client failure
    @patch("tkinter.messagebox.showwarning")
    def test_ensure_client_fail(self, mock_warn):
        self.app.current_client = None
        self.app.name.set("")

        result = self.app.ensure_client()

        self.assertFalse(result)
        mock_warn.assert_called_once()

    # 11. Test BMI info missing data
    @patch("tkinter.messagebox.showwarning")
    def test_bmi_missing_data(self, mock_warn):
        self.app.current_client = "Test"
        self.app.height.set(0)
        self.app.weight.set(0)

        self.app.show_bmi_info()
        mock_warn.assert_called_once()

    # 12. Test BMI normal case
    @patch("tkinter.messagebox.showinfo")
    def test_bmi_normal(self, mock_info):
        self.app.current_client = "Test"
        self.app.height.set(170)
        self.app.weight.set(65)

        self.app.show_bmi_info()
        mock_info.assert_called_once()

    # 13. Test progress chart no data
    @patch("tkinter.messagebox.showinfo")
    def test_progress_chart_no_data(self, mock_info):
        self.app.current_client = "Test"

        with patch("matplotlib.pyplot.show"):
            self.app.show_progress_chart()

        mock_info.assert_called_once()

    # 14. Test weight chart no data
    @patch("tkinter.messagebox.showinfo")
    def test_weight_chart_no_data(self, mock_info):
        self.app.current_client = "Test"

        with patch("matplotlib.pyplot.show"):
            self.app.show_weight_chart()

        mock_info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
