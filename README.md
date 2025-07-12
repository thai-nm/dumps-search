# ExamTopics PDF Scraper

A Python CLI tool that searches for exam questions on ExamTopics, downloads them as individual PDF files, and merges them into a single comprehensive PDF document.

## Project Status

This project is currently in **Phase 1: Foundation Setup** of development.

### Completed Features

✅ **Phase 1.1: Project Infrastructure**
- Project directory structure created
- Virtual environment setup
- Git repository initialized
- Basic `requirements.txt` with core dependencies
- `.gitignore` file with Python-specific exclusions

✅ **Phase 1.2: Configuration System**
- `config.py` module implementation with `ConfigManager` class
- `settings.json` template with sample exam configurations
- Configuration validation logic
- Comprehensive test suite for configuration management

## Project Structure

```
dumps-search/
├── src/
│   ├── __init__.py
│   └── config.py          # Configuration management
├── tests/
│   ├── __init__.py
│   └── test_config.py     # Configuration tests
├── docs/
│   ├── implementation-phases.md
│   ├── implementation-plan.md
│   └── tool-demonstration.md
├── output/                # Generated PDFs will be stored here
├── venv/                  # Virtual environment
├── .gitignore
├── requirements.txt       # Project dependencies
├── settings.json          # Configuration file
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/thai-nm/dumps-search.git
cd dumps-search
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The project uses `settings.json` for configuration. Currently configured exams:

- **SAA-C03**: AWS Certified Solutions Architect Associate

### Configuration Format

```json
{
  "site": "https://www.examtopics.com",
  "log_level": "info",
  "exams": [
    {
      "exam": "saa-c03",
      "title": "Associate SAA-C03 topic #TOPIC question #QUESTION",
      "keyword": "Associate SAA-C03 topic #TOPIC question #QUESTION",
      "url_substring": "exam-aws-certified-solutions-architect-associate-saa-c03"
    }
  ]
}
```

## Testing

Run the test suite:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_config.py -v
```

## Development Dependencies

- **duckduckgo-search**: Web search functionality
- **weasyprint**: HTML to PDF conversion
- **pypdf**: PDF manipulation and merging
- **requests**: HTTP requests for web content
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **tqdm**: Progress bars

## Next Steps

The following phases are planned for development:

- **Phase 2**: Core Functionality (Search Engine & PDF Generation)
- **Phase 3**: Integration and Processing (PDF Merger & Logging)
- **Phase 4**: Documentation and Deployment
- **Phase 5**: Testing and Quality Assurance

## License

This project is for educational purposes only.
