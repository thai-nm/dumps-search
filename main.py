import weasyprint
import PyPDF2
import pprint

from parser import prepare_parser
from googlesearch import search

EXAM = {
    "aws-scs": {
        "query": "examtopic aws certified security specialty topic 1 question",
        "keyword": "aws-certified-security-specialty-topic-1-question",
    },
    "gcp-ace": {
        "query": "examtopic gcp ace question",
        "keyword": "associate-cloud-engineer-topic-1-question",
    },
}


def get_answer_url(exam_id, index):
    query = f"{EXAM[exam_id]['query']} {index}"
    result_urls = list(search(query, sleep_interval=1))

    for url in result_urls:
        if f"{EXAM[exam_id]['keyword']}-{index}" in url:
            print(f"Found URL for question #{index}: {url}")
            return url
    return None


def save_question_pages_as_pdf(exam_id, question_index, page_range):
    answer_url = get_answer_url(exam_id, question_index)
    pdf_filename = f"question-{question_index}.pdf"

    if answer_url:
        try:
            print(f"Rendering PDF from answer page question #{question_index}")
            weasyprint.HTML(answer_url).write_pdf(pdf_filename)
            pdf = PyPDF2.PdfReader(pdf_filename)
            pdf_writer = PyPDF2.PdfWriter()

            # Save all pages if question contains answer in some first pages
            # Otherwise, save only pages belong to page_range
            if len(pdf.pages) <= 3:
                for page in pdf.pages:
                    pdf_writer.add_page(page)
            else:
                for page_num in page_range:
                    if 1 <= page_num <= len(pdf.pages):
                        pdf_writer.add_page(pdf.pages[page_num - 1])

            with open(pdf_filename, "wb") as output_file:
                pdf_writer.write(output_file)

            print(f"Question {question_index} saved as '{pdf_filename}'")
            return pdf_filename
        except Exception as e:
            print(f"Error saving question {question_index} as PDF: {e}")
    else:
        print(f"Question {index} not found")


def merge_pdfs(input_pdfs, output_pdf="merge.pdf"):
    pdf_merger = PyPDF2.PdfMerger()

    try:
        print(f"Merging PDFs to {output_pdf}")
        for pdf in input_pdfs:
            pdf_merger.append(pdf)

        with open(output_pdf, "wb") as output_file:
            pdf_merger.write(output_file)

        print(f"Merged PDFs saved as '{output_pdf}'")
    except Exception as e:
        print(f"Error merging PDFs: {e}")


if __name__ == "__main__":
    options = prepare_parser().parse_args()
    result_files = []

    for index in range(options.start, options.end + 1):
        result_file = save_question_pages_as_pdf(options.exam, index, options.pages)
        result_files.append(result_file)
    merge_pdfs(result_files)
