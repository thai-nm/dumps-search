# ExamTopics PDF Scraper - High-Level Implementation Plan

## Project Overview
A Python CLI tool that searches for exam questions on ExamTopics, downloads them as individual PDF files, and merges them into a single comprehensive PDF document.

## Architecture Components

### 1. Core Modules

#### 1.1 Configuration Manager (`config.py`)
- **Purpose**: Handle JSON configuration loading and validation
- **Responsibilities**:
  - Load settings from `settings.json`
  - Validate exam configurations
  - Provide configuration access to other modules
- **Key Functions**:
  - `load_config()`: Load and parse JSON configuration
  - `get_exam_config(exam_code)`: Retrieve specific exam settings
  - `validate_config()`: Ensure all required fields are present

#### 1.2 Search Engine (`search.py`)
- **Purpose**: Handle DuckDuckGo search operations
- **Responsibilities**:
  - Perform web searches using DuckDuckGo API
  - Filter and validate search results
  - Return relevant ExamTopics URLs
- **Key Functions**:
  - `search_question(keyword, url_substring)`: Search for specific question
  - `validate_url(url, url_substring)`: Check if URL belongs to target exam
  - `get_first_valid_url(results, url_substring)`: Extract first valid URL

#### 1.3 PDF Generator (`pdf_generator.py`)
- **Purpose**: Convert web pages to PDF using weasyprint
- **Responsibilities**:
  - Download web page content
  - Convert HTML to PDF format
  - Handle PDF generation errors
- **Key Functions**:
  - `generate_pdf(url, output_path)`: Convert URL to PDF
  - `setup_pdf_options()`: Configure weasyprint settings
  - `handle_generation_errors()`: Error handling and logging

#### 1.4 PDF Merger (`pdf_merger.py`)
- **Purpose**: Combine multiple PDF files into one
- **Responsibilities**:
  - Merge individual question PDFs
  - Maintain proper page ordering
  - Handle file cleanup
- **Key Functions**:
  - `merge_pdfs(pdf_list, output_path)`: Combine PDFs
  - `cleanup_temp_files(file_list)`: Remove temporary files
  - `validate_pdf_files(file_list)`: Check PDF integrity

#### 1.5 Logger (`logger.py`)
- **Purpose**: Centralized logging system
- **Responsibilities**:
  - Configure logging levels
  - Format log messages
  - Handle log output destinations
- **Key Functions**:
  - `setup_logger(log_level)`: Initialize logging
  - `log_progress(current, total)`: Progress tracking
  - `log_error(error, context)`: Error logging with context

### 2. Main Application (`main.py`)

#### 2.1 CLI Interface
- **Framework**: argparse
- **Parameters**:
  - `--exam`: Exam code (required)
  - `--start`: Starting question number (required)
  - `--end`: Ending question number (required)
  - `--output`: Output directory (optional, default: ./output)
  - `--config`: Configuration file path (optional, default: ./settings.json)
  - `--topic`: Topic number (optional, for exams with topics)

#### 2.2 Main Workflow
```python
def main(exam, start, end, output_dir, config_path, topic=None):
    1. Load configuration
    2. Validate exam exists in config
    3. Create output directory
    4. Initialize logger
    5. Process each question (start to end)
    6. Merge all PDFs
    7. Cleanup temporary files
    8. Report completion status
```

### 3. Data Flow

```
User Input (CLI) → Configuration Loading → Question Processing Loop → PDF Generation → PDF Merging → Final Output
```

#### 3.1 Question Processing Loop
For each question number:
1. **Template Replacement**: Replace placeholders in keyword/title templates
2. **Search Execution**: Use DuckDuckGo to find relevant URLs
3. **URL Validation**: Filter URLs containing the exam substring
4. **PDF Generation**: Convert first valid URL to PDF
5. **Error Handling**: Log failures and continue with next question

### 4. File Structure

```
dumps-search/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── search.py
│   ├── pdf_generator.py
│   ├── pdf_merger.py
│   └── logger.py
├── tests/
│   ├── test_config.py
│   ├── test_search.py
│   ├── test_pdf_generator.py
│   └── test_pdf_merger.py
├── output/
├── settings.json
├── requirements.txt
├── setup.py
└── README.md
```

### 5. Dependencies

#### 5.1 Core Dependencies
- **duckduckgo-search**: Web search functionality
- **weasyprint**: HTML to PDF conversion
- **PyPDF2/pypdf**: PDF manipulation and merging
- **argparse**: CLI interface framework (built-in)

#### 5.2 Optional Dependencies
- **tqdm**: Progress bars
- **pytest**: Testing framework

### 6. Error Handling Strategy

#### 6.1 Error Categories
- **Configuration Errors**: Invalid JSON, missing exam configs
- **Network Errors**: Search failures, URL access issues
- **PDF Generation Errors**: Conversion failures, file write issues
- **File System Errors**: Directory creation, file permissions

#### 6.2 Recovery Mechanisms
- **Retry Logic**: Automatic retries for network operations
- **Graceful Degradation**: Continue processing remaining questions on failures
- **Detailed Logging**: Comprehensive error reporting for debugging

### 7. Testing Strategy

#### 7.1 Unit Tests
- Configuration loading and validation
- Search result filtering
- PDF generation with mock URLs
- PDF merging functionality

This implementation plan provides a solid foundation for building a simple, focused ExamTopics PDF scraper CLI tool.
