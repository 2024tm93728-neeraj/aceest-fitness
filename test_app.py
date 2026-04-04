import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import os

# Import your app
import app as app_module


class TestACEestApp(unittest.TestCase):

    def setUp(self):
        # Create Tk root safely
        self.root = tk.Tk()
        self.root.withdraw()

        # Patch login window to avoid UI blocking
        with patch.object(app_module.ACEestApp, "show_login_window"):
            self.app = app_module.ACEestApp(self.root)

        # Use in-memory DB for testing
        self.app.conn = app_module.sqlite3.connect(":memory:")
        self.app.cur = self.app.conn.cursor()
        self.app.init_db()
        self.app.setup_data()

        # Mock UI-dependent methods
        self.app.set_status = MagicMock()

        # Create required UI variables manually
        self.app.name = tk.StringVar()
        self.app.age = tk.IntVar()
        self.app.height = tk.DoubleVar()
        self.app.weight = tk.DoubleVar()
        self.app.program = tk.StringVar()
        self.app.membership_var = tk.StringVar()
        self.app.summary = MagicMock()
        self.app.program_tree = MagicMock()

    def tearDown(self):
        self.app.conn.close()
        self.root.destroy()
        # Cleanup PDF if created
        if os.path.exists("TestUser_report.pdf"):
            os.remove("TestUser_report.pdf")

    # ---------- DATABASE TEST ----------

    def test_db_tables_created(self):
        self.app.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [t[0] for t in self.app.cur.fetchall()]
        self.assertIn("clients", tables)
        self.assertIn("users", tables)

    # ---------- SAVE CLIENT ----------

    @patch("app.messagebox.showinfo")
    def test_save_client(self, mock_msg):
        self.app.name.set("TestUser")
        self.app.age.set(25)
        self.app.height.set(175)
        self.app.weight.set(70)
        self.app.program.set("Beginner (BG)")
        self.app.membership_var.set("2026-12-31")

        self.app.save_client()

        self.app.cur.execute(
            "SELECT * FROM clients WHERE name=?", ("TestUser",)
        )
        row = self.app.cur.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[1], "TestUser")

    # ---------- LOAD CLIENT ----------

    def test_load_client(self):
        # Insert test data
        self.app.cur.execute(
            "INSERT INTO clients (name, age, height, weight, program) VALUES (?,?,?,?,?)",
            ("TestUser", 25, 175, 70, "Beginner (BG)"),
        )
        self.app.conn.commit()

        self.app.current_client = "TestUser"
        self.app.load_client()

        self.assertEqual(self.app.name.get(), "TestUser")

    # ---------- LOGIN SUCCESS ----------

    @patch("app.messagebox.showerror")
    def test_login_success(self, mock_error):
        # Insert test user
        self.app.cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?,?,?)",
            ("test", "123", "Admin"),
        )
        self.app.conn.commit()

        self.app.username_var = tk.StringVar(value="test")
        self.app.password_var = tk.StringVar(value="123")
        self.app.login_win = MagicMock()
        self.app.root.deiconify = MagicMock()
        self.app.setup_ui = MagicMock()

        self.app.login_user()

        self.assertEqual(self.app.current_user, "test")
        self.assertEqual(self.app.user_role, "Admin")

    # ---------- LOGIN FAILURE ----------

    @patch("app.messagebox.showerror")
    def test_login_failure(self, mock_error):
        self.app.username_var = tk.StringVar(value="wrong")
        self.app.password_var = tk.StringVar(value="wrong")

        self.app.login_user()

        mock_error.assert_called_once()

    # ---------- AI PROGRAM GENERATION ----------

    @patch("app.simpledialog.askstring", return_value="beginner")
    @patch("app.messagebox.showinfo")
    def test_generate_ai_program(self, mock_msg, mock_input):
        # Insert client
        self.app.cur.execute(
            "INSERT INTO clients (name, program) VALUES (?,?)",
            ("TestUser", "Fat Loss (FL) – 3 day"),
        )
        self.app.conn.commit()

        self.app.current_client = "TestUser"

        self.app.program_tree.get_children.return_value = []
        self.app.program_tree.insert = MagicMock()

        self.app.generate_ai_program()

        self.assertTrue(self.app.program_tree.insert.called)

    # ---------- INVALID AI INPUT ----------

    @patch("app.simpledialog.askstring", return_value="invalid")
    @patch("app.messagebox.showerror")
    def test_generate_ai_invalid_input(self, mock_error, mock_input):
        self.app.current_client = "TestUser"
        self.app.generate_ai_program()

        mock_error.assert_called_once()

    # ---------- PDF EXPORT ----------

    @patch("app.messagebox.showinfo")
    def test_export_pdf(self, mock_msg):
        # Insert client
        self.app.cur.execute(
            "INSERT INTO clients (name, age, height, weight, program, membership_expiry) VALUES (?,?,?,?,?,?)",
            ("TestUser", 25, 175, 70, "Beginner", "2026-12-31"),
        )
        self.app.conn.commit()

        self.app.current_client = "TestUser"

        self.app.export_pdf_report()

        self.assertTrue(os.path.exists("TestUser_report.pdf"))


if __name__ == "__main__":
    unittest.main()
