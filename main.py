import weasyprint
import argparse
import PyPDF2

from parser import prepare_parser
from googlesearch import search


def get_answer_url(index):
    query = f"examtopics gcp ace question {index}"
    search_urls = list(search(query))

    for url in search_urls:
        if "exam-associate-cloud-engineer" in url:
            return url
    return f"Question {index} not found"


def save_question_pages_as_pdf(question_index, pages):
    answer_url = get_answer_url(question_index)
    pdf_filename = f"question-{question_index}.pdf"

    try:
        weasyprint.HTML(answer_url).write_pdf(pdf_filename)

        pdf = PyPDF2.PdfReader(pdf_filename)
        pdf_writer = PyPDF2.PdfWriter()

        for page_num in pages:
            if 1 <= page_num <= len(pdf.pages):
                pdf_writer.add_page(pdf.pages[page_num - 1])

        with open(pdf_filename, "wb") as output_file:
            pdf_writer.write(output_file)

        print(
            f"Question {question_index} - Pages {', '.join(map(str, pages))} saved as '{pdf_filename}'"
        )
    except Exception as e:
        print(f"Error saving question {question_index} as PDF: {e}")


if __name__ == "__main__":
    options = prepare_parser().parse_args()

    for question_index in range(options.start, options.end + 1):
        save_question_pages_as_pdf(question_index, pages=options.pages)
