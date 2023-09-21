# Dumps search for ExamTopics
*To generate PDF files containing questions and discussion sessions on ExamTopic.*

# Pre-requiste
- `Python` >= `3.9`

# Supported exams
- Google Cloud Platform - Associate Cloud Engineer
- Amazon Web Services - Certified Security Specialty
# Set up
Set up virtual environment and install dependencies:
```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

# Usage
```
usage: main.py [-h] [--start START] [--end END] [--pages PAGES [PAGES ...]] [--exam {gcp-ace,aws-scs}]

Generate PDFs for GCP ACE exam questions

optional arguments:
  -h, --help                    show this help message and exit
  --start START                 first question index to query
  --end END                     last question index to query
  --pages PAGES [PAGES ...]     specify pages to generate
  --exam {gcp-ace,aws-scs}      exam name
```

Example:

- This will generate PDF files from question #1 to question #31 the exam AWS-SCS:

    ```bash
    python3 main.py --start 1 --end 31 --exam aws-scs
    ```