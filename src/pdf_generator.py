"""PDF generation module for ExamTopics PDF Scraper."""

import logging
import os
from urllib.parse import urlparse
import tempfile

# Configure logging for the WeasyPrint library to hide unsupported CSS warnings
# GitHub Issue:
# - https://github.com/Kozea/WeasyPrint/issues/312
# - https://github.com/Kozea/WeasyPrint/issues/412
wp_logger = logging.getLogger("weasyprint")
wp_logger.addHandler(logging.NullHandler())
wp_logger.setLevel(40)

from weasyprint import HTML
from pypdf import PdfReader, PdfWriter


class PDFGenerator:
    """Handles PDF generation from web pages using weasyprint."""

    def __init__(self):
        """Initialize the PDF generator."""
        self.logger = logging.getLogger(__name__)

    def generate_pdf(self, url: str, output_path: str) -> bool:
        """Convert a web page URL to PDF.

        Args:
            url: URL of the web page to convert
            output_path: Path where the PDF file should be saved

        Returns:
            True if PDF generation was successful, False otherwise
        """
        try:
            self.logger.debug(f"Generating PDF from URL: {url}")

            # Validate URL
            if not self._validate_url(url):
                self.logger.error(f"Invalid URL: {url}")
                return False

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Generate PDF to a temporary file first
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_pdf_path = temp_file.name
            
            try:
                html_doc = HTML(url=url)
                html_doc.write_pdf(temp_pdf_path)

                # Filter pages if necessary
                if not self._filter_pdf_pages(temp_pdf_path, output_path):
                    return False

                # Verify the final PDF was created and has content
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    self.logger.debug(
                        f"PDF generated successfully: {output_path} ({os.path.getsize(output_path)} bytes)"
                    )
                    return True
                else:
                    self.logger.error(
                        f"PDF file was not created or is empty: {output_path}"
                    )
                    return False
            finally:
                # Clean up temporary file
                if os.path.exists(temp_pdf_path):
                    try:
                        os.remove(temp_pdf_path)
                    except Exception:
                        pass

        except Exception as e:
            self.logger.error(f"PDF generation failed for {url}: {str(e)}")
            # Clean up partial file if it exists
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
            return False

    def _filter_pdf_pages(self, input_path: str, output_path: str) -> bool:
        """Filter PDF pages based on the specified logic.
        
        If PDF has less than 3 pages, keep as is.
        If PDF has 3 or more pages, only keep pages 3 to 5.

        Args:
            input_path: Path to the input PDF file
            output_path: Path where the filtered PDF should be saved

        Returns:
            True if filtering was successful, False otherwise
        """
        try:
            # Read the input PDF
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            
            self.logger.debug(f"PDF has {total_pages} pages")
            
            # If less than 3 pages, copy the file as is
            if total_pages < 3:
                self.logger.debug("PDF has less than 3 pages, keeping all pages")
                import shutil
                shutil.copy2(input_path, output_path)
                return True
            
            # If 3 or more pages, keep only pages 3 to 5 (0-indexed: pages 2 to 4)
            writer = PdfWriter()
            start_page = 2  # Page 3 (0-indexed)
            end_page = min(4, total_pages - 1)  # Page 5 or last page if less than 5 pages
            
            self.logger.debug(f"Filtering pages: keeping pages {start_page + 1} to {end_page + 1}")
            
            for page_num in range(start_page, end_page + 1):
                if page_num < total_pages:
                    writer.add_page(reader.pages[page_num])
            
            # Write the filtered PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            filtered_pages = len(writer.pages)
            self.logger.debug(f"Filtered PDF created with {filtered_pages} pages")
            return True
            
        except Exception as e:
            self.logger.error(f"PDF page filtering failed: {str(e)}")
            return False

    def _validate_url(self, url: str) -> bool:
        """Validate if the URL is properly formatted.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
