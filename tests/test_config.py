"""Tests for configuration management module."""

import json
import os
import tempfile
import pytest
from src.config import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        # Create a temporary config file
        config_data = {
            "site": "https://www.examtopics.com",
            "log_level": "info",
            "exams": [
                {
                    "exam": "test-exam",
                    "title": "Test Exam #QUESTION",
                    "keyword": "test keyword #QUESTION",
                    "url_substring": "test-exam-url"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            config_manager = ConfigManager(temp_config_path)
            loaded_config = config_manager.load_config()
            
            assert loaded_config == config_data
            assert config_manager.get_site_url() == "https://www.examtopics.com"
            assert config_manager.get_log_level() == "info"
            
        finally:
            os.unlink(temp_config_path)
    
    def test_load_nonexistent_config(self):
        """Test loading a non-existent configuration file."""
        config_manager = ConfigManager("nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            config_manager.load_config()
    
    def test_load_invalid_json(self):
        """Test loading an invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_config_path = f.name
        
        try:
            config_manager = ConfigManager(temp_config_path)
            
            with pytest.raises(json.JSONDecodeError):
                config_manager.load_config()
                
        finally:
            os.unlink(temp_config_path)
    
    def test_get_exam_config(self):
        """Test retrieving specific exam configuration."""
        config_data = {
            "site": "https://www.examtopics.com",
            "exams": [
                {
                    "exam": "saa-c03",
                    "title": "SAA-C03 #QUESTION",
                    "keyword": "saa keyword #QUESTION",
                    "url_substring": "saa-c03-url"
                },
                {
                    "exam": "dva-c01",
                    "title": "DVA-C01 #QUESTION",
                    "keyword": "dva keyword #QUESTION",
                    "url_substring": "dva-c01-url"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            config_manager = ConfigManager(temp_config_path)
            config_manager.load_config()
            
            saa_config = config_manager.get_exam_config("saa-c03")
            assert saa_config is not None
            assert saa_config["exam"] == "saa-c03"
            assert saa_config["title"] == "SAA-C03 #QUESTION"
            
            nonexistent_config = config_manager.get_exam_config("nonexistent")
            assert nonexistent_config is None
            
        finally:
            os.unlink(temp_config_path)
    
    def test_validate_config_missing_fields(self):
        """Test configuration validation with missing required fields."""
        # Missing 'site' field
        config_data = {
            "exams": [
                {
                    "exam": "test-exam",
                    "title": "Test #QUESTION",
                    "keyword": "test #QUESTION",
                    "url_substring": "test-url"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            config_manager = ConfigManager(temp_config_path)
            
            with pytest.raises(ValueError, match="Missing required field: site"):
                config_manager.load_config()
                
        finally:
            os.unlink(temp_config_path)
    
    def test_validate_exam_config_missing_fields(self):
        """Test exam configuration validation with missing required fields."""
        # Missing 'title' field in exam config
        config_data = {
            "site": "https://www.examtopics.com",
            "exams": [
                {
                    "exam": "test-exam",
                    "keyword": "test #QUESTION",
                    "url_substring": "test-url"
                    # Missing 'title' field
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            config_manager = ConfigManager(temp_config_path)
            
            with pytest.raises(ValueError, match="Missing required field 'title' in exam 0"):
                config_manager.load_config()
                
        finally:
            os.unlink(temp_config_path)
    
    def test_list_available_exams(self):
        """Test listing available exam codes."""
        config_data = {
            "site": "https://www.examtopics.com",
            "exams": [
                {
                    "exam": "saa-c03",
                    "title": "SAA-C03 #QUESTION",
                    "keyword": "saa keyword #QUESTION",
                    "url_substring": "saa-c03-url"
                },
                {
                    "exam": "dva-c01",
                    "title": "DVA-C01 #QUESTION",
                    "keyword": "dva keyword #QUESTION",
                    "url_substring": "dva-c01-url"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            config_manager = ConfigManager(temp_config_path)
            config_manager.load_config()
            
            available_exams = config_manager.list_available_exams()
            assert available_exams == ["saa-c03", "dva-c01"]
            
        finally:
            os.unlink(temp_config_path)
