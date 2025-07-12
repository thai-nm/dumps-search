# ExamTopics PDF Scraper

A Python CLI tool that searches for exam questions on ExamTopics, downloads them as individual PDF files, and merges them into a single comprehensive PDF document.

## Project Status

This project is currently in **Phase 2: Core Functionality** of development.

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

✅ **Phase 2.1: Search Engine Implementation**
- `search.py` module with DuckDuckGo integration
- URL validation and filtering logic
- Search result processing functions
- Error handling for network operations

✅ **Phase 2.2: Main Application Integration**
- `main.py` with complete CLI interface
- Support for question ranges (--begin and --end parameters)
- Argument parsing and validation
- Main workflow orchestration for processing multiple questions
- Progress tracking and summary reporting

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

## Usage

The tool now supports processing ranges of questions using the `--begin` and `--end` parameters:

```bash
# Search for questions 1-5 in SAA-C03 exam, topic 1
python src/main.py --exam saa-c03 --begin 1 --end 5 --topic 1

# Search for questions 10-15 with debug logging
python src/main.py --exam saa-c03 --begin 10 --end 15 --topic 1 --log-level debug

# Use custom configuration file
python src/main.py --exam saa-c03 --begin 1 --end 3 --config my-settings.json
```

### Command Line Options

- `--exam`: Exam code (required) - must match an exam in the configuration
- `--begin`: Beginning question number (required)
- `--end`: Ending question number (required)
- `--topic`: Topic number (optional, default: 1)
- `--config`: Configuration file path (optional, default: settings.json)
- `--log-level`: Logging level (optional, choices: debug, info, warning, error)

### Example Output

```
PROCESSING SUMMARY
Total questions processed: 3
Successful: 3
Failed: 0

✓ SUCCESSFUL QUESTIONS:
  Question 1: https://www.examtopics.com/discussions/amazon/view/84973-exam-aws-certified-solutions-architect-associate-saa-c03/
  Question 2: https://www.examtopics.com/discussions/amazon/view/84848-exam-aws-certified-solutions-architect-associate-saa-c03/
  Question 3: https://www.examtopics.com/discussions/amazon/view/84838-exam-aws-certified-solutions-architect-associate-saa-c03/
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
