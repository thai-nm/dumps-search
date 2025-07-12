import weasyprint
import PyPDF2
import pprint
import time
import asyncio
import urllib.parse
from urllib.parse import urljoin

from parser import prepare_parser
from playwright.async_api import async_playwright

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


async def get_answer_url(exam_id, index, max_retries=3):
    query = f"{EXAM[exam_id]['query']} {index}"
    
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                # Launch browser with more human-like settings
                browser = await p.chromium.launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-extensions',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/New_York'
                )
                
                # Add extra headers to look more human
                await context.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                })
                
                page = await context.new_page()
                
                # Remove automation indicators
                await page.evaluate('''
                    () => {
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                    }
                ''')
                
                print(f"Navigating to Google search for: {query}")
                
                # First, go to Google homepage to establish session
                await page.goto("https://www.google.com")
                await asyncio.sleep(2)
                
                # Simulate human behavior: scroll and move mouse
                await page.mouse.move(400, 300)
                await asyncio.sleep(1)
                await page.mouse.move(600, 400)
                await asyncio.sleep(1)
                
                # Navigate to search
                search_url = "https://www.google.com/search?q=" + query.replace(" ", "+")
                await page.goto(search_url)
                
                # Wait and simulate human reading behavior
                await asyncio.sleep(3)
                await page.mouse.move(500, 500)
                await asyncio.sleep(2)
                
                # Check what we actually got
                title = await page.title()
                print(f"Page title: {title}")
                
                # Check for CAPTCHA or bot detection
                page_content = await page.content()
                if 'captcha' in page_content.lower() or 'robot' in page_content.lower():
                    print("CAPTCHA detected! Trying to wait it out...")
                    await page.screenshot(path=f"captcha_screenshot_{index}_{attempt}.png")
                    
                    # Wait longer and try to proceed
                    await asyncio.sleep(10)
                    
                    # Try to refresh the page
                    await page.reload()
                    await asyncio.sleep(5)
                    
                    # Check again
                    page_content = await page.content()
                    if 'captcha' in page_content.lower():
                        print("Still showing CAPTCHA after refresh")
                        await browser.close()
                        continue
                
                # Try different selectors that might work
                search_selectors = [
                    "div#search",
                    "div#main",
                    "div[role='main']",
                    "#search",
                    "#main",
                    ".g",  # Google search result items
                    "[data-ved]",  # Google search results have data-ved attributes
                    "div.g"  # More specific search result selector
                ]
                
                found_selector = None
                for selector in search_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        found_selector = selector
                        print(f"Found selector: {selector}")
                        break
                    except:
                        continue
                
                if not found_selector:
                    # If no selector found, let's see what's on the page
                    print("No search results selectors found. Checking page content...")
                    print(f"Page contains 'search'? {'search' in page_content.lower()}")
                    print(f"Page contains 'captcha'? {'captcha' in page_content.lower()}")
                    print(f"Page contains 'sorry'? {'sorry' in page_content.lower()}")
                    
                    # Save a screenshot for debugging
                    await page.screenshot(path=f"debug_screenshot_{index}_{attempt}.png")
                    print(f"Screenshot saved as debug_screenshot_{index}_{attempt}.png")
                    
                    await browser.close()
                    continue
                
                # Extract search result URLs using multiple methods
                results = []
                
                # Method 1: Traditional Google search links
                try:
                    results1 = await page.evaluate('''
                        () => {
                            const links = Array.from(document.querySelectorAll('a[href*="/url?q="]'));
                            return links.map(link => {
                                const url = new URL(link.href);
                                return url.searchParams.get('q');
                            }).filter(url => url && url.startsWith('http'));
                        }
                    ''')
                    results.extend(results1)
                except Exception as e:
                    print(f"Method 1 failed: {e}")
                
                # Method 2: Direct links in search results
                try:
                    results2 = await page.evaluate('''
                        () => {
                            const links = Array.from(document.querySelectorAll('a[href^="http"]'));
                            return links.map(link => link.href).filter(url => 
                                url.includes('examtopic') || url.includes('exam')
                            );
                        }
                    ''')
                    results.extend(results2)
                except Exception as e:
                    print(f"Method 2 failed: {e}")
                
                # Method 3: All links containing examtopic
                try:
                    results3 = await page.evaluate('''
                        () => {
                            const links = Array.from(document.querySelectorAll('a'));
                            return links.map(link => link.href).filter(url => 
                                url && url.includes('examtopic')
                            );
                        }
                    ''')
                    results.extend(results3)
                except Exception as e:
                    print(f"Method 3 failed: {e}")
                
                # Remove duplicates
                results = list(set(results))
                print(f"Found {len(results)} total URLs")
                
                await browser.close()
                
                # Find the URL that matches our keyword pattern
                for url in results:
                    print(f"Checking URL: {url}")
                    
                    # Extract original URL from Google Translate links
                    original_url = url
                    if 'translate.google.com' in url and 'u=' in url:
                        parsed = urllib.parse.urlparse(url)
                        params = urllib.parse.parse_qs(parsed.query)
                        if 'u' in params:
                            original_url = params['u'][0]
                            print(f"Extracted original URL: {original_url}")
                    
                    if f"{EXAM[exam_id]['keyword']}-{index}" in original_url:
                        print(f"Found URL for question #{index}: {original_url}")
                        return original_url
                
                print(f"No matching URL found for question #{index} in {len(results)} results")
                if results:
                    print("Available URLs:")
                    for i, url in enumerate(results[:5]):  # Show first 5 URLs
                        print(f"  {i+1}. {url}")
                return None
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for question {index}: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5  # Longer wait times
                print(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                print(f"All attempts failed for question {index}")
                return None


def save_question_pages_as_pdf(exam_id, question_index, page_range):
    answer_url = asyncio.run(get_answer_url(exam_id, question_index))
    pdf_filename = f"question-{question_index}.pdf"

    if answer_url:
        try:
            print(f"Rendering PDF from answer page question #{question_index}")
            # Use weasyprint to generate PDF from URL
            html_doc = weasyprint.HTML(answer_url)
            html_doc.write_pdf(pdf_filename)
            
            # Read the generated PDF
            with open(pdf_filename, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
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
            return None
    else:
        print(f"Question {question_index} not found")
        return None


def merge_pdfs(input_pdfs, output_pdf="merge.pdf"):
    pdf_merger = PyPDF2.PdfMerger()

    try:
        print(f"Merging PDFs to {output_pdf}")
        for pdf in input_pdfs:
            if pdf:  # Only merge if PDF was successfully created
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
