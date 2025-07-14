# ExamTopics PDF Scraper

*With the free tier, ExamTopics only allows limited access to questions and answers. This tool searches for exam questions on ExamTopics, downloads them as individual PDF files, and optionally merges them into a single comprehensive study document.*

## Prerequisites

- `python` >= `3.9`

## Supported Exams

- `saa-c03`: AWS Certified Solutions Architect Associate (Topic 1)
- `az-104-1`: Microsoft Azure Administrator (Topic 1)
- `sap-c02-01`: AWS Certified Solutions Architect Professional (Topic 1) 

## Setup

This tool uses [Weasyprint](https://weasyprint.org/). 

So depends on your OS, you might need to install its dependencies first:

- Linux: [Install weasyprint on Linux](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#linux)
- macOS with `python` installed by `homebrew`:
```bash
brew install weasyprint
```bash
brew install weasyprint

# GitHub issue: https://github.com/Kozea/WeasyPrint/issues/1448
sudo mkdir -p /usr/local/lib
sudo ln -s /opt/homebrew/opt/glib/lib/libgobject-2.0.0.dylib /usr/local/lib/gobject-2.0
sudo ln -s /opt/homebrew/opt/pango/lib/libpango-1.0.dylib /usr/local/lib/pango-1.0
sudo ln -s /opt/homebrew/opt/harfbuzz/lib/libharfbuzz.dylib /usr/local/lib/harfbuzz
sudo ln -s /opt/homebrew/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1
sudo ln -s /opt/homebrew/opt/pango/lib/libpangoft2-1.0.dylib /usr/local/lib/pangoft2-1.0
```

Set up virtual environment and install dependencies:
```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py --exam EXAM_CODE --begin START --end END [OPTIONS]
```

### Required Arguments

- `--exam`: Exam code
- `--begin`: Starting question number
- `--end`: Ending question number

### Optional Arguments

- `--output`: Output directory (default: `output`)
- `--config`: Configuration file path (default: `settings.json`)
- `--no-merge`: Skip PDF merging, keep only individual files
- `--keep-individual`: Keep individual PDFs after merging

### Examples

- Download questions 1-10 for AWS SAA-C03:
```bash
python src/main.py --exam saa-c03 --begin 1 --end 10
```

- Download to custom directory without merging:
```bash
python src/main.py --exam saa-c03 --begin 1 --end 5 --output my-pdfs --no-merge
```

## Configuration

The tool uses `settings.json` to configure exam parameters and search behavior. Here's how to understand and modify the settings:

### Settings Structure

```json
{
  "site": "https://www.examtopics.com",
  "log_level": "info",
  "exams": [
    {
      "exam": "saa-c03",
      "title": "Associate SAA-C03 topic 1 question #QUESTION discussion",
      "keyword": "Associate SAA-C03 topic 1 question #QUESTION discussion",
      "url_substring": "exam-aws-certified-solutions-architect-associate-saa-c03"
    }
  ]
}
```

### Settings Explanation

**Global Settings:**
- `site`: The base ExamTopics URL (usually doesn't need to change)
- `log_level`: Logging verbosity (`debug`, `info`, `warning`, `error`)

**Exam Configuration:**
- `exam`: Unique identifier used with `--exam` parameter
- `title`: Page title used to find question URLs
- `keyword`: Search keyword used to find question URLs
- `url_substring`: Unique part of ExamTopics URLs to validate correct results

**Placeholders:**
- `#QUESTION`: Automatically replaced with the actual question number during search

### Adding New Exams

You can open an issue to ask for support on a new exam.

OR you can add it yourself by:

- Find the exam on ExamTopics and note the URL pattern
- Add a new exam object to the `exams` array of `settings.json`:

```json
{
  "exam": "your-exam-code",
  "title": "Exam Title topic 1 question #QUESTION discussion",
  "keyword": "Exam Title topic 1 question #QUESTION discussion",
  "url_substring": "unique-part-of-exam-url"
}
```
