import requests
from bs4 import BeautifulSoup
import pdfkit
import time
from lxml import html
import re
from tqdm import tqdm
import os

###################### CHANGE THESE #################################
BOOK_URL = "https://www.royalroad.com/fiction/21220/mother-of-learning"
BOOK_NAME = "Mother of Learning"
WKHTMLTOPDF_PATH = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
#####################################################################


BOOK_FOLDER = "books"
TEMP_HTML_FILE = "temp_book.html"
TIME_DELAY = 0.1

headers = {
	"User-Agent": "Mozilla/5.0"
}

toc = {
    'toc-header-text': 'Table of Contents',
}

options = {
    'page-width': '6in',
    'page-height': '9in',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8',
    'disable-smart-shrinking': ''
}

def extract_chapter_slugs_and_ids(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    tree = html.fromstring(response.content)

    # XPath to select all chapter rows in the table of contents
    chapter_rows = tree.xpath('//table[@id="chapters"]/tbody/tr')

    chapters = []

    def chapter_title_to_slug(title):
        # Replace ' - ' or em-dash/en-dash with a hyphen
        title = re.sub(r'\s*[-–—]\s*', '-', title)
        # Remove characters not allowed in slugs (keep alphanumerics and hyphens)
        title = re.sub(r'[^\w\- ]', '', title)
        # Replace all whitespace with hyphens
        title = re.sub(r'\s+', '-', title)
        # Collapse multiple hyphens
        title = re.sub(r'-{2,}', '-', title)
        # Strip leading/trailing hyphens
        return title.strip('-')

    for row in chapter_rows:
        # Extract the chapter name and link
        chapter_name = row.xpath('.//td[1]/a/text()')
        href = row.xpath('.//td[1]/a/@href')

        if chapter_name and href:
            # Extract chapter ID from the href link
            match = re.search(r'/chapter/(\d+)', href[0])
            if match:
                chapter_id = match.group(1)
                # Append the tuple (slug, chapter_id)
                chapter_slug = chapter_title_to_slug(chapter_name[0].strip())
                chapters.append((chapter_slug, chapter_id))

    return chapters



# Function to extract the HTML content of each chapter
def extract_chapter_html(chapter_url):
    # print(f"Extracting {chapter_url}")
    res = requests.get(chapter_url, headers=headers)
    res.raise_for_status()  # Ensure we notice bad responses
    soup = BeautifulSoup(res.text, "lxml")

    # Extract chapter content
    content_div = soup.select_one('div.chapter-inner.chapter-content')
    title = soup.select_one('h1')  # Optional, add title per chapter

    html = f"<h1>{title.text.strip()}</h1>\n" if title else ""
    html += str(content_div)

    return html



# Main function to process all chapters and generate a PDF
def main():
    os.makedirs(BOOK_FOLDER, exist_ok=True)
    chapters = extract_chapter_slugs_and_ids(BOOK_URL)

    full_html = "<html><head><meta charset='UTF-8'></head><body>"
    
    for slug, chapter_id in tqdm(chapters, desc="Processing Chapters", unit="chapter"):
        chapter_url = f'{BOOK_URL}/chapter/{chapter_id}/{slug}'
        try:
            # tqdm.write(f"Processing chapter: {slug}")
            chapter_html = extract_chapter_html(chapter_url)
            full_html += chapter_html + "<div style='page-break-after: always;'></div>"
        except Exception as e:
            tqdm.write(f"Failed to extract {chapter_url}: {e}")
        time.sleep(TIME_DELAY)  # Add delay to prevent overwhelming the server

    full_html += "</body></html>"

    # Save HTML to a temporary file
    with open(TEMP_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(full_html)

    # Convert HTML file to PDF with TOC
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdfkit.from_file(
        TEMP_HTML_FILE,
        f"{BOOK_FOLDER}/{BOOK_NAME}.pdf",
        configuration=config,
        options=options,
        toc=toc
    )

    # Remove the temporary HTML file
    os.remove(TEMP_HTML_FILE)
    print(f"PDF created: {BOOK_NAME}.pdf")


if __name__ == "__main__":
    main()	
