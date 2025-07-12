"""Configuration management for ExamTopics PDF Scraper."""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration loading and validation for the scraper."""
    
    def __init__(self, config_path: str = "settings.json"):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config_path = config_path
        self.config = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file.
        
        Returns:
            Dictionary containing the configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.validate_config()
            return self.config
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file: {e}", e.doc, e.pos)
    
    def get_exam_config(self, exam_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve configuration for a specific exam.
        
        Args:
            exam_code: The exam code to look up
            
        Returns:
            Dictionary containing exam configuration or None if not found
        """
        if not self.config:
            self.load_config()
            
        for exam in self.config.get('exams', []):
            if exam.get('exam') == exam_code:
                return exam
                
        return None
    
    def validate_config(self) -> None:
        """Validate the loaded configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config:
            raise ValueError("No configuration loaded")
            
        # Check required top-level fields
        required_fields = ['site', 'exams']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate exams configuration
        if not isinstance(self.config['exams'], list):
            raise ValueError("'exams' must be a list")
            
        if not self.config['exams']:
            raise ValueError("At least one exam configuration is required")
            
        # Validate each exam configuration
        for i, exam in enumerate(self.config['exams']):
            self._validate_exam_config(exam, i)
    
    def _validate_exam_config(self, exam: Dict[str, Any], index: int) -> None:
        """Validate a single exam configuration.
        
        Args:
            exam: Exam configuration dictionary
            index: Index of the exam in the list (for error messages)
            
        Raises:
            ValueError: If exam configuration is invalid
        """
        required_exam_fields = ['exam', 'title', 'keyword', 'url_substring']
        
        for field in required_exam_fields:
            if field not in exam:
                raise ValueError(f"Missing required field '{field}' in exam {index}")
            
            if not isinstance(exam[field], str) or not exam[field].strip():
                raise ValueError(f"Field '{field}' must be a non-empty string in exam {index}")
    
    def get_site_url(self) -> str:
        """Get the base site URL.
        
        Returns:
            Base site URL
        """
        if not self.config:
            self.load_config()
            
        return self.config.get('site', 'https://www.examtopics.com')
    
    def get_log_level(self) -> str:
        """Get the configured log level.
        
        Returns:
            Log level string (default: 'info')
        """
        if not self.config:
            self.load_config()
            
        return self.config.get('log_level', 'info')
    
    def list_available_exams(self) -> list:
        """Get list of available exam codes.
        
        Returns:
            List of exam codes
        """
        if not self.config:
            self.load_config()
            
        return [exam['exam'] for exam in self.config.get('exams', [])]
