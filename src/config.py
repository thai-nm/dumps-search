import json
import os
from typing import Dict, Any, Optional


class ConfigManager:

    def __init__(self, config_path: str = "settings.json"):
        self.config_path = config_path
        self.config = None

    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

            self.validate_config()
            return self.config

        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in config file: {e}", e.doc, e.pos
            )

    def get_exam_config(self, exam_code: str) -> Optional[Dict[str, Any]]:
        if not self.config:
            self.load_config()

        for exam in self.config.get("exams", []):
            if exam.get("exam") == exam_code:
                return exam

        return None

    def validate_config(self) -> None:
        if not self.config:
            raise ValueError("No configuration loaded")

        # Check required top-level fields
        required_fields = ["site", "exams"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field: {field}")

        # Validate exams configuration
        if not isinstance(self.config["exams"], list):
            raise ValueError("'exams' must be a list")

        if not self.config["exams"]:
            raise ValueError("At least one exam configuration is required")

        # Validate each exam configuration
        for i, exam in enumerate(self.config["exams"]):
            self._validate_exam_config(exam, i)

    def _validate_exam_config(self, exam: Dict[str, Any], index: int) -> None:
        required_exam_fields = ["exam", "title", "keyword", "url_substring"]

        for field in required_exam_fields:
            if field not in exam:
                raise ValueError(f"Missing required field '{field}' in exam {index}")

            if not isinstance(exam[field], str) or not exam[field].strip():
                raise ValueError(
                    f"Field '{field}' must be a non-empty string in exam {index}"
                )

    def get_site_url(self) -> str:
        if not self.config:
            self.load_config()

        return self.config.get("site", "https://www.examtopics.com")

    def get_log_level(self) -> str:
        if not self.config:
            self.load_config()

        return self.config.get("log_level", "info")

    def list_available_exams(self) -> list:
        if not self.config:
            self.load_config()

        return [exam["exam"] for exam in self.config.get("exams", [])]
