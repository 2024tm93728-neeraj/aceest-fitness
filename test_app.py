import unittest
import tkinter as tk
from app import ACEestApp

class TestACEestApp(unittest.TestCase):

    def setUp(self):
        """Setup test environment"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide GUI
        self.app = ACEestApp(self.root)

    def tearDown(self):
        """Clean up after tests"""
        self.root.destroy()

    # Test 1: Programs dictionary exists
    def test_programs_exist(self):
        self.assertIsInstance(self.app.programs, dict)
        self.assertEqual(len(self.app.programs), 3)

    # Test 2: Check program keys
    def test_program_keys(self):
        expected = ["Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"]
        for key in expected:
            self.assertIn(key, self.app.programs)

    # Test 3: Dropdown values match programs
    def test_combobox_values(self):
        values = list(self.app.prog_menu["values"])
        self.assertEqual(values, list(self.app.programs.keys()))

    # Test 4: Default label text
    def test_default_labels(self):
        self.assertIn("Select a profile", self.app.work_label.cget("text"))
        self.assertIn("Select a profile", self.app.diet_label.cget("text"))

    # Test 5: Update display - Fat Loss
    def test_update_display_fat_loss(self):
        self.app.prog_var.set("Fat Loss (FL)")
        self.app.update_display(None)

        self.assertIn("Back Squat", self.app.work_label.cget("text"))
        self.assertIn("Egg Whites", self.app.diet_label.cget("text"))

    # Test 6: Update display - Muscle Gain
    def test_update_display_muscle_gain(self):
        self.app.prog_var.set("Muscle Gain (MG)")
        self.app.update_display(None)

        self.assertIn("Squat 5x5", self.app.work_label.cget("text"))
        self.assertIn("Chicken Biryani", self.app.diet_label.cget("text"))

    # Test 7: Update display - Beginner
    def test_update_display_beginner(self):
        self.app.prog_var.set("Beginner (BG)")
        self.app.update_display(None)

        self.assertIn("Circuit Training", self.app.work_label.cget("text"))
        self.assertIn("Balanced Tamil Meals", self.app.diet_label.cget("text"))

    # Test 8: Color applied correctly
    def test_color_update(self):
        self.app.prog_var.set("Fat Loss (FL)")
        self.app.update_display(None)

        self.assertEqual(self.app.work_label.cget("fg"), "#e74c3c")

    # Test 9: Invalid selection handling (edge case)
    def test_invalid_program(self):
        self.app.prog_var.set("Invalid Program")

        with self.assertRaises(KeyError):
            self.app.update_display(None)


if __name__ == "__main__":
    unittest.main()
