import unittest
import tkinter as tk
from unittest.mock import patch, mock_open
from app import ACEestApp


class TestACEestApp(unittest.TestCase):

    def setUp(self):
        """Setup Tkinter app in headless mode"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = ACEestApp(self.root)

    def tearDown(self):
        """Destroy Tkinter instance"""
        self.root.destroy()

    # 1. Test programs dictionary
    def test_programs_loaded(self):
        self.assertEqual(len(self.app.programs), 3)
        self.assertIn("Fat Loss (FL)", self.app.programs)

    # 2. Test dropdown values
    def test_program_dropdown_values(self):
        values = list(self.app.program_box["values"])
        self.assertEqual(values, list(self.app.programs.keys()))

    # 3. Test update program
    def test_update_program(self):
        self.app.program_var.set("Fat Loss (FL)")
        self.app.weight_var.set(70)

        self.app.update_program()

        workout = self.app.workout_text.get("1.0", "end")
        diet = self.app.diet_text.get("1.0", "end")

        self.assertIn("Back Squat", workout)
        self.assertIn("Egg Whites", diet)
        self.assertIn("Estimated Calories", self.app.calorie_label.cget("text"))

    # 4. Test calorie calculation
    def test_calorie_calculation(self):
        self.app.program_var.set("Muscle Gain (MG)")
        self.app.weight_var.set(80)

        self.app.update_program()

        expected = 80 * 35
        self.assertIn(str(expected), self.app.calorie_label.cget("text"))

    # 5. Test save client success
    @patch("tkinter.messagebox.showinfo")
    def test_save_client_success(self, mock_info):
        self.app.name_var.set("John")
        self.app.program_var.set("Fat Loss (FL)")
        self.app.age_var.set(25)
        self.app.weight_var.set(70)
        self.app.progress_var.set(80)
        self.app.notes_var.set("Good progress")

        self.app.save_client()

        self.assertEqual(len(self.app.clients), 1)
        mock_info.assert_called_once()

    # 6. Test save client validation
    @patch("tkinter.messagebox.showwarning")
    def test_save_client_validation(self, mock_warning):
        self.app.name_var.set("")
        self.app.program_var.set("")

        self.app.save_client()

        mock_warning.assert_called_once()

    # 7. Test table insertion
    def test_client_table_insert(self):
        self.app.name_var.set("Alice")
        self.app.program_var.set("Beginner (BG)")

        with patch("tkinter.messagebox.showinfo"):
            self.app.save_client()

        items = self.app.client_table.get_children()
        self.assertEqual(len(items), 1)

    # 8. Test export CSV - no data
    @patch("tkinter.messagebox.showwarning")
    def test_export_csv_no_data(self, mock_warning):
        self.app.export_csv()
        mock_warning.assert_called_once()

    # 9. Test export CSV with data
    @patch("tkinter.filedialog.asksaveasfilename", return_value="test.csv")
    @patch("builtins.open", new_callable=mock_open)
    @patch("tkinter.messagebox.showinfo")
    def test_export_csv_success(self, mock_info, mock_file, mock_dialog):
        self.app.clients.append(("John", 25, 70, "Fat Loss (FL)", 80, "Note"))

        self.app.export_csv()

        mock_file.assert_called_once()
        mock_info.assert_called_once()

    # 10. Test update chart
    def test_update_chart(self):
        self.app.clients.append(("John", 25, 70, "FL", 80, "Note"))
        self.app.clients.append(("Alice", 30, 60, "MG", 90, "Note"))

        self.app.update_chart()

        self.assertEqual(len(self.app.ax.patches), 2)

    # 11. Test reset functionality
    def test_reset(self):
        self.app.name_var.set("Test")
        self.app.age_var.set(25)
        self.app.weight_var.set(70)
        self.app.program_var.set("Fat Loss (FL)")
        self.app.progress_var.set(80)
        self.app.notes_var.set("Note")

        self.app.reset()

        self.assertEqual(self.app.name_var.get(), "")
        self.assertEqual(self.app.age_var.get(), 0)
        self.assertEqual(self.app.weight_var.get(), 0)
        self.assertEqual(self.app.program_var.get(), "")
        self.assertEqual(self.app.progress_var.get(), 0)
        self.assertEqual(self.app.notes_var.get(), "")

    # 12. Edge case: empty program selection
    def test_update_program_empty(self):
        self.app.program_var.set("")
        self.app.update_program()

        self.assertEqual(self.app.calorie_label.cget("text"), "Estimated Calories: --")


if __name__ == "__main__":
    unittest.main()
