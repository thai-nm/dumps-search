#!/usr/bin/env python3

import argparse
import os
import sys

from .config import ConfigManager
from .search import SearchEngine
from .pdf_generator import PDFGenerator
from .pdf_merger import PDFMerger
from .logger import setup_logging, get_app_logger


def main():
    parser = argparse.ArgumentParser(description="ExamTopics PDF Scraper")

    parser.add_argument("--exam", required=True, help="Exam code (e.g., saa-c03)")
    parser.add_argument(
        "--begin", type=int, required=True, help="Beginning question number"
    )
    parser.add_argument("--end", type=int, required=True, help="Ending question number")
    parser.add_argument(
        "--topic", type=int, default=1, help="Topic number (default: 1)"
    )
    parser.add_argument(
        "--output", default="output", help="Output directory for PDF files"
    )
    parser.add_argument(
        "--config", default="settings.json", help="Configuration file path"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge all generated PDFs into a single file",
    )
    parser.add_argument(
        "--keep-individual",
        action="store_true",
        help="Keep individual PDF files after merging (default: delete them)",
    )

    args = parser.parse_args()

    try:
        # Initialize config manager first to get log level from settings
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()

        # Setup logging using config from settings.json (override CLI argument)
        config_log_level = config_manager.get_log_level()
        setup_logging(config_log_level)
        logger = get_app_logger()

        # Initialize components
        logger.info("Starting ExamTopics PDF Scraper...")
        search_engine = SearchEngine()
        pdf_generator = PDFGenerator()

        logger.info("Configuration loaded successfully")

        # Get exam configuration
        exam_config = config_manager.get_exam_config(args.exam)
        if not exam_config:
            logger.error(f"Exam '{args.exam}' not found in configuration")
            logger.info(f"Available exams: {config_manager.list_available_exams()}")
            return

        logger.info(f"Found exam config for: {args.exam}")

        # Validate question range
        if args.begin > args.end:
            logger.error(
                f"Begin question number ({args.begin}) cannot be greater than end question number ({args.end})"
            )
            return

        url_substring = exam_config["url_substring"]

        logger.info(
            f"Processing questions {args.begin} to {args.end} in topic {args.topic}"
        )

        # Track results
        successful_urls = []
        failed_questions = []
        generated_pdfs = []
        pdf_failures = []

        # Process each question in the range
        for question_num in range(args.begin, args.end + 1):
            logger.info(f"Processing question {question_num}...")

            # Replace placeholders in title and keyword for current question
            title = (
                exam_config["title"]
                .replace("#TOPIC", str(args.topic))
                .replace("#QUESTION", str(question_num))
            )
            keyword = (
                exam_config["keyword"]
                .replace("#TOPIC", str(args.topic))
                .replace("#QUESTION", str(question_num))
            )

            logger.debug(f"Question {question_num} - Title: {title}")
            logger.debug(f"Question {question_num} - Keyword: {keyword}")

            # Perform search for current question
            result_url = search_engine.search_question(keyword, title, url_substring)

            if result_url:
                successful_urls.append((question_num, result_url))
                logger.info(f"✓ SUCCESS: Found URL for question {question_num}")

                # Generate PDF from the found URL
                pdf_filename = (
                    f"{args.exam}_topic{args.topic}_question{question_num}.pdf"
                )
                pdf_path = os.path.join(args.output, pdf_filename)

                logger.info(f"Generating PDF for question {question_num}...")
                pdf_success = pdf_generator.generate_pdf(result_url, pdf_path)

                if pdf_success:
                    generated_pdfs.append((question_num, pdf_path))
                    logger.info(f"✓ PDF SUCCESS: Generated {pdf_filename}")
                else:
                    pdf_failures.append((question_num, result_url))
                    logger.error(
                        f"✗ PDF FAILED: Could not generate PDF for question {question_num}"
                    )
            else:
                failed_questions.append(question_num)
                logger.warning(
                    f"✗ FAILED: No valid URL found for question {question_num}"
                )

        # Log summary
        logger.info(f"{'='*60}")
        logger.info(f"PROCESSING SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total questions processed: {args.end - args.begin + 1}")
        logger.info(f"URLs found: {len(successful_urls)}")
        logger.info(f"PDFs generated: {len(generated_pdfs)}")
        logger.info(f"PDF generation failed: {len(pdf_failures)}")
        logger.info(f"No URLs found: {len(failed_questions)}")

        if generated_pdfs:
            logger.info(f"\n✓ SUCCESSFULLY GENERATED PDFs:")
            for question_num, pdf_path in generated_pdfs:
                logger.debug(f"  Question {question_num}: {pdf_path}")

        if pdf_failures:
            logger.info(f"\n✗ PDF GENERATION FAILURES:")
            for question_num, url in pdf_failures:
                logger.debug(
                    f"  Question {question_num}: Failed to generate PDF from {url}"
                )

        if failed_questions:
            logger.info(f"\n✗ NO URLs FOUND:")
            for question_num in failed_questions:
                logger.debug(f"  Question {question_num}: No valid URL found")

        # Merge PDFs if requested and we have generated PDFs
        if args.merge and generated_pdfs:
            logger.info("Starting PDF merge process...")
            pdf_merger = PDFMerger()

            try:
                # Extract just the file paths from generated_pdfs
                pdf_paths = [pdf_path for _, pdf_path in generated_pdfs]

                # Create merged PDF filename
                merged_filename = f"{args.exam}_topic{args.topic}_questions{args.begin}-{args.end}_merged.pdf"
                merged_path = os.path.join(args.output, merged_filename)

                logger.info(f"Merging {len(pdf_paths)} PDFs into: {merged_filename}")

                # Perform the merge
                merge_success = pdf_merger.merge_pdfs(pdf_paths, merged_path)

                if merge_success:
                    logger.info(f"{'='*60}")
                    logger.info(f"PDF MERGE SUMMARY")
                    logger.info(f"{'='*60}")
                    logger.info(f"✓ MERGE SUCCESS: Created {merged_filename}")
                    logger.debug(f"  Location: {merged_path}")
                    logger.debug(f"  Merged {len(pdf_paths)} individual PDFs")

                    # Clean up individual PDFs if not keeping them
                    if not args.keep_individual:
                        logger.debug("Cleaning up individual PDF files...")
                        cleanup_count = 0
                        cleanup_failures = 0

                        for _, pdf_path in generated_pdfs:
                            try:
                                if os.path.exists(pdf_path):
                                    os.remove(pdf_path)
                                    cleanup_count += 1
                                    logger.debug(f"Removed individual PDF: {pdf_path}")
                            except Exception as e:
                                cleanup_failures += 1
                                logger.warning(f"Failed to remove {pdf_path}: {str(e)}")

                        logger.debug(
                            f"  Cleaned up {cleanup_count} individual PDF files"
                        )
                        if cleanup_failures > 0:
                            logger.warning(
                                f"  Failed to clean up {cleanup_failures} files"
                            )
                    else:
                        logger.debug(f"  Individual PDF files preserved")

                else:
                    logger.error(f"\n✗ MERGE FAILED: Could not create merged PDF")
                    logger.error("PDF merge operation failed")

            except Exception as e:
                logger.error(f"PDF merge error: {str(e)}")
                logger.error(f"\n✗ MERGE ERROR: {str(e)}")
            finally:
                # Clean up any temporary files created by the merger
                pdf_merger.cleanup_temp_files()

        elif args.merge and not generated_pdfs:
            logger.warning("PDF merge requested but no PDFs were generated")
            logger.warning(f"\n⚠ MERGE SKIPPED: No PDFs available to merge")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
