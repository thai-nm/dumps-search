"""PDF generation module for ExamTopics PDF Scraper."""

import logging
import os
from urllib.parse import urlparse

from weasyprint import HTML


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
            self.logger.info(f"Generating PDF from URL: {url}")

            # Validate URL
            if not self._validate_url(url):
                self.logger.error(f"Invalid URL: {url}")
                return False

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Generate PDF directly from URL
            html_doc = HTML(url=url)
            html_doc.write_pdf(output_path)

            # Verify the PDF was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.logger.info(
                    f"PDF generated successfully: {output_path} ({os.path.getsize(output_path)} bytes)"
                )
                return True
            else:
                self.logger.error(
                    f"PDF file was not created or is empty: {output_path}"
                )
                return False

        except Exception as e:
            self.logger.error(f"PDF generation failed for {url}: {str(e)}")
            # Clean up partial file if it exists
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
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
