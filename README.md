# dumps-search

A simple Python CLI tool to search for questions/answers of a specific topic on Exam Topics and save them as PDF files.

## Current Status

**Phase 1: Project Setup and Foundation** ✅ **COMPLETED**

- ✅ Basic project structure created
- ✅ CLI interface with argparse implemented
- ✅ Argument validation working
- ✅ Help and version commands functional
- ✅ Development environment ready

## Installation

1. Clone the repository:
```bash
git clone https://github.com/thai-nm/dumps-search.git
cd dumps-search
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

```bash
python3 -m src.dumps_search.cli "keyword" start_number end_number [options]
```

### Examples

```bash
# Basic usage
python3 -m src.dumps_search.cli "AWS Solutions Architect" 1 50

# With custom output file
python3 -m src.dumps_search.cli "Azure Fundamentals" 10 25 --output azure_questions.pdf

# Dry run to see what would be done
python3 -m src.dumps_search.cli "CompTIA Security+" 1 100 --dry-run --verbose

# Show help
python3 -m src.dumps_search.cli --help

# Show version
python3 -m src.dumps_search.cli --version
```

### Options

- `keyword`: The keyword to search for the topic on Exam Topics
- `start`: The start number of question (inclusive)
- `end`: The end number of question (inclusive)
- `--output, -o`: Output PDF filename (default: output.pdf)
- `--verbose`: Enable verbose output
- `--dry-run`: Show what would be done without actually doing it
- `--help, -h`: Show help message
- `--version, -v`: Show version number

## Project Structure

```
dumps-search/
├── src/
│   └── dumps_search/
│       ├── __init__.py
│       └── cli.py
├── tests/
│   └── __init__.py
├── requirements.txt
├── README.md
├── tool-demonstration.md
└── .gitignore
```

## Development Phases

- **Phase 1**: Project Setup and Foundation ✅
- **Phase 2**: Search Functionality (Next)
- **Phase 3**: PDF Generation from URLs
- **Phase 4**: PDF Processing and Merging
- **Phase 5**: Enhanced CLI and User Experience
- **Phase 6**: Testing and Quality Assurance

## Contributing

This is a personal project for educational purposes. See `tool-demonstration.md` for detailed implementation plans.

## License

MIT License
