import unittest
import tkinter as tk
from unittest.mock import patch
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

    # 3. Test update program - Fat Loss
    def test_update_program_fat_loss(self):
        self.app.program_var.set("Fat Loss (FL)")
        self.app.weight_var.set(70)

        self.app.update_program()

        workout_text = self.app.workout_text.get("1.0", "end")
        diet_text = self.app.diet_text.get("1.0", "end")

        self.assertIn("Back Squat", workout_text)
        self.assertIn("Egg Whites", diet_text)
        self.assertIn("Estimated Calories", self.app.calorie_label.cget("text"))

    # 4. Test calorie calculation
    def test_calorie_calculation(self):
        self.app.program_var.set("Muscle Gain (MG)")
        self.app.weight_var.set(80)

        self.app.update_program()

        expected = 80 * 35
        self.assertIn(str(expected), self.app.calorie_label.cget("text"))

    # 5. Test update text helper
    def test_update_text_method(self):
        self.app._update_text(self.app.workout_text, "Test Content", "red")

        content = self.app.workout_text.get("1.0", "end")
        self.assertIn("Test Content", content)

    # 6. Test save client success
    @patch("tkinter.messagebox.showinfo")
    def test_save_client_success(self, mock_showinfo):
        self.app.name_var.set("John")
        self.app.program_var.set("Fat Loss (FL)")
        self.app.progress_var.set(80)

        self.app.save_client()
        mock_showinfo.assert_called_once()

    # 7. Test save client validation
    @patch("tkinter.messagebox.showwarning")
    def test_save_client_warning(self, mock_warning):
        self.app.name_var.set("")
        self.app.program_var.set("")

        self.app.save_client()
        mock_warning.assert_called_once()

    # 8. Test reset functionality
    def test_reset_function(self):
        self.app.name_var.set("Test")
        self.app.age_var.set(25)
        self.app.weight_var.set(70)
        self.app.program_var.set("Fat Loss (FL)")
        self.app.progress_var.set(90)

        self.app.reset()

        self.assertEqual(self.app.name_var.get(), "")
        self.assertEqual(self.app.age_var.get(), 0)
        self.assertEqual(self.app.weight_var.get(), 0)
        self.assertEqual(self.app.program_var.get(), "")
        self.assertEqual(self.app.progress_var.get(), 0)
        self.assertIn("--", self.app.calorie_label.cget("text"))

    # 9. Edge case: no weight
    def test_no_weight_no_calculation(self):
        self.app.program_var.set("Fat Loss (FL)")
        self.app.weight_var.set(0)

        self.app.update_program()

        self.assertEqual(self.app.calorie_label.cget("text"), "Estimated Calories: --")


if __name__ == "__main__":
    unittest.main()
