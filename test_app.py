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

        # Prevent UI loading
        with patch.object(app.ACEestApp, "login_screen"):
            self.app = app.ACEestApp(self.root)

        # Mock UI components
        self.app.summary_text = MagicMock()
        self.app.tree_workouts = MagicMock()
        self.app.chart_frame = MagicMock()
        self.app.client_list = MagicMock()

    def tearDown(self):
        self.app.conn.close()
        if os.path.exists("test_aceest.db"):
            os.remove("test_aceest.db")

    # ---------- DATABASE ----------

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
        self.assertIsNotNone(self.app.cur.fetchone())

    # ---------- LOGIN ----------

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

    # ---------- CLIENT ----------

    @patch("tkinter.simpledialog.askstring", return_value="John")
    @patch("tkinter.messagebox.showinfo")
    def test_add_save_client(self, mock_info, _):
        self.app.add_save_client()

        self.app.cur.execute("SELECT * FROM clients WHERE name='John'")
        self.assertIsNotNone(self.app.cur.fetchone())

        mock_info.assert_called_once()

    def test_refresh_client_list(self):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("Alice", "Active")
        )
        self.app.conn.commit()

        self.app.refresh_client_list()

        self.app.client_list.__setitem__.assert_called()

    def test_load_client(self):
        self.app.refresh_summary = MagicMock()
        self.app.refresh_workouts = MagicMock()
        self.app.plot_charts = MagicMock()

        self.app.client_list.get.return_value = "TestClient"

        self.app.load_client()

        self.assertEqual(self.app.current_client, "TestClient")
        self.app.refresh_summary.assert_called_once()
        self.app.refresh_workouts.assert_called_once()
        self.app.plot_charts.assert_called_once()

    # ---------- PROGRAM ----------

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
        self.assertIsNotNone(self.app.cur.fetchone()[0])

        mock_info.assert_called_once()

    @patch("tkinter.messagebox.showwarning")
    def test_generate_program_no_client(self, mock_warn):
        self.app.current_client = None
        self.app.generate_program()
        mock_warn.assert_called_once()

    # ---------- PDF ----------

    @patch("app.FPDF")
    @patch("tkinter.messagebox.showinfo")
    def test_generate_pdf(self, mock_info, mock_pdf):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("PDFUser", "Active")
        )
        self.app.conn.commit()

        self.app.current_client = "PDFUser"

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

    # ---------- CHARTS ----------

    def test_plot_charts_no_data(self):
        self.app.current_client = "NoData"
        self.app.plot_charts()  # should not crash

    @patch("app.FigureCanvasTkAgg")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_charts_with_data(self, mock_subplots, mock_canvas):
        self.app.current_client = "ChartUser"

        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("ChartUser", "Active")
        )
        self.app.cur.execute(
            "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
            ("ChartUser", "Week1", 80)
        )
        self.app.conn.commit()

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        self.app.plot_charts()

        mock_ax.plot.assert_called()
        mock_canvas.assert_called_once()

    # ---------- WORKOUT ----------

    def test_refresh_workouts_no_client(self):
        self.app.current_client = None
        self.app.refresh_workouts()

    def test_refresh_workouts_with_data(self):
        self.app.current_client = "WorkoutUser"

        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("WorkoutUser", "Active")
        )
        self.app.cur.execute(
            "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
            ("WorkoutUser", "2024-01-01", "Strength", 60, "Test")
        )
        self.app.conn.commit()

        self.app.refresh_workouts()

        self.app.tree_workouts.insert.assert_called()

    # ---------- UTILITY ----------

    def test_clear_root(self):
        mock_widget = MagicMock()
        self.root.winfo_children.return_value = [mock_widget]

        self.app.clear_root()

        mock_widget.destroy.assert_called_once()

    @patch("app.ttk.Notebook")
    @patch("app.tk.Frame")
    @patch("app.tk.Label")
    def test_dashboard(self, mock_label, mock_frame, mock_notebook):
        self.app.current_role = "Admin"

        self.app.dashboard()

        mock_label.assert_called()

    @patch("app.ttk.Treeview")
    def test_setup_workout_tab(self, mock_tree):
        self.app.tab_workouts = MagicMock()
        self.app.setup_workout_tab()
        mock_tree.assert_called_once()

    def test_plot_charts_cleanup(self):
        mock_widget = MagicMock()
        self.app.chart_frame.winfo_children.return_value = [mock_widget]

        self.app.current_client = None
        self.app.plot_charts()

        mock_widget.destroy.assert_called_once()
    
    @patch("tkinter.messagebox.showinfo")
    def test_generate_program_with_data(self, mock_info):
        self.app.cur.execute(
            "INSERT INTO clients (name, weight, target_weight, membership_status) VALUES (?, ?, ?, ?)",
            ("DeepUser", 80, 70, "Active")
        )
        self.app.conn.commit()

        self.app.current_client = "DeepUser"

        self.app.generate_program()

        self.app.cur.execute("SELECT program FROM clients WHERE name='DeepUser'")
        self.assertIsNotNone(self.app.cur.fetchone()[0])

    @patch("tkinter.messagebox.showinfo")
    def test_check_membership_with_date(self, mock_info):
        self.app.cur.execute(
            "INSERT INTO clients (name, membership_status, membership_end) VALUES (?, ?, ?)",
            ("ExpireUser", "Active", "2020-01-01")
        )
        self.app.conn.commit()

        self.app.current_client = "ExpireUser"

        self.app.check_membership()

        mock_info.assert_called_once() 
             
if __name__ == "__main__":
    unittest.main()
