#!/usr/bin/env python3
"""Simple main CLI application for ExamTopics PDF Scraper."""

import argparse
import logging
import os
import sys

from config import ConfigManager
from search import SearchEngine
from pdf_generator import PDFGenerator


def setup_logging(log_level: str = "info"):
    """Setup logging configuration."""
    level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }
    
    level = level_map.get(log_level.lower(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="ExamTopics PDF Scraper")
    
    parser.add_argument('--exam', required=True, help='Exam code (e.g., saa-c03)')
    parser.add_argument('--begin', type=int, required=True, help='Beginning question number')
    parser.add_argument('--end', type=int, required=True, help='Ending question number')
    parser.add_argument('--topic', type=int, default=1, help='Topic number (default: 1)')
    parser.add_argument('--output', default='output', help='Output directory for PDF files')
    parser.add_argument('--config', default='settings.json', help='Configuration file path')
    parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error'], 
                       default='info', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        logger.info("Starting ExamTopics PDF Scraper...")
        config_manager = ConfigManager(args.config)
        search_engine = SearchEngine()
        pdf_generator = PDFGenerator()
        
        # Load configuration
        logger.info("Loading configuration...")
        config = config_manager.load_config()
        
        # Get exam configuration
        exam_config = config_manager.get_exam_config(args.exam)
        if not exam_config:
            logger.error(f"Exam '{args.exam}' not found in configuration")
            logger.info(f"Available exams: {config_manager.list_available_exams()}")
            return
        
        logger.info(f"Found exam config for: {args.exam}")
        
        # Validate question range
        if args.begin > args.end:
            logger.error(f"Begin question number ({args.begin}) cannot be greater than end question number ({args.end})")
            return
        
        url_substring = exam_config['url_substring']
        
        logger.info(f"Processing questions {args.begin} to {args.end} in topic {args.topic}")
        
        # Track results
        successful_urls = []
        failed_questions = []
        generated_pdfs = []
        pdf_failures = []
        
        # Process each question in the range
        for question_num in range(args.begin, args.end + 1):
            logger.info(f"Processing question {question_num}...")
            
            # Replace placeholders in title and keyword for current question
            title = exam_config['title'].replace('#TOPIC', str(args.topic)).replace('#QUESTION', str(question_num))
            keyword = exam_config['keyword'].replace('#TOPIC', str(args.topic)).replace('#QUESTION', str(question_num))
            
            logger.debug(f"Question {question_num} - Title: {title}")
            logger.debug(f"Question {question_num} - Keyword: {keyword}")
            
            # Perform search for current question
            result_url = search_engine.search_question(keyword, title, url_substring)
            
            if result_url:
                successful_urls.append((question_num, result_url))
                logger.info(f"✓ SUCCESS: Found URL for question {question_num}")
                
                # Generate PDF from the found URL
                pdf_filename = f"{args.exam}_topic{args.topic}_question{question_num}.pdf"
                pdf_path = os.path.join(args.output, pdf_filename)
                
                logger.info(f"Generating PDF for question {question_num}...")
                pdf_success = pdf_generator.generate_pdf(result_url, pdf_path)
                
                if pdf_success:
                    generated_pdfs.append((question_num, pdf_path))
                    logger.info(f"✓ PDF SUCCESS: Generated {pdf_filename}")
                else:
                    pdf_failures.append((question_num, result_url))
                    logger.error(f"✗ PDF FAILED: Could not generate PDF for question {question_num}")
            else:
                failed_questions.append(question_num)
                logger.warning(f"✗ FAILED: No valid URL found for question {question_num}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total questions processed: {args.end - args.begin + 1}")
        print(f"URLs found: {len(successful_urls)}")
        print(f"PDFs generated: {len(generated_pdfs)}")
        print(f"PDF generation failed: {len(pdf_failures)}")
        print(f"No URLs found: {len(failed_questions)}")
        
        if generated_pdfs:
            print(f"\n✓ SUCCESSFULLY GENERATED PDFs:")
            for question_num, pdf_path in generated_pdfs:
                print(f"  Question {question_num}: {pdf_path}")
        
        if pdf_failures:
            print(f"\n✗ PDF GENERATION FAILURES:")
            for question_num, url in pdf_failures:
                print(f"  Question {question_num}: Failed to generate PDF from {url}")
        
        if failed_questions:
            print(f"\n✗ NO URLs FOUND:")
            for question_num in failed_questions:
                print(f"  Question {question_num}: No valid URL found")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
