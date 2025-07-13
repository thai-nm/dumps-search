# tool-demonstration.md

## Objective

A simple Python CLI tool to search for questions/answers of a specific topic on Exam Topics and save them as PDF files.
These PDF files later on will be merged into a single PDF file.

## How it works

- Tool parameters:
  - `exam`: Exam code name
  - `start`: Start number of question
  - `end`: End number of question
- The tool will:
  - Read the JSON configuration file to get the exam setting
    ```json
    {
      "site": "https://www.examtopics.com",
      "log_level": "info",
      "exams": [
        {
          "exam": "saa-c03",
          "title": "Associate SAA-C03 topic 1 question #QUESTION",
          "keyword": "Associate SAA-C03 topic 1 question #QUESTION",
          "url_substring": "exam-aws-certified-solutions-architect-associate-saa-c03"
        }
      ]
    }
    ```

    Explanation:
    - `site`: The site to search
    - `log_level`: Log level of the tool
    - `exam`: Exam code name. The tool will use the input parameter and find if it has a corresponding exam by looking into this field.
    - `title`: The title of the site. The search engine will search for results containing this title
    - `keyword`: The exact keyword for search engine to search
    - `url_substring`: The substring of the question URL. This will use to determine if returned URLs are belong to the target exam.
  - For each question number from `start` to `end`:
    - Search for ExamTopics URLs:
      - Replace the placeholder #QUESTION with the question number
      - Use Duckduckgo to search for top 10 results with the provided exam settings
      - Validate if the result URLs contain `url_substring`
      - Return the first validated URL. If there're none, log to console and skip

    - Use weasyprint to save the returned URL as a PDF file
  - Merge all PDF files into one
