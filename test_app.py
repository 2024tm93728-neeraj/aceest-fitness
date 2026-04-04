import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3

import app  # your main file


class TestACEestApp(unittest.TestCase):

    def setUp(self):
        # Use separate test DB
        app.DB_NAME = "test_aceest.db"
        app.init_db()

        # Mock root
        self.root = MagicMock()

        # Prevent UI from loading
        with patch.object(app.ACEestApp, "login_screen"):
            self.app = app.ACEestApp(self.root)

        # ✅ Mock UI components globally (IMPORTANT FIX)
        self.app.summary_text = MagicMock()
        self.app.tree_workouts = MagicMock()
        self.app.chart_frame = MagicMock()
        self.app.client_list = MagicMock()

    def tearDown(self):
        self.app.conn.close()
        if os.path.exists("test_aceest.db"):
            os.remove("test_aceest.db")

    # ---------- DATABASE TESTS ----------

    def test_init_db_creates_tables(self):
        conn = sqlite3.connect(app.DB_NAME)
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]

        self.assertIn("clients", tables)
        self.assertIn("users", tables)
        conn.close()

    def test_default_admin_exists(self):
        self.app.cur.execute("SELECT * FROM users WHERE username='admin'")
        user = self.app.cur.fetchone()
        self.assertIsNotNone(user)

    # ---------- LOGIN TESTS ----------

    @patch("tkinter.messagebox.showerror")
    def test_login_failure(self, mock_error):
        self.app.username_var = MagicMock()
        self.app.password_var = MagicMock()

        self.app.username_var.get.return_value = "wrong"
        self.app.password_var.get.return_value = "wrong"

        self.app.login()

        mock_error.assert_called_once()

    def test_login_success(self):
        self.app.username_var = MagicMock()
        self.app.password_var = MagicMock()

        self.app.username_var.get.return_value = "admin"
        self.app.password_var.get.return_value = "admin"

        with patch.object(self.app, "dashboard") as mock_dashboard:
            self.app.login()
            mock_dashboard.assert_called_once()

    # ---------- CLIENT TESTS ----------

    @patch("tkinter.simpledialog.askstring", return_value="John")
    @patch("tkinter.messagebox.showinfo")
    def test_add_save_client(self, mock_info, mock_input):
        self.app.add_save_client()

        self.app.cur.execute("SELECT * FROM clients WHERE name='John'")
        client = self.app.cur.fetchone()

        self.assertIsNotNone(client)
        mock_info.assert_called_once()

    def test_refresh_client_list(self):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("Alice", "Active")
        )
        self.app.conn.commit()

        self.app.refresh_client_list()

        self.app.client_list.__setitem__.assert_called()

    # ---------- PROGRAM GENERATION ----------

    @patch("tkinter.messagebox.showinfo")
    def test_generate_program(self, mock_info):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("Bob", "Active")
        )
        self.app.conn.commit()

        self.app.current_client = "Bob"

        self.app.generate_program()

        self.app.cur.execute("SELECT program FROM clients WHERE name='Bob'")
        program = self.app.cur.fetchone()[0]

        self.assertIsNotNone(program)
        mock_info.assert_called_once()

    @patch("tkinter.messagebox.showwarning")
    def test_generate_program_no_client(self, mock_warn):
        self.app.current_client = None
        self.app.generate_program()
        mock_warn.assert_called_once()

    # ---------- PDF GENERATION ----------

    @patch("app.FPDF")
    @patch("tkinter.messagebox.showinfo")
    def test_generate_pdf(self, mock_info, mock_pdf):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("TestPDF", "Active")
        )
        self.app.conn.commit()

        self.app.current_client = "TestPDF"

        pdf_instance = MagicMock()
        mock_pdf.return_value = pdf_instance

        self.app.generate_pdf()

        pdf_instance.add_page.assert_called()
        pdf_instance.output.assert_called()
        mock_info.assert_called_once()

    # ---------- MEMBERSHIP ----------

    @patch("tkinter.messagebox.showinfo")
    def test_check_membership(self, mock_info):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("Sam", "Active")
        )
        self.app.conn.commit()

        self.app.current_client = "Sam"

        self.app.check_membership()

        mock_info.assert_called_once()

    # ---------- SUMMARY ----------

    def test_refresh_summary(self):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("Mike", "Active")
        )
        self.app.conn.commit()

        self.app.current_client = "Mike"

        self.app.refresh_summary()

        self.app.summary_text.insert.assert_called()

    # ---------- WORKOUT ----------

    def test_refresh_workouts_no_client(self):
        self.app.current_client = None
        self.app.refresh_workouts()  # should not crash

    # ---------- UTILITY ----------

    def test_clear_root(self):
        mock_widget = MagicMock()
        self.root.winfo_children.return_value = [mock_widget]

        self.app.clear_root()

        mock_widget.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
