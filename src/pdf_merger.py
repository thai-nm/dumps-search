import os
import tempfile
from typing import List, Optional
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from logger import get_app_logger


class PDFMerger:

    def __init__(self):
        self.logger = get_app_logger()
        self.temp_files: List[str] = []

    def merge_pdfs(self, pdf_list: List[str], output_path: str) -> bool:
        if not pdf_list:
            self.logger.error("No PDF files provided for merging")
            return False

        try:
            self.logger.debug(f"Starting PDF merge operation with {len(pdf_list)} files")
            
            valid_pdfs = self._validate_pdf_files(pdf_list)
            if not valid_pdfs:
                self.logger.error("No valid PDF files found for merging")
                return False

            if len(valid_pdfs) < len(pdf_list):
                self.logger.warning(
                    f"Only {len(valid_pdfs)} out of {len(pdf_list)} PDF files are valid"
                )

            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            writer = PdfWriter()
            total_pages = 0

            # Merge all valid PDFs
            for pdf_path in valid_pdfs:
                try:
                    self.logger.debug(f"Processing PDF: {pdf_path}")
                    reader = PdfReader(pdf_path)
                    page_count = len(reader.pages)
                    
                    # Add all pages from current PDF
                    for page_num in range(page_count):
                        writer.add_page(reader.pages[page_num])
                    
                    total_pages += page_count
                    self.logger.debug(f"Added {page_count} pages from {pdf_path}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process PDF {pdf_path}: {str(e)}")
                    continue

            if total_pages > 0:
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                # Verify the output file was created successfully
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    self.logger.debug(
                        f"PDF merge completed successfully: {output_path} "
                        f"({total_pages} pages, {os.path.getsize(output_path)} bytes)"
                    )
                    return True
                else:
                    self.logger.error("Merged PDF file was not created or is empty")
                    return False
            else:
                self.logger.error("No pages were added to the merged PDF")
                return False

        except Exception as e:
            self.logger.error(f"PDF merge operation failed: {str(e)}")
            # Clean up partial output file if it exists
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
            return False

    def _validate_pdf_files(self, pdf_list: List[str]) -> List[str]:
        valid_pdfs = []
        
        for pdf_path in pdf_list:
            if self._is_valid_pdf(pdf_path):
                valid_pdfs.append(pdf_path)
            else:
                self.logger.warning(f"Invalid or corrupted PDF file: {pdf_path}")
        
        return valid_pdfs

    def _is_valid_pdf(self, pdf_path: str) -> bool:
        try:
            if not os.path.exists(pdf_path):
                self.logger.debug(f"PDF file does not exist: {pdf_path}")
                return False
            
            if os.path.getsize(pdf_path) == 0:
                self.logger.debug(f"PDF file is empty: {pdf_path}")
                return False

            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            
            if page_count == 0:
                self.logger.debug(f"PDF file has no pages: {pdf_path}")
                return False
            
            # Try to access the first page to ensure it's readable
            _ = reader.pages[0]
            
            self.logger.debug(f"PDF file is valid: {pdf_path} ({page_count} pages)")
            return True
            
        except Exception as e:
            self.logger.debug(f"PDF validation failed for {pdf_path}: {str(e)}")
            return False

    def add_temp_file(self, file_path: str) -> None:
        if file_path and file_path not in self.temp_files:
            self.temp_files.append(file_path)
            self.logger.debug(f"Added temporary file for cleanup: {file_path}")

    def cleanup_temp_files(self, file_list: Optional[List[str]] = None) -> None:
        files_to_clean = file_list if file_list is not None else self.temp_files.copy()
        
        if not files_to_clean:
            self.logger.debug("No temporary files to clean up")
            return

        cleaned_count = 0
        failed_count = 0

        for file_path in files_to_clean:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
                    self.logger.debug(f"Cleaned up temporary file: {file_path}")
                    
                    # Remove from tracked temp files if it was there
                    if file_path in self.temp_files:
                        self.temp_files.remove(file_path)
                else:
                    self.logger.debug(f"Temporary file already removed: {file_path}")
                    
                # Remove from tracked temp files regardless of whether file exists
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
                    
            except Exception as e:
                failed_count += 1
                self.logger.warning(f"Failed to clean up temporary file {file_path}: {str(e)}")
                # Remove from tracked temp files even if removal failed
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)

        if cleaned_count > 0 or failed_count > 0:
            self.logger.debug(
                f"Cleanup completed: {cleaned_count} files removed, {failed_count} failures"
            )

    def create_temp_file(self, suffix: str = '.pdf', prefix: str = 'examtopics_') -> str:
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(temp_fd)  # Close the file descriptor
            
            # Track for cleanup
            self.add_temp_file(temp_path)
            
            self.logger.debug(f"Created temporary file: {temp_path}")
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Failed to create temporary file: {str(e)}")
            raise

    def get_temp_files_count(self) -> int:
        return len(self.temp_files)

    def __del__(self):
        # Cleanup temporary files when the object is destroyed
        if hasattr(self, 'temp_files') and self.temp_files:
            try:
                self.cleanup_temp_files()
            except Exception:
                # Ignore cleanup errors during destruction
                pass
