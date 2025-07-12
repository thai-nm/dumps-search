#!/usr/bin/env python3
"""Simple main CLI application for ExamTopics PDF Scraper."""

import argparse
import logging
import sys

from config import ConfigManager
from search import SearchEngine


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
    parser.add_argument('--question', type=int, required=True, help='Question number to search')
    parser.add_argument('--topic', type=int, default=1, help='Topic number (default: 1)')
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
        
        # Replace placeholders in title and keyword
        title = exam_config['title'].replace('#TOPIC', str(args.topic)).replace('#QUESTION', str(args.question))
        keyword = exam_config['keyword'].replace('#TOPIC', str(args.topic)).replace('#QUESTION', str(args.question))
        url_substring = exam_config['url_substring']
        
        logger.info(f"Searching for question {args.question} in topic {args.topic}")
        logger.info(f"Title: {title}")
        logger.info(f"Keyword: {keyword}")
        
        # Perform search
        result_url = search_engine.search_question(keyword, title, url_substring)
        
        if result_url:
            print(f"\n✓ SUCCESS: Found URL for question {args.question}")
            print(f"URL: {result_url}")
        else:
            print(f"\n✗ FAILED: No valid URL found for question {args.question}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
