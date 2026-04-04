import unittest
import tkinter as tk
import os
import sqlite3
from unittest.mock import patch

from app import ACEestApp  # change if filename differs


class TestACEestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use test DB
        cls.test_db = "test_aceest.db"

    def setUp(self):
        # Remove old test DB
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        # Patch DB_NAME dynamically
        import app
        app.DB_NAME = self.test_db

        self.root = tk.Tk()
        self.root.withdraw()  # prevent UI

        self.app = ACEestApp(self.root)

    def tearDown(self):
        self.app.conn.close()
        self.root.destroy()

        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    # ---------- DB TESTS ----------

    def test_tables_created(self):
        self.app.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in self.app.cur.fetchall()}

        self.assertIn("clients", tables)
        self.assertIn("progress", tables)
        self.assertIn("workouts", tables)
        self.assertIn("exercises", tables)
        self.assertIn("metrics", tables)

    # ---------- PROGRAM DATA ----------

    def test_programs_loaded(self):
        self.assertIn("Fat Loss (FL) – 3 day", self.app.programs)
        self.assertIn("Muscle Gain (MG) – PPL", self.app.programs)

    # ---------- CLIENT ----------

    @patch("tkinter.messagebox.showinfo")
    def test_save_client_success(self, mock_info):
        self.app.name.set("John")
        self.app.age.set(25)
        self.app.height.set(175)
        self.app.weight.set(70)
        self.app.program.set("Fat Loss (FL) – 3 day")

        self.app.save_client()

        self.app.cur.execute("SELECT * FROM clients WHERE name=?", ("John",))
        row = self.app.cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[1], "John")

    @patch("tkinter.messagebox.showerror")
    def test_save_client_validation(self, mock_error):
        self.app.name.set("")
        self.app.program.set("")

        self.app.save_client()

        mock_error.assert_called()

    @patch("tkinter.messagebox.showwarning")
    def test_load_client_not_found(self, mock_warning):
        self.app.name.set("Ghost")
        self.app.load_client()

        mock_warning.assert_called()

    @patch("tkinter.messagebox.showinfo")
    def test_load_client_success(self, mock_info):
        # Insert manually
        self.app.cur.execute("""
            INSERT INTO clients
            (name, age, height, weight, program, calories, target_weight, target_adherence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("John", 25, 175, 70, "Beginner (BG)", 1800, 65, 80))
        self.app.conn.commit()

        self.app.name.set("John")
        self.app.load_client()

        self.assertEqual(self.app.age.get(), 25)
        self.assertEqual(self.app.weight.get(), 70)

    # ---------- PROGRESS ----------

    @patch("tkinter.messagebox.showinfo")
    def test_save_progress(self, mock_info):
        self.app.name.set("John")
        self.app.adherence.set(85)

        self.app.save_progress()

        self.app.cur.execute("SELECT * FROM progress WHERE client_name=?", ("John",))
        row = self.app.cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[3], 85)

    # ---------- METRICS ----------

    def test_metrics_insert(self):
        self.app.cur.execute("""
            INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
            VALUES (?, ?, ?, ?, ?)
        """, ("John", "2026-01-01", 70, 80, 15))
        self.app.conn.commit()

        self.app.cur.execute("SELECT * FROM metrics WHERE client_name=?", ("John",))
        row = self.app.cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[2], "2026-01-01")

    # ---------- SUMMARY ----------

    def test_refresh_summary_no_crash(self):
        self.app.current_client = "John"

        # Insert minimal client
        self.app.cur.execute("""
            INSERT INTO clients
            (name, age, height, weight, program, calories, target_weight, target_adherence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("John", 25, 175, 70, "Beginner (BG)", 1800, None, None))
        self.app.conn.commit()

        # Should not crash
        self.app.refresh_summary()

    # ---------- HELPER ----------

    def test_ensure_client_false(self):
        self.app.current_client = None
        self.app.name.set("")
        self.app.client_list.set("")

        with patch("tkinter.messagebox.showwarning") as mock_warn:
            result = self.app.ensure_client()
            self.assertFalse(result)
            mock_warn.assert_called()

    def test_ensure_client_true(self):
        self.app.name.set("John")
        result = self.app.ensure_client()

        self.assertTrue(result)
        self.assertEqual(self.app.current_client, "John")

    # ---------- CHARTS ----------

    @patch("matplotlib.pyplot.show")
    def test_show_progress_chart_no_data(self, mock_show):
        self.app.current_client = "John"

        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.app.show_progress_chart()
            mock_info.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_show_weight_chart_no_data(self, mock_show):
        self.app.current_client = "John"

        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.app.show_weight_chart()
            mock_info.assert_called()

    # ---------- BMI ----------

    @patch("tkinter.messagebox.showinfo")
    def test_bmi_calculation(self, mock_info):
        self.app.current_client = "John"
        self.app.height.set(175)
        self.app.weight.set(70)

        self.app.show_bmi_info()

        mock_info.assert_called()


if __name__ == "__main__":
    unittest.main()
