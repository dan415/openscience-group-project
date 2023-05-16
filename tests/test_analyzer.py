import unittest
import os
import subprocess

class TestAnalyzer(unittest.TestCase):
    def test_blank_pdf(self):
        # Case: Run with a blank PDF file
        input_folder = "res/datasets/space/raw/blank.pdf"

        # Run the program with the input folder
        command = f"python src/main.py --input {input_folder}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check the program's output
        self.assertNotEqual(result.returncode, 0)  # Verify that the program exited with a non-zero return code
        self.assertIn("Error:", result.stderr)  # Verify that an error message is present in the stderr output

    def test_single_pdf(self):
        # Case: Run with a single valid PDF file
        input_folder = "res/datasets/space/raw/2007000499.pdf"

        # Run the program with the input folder
        command = f"python src/main.py --input {input_folder}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check the program's output
        self.assertEqual(result.returncode, 0)  # Verify that the program exited with a return code of 0
        print("stdout:", result.stdout)  # Print the program's standard output
        print("stderr:", result.stderr)  # Print the program's standard error

    def test_specific_pdf(self):
        # Case: Run with a specific valid PDF file
        input_folder = "res/datasets/space/raw/Emotion_Analysis_in_Man-Machine_Interaction_System.pdf"

        # Run the program with the input folder
        command = f"python src/main.py --input {input_folder}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check the program's output
        self.assertEqual(result.returncode, 0)  # Verify that the program exited with a return code of 0
        print("stdout:", result.stdout)  # Print the program's standard output
        print("stderr:", result.stderr)  # Print the program's standard error

    def test_multiple_pdfs(self):
        # Case: Run with multiple valid PDF files
        input_folder = "res/datasets/space/raw/"

        # Run the program with the input folder
        command = f"python src/main.py --input {input_folder}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check the program's output
        self.assertEqual(result.returncode, 0)  # Verify that the program exited with a return code of 0
        print("stdout:", result.stdout)  # Print the program's standard output
        print("stderr:", result.stderr)  # Print the program's standard error