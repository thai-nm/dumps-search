import logging
import sys


def get_app_logger(name: str = "examtopics") -> logging.Logger:
    """Get the application logger instance."""
    return logging.getLogger(name)


def setup_logging(log_level: str = "info", logger_name: str = "examtopics"):
    """Setup logging configuration for the application."""
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }

    level = level_map.get(log_level.lower(), logging.INFO)

    # Root logger
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Application logger
    app_logger = logging.getLogger(logger_name)
    app_logger.setLevel(level)
    
    return app_logger
