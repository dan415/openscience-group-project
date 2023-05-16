import pytest
from analyzer import Analyzer

class TestAnalyzer:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Common initial setup for all test cases
        self.analyzer = Analyzer()

    def test_blank_pdf(self):
        # Test Case 01: Run with a blank PDF file
        # Verify that the expected files are generated and no exceptions are raised
        result = self.analyzer.run("C:\\Users\\aleja\\OneDrive\\Documents\\UNI\\UPM\\OPTATIVAS\\IA\\BLANK.pdf")
        assert result["figures"] == []                                                                 
        assert result["links"] == []
        assert result["summary"] == {}
        assert "wordcloud" not in result

    def test_correct_num_papers(self):
        # Test Case 02: Run with 3 valid PDF files
        # Verify that the expected files are generated and no exceptions are raised
        result = self.analyzer.run("C:\\Users\\aleja\\OneDrive\\Documents\\UNI\\UPM\\OPTATIVAS\\IA\\1901.04407.pdf", "C:\\Users\\aleja\\OneDrive\\Documents\\UNI\UPM\\OPTATIVAS\\IA\\08220479.pdf", "C:\\Users\\aleja\\OneDrive\\Documents\\UNI\\UPM\\OPTATIVAS\\IA\\f_1730.pdf")
        assert len(result["figures"]) == 7
        assert len(result["links"]) == 7
        assert len(result["summary"]) == 7
        assert "wordcloud" not in result

    def test_correct_num_figures(self):
        # Test Case 03: Run with 4 valid PDF files
        # Verify that the expected files are generated and no exceptions are raised
        result = self.analyzer.run("C:\\Users\\aleja\\OneDrive\\Documents\\UNI\\UPM\\OPTATIVAS\\IA\\1901.04407.pdf", "C:\\Users\\aleja\\OneDrive\\Documents\\UNI\UPM\\OPTATIVAS\\IA\\08220479.pdf", "C:\\Users\\aleja\\OneDrive\\Documents\\UNI\\UPM\\OPTATIVAS\\IA\\f_1730.pdf")
        assert len(result["figures"]) == 25
        assert len(result["links"]) == 4
        assert len(result["summary"]) == 4
        assert "wordcloud" not in result

    def test_correct_num_links(self):
        # Test Case 04: Run with 4 valid PDF files
        # Verify that the expected files are generated and no exceptions are raised
        result = self.analyzer.run("C:\\Users\\aleja\\OneDrive\\Documents\\UNI\\UPM\\OPTATIVAS\\IA\\1901.04407.pdf", "C:\\Users\\aleja\\OneDrive\\Documents\\UNI\UPM\\OPTATIVAS\\IA\\08220479.pdf", "C:\\Users\\aleja\\OneDrive\\Documents\\UNI\\UPM\\OPTATIVAS\\IA\\f_1730.pdf")
        assert len(result["figures"]) == 25
        assert len(result["links"]) == 8
        assert len(result["summary"]) == 4
        assert "wordcloud" not in result
