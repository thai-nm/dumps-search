"""Tests for PDF generator page filtering functionality."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

from src.pdf_generator import PDFGenerator


class TestPDFGenerator(unittest.TestCase):
    """Test cases for PDFGenerator page filtering."""

    def setUp(self):
        """Set up test fixtures."""
        self.pdf_generator = PDFGenerator()

    def test_filter_pdf_pages_less_than_3_pages(self):
        """Test that PDFs with less than 3 pages are kept as is."""
        # Mock a PDF with 2 pages
        mock_reader = Mock()
        mock_reader.pages = [Mock(), Mock()]  # 2 pages
        
        with patch('src.pdf_generator.PdfReader', return_value=mock_reader), \
             patch('shutil.copy2') as mock_copy, \
             tempfile.NamedTemporaryFile() as temp_input, \
             tempfile.NamedTemporaryFile() as temp_output:
            
            result = self.pdf_generator._filter_pdf_pages(temp_input.name, temp_output.name)
            
            self.assertTrue(result)
            mock_copy.assert_called_once_with(temp_input.name, temp_output.name)

    def test_filter_pdf_pages_3_or_more_pages(self):
        """Test that PDFs with 3+ pages are filtered to pages 3-5."""
        # Mock a PDF with 6 pages
        mock_pages = [Mock() for _ in range(6)]
        mock_reader = Mock()
        mock_reader.pages = mock_pages
        
        mock_writer = Mock()
        mock_writer.pages = []
        
        with patch('src.pdf_generator.PdfReader', return_value=mock_reader), \
             patch('src.pdf_generator.PdfWriter', return_value=mock_writer), \
             patch('builtins.open', create=True) as mock_open, \
             tempfile.NamedTemporaryFile() as temp_input, \
             tempfile.NamedTemporaryFile() as temp_output:
            
            result = self.pdf_generator._filter_pdf_pages(temp_input.name, temp_output.name)
            
            self.assertTrue(result)
            # Should add pages 2, 3, 4 (0-indexed, which are pages 3, 4, 5)
            self.assertEqual(mock_writer.add_page.call_count, 3)
            mock_writer.write.assert_called_once()

    def test_filter_pdf_pages_exactly_5_pages(self):
        """Test filtering when PDF has exactly 5 pages."""
        # Mock a PDF with 5 pages
        mock_pages = [Mock() for _ in range(5)]
        mock_reader = Mock()
        mock_reader.pages = mock_pages
        
        mock_writer = Mock()
        mock_writer.pages = []
        
        with patch('src.pdf_generator.PdfReader', return_value=mock_reader), \
             patch('src.pdf_generator.PdfWriter', return_value=mock_writer), \
             patch('builtins.open', create=True) as mock_open, \
             tempfile.NamedTemporaryFile() as temp_input, \
             tempfile.NamedTemporaryFile() as temp_output:
            
            result = self.pdf_generator._filter_pdf_pages(temp_input.name, temp_output.name)
            
            self.assertTrue(result)
            # Should add pages 2, 3, 4 (0-indexed, which are pages 3, 4, 5)
            self.assertEqual(mock_writer.add_page.call_count, 3)

    def test_filter_pdf_pages_only_4_pages(self):
        """Test filtering when PDF has only 4 pages."""
        # Mock a PDF with 4 pages
        mock_pages = [Mock() for _ in range(4)]
        mock_reader = Mock()
        mock_reader.pages = mock_pages
        
        mock_writer = Mock()
        mock_writer.pages = []
        
        with patch('src.pdf_generator.PdfReader', return_value=mock_reader), \
             patch('src.pdf_generator.PdfWriter', return_value=mock_writer), \
             patch('builtins.open', create=True) as mock_open, \
             tempfile.NamedTemporaryFile() as temp_input, \
             tempfile.NamedTemporaryFile() as temp_output:
            
            result = self.pdf_generator._filter_pdf_pages(temp_input.name, temp_output.name)
            
            self.assertTrue(result)
            # Should add pages 2, 3 (0-indexed, which are pages 3, 4)
            self.assertEqual(mock_writer.add_page.call_count, 2)


if __name__ == '__main__':
    unittest.main()
