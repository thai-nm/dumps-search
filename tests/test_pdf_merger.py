"""Unit tests for the PDF merger module."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from src.pdf_merger import PDFMerger


class TestPDFMerger(unittest.TestCase):
    """Test cases for PDFMerger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.merger = PDFMerger()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up any temporary files created during tests
        self.merger.cleanup_temp_files()

        # Clean up temp directory
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test PDFMerger initialization."""
        merger = PDFMerger()
        self.assertIsNotNone(merger.logger)
        self.assertEqual(merger.temp_files, [])

    def test_merge_pdfs_empty_list(self):
        """Test merge_pdfs with empty PDF list."""
        output_path = os.path.join(self.temp_dir, "merged.pdf")
        result = self.merger.merge_pdfs([], output_path)
        self.assertFalse(result)

    @patch("src.pdf_merger.PdfReader")
    @patch("src.pdf_merger.PdfWriter")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("os.makedirs")
    def test_merge_pdfs_success(
        self,
        mock_makedirs,
        mock_getsize,
        mock_exists,
        mock_writer_class,
        mock_reader_class,
    ):
        """Test successful PDF merging."""
        # Setup mocks
        mock_exists.side_effect = lambda path: path.endswith(
            ".pdf"
        ) or path == os.path.join(self.temp_dir, "merged.pdf")
        mock_getsize.side_effect = lambda path: 1000 if path.endswith(".pdf") else 2000

        # Mock PDF reader
        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page2 = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_reader_class.return_value = mock_reader

        # Mock PDF writer
        mock_writer = Mock()
        mock_writer_class.return_value = mock_writer

        # Test data
        pdf_list = [
            os.path.join(self.temp_dir, "test1.pdf"),
            os.path.join(self.temp_dir, "test2.pdf"),
        ]
        output_path = os.path.join(self.temp_dir, "merged.pdf")

        # Mock file writing
        with patch("builtins.open", mock_open()):
            result = self.merger.merge_pdfs(pdf_list, output_path)

        self.assertTrue(result)
        # Verify that pages were added (2 PDFs × 2 pages each = 4 add_page calls)
        self.assertEqual(mock_writer.add_page.call_count, 4)
        mock_writer.write.assert_called_once()

    @patch("src.pdf_merger.PdfReader")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_merge_pdfs_invalid_files(
        self, mock_getsize, mock_exists, mock_reader_class
    ):
        """Test merge_pdfs with invalid PDF files."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1000
        mock_reader_class.side_effect = Exception("Invalid PDF")

        pdf_list = [os.path.join(self.temp_dir, "invalid.pdf")]
        output_path = os.path.join(self.temp_dir, "merged.pdf")

        result = self.merger.merge_pdfs(pdf_list, output_path)
        self.assertFalse(result)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_is_valid_pdf_file_not_exists(self, mock_getsize, mock_exists):
        """Test _is_valid_pdf with non-existent file."""
        mock_exists.return_value = False

        result = self.merger._is_valid_pdf("nonexistent.pdf")
        self.assertFalse(result)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_is_valid_pdf_empty_file(self, mock_getsize, mock_exists):
        """Test _is_valid_pdf with empty file."""
        mock_exists.return_value = True
        mock_getsize.return_value = 0

        result = self.merger._is_valid_pdf("empty.pdf")
        self.assertFalse(result)

    @patch("src.pdf_merger.PdfReader")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_is_valid_pdf_no_pages(self, mock_getsize, mock_exists, mock_reader_class):
        """Test _is_valid_pdf with PDF that has no pages."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1000

        mock_reader = Mock()
        mock_reader.pages = []
        mock_reader_class.return_value = mock_reader

        result = self.merger._is_valid_pdf("no_pages.pdf")
        self.assertFalse(result)

    @patch("src.pdf_merger.PdfReader")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_is_valid_pdf_success(self, mock_getsize, mock_exists, mock_reader_class):
        """Test _is_valid_pdf with valid PDF."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1000

        mock_reader = Mock()
        mock_page = Mock()
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader

        result = self.merger._is_valid_pdf("valid.pdf")
        self.assertTrue(result)

    @patch("src.pdf_merger.PdfReader")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_is_valid_pdf_exception(self, mock_getsize, mock_exists, mock_reader_class):
        """Test _is_valid_pdf with exception during PDF reading."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1000
        mock_reader_class.side_effect = Exception("PDF read error")

        result = self.merger._is_valid_pdf("corrupted.pdf")
        self.assertFalse(result)

    def test_validate_pdf_files(self):
        """Test _validate_pdf_files method."""
        pdf_list = ["valid1.pdf", "invalid.pdf", "valid2.pdf"]

        with patch.object(self.merger, "_is_valid_pdf") as mock_is_valid:
            mock_is_valid.side_effect = [True, False, True]

            result = self.merger._validate_pdf_files(pdf_list)

            self.assertEqual(result, ["valid1.pdf", "valid2.pdf"])
            self.assertEqual(mock_is_valid.call_count, 3)

    def test_add_temp_file(self):
        """Test add_temp_file method."""
        file_path = "/tmp/test.pdf"
        self.merger.add_temp_file(file_path)

        self.assertIn(file_path, self.merger.temp_files)

        # Test adding the same file again (should not duplicate)
        self.merger.add_temp_file(file_path)
        self.assertEqual(self.merger.temp_files.count(file_path), 1)

    def test_add_temp_file_empty_path(self):
        """Test add_temp_file with empty path."""
        self.merger.add_temp_file("")
        self.merger.add_temp_file(None)

        self.assertEqual(len(self.merger.temp_files), 0)

    @patch("os.path.exists")
    @patch("os.remove")
    def test_cleanup_temp_files_success(self, mock_remove, mock_exists):
        """Test successful cleanup of temporary files."""
        mock_exists.return_value = True

        # Add some temp files
        temp_files = ["/tmp/test1.pdf", "/tmp/test2.pdf"]
        for file_path in temp_files:
            self.merger.add_temp_file(file_path)

        self.merger.cleanup_temp_files()

        self.assertEqual(mock_remove.call_count, 2)
        self.assertEqual(len(self.merger.temp_files), 0)

    @patch("os.path.exists")
    @patch("os.remove")
    def test_cleanup_temp_files_with_specific_list(self, mock_remove, mock_exists):
        """Test cleanup with specific file list."""
        mock_exists.return_value = True

        # Add some temp files to tracker
        self.merger.add_temp_file("/tmp/tracked1.pdf")
        self.merger.add_temp_file("/tmp/tracked2.pdf")

        # Clean up specific files (not tracked)
        specific_files = ["/tmp/specific1.pdf", "/tmp/specific2.pdf"]
        self.merger.cleanup_temp_files(specific_files)

        self.assertEqual(mock_remove.call_count, 2)
        # Tracked files should still be there
        self.assertEqual(len(self.merger.temp_files), 2)

    @patch("os.path.exists")
    @patch("os.remove")
    def test_cleanup_temp_files_file_not_exists(self, mock_remove, mock_exists):
        """Test cleanup when files don't exist."""
        mock_exists.return_value = False

        self.merger.add_temp_file("/tmp/nonexistent.pdf")
        self.merger.cleanup_temp_files()

        mock_remove.assert_not_called()
        self.assertEqual(len(self.merger.temp_files), 0)

    @patch("os.path.exists")
    @patch("os.remove")
    def test_cleanup_temp_files_remove_failure(self, mock_remove, mock_exists):
        """Test cleanup when file removal fails."""
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")

        self.merger.add_temp_file("/tmp/protected.pdf")
        self.merger.cleanup_temp_files()

        mock_remove.assert_called_once()
        # File should still be removed from tracked list even if removal failed
        # because the cleanup logic removes it regardless of file existence
        self.assertEqual(len(self.merger.temp_files), 0)

    @patch("tempfile.mkstemp")
    @patch("os.close")
    def test_create_temp_file_success(self, mock_close, mock_mkstemp):
        """Test successful temporary file creation."""
        mock_mkstemp.return_value = (123, "/tmp/examtopics_abc123.pdf")

        result = self.merger.create_temp_file()

        self.assertEqual(result, "/tmp/examtopics_abc123.pdf")
        self.assertIn("/tmp/examtopics_abc123.pdf", self.merger.temp_files)
        mock_close.assert_called_once_with(123)

    @patch("tempfile.mkstemp")
    @patch("os.close")
    def test_create_temp_file_custom_params(self, mock_close, mock_mkstemp):
        """Test temporary file creation with custom parameters."""
        mock_mkstemp.return_value = (456, "/tmp/custom_xyz789.txt")

        result = self.merger.create_temp_file(suffix=".txt", prefix="custom_")

        self.assertEqual(result, "/tmp/custom_xyz789.txt")
        mock_mkstemp.assert_called_once_with(suffix=".txt", prefix="custom_")
        mock_close.assert_called_once_with(456)

    @patch("tempfile.mkstemp")
    def test_create_temp_file_failure(self, mock_mkstemp):
        """Test temporary file creation failure."""
        mock_mkstemp.side_effect = OSError("No space left on device")

        with self.assertRaises(OSError):
            self.merger.create_temp_file()

    def test_get_temp_files_count(self):
        """Test get_temp_files_count method."""
        self.assertEqual(self.merger.get_temp_files_count(), 0)

        self.merger.add_temp_file("/tmp/test1.pdf")
        self.assertEqual(self.merger.get_temp_files_count(), 1)

        self.merger.add_temp_file("/tmp/test2.pdf")
        self.assertEqual(self.merger.get_temp_files_count(), 2)

    def test_cleanup_temp_files_empty_list(self):
        """Test cleanup with empty temp files list."""
        # Should not raise any exceptions
        self.merger.cleanup_temp_files()
        self.assertEqual(len(self.merger.temp_files), 0)

    @patch("src.pdf_merger.PdfWriter")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("os.makedirs")
    def test_merge_pdfs_output_directory_creation(
        self, mock_makedirs, mock_getsize, mock_exists, mock_writer_class
    ):
        """Test that output directory is created when it doesn't exist."""
        mock_exists.side_effect = lambda path: path.endswith("input.pdf")
        mock_getsize.return_value = 1000

        # Mock PDF components
        mock_writer = Mock()
        mock_writer_class.return_value = mock_writer

        with patch.object(
            self.merger, "_validate_pdf_files", return_value=["input.pdf"]
        ):
            output_path = os.path.join(self.temp_dir, "subdir", "merged.pdf")
            with patch("builtins.open", mock_open()):
                self.merger.merge_pdfs(["input.pdf"], output_path)

            # Verify makedirs was called for the output directory
            expected_dir = os.path.dirname(output_path)
            mock_makedirs.assert_called_with(expected_dir, exist_ok=True)



if __name__ == "__main__":
    unittest.main()
